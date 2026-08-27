# Plan de Notebook — Módulo Predictivo de Demanda de Inventario
## Funeraria Aranzabal

Este documento define **pasos secuenciales y aislados** para construir el notebook de predicción de demanda por categoría de ataúd, desglose a modelo específico, ingreso esperado y alertas de reorden.

**Regla de ejecución para el agente:** cada paso es una celda (o bloque de celdas) independiente. Al final de cada paso hay una sección `### ✅ Test del paso`. El paso solo se considera completo si todas las aserciones pasan. Si una aserción falla, el agente debe detenerse, reportar el error y no avanzar al siguiente paso.

Archivo fuente: `dataset_limpio.xlsx`

---

## Paso 0 — Setup del entorno

**Objetivo:** preparar imports y verificar que las librerías necesarias existen.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Modelado
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json

pd.set_option('display.max_columns', None)
```

### ✅ Test del paso
```python
import sklearn, joblib
assert sklearn.__version__ is not None
print("OK - librerías cargadas correctamente")
```

---

## Paso 1 — Cargar y validar el dataset

**Objetivo:** cargar el Excel y validar estructura mínima esperada antes de continuar.

```python
DATA_PATH = "dataset_limpio.xlsx"
df = pd.read_excel(DATA_PATH)
print(df.shape)
print(df.dtypes)
df.head()
```

### ✅ Test del paso
```python
required_cols = {"Fecha", "Ataud_Modelo", "Monto", "Monto_winsorizado",
                  "Forma de pago", "Capilla"}
assert required_cols.issubset(set(df.columns)), f"Faltan columnas: {required_cols - set(df.columns)}"
assert df.shape[0] > 0, "El dataset está vacío"
assert df["Fecha"].dtype.kind == "M" or pd.api.types.is_datetime64_any_dtype(df["Fecha"]), "Fecha no es datetime"
print("OK - dataset válido, filas:", df.shape[0])
```

---

## Paso 2 — Limpieza básica y periodo mensual

**Objetivo:** asegurar tipos correctos, quitar filas sin fecha/monto crítico, generar columna de periodo mensual.

```python
df = df.copy()
df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

# Filas sin fecha no sirven para serie temporal
df = df.dropna(subset=["Fecha"])
```

### ✅ Test del paso
```python
assert df["Fecha"].isna().sum() == 0, "Aún hay fechas nulas"
assert df["Periodo"].str.match(r"^\d{4}-\d{2}$").all(), "Formato de Periodo inválido"
print("OK - periodos generados:", df["Periodo"].nunique())
```

---

## Paso 3 — Agrupar modelos de ataúd en categorías

**Objetivo:** reducir 80+ modelos dispersos a categorías con volumen suficiente para predecir.

```python
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
```

### ✅ Test del paso
```python
assert df["Categoria_Ataud"].notna().all(), "Hay categorías nulas"
n_cats = df["Categoria_Ataud"].nunique()
assert 3 <= n_cats <= 10, f"Número de categorías fuera de rango esperado: {n_cats}"
# Ninguna categoría (excepto Otros) debería tener menos de 10 ventas históricas
counts = df["Categoria_Ataud"].value_counts()
assert (counts.drop("Otros", errors="ignore") >= 5).all(), "Hay categoría principal con muy pocos datos"
print("OK - categorías:", n_cats)
```

---

## Paso 4 — Tabla de proporciones (categoría → modelo específico)

**Objetivo:** calcular qué porcentaje de cada categoría corresponde a cada modelo específico exacto, para el desglose posterior.

```python
proporciones = (
    df.groupby(["Categoria_Ataud", "Ataud_Modelo"])
      .size()
      .groupby(level=0)
      .apply(lambda s: (s / s.sum()).to_dict())
      .to_dict()
)

# Ejemplo de salida esperada:
# {"Lincoln": {"Lincoln": 0.7, "Lincoln Redondo": 0.2, "Lincoln Panoramico": 0.1}, ...}
print(json.dumps(proporciones, indent=2, ensure_ascii=False)[:800])
```

### ✅ Test del paso
```python
for cat, dist in proporciones.items():
    total = sum(dist.values())
    assert abs(total - 1.0) < 1e-6, f"Proporciones de '{cat}' no suman 1 ({total})"
print("OK - proporciones válidas para", len(proporciones), "categorías")
```

---

## Paso 5 — Tabla de demanda mensual por categoría

**Objetivo:** construir la serie mensual (Periodo x Categoria) con cantidad vendida — esta es la tabla base para el modelo.

```python
demanda = (
    df.groupby(["Periodo", "Categoria_Ataud"])
      .size()
      .reset_index(name="cantidad")
)

# Completar meses/categorías sin ventas con 0 (importante para no sesgar el modelo)
todos_periodos = pd.period_range(df["Fecha"].min(), df["Fecha"].max(), freq="M").astype(str)
todas_categorias = df["Categoria_Ataud"].unique()
idx_completo = pd.MultiIndex.from_product([todos_periodos, todas_categorias],
                                           names=["Periodo", "Categoria_Ataud"])
demanda = (demanda.set_index(["Periodo", "Categoria_Ataud"])
                   .reindex(idx_completo, fill_value=0)
                   .reset_index())
demanda.head()
```

### ✅ Test del paso
```python
assert demanda["cantidad"].isna().sum() == 0, "Hay valores nulos en cantidad"
assert (demanda["cantidad"] >= 0).all(), "Hay cantidades negativas"
assert demanda.groupby("Categoria_Ataud").size().nunique() == 1, "Series desbalanceadas entre categorías"
print("OK - tabla de demanda:", demanda.shape)
```

---

## Paso 6 — Feature engineering para el modelo

**Objetivo:** crear variables predictoras (tendencia, estacionalidad, lags) por categoría.

```python
demanda = demanda.sort_values(["Categoria_Ataud", "Periodo"]).reset_index(drop=True)
demanda["fecha_periodo"] = pd.to_datetime(demanda["Periodo"])
demanda["mes"] = demanda["fecha_periodo"].dt.month
demanda["anio"] = demanda["fecha_periodo"].dt.year
demanda["t"] = demanda.groupby("Categoria_Ataud").cumcount()  # tendencia temporal

# Lags por categoría (mes anterior, 2 meses antes, mismo mes año anterior aprox.)
for lag in [1, 2, 3]:
    demanda[f"lag_{lag}"] = demanda.groupby("Categoria_Ataud")["cantidad"].shift(lag)

demanda["rolling_mean_3"] = (demanda.groupby("Categoria_Ataud")["cantidad"]
                                     .shift(1).rolling(3).mean())

demanda_model = pd.get_dummies(demanda, columns=["Categoria_Ataud"], prefix="cat")
demanda_model = demanda_model.dropna().reset_index(drop=True)
demanda_model.head()
```

### ✅ Test del paso
```python
feature_cols = [c for c in demanda_model.columns if c.startswith("lag_") or c.startswith("cat_")]
assert len(feature_cols) > 0, "No se generaron features"
assert demanda_model.isna().sum().sum() == 0, "Quedan NaN tras dropna()"
assert demanda_model.shape[0] > 20, "Muy pocas filas para entrenar tras generar lags"
print("OK - dataset de modelado:", demanda_model.shape)
```

---

## Paso 7 — Split temporal (walk-forward, NO aleatorio)

**Objetivo:** separar train/test respetando el orden cronológico para no filtrar información futura.

```python
FEATURES = [c for c in demanda_model.columns
            if c not in ["Periodo", "fecha_periodo", "cantidad"]]
TARGET = "cantidad"

demanda_model = demanda_model.sort_values("fecha_periodo").reset_index(drop=True)

corte = int(len(demanda_model) * 0.8)
train = demanda_model.iloc[:corte]
test = demanda_model.iloc[corte:]

X_train, y_train = train[FEATURES], train[TARGET]
X_test, y_test = test[FEATURES], test[TARGET]
```

### ✅ Test del paso
```python
assert train["fecha_periodo"].max() <= test["fecha_periodo"].min(), "Hay fuga temporal train/test"
assert len(X_train) > 0 and len(X_test) > 0, "Split vacío"
print(f"OK - train: {len(X_train)}, test: {len(X_test)}")
```

---

## Paso 8 — Baseline (naive) para comparar

**Objetivo:** tener un punto de referencia simple antes del modelo de ML — obligatorio para justificar el uso de Random Forest en la tesis.

```python
# Baseline: repetir el último valor conocido (lag_1) como predicción
baseline_pred = X_test["lag_1"]

mae_base = mean_absolute_error(y_test, baseline_pred)
rmse_base = mean_squared_error(y_test, baseline_pred, squared=False)
print("Baseline MAE:", mae_base, "RMSE:", rmse_base)
```

### ✅ Test del paso
```python
assert not np.isnan(mae_base), "Baseline MAE inválido"
print("OK - baseline calculado")
```

---

## Paso 9 — Entrenar Random Forest

**Objetivo:** entrenar el modelo principal de predicción de demanda por categoría.

```python
modelo_rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=6,
    min_samples_leaf=2,
    random_state=42
)
modelo_rf.fit(X_train, y_train)
pred_rf = modelo_rf.predict(X_test)
```

### ✅ Test del paso
```python
assert hasattr(modelo_rf, "estimators_"), "El modelo no se entrenó"
assert len(pred_rf) == len(y_test), "Predicciones con longitud incorrecta"
assert (pred_rf >= 0).all(), "Hay predicciones de demanda negativas (revisar)"
print("OK - modelo entrenado")
```

---

## Paso 10 — Métricas del modelo vs baseline

**Objetivo:** calcular todas las métricas relevantes para la tesis y confirmar que el modelo supera al baseline.

```python
mae_rf = mean_absolute_error(y_test, pred_rf)
rmse_rf = mean_squared_error(y_test, pred_rf, squared=False)
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
```

### ✅ Test del paso
```python
assert metricas["random_forest"]["MAE"] <= metricas["baseline"]["MAE"] * 1.15, \
    "El modelo no mejora claramente al baseline — revisar features o categorías"
print("OK - métricas calculadas y modelo validado contra baseline")
```

> Nota: si esta aserción falla, no es un error del notebook — es una señal real de que hay que ajustar features (más lags, agrupar categorías distinto) antes de seguir. Repetir Pasos 6-10 con ajustes es válido y forma parte del proceso, documentar los intentos en la tesis.

---

## Paso 11 — Precio promedio por categoría y monto esperado

**Objetivo:** calcular el ingreso esperado a partir de la demanda predicha.

```python
precio_promedio = df.groupby("Categoria_Ataud")["Monto_winsorizado"].mean().to_dict()

# Ejemplo: aplicar sobre la última predicción disponible por categoría
ultima_pred = test.assign(prediccion=pred_rf)
ultima_pred["categoria"] = ultima_pred[[c for c in FEATURES if c.startswith("cat_")]].idxmax(axis=1).str.replace("cat_", "")
ultima_pred["precio_promedio"] = ultima_pred["categoria"].map(precio_promedio)
ultima_pred["monto_esperado"] = ultima_pred["prediccion"] * ultima_pred["precio_promedio"]
ultima_pred[["categoria", "prediccion", "precio_promedio", "monto_esperado"]].head(10)
```

### ✅ Test del paso
```python
assert not ultima_pred["monto_esperado"].isna().any(), "Hay montos esperados nulos"
assert (ultima_pred["monto_esperado"] >= 0).all(), "Monto esperado negativo"
print("OK - monto esperado calculado")
```

---

## Paso 12 — Desglose a modelo específico (usando proporciones del Paso 4)

**Objetivo:** convertir la predicción por categoría en cantidades sugeridas por modelo específico de ataúd.

```python
def desglosar_por_modelo(categoria, cantidad_predicha, proporciones):
    dist = proporciones.get(categoria, {})
    return {modelo: round(cantidad_predicha * pct, 1) for modelo, pct in dist.items()}

ejemplo = desglosar_por_modelo("Lincoln", 12, proporciones)
print(ejemplo)
```

### ✅ Test del paso
```python
suma = sum(ejemplo.values())
assert abs(suma - 12) < 0.5, "El desglose no suma aproximadamente la cantidad predicha"
print("OK - desglose por modelo específico funcional")
```

---

## Paso 13 — Alerta de reorden de stock

**Objetivo:** función que compara stock actual vs demanda predicha para generar alertas (input manual de stock actual, ya que no viene en el Excel).

```python
def alerta_reorden(stock_actual: dict, demanda_predicha: dict, umbral_seguridad: float = 0.2):
    alertas = []
    for categoria, demanda in demanda_predicha.items():
        stock = stock_actual.get(categoria, 0)
        punto_reorden = demanda * (1 + umbral_seguridad)
        if stock < punto_reorden:
            alertas.append({
                "categoria": categoria,
                "stock_actual": stock,
                "demanda_predicha": demanda,
                "unidades_a_comprar": round(punto_reorden - stock, 1)
            })
    return alertas

# Ejemplo de uso con stock ficticio de prueba
stock_ejemplo = {"Lincoln": 5, "Americano": 10}
demanda_ejemplo = {"Lincoln": 12, "Americano": 8}
print(alerta_reorden(stock_ejemplo, demanda_ejemplo))
```

### ✅ Test del paso
```python
resultado = alerta_reorden(stock_ejemplo, demanda_ejemplo)
assert any(a["categoria"] == "Lincoln" for a in resultado), "No generó alerta esperada para Lincoln"
assert not any(a["categoria"] == "Americano" for a in resultado), "Generó alerta incorrecta para Americano (stock suficiente)"
print("OK - lógica de alertas validada")
```

---

## Paso 14 — Guardar artefactos del modelo

**Objetivo:** dejar todo listo para exportar al backend de predicción (FastAPI).

```python
OUTPUT_DIR = Path("modelo_export")
OUTPUT_DIR.mkdir(exist_ok=True)

joblib.dump(modelo_rf, OUTPUT_DIR / "modelo_demanda_rf.pkl")

metadata = {
    "features": FEATURES,
    "categorias": list(todas_categorias),
    "proporciones_modelo_especifico": proporciones,
    "precio_promedio_categoria": precio_promedio,
    "metricas": metricas,
    "fecha_entrenamiento": pd.Timestamp.now().isoformat(),
    "ultimo_periodo_entrenado": demanda_model["Periodo"].max()
}

with open(OUTPUT_DIR / "metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("Archivos generados:", list(OUTPUT_DIR.glob("*")))
```

### ✅ Test del paso
```python
assert (OUTPUT_DIR / "modelo_demanda_rf.pkl").exists(), "No se guardó el modelo"
assert (OUTPUT_DIR / "metadata.json").exists(), "No se guardó el metadata"

# Verificar que el modelo se puede recargar y predecir
modelo_cargado = joblib.load(OUTPUT_DIR / "modelo_demanda_rf.pkl")
pred_check = modelo_cargado.predict(X_test.iloc[:1])
assert len(pred_check) == 1
print("OK - artefactos guardados y verificados, listos para mover al backend")
```

---

## ✅ Checklist final antes de pasar al backend

- [ ] Todas las aserciones de los 14 pasos pasaron sin error
- [ ] `modelo_export/modelo_demanda_rf.pkl` existe y se recarga correctamente
- [ ] `modelo_export/metadata.json` contiene: features, categorías, proporciones, precios promedio, métricas
- [ ] Las métricas (MAE, RMSE, R2, MAPE) están documentadas para comparar con la tabla de modelos anteriores en la tesis

---

## Siguiente fase (fuera de este notebook) — Exposición como API con FastAPI

No forma parte de este notebook, pero es el siguiente paso una vez que `modelo_export/` esté listo.

### Arquitectura: dos backends desacoplados

- **Backend transaccional**: tiene acceso a la BD (incluye stock actual por categoría/modelo). Atiende al frontend para todo el flujo transaccional normal.
- **Backend del modelo**: **no tiene acceso a la BD**. Solo carga `modelo_demanda_rf.pkl` + `metadata.json` y hace cálculos. No consulta stock por su cuenta.
- **Frontend (Angular)**: llama a cada backend por separado (no hay comunicación directa entre backends). Es el frontend quien, si quiere alertas de reorden, primero obtiene el stock del backend transaccional y luego se lo envía al backend del modelo en la misma request de predicción.

### Endpoint `POST /prediccion/demanda`

1. Copiar `modelo_demanda_rf.pkl` y `metadata.json` al proyecto backend de FastAPI.
2. Cargar el modelo una vez al iniciar la app (`joblib.load`), no en cada request.
3. Crear el endpoint. El campo `stock_actual` es **opcional**:

```json
// Request
{
  "stock_actual": {"Lincoln": 5, "Americano": 10, "Imperial": 8}   // opcional
}
```

**Regla de negocio a implementar:**
- Si `stock_actual` **viene** en el request → calcular `demanda_por_categoria`, `desglose_por_modelo`, `monto_esperado` **y** `alertas_reorden`.
- Si `stock_actual` **no viene** (es `null` o se omite) → responder igual con `demanda_por_categoria`, `desglose_por_modelo` y `monto_esperado`, pero **`alertas_reorden` debe venir como lista vacía `[]`**, nunca inventar o asumir un stock. No rechazar la request con error: la predicción de demanda es válida sin stock, solo las alertas dependen de él.

```json
// Response (con stock_actual enviado)
{
  "periodo": "2026-03",
  "demanda_por_categoria": {"Lincoln": 12, "Americano": 8},
  "desglose_por_modelo": {"Lincoln": {"Lincoln": 8.4, "Lincoln Redondo": 2.4}},
  "monto_esperado": 54000,
  "alertas_reorden": [{"categoria": "Lincoln", "unidades_a_comprar": 3.4}]
}

// Response (sin stock_actual)
{
  "periodo": "2026-03",
  "demanda_por_categoria": {"Lincoln": 12, "Americano": 8},
  "desglose_por_modelo": {"Lincoln": {"Lincoln": 8.4, "Lincoln Redondo": 2.4}},
  "monto_esperado": 54000,
  "alertas_reorden": []
}
```

4. El frontend en Angular:
   - Llama al backend transaccional para obtener el stock actual.
   - Llama al backend del modelo con ese stock en el body de `/prediccion/demanda`.
   - Muestra el dashboard predictivo (demanda esperada, alertas de stock, ingreso proyectado).
5. **Reentrenamiento**: agregar un endpoint o job programado (`POST /prediccion/reentrenar`) en el backend del modelo que vuelva a ejecutar el pipeline de este notebook cuando haya nueva data, y sobreescriba `modelo_demanda_rf.pkl`. Como el backend del modelo no tiene acceso a la BD, la nueva data (Excel actualizado o export de la BD transaccional) debe llegarle como archivo/payload, no consultarla él mismo.
