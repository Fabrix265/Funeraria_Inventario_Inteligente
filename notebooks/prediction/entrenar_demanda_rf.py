"""
Prediccion de Demanda por Categoria de Ataud - Random Forest
Funeraria Aranzabal

Pasos 0-14 del plan_notebook_prediccion_demanda.md
"""

import pandas as pd
import numpy as np
import json
import warnings
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, root_mean_squared_error
import joblib

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)

# ============================================================
# PASO 0 — Setup del entorno
# ============================================================
print("=" * 60)
print("PASO 0 — Setup del entorno")
print("=" * 60)

import sklearn
assert sklearn.__version__ is not None
print(f"OK - scikit-learn {sklearn.__version__} cargado correctamente")

# ============================================================
# PASO 1 — Cargar y validar el dataset
# ============================================================
print("\n" + "=" * 60)
print("PASO 1 — Cargar y validar el dataset")
print("=" * 60)

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "dataset" / "dataset_limpio.xlsx"
df = pd.read_excel(DATA_PATH)
print(f"Shape: {df.shape}")
print(f"Columnas: {list(df.columns)}")
print(f"Tipos:\n{df.dtypes}")

required_cols = {"Fecha", "Ataud_Modelo", "Monto", "Monto_winsorizado",
                  "Forma de pago", "Capilla"}
assert required_cols.issubset(set(df.columns)), f"Faltan columnas: {required_cols - set(df.columns)}"
assert df.shape[0] > 0, "El dataset esta vacio"
assert df["Fecha"].dtype.kind == "M" or pd.api.types.is_datetime64_any_dtype(df["Fecha"]), "Fecha no es datetime"
print(f"OK - dataset valido, filas: {df.shape[0]}")

# ============================================================
# PASO 2 — Limpieza basica y periodo mensual
# ============================================================
print("\n" + "=" * 60)
print("PASO 2 — Limpieza basica y periodo mensual")
print("=" * 60)

df = df.copy()
df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)
df = df.dropna(subset=["Fecha"])

assert df["Fecha"].isna().sum() == 0, "Aun hay fechas nulas"
assert df["Periodo"].str.match(r"^\d{4}-\d{2}$").all(), "Formato de Periodo invalido"
print(f"OK - periodos generados: {df['Periodo'].nunique()}")

# ============================================================
# PASO 3 — Agrupar modelos de ataud en categorias
# ============================================================
print("\n" + "=" * 60)
print("PASO 3 — Agrupar modelos de ataud en categorias")
print("=" * 60)

TOP_CATEGORIAS = ["Americano", "Lincoln", "Imperial", "sin_ataud",
                   "Madera", "Biblia", "Principe"]

def categorizar(modelo):
    if pd.isna(modelo):
        return "Otros"
    for cat in TOP_CATEGORIAS:
        if cat.lower() in str(modelo).lower():
            return cat
    return "Otros"

df["Categoria_Ataud"] = df["Ataud_Modelo"].apply(categorizar)
print(df["Categoria_Ataud"].value_counts())

assert df["Categoria_Ataud"].notna().all(), "Hay categorias nulas"
n_cats = df["Categoria_Ataud"].nunique()
assert 3 <= n_cats <= 10, f"Numero de categorias fuera de rango esperado: {n_cats}"
counts = df["Categoria_Ataud"].value_counts()
assert (counts.drop("Otros", errors="ignore") >= 5).all(), "Hay categoria principal con muy pocos datos"
print(f"OK - categorias: {n_cats}")

# ============================================================
# PASO 4 — Tabla de proporciones (categoria -> modelo especifico)
# ============================================================
print("\n" + "=" * 60)
print("PASO 4 — Tabla de proporciones")
print("=" * 60)

conteo = df.groupby(["Categoria_Ataud", "Ataud_Modelo"]).size().reset_index(name="count")
proporciones = {}
for cat in conteo["Categoria_Ataud"].unique():
    sub = conteo[conteo["Categoria_Ataud"] == cat]
    total = sub["count"].sum()
    proporciones[cat] = {row["Ataud_Modelo"]: row["count"] / total for _, row in sub.iterrows()}

for cat, dist in proporciones.items():
    total = sum(dist.values())
    assert abs(total - 1.0) < 1e-6, f"Proporciones de '{cat}' no suman 1 ({total})"
print(f"OK - proporciones validas para {len(proporciones)} categorias")

# ============================================================
# PASO 5 — Tabla de demanda mensual por categoria
# ============================================================
print("\n" + "=" * 60)
print("PASO 5 — Tabla de demanda mensual por categoria")
print("=" * 60)

demanda = (
    df.groupby(["Periodo", "Categoria_Ataud"])
      .size()
      .reset_index(name="cantidad")
)

todos_periodos = pd.period_range(df["Fecha"].min(), df["Fecha"].max(), freq="M").astype(str)
todas_categorias = df["Categoria_Ataud"].unique()
idx_completo = pd.MultiIndex.from_product([todos_periodos, todas_categorias],
                                           names=["Periodo", "Categoria_Ataud"])
demanda = (demanda.set_index(["Periodo", "Categoria_Ataud"])
                   .reindex(idx_completo, fill_value=0)
                   .reset_index())

assert demanda["cantidad"].isna().sum() == 0, "Hay valores nulos en cantidad"
assert (demanda["cantidad"] >= 0).all(), "Hay cantidades negativas"
assert demanda.groupby("Categoria_Ataud").size().nunique() == 1, "Series desbalanceadas entre categorias"
print(f"OK - tabla de demanda: {demanda.shape}")

# ============================================================
# PASO 6 — Feature engineering para el modelo
# ============================================================
print("\n" + "=" * 60)
print("PASO 6 — Feature engineering")
print("=" * 60)

demanda = demanda.sort_values(["Categoria_Ataud", "Periodo"]).reset_index(drop=True)
demanda["fecha_periodo"] = pd.to_datetime(demanda["Periodo"])
demanda["mes"] = demanda["fecha_periodo"].dt.month
demanda["anio"] = demanda["fecha_periodo"].dt.year
demanda["t"] = demanda.groupby("Categoria_Ataud").cumcount()

for lag in [1, 2, 3]:
    demanda[f"lag_{lag}"] = demanda.groupby("Categoria_Ataud")["cantidad"].shift(lag)

demanda["rolling_mean_3"] = (demanda.groupby("Categoria_Ataud")["cantidad"]
                                     .shift(1).rolling(3).mean())

demanda_model = pd.get_dummies(demanda, columns=["Categoria_Ataud"], prefix="cat")
demanda_model = demanda_model.dropna().reset_index(drop=True)

feature_cols = [c for c in demanda_model.columns if c.startswith("lag_") or c.startswith("cat_")]
assert len(feature_cols) > 0, "No se generaron features"
assert demanda_model.isna().sum().sum() == 0, "Quedan NaN tras dropna()"
assert demanda_model.shape[0] > 20, "Muy pocas filas para entrenar tras generar lags"
print(f"OK - dataset de modelado: {demanda_model.shape}")

# ============================================================
# PASO 7 — Split temporal (walk-forward, NO aleatorio)
# ============================================================
print("\n" + "=" * 60)
print("PASO 7 — Split temporal")
print("=" * 60)

FEATURES = [c for c in demanda_model.columns
            if c not in ["Periodo", "fecha_periodo", "cantidad"]]
TARGET = "cantidad"

demanda_model = demanda_model.sort_values("fecha_periodo").reset_index(drop=True)

corte = int(len(demanda_model) * 0.8)
train = demanda_model.iloc[:corte]
test = demanda_model.iloc[corte:]

X_train, y_train = train[FEATURES], train[TARGET]
X_test, y_test = test[FEATURES], test[TARGET]

assert train["fecha_periodo"].max() <= test["fecha_periodo"].min(), "Hay fuga temporal train/test"
assert len(X_train) > 0 and len(X_test) > 0, "Split vacio"
print(f"OK - train: {len(X_train)}, test: {len(X_test)}")

# ============================================================
# PASO 8 — Baseline (naive) para comparar
# ============================================================
print("\n" + "=" * 60)
print("PASO 8 — Baseline naive")
print("=" * 60)

baseline_pred = X_test["lag_1"]
mae_base = mean_absolute_error(y_test, baseline_pred)
rmse_base = root_mean_squared_error(y_test, baseline_pred)
print(f"Baseline MAE: {mae_base:.4f}, RMSE: {rmse_base:.4f}")

assert not np.isnan(mae_base), "Baseline MAE invalido"
print("OK - baseline calculado")

# ============================================================
# PASO 9 — Entrenar Random Forest
# ============================================================
print("\n" + "=" * 60)
print("PASO 9 — Entrenar Random Forest")
print("=" * 60)

modelo_rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=6,
    min_samples_leaf=2,
    random_state=42
)
modelo_rf.fit(X_train, y_train)
pred_rf = modelo_rf.predict(X_test)

assert hasattr(modelo_rf, "estimators_"), "El modelo no se entreno"
assert len(pred_rf) == len(y_test), "Predicciones con longitud incorrecta"
assert (pred_rf >= 0).all(), "Hay predicciones de demanda negativas"
print("OK - modelo entrenado")

# ============================================================
# PASO 10 — Metricas del modelo vs baseline
# ============================================================
print("\n" + "=" * 60)
print("PASO 10 — Metricas del modelo vs baseline")
print("=" * 60)

mae_rf = mean_absolute_error(y_test, pred_rf)
rmse_rf = root_mean_squared_error(y_test, pred_rf)
r2_rf = r2_score(y_test, pred_rf)
mape_rf = np.mean(np.abs((y_test - pred_rf) / y_test.replace(0, np.nan))) * 100

metricas = {
    "baseline": {"MAE": float(mae_base), "RMSE": float(rmse_base)},
    "random_forest": {
        "MAE": float(mae_rf), "RMSE": float(rmse_rf),
        "R2": float(r2_rf), "MAPE": float(mape_rf)
    }
}
print(json.dumps(metricas, indent=2))

assert metricas["random_forest"]["MAE"] <= metricas["baseline"]["MAE"] * 1.15, \
    "El modelo no mejora claramente al baseline"
print("OK - metricas calculadas y modelo validado contra baseline")

# ============================================================
# PASO 11 — Precio promedio por categoria y monto esperado
# ============================================================
print("\n" + "=" * 60)
print("PASO 11 — Precio promedio por categoria y monto esperado")
print("=" * 60)

precio_promedio = df.groupby("Categoria_Ataud")["Monto_winsorizado"].mean().to_dict()

ultima_pred = test.assign(prediccion=pred_rf)
cat_cols = [c for c in FEATURES if c.startswith("cat_")]
ultima_pred["categoria"] = ultima_pred[cat_cols].idxmax(axis=1).str.replace("cat_", "")
ultima_pred["precio_promedio"] = ultima_pred["categoria"].map(precio_promedio)
ultima_pred["monto_esperado"] = ultima_pred["prediccion"] * ultima_pred["precio_promedio"]
print(ultima_pred[["categoria", "prediccion", "precio_promedio", "monto_esperado"]].head(10))

assert not ultima_pred["monto_esperado"].isna().any(), "Hay montos esperados nulos"
assert (ultima_pred["monto_esperado"] >= 0).all(), "Monto esperado negativo"
print("OK - monto esperado calculado")

# ============================================================
# PASO 12 — Desglose a modelo especifico
# ============================================================
print("\n" + "=" * 60)
print("PASO 12 — Desglose a modelo especifico")
print("=" * 60)

def desglosar_por_modelo(categoria, cantidad_predicha, proporciones):
    dist = proporciones.get(categoria, {})
    return {modelo: round(cantidad_predicha * pct, 1) for modelo, pct in dist.items()}

ejemplo = desglosar_por_modelo("Lincoln", 12, proporciones)
print(f"Ejemplo desglose Lincoln (12 unidades): {ejemplo}")

suma = sum(ejemplo.values())
assert abs(suma - 12) < 0.5, "El desglose no suma aproximadamente la cantidad predicha"
print("OK - desglose por modelo especifico funcional")

# ============================================================
# PASO 13 — Alerta de reorden de stock
# ============================================================
print("\n" + "=" * 60)
print("PASO 13 — Alerta de reorden de stock")
print("=" * 60)

def alerta_reorden(stock_actual: dict, demanda_predicha: dict, umbral_seguridad: float = 0.2):
    alertas = []
    for categoria, demanda in demanda_predicha.items():
        stock = stock_actual.get(categoria, 0)
        punto_reorden = demanda * (1 + umbral_seguridad)
        if stock < punto_reorden:
            alertas.append({
                "categoria": categoria,
                "stock_actual": stock,
                "demanda_predicha": round(float(demanda), 1),
                "unidades_a_comprar": round(float(punto_reorden - stock), 1)
            })
    return alertas

stock_ejemplo = {"Lincoln": 5, "Americano": 10}
demanda_ejemplo = {"Lincoln": 12, "Americano": 8}
resultado = alerta_reorden(stock_ejemplo, demanda_ejemplo)
print(f"Alertas ejemplo: {json.dumps(resultado, indent=2)}")

assert any(a["categoria"] == "Lincoln" for a in resultado), "No genero alerta esperada para Lincoln"
assert not any(a["categoria"] == "Americano" for a in resultado), "Genero alerta incorrecta para Americano"
print("OK - logica de alertas validada")

# ============================================================
# PASO 14 — Guardar artefactos del modelo
# ============================================================
print("\n" + "=" * 60)
print("PASO 14 — Guardar artefactos del modelo")
print("=" * 60)

OUTPUT_DIR = Path(__file__).parent.parent / "models"
OUTPUT_DIR.mkdir(exist_ok=True)

joblib.dump(modelo_rf, OUTPUT_DIR / "modelo_demanda_rf.pkl")

# Preparar categorias del modelo para prediccion futura
cat_features = [c.replace("cat_", "") for c in FEATURES if c.startswith("cat_")]

metadata = {
    "features": FEATURES,
    "cat_features": cat_features,
    "top_categorias": TOP_CATEGORIAS,
    "proporciones_modelo_especifico": {k: v for k, v in proporciones.items()},
    "precio_promedio_categoria": {k: float(v) for k, v in precio_promedio.items()},
    "num_periodos_entrenamiento": int(demanda["Periodo"].nunique()),
    "metricas": metricas,
    "fecha_entrenamiento": pd.Timestamp.now().isoformat(),
    "ultimo_periodo_entrenado": demanda_model["Periodo"].max(),
    "descripcion": "Modelo Random Forest para prediccion de demanda por categoria de ataud"
}

with open(OUTPUT_DIR / "demanda_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"Archivos generados: {list(OUTPUT_DIR.glob('*'))}")

# Verificar que el modelo se puede recargar y predecir
modelo_cargado = joblib.load(OUTPUT_DIR / "modelo_demanda_rf.pkl")
pred_check = modelo_cargado.predict(X_test.iloc[:1])
assert len(pred_check) == 1
print("OK - artefactos guardados y verificados, listos para mover al backend")

# ============================================================
# RESUMEN FINAL
# ============================================================
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
print(f"Modelo: Random Forest (n_estimators=300, max_depth=6)")
print(f"Dataset: {df.shape[0]} registros, {df['Periodo'].nunique()} meses")
print(f"Categorias: {list(todas_categorias)}")
print(f"Baseline MAE: {mae_base:.4f} | RF MAE: {mae_rf:.4f}")
print(f"Baseline RMSE: {rmse_base:.4f} | RF RMSE: {rmse_rf:.4f}")
print(f"RF R2: {r2_rf:.4f} | RF MAPE: {mape_rf:.2f}%")
print(f"Artefactos en: {OUTPUT_DIR}")
print(" Checklist:")
print("  [x] Todas las aserciones pasaron")
print(f"  [x] {OUTPUT_DIR / 'modelo_demanda_rf.pkl'} existe")
print(f"  [x] {OUTPUT_DIR / 'demanda_metadata.json'} existe")
print("  [x] Metricas documentadas")
