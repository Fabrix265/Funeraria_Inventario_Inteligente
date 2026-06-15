# PLAN DE EJECUCIÓN MODULAR
## Sistema de Predicción de Demanda — Funeraria Inventario Inteligente
### Versión: 1.0 | Arquitecto: Claude Sonnet 4.6

---

> **ANÁLISIS PREVIO DEL DATASET (37 registros, 18 columnas)**
>
> Antes de las fichas técnicas, se expone el diagnóstico del dataset real para que cada notebook programe sus reglas con precisión:
>
> **Problemas detectados:**
> - `Fecha`: string `"DD/MM/YYYY"`, con 3 registros con valor `"Vacío"` (filas Nro 311, 315, 332). Una fecha outlier `"28/07/2023"`, otra `"12/08/2022"`, otra `"29/08/2022"` — posiblemente errores tipográficos vs. 2025.
> - `Monto`: float64 con outlier extremo de **207,000** (fila 313 — probable captura en centavos o error). El resto oscila entre 250 y 7,500.
> - `Ataud_Modelo`: inconsistencias de capitalización (`Americano` / `AMERICANO`), abreviaciones (`LINCOL` vs `LINCOLN`), registros vacíos (`Vacío`).
> - `Ataud_Color`: inconsistencias (`BLANCO` / `blanco` / `Blanco`), valor `Vacío` en 10 registros — regla especial: se codifica como `"no_especificado"`.
> - `Capilla`: múltiples variantes del mismo tipo (`ILUMINADA` / `Iluminada` / `ardiente iluminada`).
> - `Forma de pago`: 2 registros `"Vacío"`.
> - `Velatorio`: columna informativa de lugar/contexto, **no predictiva** — excluir de features.
> - `DNI`, `Dirección`, `Teléfono`, `Contratante`, `Fallecido`: datos personales — excluir de features.
> - `Carroza`: casi siempre `si` (35/37) — baja varianza, modelar con cautela.
> - Columnas binarias (`Carroza`, `Auto`, `Microbus`, `Carroza flores`): string `"si"`/`"no"` → encodear a 1/0.
> - `Cargadores`: int, valores 0, 4 o 6.
> - **Agrupación temporal: MENSUAL** — con solo 37 registros distribuidos en ~5 meses, la granularidad mensual es la única estadísticamente válida.

---

## ANÁLISIS DE VIABILIDAD DEL PLAN

### ¿Los datos son suficientes para el objetivo?

**Respuesta honesta: Parcialmente.** Los datos son suficientes para **construir y experimentar** la arquitectura completa, pero con limitaciones conocidas que deben documentarse en cada notebook:

| Aspecto | Estado | Acción |
|---|---|---|
| Volumen (37 registros → ~5 meses) | ⚠️ Bajo | SMOTE + Bootstrapping + Sliding Window compensan |
| Granularidad mensual | ✅ Correcta para este volumen | Agregar por mes/año |
| Variables para predicción de ataúd | ✅ Modelo + Color disponibles | Regla de color `Vacío` → `no_especificado` |
| Variables para predicción de servicios | ✅ Capilla, Carroza, Auto, Microbus, Carroza flores, Cargadores | Todas disponibles |
| Variable target de ganancias | ✅ `Monto` disponible | Limpiar outlier 207,000 |
| Serie temporal continua | ⚠️ Gaps y fechas erróneas | Detectar y documentar en métricas |

### ¿Los modelos seleccionados son correctos?

| Modelo | Adecuación | Observación |
|---|---|---|
| **SARIMA** | ⚠️ Marginal | Requiere mínimo ~24 puntos mensuales para estacionalidad. Con ~5 meses funciona como baseline, no para estacionalidad real. Documentar limitación. |
| **Prophet** | ✅ Bueno | Robusto con pocos datos, maneja gaps bien, ideal para series cortas. Recomendado como modelo principal. |
| **XGBoost/LightGBM con Lags** | ✅ Bueno | Con augmentation llega a volumen suficiente. Los lags (1, 2, 3 meses) son features válidos. |
| **LSTM** | ⚠️ Experimental | Underfitting esperado con serie corta incluso augmentada. Incluir con fines experimentales/comparativos explícitos. |
| **ETS** | ✅ Bueno | Ideal para series cortas, no requiere estacionalidad. Funcionará bien. |
| **Apriori** | ✅ Correcto (separado) | Análisis de asociación entre servicios (ataúd + capilla + carroza + etc.). Totalmente válido y separado. |

### Decisión de arquitectura sobre los datos base vs. augmentados:
- Los notebooks de **modelos temporales** se aplican **sobre los datos del excel base limpio** (preprocesados), con mención explícita de que el augmentation es complementario para el entrenamiento cuando el modelo lo permite.
- El notebook de **Data Augmentation** genera los 3 datasets pero **no reemplaza** al base.

---

## FICHA TÉCNICA NRO. 1
### Notebook: `01_preprocesamiento.ipynb`

---

**OBJETIVO EXACTO:**
Transformar el dataset crudo `Dataset_ML.xlsx` en un dataset limpio, normalizado y agregado mensualmente, listo para modelado. Calcular métricas de calidad de datos. Exportar dos artefactos: (1) dataset limpio a nivel registro, (2) dataset agregado mensualmente.

---

**INPUTS:**
```
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\dataset\Dataset_ML.xlsx
```

**OUTPUTS:**
```
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\dataset\dataset_limpio.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\dataset\dataset_mensual.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\dataset\metricas_preprocesamiento.xlsx
```

---

**LÓGICA DE NEGOCIO DETALLADA:**

**1. Carga y configuración:**
```python
# Columnas a EXCLUIR completamente (no predictivas o PII):
COLS_EXCLUIR = ['Nro', 'Contratante', 'Dirección', 'DNI', 'Teléfono', 'Fallecido', 'Velatorio']
# Columnas binarias si/no → 1/0:
COLS_BINARIAS = ['Carroza', 'Carroza flores', 'Auto', 'Microbus']
```

**2. Limpieza de `Fecha`:**
- Reemplazar string `"Vacío"` → `NaT`
- Parsear con `pd.to_datetime(col, format='%d/%m/%Y', errors='coerce')`
- Detectar fechas con año != año_modal (2025): años 2022 y 2023 encontrados en filas 302, 313, 322. Registrar como anomalías temporales pero **conservar** (son servicios reales pasados). Si el año difiere en más de 3 años del año modal, marcar como `fecha_sospechosa = True`.
- Registros con `Fecha = NaT` (3 registros, Nro 311, 315, 332): **imputar con la fecha del registro anterior** (forward-fill por orden de `Nro`). Registrar como corregidos.

**3. Limpieza de `Monto`:**
- Detectar outliers con IQR: Q1 - 3*IQR y Q3 + 3*IQR (usar multiplicador 3 por la alta variabilidad del negocio).
- El valor 207,000 es outlier extremo. Registrarlo. **No eliminarlo** — marcarlo como `monto_outlier = True` y crear versión con winsorización al percentil 99 para los modelos de regresión de monto. Mantener el original en el dataset limpio.
- Los montos terminados en `.00` son correctos (precios fijos). No modificar.

**4. Limpieza de `Ataud_Modelo`:**
```python
# Mapeo de normalización (aplicar lower().strip() primero, luego mapear):
ATAUD_MODELO_MAP = {
    'americano': 'Americano',
    'biblia': 'Biblia',
    'biblia panoramico': 'Biblia Panoramico',
    'lincoln biblia': 'Lincoln Biblia',
    'lincoln': 'Lincoln',
    'lincol': 'Lincoln',  # typo
    'modelo': 'Modelo',
    'foroon': 'Foroon',
    'redondo': 'Redondo',
    'farana': 'Farana',
    'imperim': 'Imperial',  # normalizar
    'impor.': 'Imperial',   # abreviación
    'imperial': 'Imperial',
    'semivicado': 'Semivicado',
    'llanol': 'Llanol',
    'principe': 'Principe',
    'vacío': 'sin_ataud',
    'vacio': 'sin_ataud',
}
```

**5. Limpieza de `Ataud_Color`:**
```python
# Regla especial: Vacío NO significa ausencia, significa no especificado.
# Aplicar lower().strip() primero:
ATAUD_COLOR_MAP = {
    'vacío': 'no_especificado',
    'vacio': 'no_especificado',
    'blanco': 'Blanco',
    'natural': 'Natural',
    'madera': 'Madera',
    'perla': 'Perla',
    'mate': 'Mate',
    'cops': 'Cops',
    'nare': 'Nare',  # posible typo de "Natural" pero conservar como está
}
# Si Ataud_Modelo == 'sin_ataud' y Ataud_Color == 'no_especificado' → combinación válida
# Si Ataud_Modelo != 'sin_ataud' y Ataud_Color == 'no_especificado' → también válida
```

**6. Limpieza de `Capilla`:**
```python
CAPILLA_MAP = {
    'iluminada': 'Iluminada',
    'iluminada de madera': 'Iluminada de Madera',
    'iluminada blanca': 'Iluminada Blanca',
    'ardiente iluminada': 'Iluminada',  # variante, normalizar
    'humado': 'Humado',
    'de madera': 'De Madera',
    'de flores': 'De Flores',
    'vacío': 'sin_capilla',
    'vacio': 'sin_capilla',
}
```

**7. Limpieza de `Forma de pago`:**
```python
PAGO_MAP = {
    'vacío': 'no_especificado',
    'vacio': 'no_especificado',
    'directo': 'directo',
    'mixto': 'mixto',
    'seguro': 'seguro',
}
```

**8. Columnas binarias:**
```python
# "si" → 1, "no" → 0 (case-insensitive)
for col in COLS_BINARIAS:
    df[col] = df[col].str.strip().str.lower().map({'si': 1, 'no': 0})
```

**9. `Cargadores`:**
- Ya es int64. Verificar que solo tenga valores {0, 4, 6}. Registrar si hay otro valor.

**10. Creación de feature `Ataud_completo`:**
```python
# Combinación modelo+color para predicción conjunta:
df['Ataud_completo'] = df['Ataud_Modelo'] + '_' + df['Ataud_Color']
# Ejemplo: "Americano_Natural", "Biblia_no_especificado"
```

**11. Agregación mensual (`dataset_mensual.xlsx`):**
```python
# Crear columna periodo:
df['Periodo'] = df['Fecha'].dt.to_period('M')  # Ej: 2025-07, 2025-08

# Por cada mes calcular:
AGG_DICT = {
    # Conteos de demanda por tipo de ataúd (top features):
    'servicios_totales': ('Fecha', 'count'),
    'monto_total': ('Monto', 'sum'),
    'monto_promedio': ('Monto', 'mean'),
    'monto_mediana': ('Monto', 'median'),
    'carroza_count': ('Carroza', 'sum'),
    'carroza_flores_count': ('Carroza flores', 'sum'),
    'auto_count': ('Auto', 'sum'),
    'microbus_count': ('Microbus', 'sum'),
    'cargadores_total': ('Cargadores', 'sum'),
}
# Para Ataud_Modelo, Ataud_Color, Capilla → pivot_table con count por categoría
# El resultado final es un DataFrame con índice = Periodo (mensual)
```

**12. Detección de lagunas temporales:**
```python
# Sobre el dataset_mensual, verificar que todos los meses entre min y max fecha estén presentes
# Calcular el rango completo de meses y hacer reindex
# Los meses faltantes → registrar en métrica 'lagunas_temporales'
# Rellenar meses faltantes con 0 en conteos y NaN en montos (para modelos de series temporales)
```

---

**ESTRUCTURA DE CÓDIGO RECOMENDADA:**

```python
# Sección 1: Importaciones y configuración de rutas
# Sección 2: Carga de datos y diagnóstico inicial
def cargar_datos(ruta: str) -> pd.DataFrame
def diagnostico_inicial(df: pd.DataFrame) -> dict  # retorna conteo de nulls, dtypes, shape

# Sección 3: Funciones de limpieza
def limpiar_fechas(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]  # retorna df + log de cambios
def limpiar_monto(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]
def normalizar_categoricas(df: pd.DataFrame, mapas: dict) -> tuple[pd.DataFrame, dict]
def encodear_binarias(df: pd.DataFrame, cols: list) -> pd.DataFrame

# Sección 4: Feature engineering
def crear_ataud_completo(df: pd.DataFrame) -> pd.DataFrame
def agregar_mensual(df: pd.DataFrame) -> pd.DataFrame

# Sección 5: Métricas de calidad
def calcular_metricas_calidad(df_original: pd.DataFrame, df_limpio: pd.DataFrame, df_mensual: pd.DataFrame, logs: dict) -> pd.DataFrame

# Sección 6: Exportación
def exportar_resultados(df_limpio, df_mensual, df_metricas, rutas: dict)

# Main pipeline:
if __name__ == '__main__':
    df_raw = cargar_datos(RUTA_INPUT)
    df, log_fechas = limpiar_fechas(df_raw.copy())
    df, log_monto = limpiar_monto(df)
    df, log_cats = normalizar_categoricas(df, {...})
    df = encodear_binarias(df, COLS_BINARIAS)
    df = crear_ataud_completo(df)
    df_mensual = agregar_mensual(df)
    df_metricas = calcular_metricas_calidad(df_raw, df, df_mensual, {**log_fechas, **log_monto, **log_cats})
    exportar_resultados(df, df_mensual, df_metricas, RUTAS)
```

---

**MÉTRICAS DE VALIDACIÓN A CALCULAR:**

Exportar en `metricas_preprocesamiento.xlsx` con una fila por métrica:

| Métrica | Descripción | Cómo calcular |
|---|---|---|
| **Tasa de Limpieza** | % de registros con errores de formato o nulos corregidos | `(total_correcciones / total_registros) * 100` donde total_correcciones = suma de todos los cambios registrados en logs |
| **Integridad de Datos** | % de registros que mantienen relación lógica | Verificar: si `Ataud_Modelo == 'sin_ataud'` entonces `Cargadores` debería ser 0 o bajo; si `Carroza == 1` hay servicios relacionados. Calcular % de registros sin inconsistencias lógicas |
| **Consistencia Temporal** | Lagunas/saltos de tiempo detectados y tratados | Contar meses faltantes en el rango min-max de fechas después de agregar mensualmente |
| **Registros con Fecha Imputada** | Conteo absoluto | Registros donde Fecha era 'Vacío' y fue imputada |
| **Registros con Fecha Sospechosa** | Conteo absoluto | Registros con año que difiere >3 del año modal |
| **Outliers en Monto** | Conteo y % | Registros marcados como monto_outlier |
| **Categorías Normalizadas** | Por columna | Conteo de valores cambiados en cada columna categórica |
| **Cobertura Temporal** | Rango de fechas válidas | Fecha mínima, fecha máxima, total de meses |
| **Distribución por Mes** | Servicios por mes | Tabla con mes y count de servicios |

---

## FICHA TÉCNICA NRO. 2
### Notebook: `02_data_augmentation.ipynb`

---

**OBJETIVO EXACTO:**
Aplicar tres técnicas de data augmentation sobre el `dataset_limpio.xlsx` para compensar el bajo volumen de datos. Generar tres datasets aumentados independientes y exportarlos. Estos datasets son **complementarios** al base; los modelos se entrenan principalmente con el dataset mensual base, y los augmentados se usan para experimentos comparativos o como conjunto de entrenamiento extendido.

---

**INPUTS:**
```
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\dataset\dataset_limpio.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\dataset\dataset_mensual.xlsx
```

**OUTPUTS:**
```
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\augmented\dataset_smote.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\augmented\dataset_bootstrap.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\augmented\dataset_sliding_window.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\augmented\reporte_augmentation.xlsx
```

---

**LÓGICA DE NEGOCIO DETALLADA:**

**IMPORTANTE — Qué dataset usar como base para cada técnica:**
- SMOTE y Bootstrapping → usar `dataset_limpio.xlsx` (nivel registro)
- Sliding Window → usar `dataset_mensual.xlsx` (serie temporal)

**Técnica 1: SMOTE**
- Target para SMOTE: `Ataud_Modelo` (variable de clasificación con múltiples clases)
- Features: variables numéricas y ordinales disponibles (`Monto`, `Cargadores`, `Carroza`, `Carroza flores`, `Auto`, `Microbus`)
- Usar `SMOTENC` (de imbalanced-learn) si hay variables categóricas adicionales en features, o `SMOTE` si solo se usan numéricas.
- Estrategia: `strategy='not majority'` — solo over-samplear las clases minoritarias de Ataud_Modelo hasta igualar la mayoritaria.
- Las columnas no-numéricas (Capilla, Ataud_Color, etc.) se encodean previamente con `LabelEncoder` solo para SMOTE y se decodifican en el output.
- Exportar dataset con columna `origen` = `"original"` o `"smote_sintetico"` para trazabilidad.
- **Advertencia a documentar en el notebook**: SMOTE en datos funerarios con solo 37 registros puede generar interpolaciones no-realistas. Usar con precaución.

**Técnica 2: Bootstrapping Temporal**
- Sobre `dataset_limpio.xlsx`, generar N muestras bootstrap del mismo tamaño (N = 5 iteraciones × 37 registros = 185 registros sintéticos adicionales, total ~222).
- Preservar la distribución temporal: al hacer resample, agregar ruido gaussiano pequeño al `Monto` (σ = 50 soles) para evitar duplicados exactos.
- El campo `Fecha` en los registros sintéticos: asignar la misma fecha del registro original + ruido de ±3 días (dentro del mismo mes).
- Columna `origen` = `"bootstrap_N"` donde N es la iteración.
- Exportar el dataset combinado (originales + bootstrap).

**Técnica 3: Sliding Window**
- Aplicar sobre `dataset_mensual.xlsx` (serie temporal mensual).
- Generar ventanas deslizantes con `window_size = 3` (3 meses de historia → 1 mes a predecir).
- Para cada target (`servicios_totales`, `monto_total`): crear columnas `lag_1`, `lag_2`, `lag_3` y `target`.
- Si la serie tiene `N` puntos temporales, genera `N - window_size` samples.
- Exportar como formato tabular listo para modelos de regresión con lags (XGBoost, LightGBM).
- Incluir columna `mes_target` para identificar el mes que se predice.

---

**ESTRUCTURA DE CÓDIGO RECOMENDADA:**

```python
# Sección 1: Importaciones
# pip install imbalanced-learn sklearn

# Sección 2: Carga
def cargar_datos_limpios(ruta_limpio, ruta_mensual) -> tuple[pd.DataFrame, pd.DataFrame]

# Sección 3: SMOTE
def preparar_features_smote(df: pd.DataFrame) -> tuple[np.array, np.array, encoders]
def aplicar_smote(X, y, strategy='not majority') -> tuple[np.array, np.array]
def reconstruir_df_smote(X_res, y_res, encoders, df_original) -> pd.DataFrame
def exportar_smote(df_smote, ruta)

# Sección 4: Bootstrapping
def bootstrap_temporal(df: pd.DataFrame, n_iter=5, ruido_monto=50, ruido_dias=3) -> pd.DataFrame
def exportar_bootstrap(df_bootstrap, ruta)

# Sección 5: Sliding Window
def crear_sliding_windows(df_mensual: pd.DataFrame, window_size=3, targets: list) -> pd.DataFrame
def exportar_sliding(df_windows, ruta)

# Sección 6: Reporte
def generar_reporte_augmentation(df_orig, df_smote, df_bootstrap, df_windows) -> pd.DataFrame
# El reporte debe incluir: tamaño original, tamaño de cada dataset augmentado,
# distribución de clases antes/después de SMOTE, rango de fechas en bootstrap

# Main:
if __name__ == '__main__':
    df_limpio, df_mensual = cargar_datos_limpios(...)
    df_smote = reconstruir_df_smote(*aplicar_smote(*preparar_features_smote(df_limpio)))
    df_bootstrap = bootstrap_temporal(df_limpio)
    df_windows = crear_sliding_windows(df_mensual, window_size=3, targets=['servicios_totales', 'monto_total'])
    reporte = generar_reporte_augmentation(df_limpio, df_smote, df_bootstrap, df_windows)
    exportar_smote(df_smote, RUTA_SMOTE)
    exportar_bootstrap(df_bootstrap, RUTA_BOOTSTRAP)
    exportar_sliding(df_windows, RUTA_SLIDING)
```

---

**MÉTRICAS DE VALIDACIÓN A CALCULAR:**

| Métrica | Descripción |
|---|---|
| `registros_originales` | 37 |
| `registros_smote_total` | Total registros dataset SMOTE (original + sintéticos) |
| `registros_smote_sinteticos` | Solo los registros nuevos generados |
| `distribucion_clases_antes` | Count por Ataud_Modelo antes de SMOTE |
| `distribucion_clases_despues` | Count por Ataud_Modelo después de SMOTE |
| `registros_bootstrap_total` | Total registros dataset bootstrap |
| `ventanas_generadas` | Número de sliding windows creadas |
| `window_size` | 3 |

---

## FICHA TÉCNICA NRO. 3
### Notebook: `03_modelos_temporales.ipynb`

---

**OBJETIVO EXACTO:**
Implementar y comparar 5 modelos de predicción de demanda y ganancias sobre el `dataset_mensual.xlsx` (datos base limpios). Los targets de predicción son: `servicios_totales` (demanda de servicios por mes) y `monto_total` (ganancias por mes). Generar tabla comparativa de métricas y visualizaciones. Exportar predicciones y tabla de resultados.

**Targets de predicción:**
1. `servicios_totales` (demanda mensual de servicios)
2. `monto_total` (ingresos mensuales)
3. *(Opcional/complementario)* Demanda por `Ataud_Modelo` por mes (usando columnas pivoteadas del dataset mensual)

---

**INPUTS:**
```
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\dataset\dataset_mensual.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\augmented\dataset_sliding_window.xlsx
```

**OUTPUTS:**
```
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\resultados\comparativa_modelos.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\resultados\predicciones_todos_modelos.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\notebooks\prediction\graficas\  (carpeta con .png de cada modelo)
```

---

**LÓGICA DE NEGOCIO DETALLADA:**

**Split de datos:**
- Con ~5-8 meses de datos mensuales: usar Leave-One-Out o Train/Test con 80/20 (último mes = test).
- Para todos los modelos: train = todos los meses excepto el último, test = último mes.
- Dado el volumen mínimo, los resultados son **indicativos**, no definitivos. Documentar esto.

**Configuración por modelo:**

**SARIMA:**
```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
# Con tan pocos puntos, desactivar componente estacional:
# Orden (p,d,q) = (1,1,1) como punto de partida
# Orden estacional (P,D,Q,m) = (0,0,0,0) — no hay suficiente historia para estacionalidad
# Usar auto_arima de pmdarima para selección automática de orden si está disponible
# pip install pmdarima statsmodels
```

**Prophet:**
```python
from prophet import Prophet
# df debe tener columnas 'ds' (datetime) y 'y' (valor)
# Configuración: yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False
# (no hay datos suficientes para estacionalidades)
# changepoint_prior_scale=0.5 (más flexible para datos escasos)
# Generar forecast para los próximos 3 meses
# pip install prophet
```

**XGBoost con Lags:**
```python
from xgboost import XGBRegressor
# Usar dataset_sliding_window.xlsx como input (ya tiene lag_1, lag_2, lag_3)
# Features: lag_1, lag_2, lag_3 + features adicionales si existen
# Target: target (mes siguiente)
# n_estimators=100, max_depth=3, learning_rate=0.1 (conservador para datos pequeños)
# pip install xgboost
```

**LightGBM con Lags:**
```python
from lightgbm import LGBMRegressor
# Misma lógica que XGBoost, mismos features
# num_leaves=15, n_estimators=100, learning_rate=0.05
# pip install lightgbm
```

**LSTM:**
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
# Arquitectura mínima: LSTM(32 units) → Dense(1)
# input_shape = (window_size, n_features) = (3, 1) para univariado
# epochs=50, batch_size=4 (muy pequeño por el volumen)
# Normalizar datos con MinMaxScaler antes de entrenar
# ADVERTENCIA: esperar underfitting pronunciado. Documentar.
# pip install tensorflow
```

**ETS:**
```python
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
# O usar: from statsmodels.tsa.holtwinters import ExponentialSmoothing
# error='add', trend='add', seasonal=None (sin estacionalidad por datos insuficientes)
# optimized=True — dejar que statsmodels optimice alpha, beta
```

---

**ESTRUCTURA DE CÓDIGO RECOMENDADA:**

```python
# Sección 1: Importaciones y configuración
MODELOS = ['SARIMA', 'Prophet', 'XGBoost', 'LightGBM', 'LSTM', 'ETS']
TARGETS = ['servicios_totales', 'monto_total']

# Sección 2: Carga y preparación
def cargar_serie_temporal(ruta_mensual) -> pd.DataFrame  # retorna df con index DatetimeIndex
def preparar_split(df, target_col, test_size=1) -> tuple  # retorna X_train, X_test, y_train, y_test
def preparar_lags(df_windows, target_col) -> tuple       # para XGBoost y LGBM

# Sección 3: Un wrapper por modelo
def entrenar_evaluar_sarima(y_train, y_test) -> dict      # retorna dict con métricas + tiempo
def entrenar_evaluar_prophet(df_train, df_test) -> dict
def entrenar_evaluar_xgboost(X_train, X_test, y_train, y_test) -> dict
def entrenar_evaluar_lgbm(X_train, X_test, y_train, y_test) -> dict
def entrenar_evaluar_lstm(y_train, y_test, window_size=3) -> dict
def entrenar_evaluar_ets(y_train, y_test) -> dict

# Cada función retorna:
# {
#   'modelo': str,
#   'target': str,
#   'MAE': float,
#   'RMSE': float,
#   'R2': float,
#   'MAPE': float,          # adicional
#   'tiempo_entrenamiento': float,  # segundos
#   'predicciones': list,
#   'real': list,
# }

# Sección 4: Comparativa
def construir_tabla_comparativa(resultados: list) -> pd.DataFrame
def graficar_comparativa(df_comparativa)  # barplot MAE, RMSE, R2 por modelo
def graficar_predicciones(resultados, df_mensual)  # línea: real vs predicho por modelo

# Sección 5: Exportación
def exportar_resultados(df_comparativa, df_predicciones, rutas)

# Main: loop sobre TARGETS × MODELOS
```

---

**MÉTRICAS DE VALIDACIÓN — OBLIGATORIAS Y ADICIONALES:**

| Métrica | Descripción | Obligatoria |
|---|---|---|
| **MAE** | `mean_absolute_error(y_real, y_pred)` | ✅ Sí |
| **RMSE** | `sqrt(mean_squared_error(y_real, y_pred))` | ✅ Sí |
| **R² Score** | `r2_score(y_real, y_pred)` | ✅ Sí |
| **Tiempo de Entrenamiento** | `time.time()` antes y después de `.fit()` | ✅ Sí |
| **MAPE** | `mean(|y_real - y_pred| / y_real) * 100` | Adicional |
| **MAE Normalizado** | `MAE / mean(y_real)` — comparable entre targets | Adicional |
| **Dirección Correcta** | % de veces que el modelo predijo la dirección (sube/baja) correctamente | Adicional |
| **AIC/BIC** | Solo para SARIMA y ETS (indicador de ajuste del modelo) | Adicional |

**NOTA CRÍTICA:** Con solo 1 punto de test, MAE = error absoluto en ese único punto, RMSE = MAE, R² puede ser negativo o 1.0 artificialmente. Documentar esta limitación en una celda Markdown dentro del notebook y recomendar recolectar más datos.

---

## FICHA TÉCNICA NRO. 4
### Notebook: `04_apriori_asociacion.ipynb`

---

**OBJETIVO EXACTO:**
Aplicar el algoritmo Apriori para descubrir reglas de asociación entre los servicios contratados en cada funeral. Identificar qué combinaciones de servicios (ataúd + capilla + carroza + cargadores + auto + microbus) tienden a contratarse juntas, con qué frecuencia y con qué confianza. Este análisis es **independiente de la predicción temporal** y responde a la pregunta de negocio: "¿Qué servicios se venden juntos?" para estrategias de bundle o inventario conjunto.

---

**INPUTS:**
```
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\dataset\dataset_limpio.xlsx
```

**OUTPUTS:**
```
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\resultados\reglas_asociacion.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\data\processed\resultados\itemsets_frecuentes.xlsx
C:\Users\fabri\OneDrive\Desktop\UPAO\Funeraria_Inventario_Inteligente\notebooks\prediction\graficas\apriori_heatmap.png
```

---

**LÓGICA DE NEGOCIO DETALLADA:**

**Construcción de transacciones:**
Cada registro del dataset = una "transacción" (un servicio funerario completo). Los "items" son los servicios activos en esa transacción:

```python
# Para cada registro, construir la lista de items presentes:
def construir_transaccion(row) -> list:
    items = []
    # Ataúd: incluir siempre si no es 'sin_ataud'
    if row['Ataud_Modelo'] != 'sin_ataud':
        items.append(f"Ataud_{row['Ataud_Modelo']}")
    # Color del ataúd: incluir si no es 'no_especificado'
    if row['Ataud_Color'] != 'no_especificado':
        items.append(f"Color_{row['Ataud_Color']}")
    # Capilla: incluir si no es 'sin_capilla'
    if row['Capilla'] != 'sin_capilla':
        items.append(f"Capilla_{row['Capilla']}")
    # Servicios binarios: incluir solo si == 1
    if row['Carroza'] == 1: items.append('Carroza')
    if row['Carroza flores'] == 1: items.append('Carroza_flores')
    if row['Auto'] == 1: items.append('Auto')
    if row['Microbus'] == 1: items.append('Microbus')
    # Cargadores: incluir como item si > 0
    if row['Cargadores'] > 0: items.append(f"Cargadores_{row['Cargadores']}")
    # Forma de pago: incluir como item
    if row['Forma de pago'] != 'no_especificado':
        items.append(f"Pago_{row['Forma de pago']}")
    return items
```

**Parámetros de Apriori:**
- Dado el bajo volumen (37 transacciones), usar umbrales más bajos de lo habitual:
```python
min_support = 0.3    # ítem presente en al menos 30% de transacciones (~11 registros)
min_confidence = 0.5  # regla correcta al menos 50% de las veces
min_lift = 1.0        # solo reglas con lift positivo
# pip install mlxtend
from mlxtend.frequent_patterns import apriori, association_rules
```

**Formato de entrada para mlxtend:**
- Transformar las transacciones a formato one-hot encoding (DataFrame de True/False por item).
- Usar `TransactionEncoder` de mlxtend.

**Interpretación de negocio a incluir en notebook:**
- Lift > 1.5: los items se compran juntos más de lo esperado → considerar bundle/descuento conjunto.
- Lift < 1: los items se excluyen mutuamente → no ofrecer juntos.
- Reglas de alta confianza y alto soporte → comportamiento estándar del cliente.

---

**ESTRUCTURA DE CÓDIGO RECOMENDADA:**

```python
# Sección 1: Importaciones
# pip install mlxtend

# Sección 2: Carga
def cargar_datos(ruta) -> pd.DataFrame

# Sección 3: Preparación de transacciones
def construir_transacciones(df) -> list[list]  # lista de listas de items
def encodear_transacciones(transacciones) -> pd.DataFrame  # one-hot DataFrame

# Sección 4: Apriori
def ejecutar_apriori(df_encoded, min_support=0.3) -> pd.DataFrame  # frequent itemsets
def generar_reglas(frequent_itemsets, min_confidence=0.5) -> pd.DataFrame

# Sección 5: Visualización
def graficar_soporte_confianza(reglas: pd.DataFrame)  # scatter plot support vs confidence, size=lift
def graficar_heatmap_lift(reglas: pd.DataFrame)  # heatmap antecedent vs consequent coloreado por lift
def graficar_top_itemsets(frequent_itemsets, top_n=15)  # barplot de itemsets más frecuentes

# Sección 6: Interpretación automática
def interpretar_reglas(reglas: pd.DataFrame) -> pd.DataFrame
# Añadir columna 'interpretacion' con texto: "Cuando se contrata X, también se contrata Y
# en el N% de los casos (lift=Z). Esto sugiere: [bundle / exclusión / oportunidad]"

# Sección 7: Exportación
def exportar_resultados(frequent_itemsets, reglas, rutas)

# Main:
if __name__ == '__main__':
    df = cargar_datos(RUTA_INPUT)
    transacciones = construir_transacciones(df)
    df_encoded = encodear_transacciones(transacciones)
    itemsets = ejecutar_apriori(df_encoded, min_support=0.3)
    reglas = generar_reglas(itemsets, min_confidence=0.5)
    graficar_soporte_confianza(reglas)
    graficar_heatmap_lift(reglas)
    exportar_resultados(itemsets, reglas, RUTAS)
```

---

**MÉTRICAS DE VALIDACIÓN A CALCULAR:**

| Métrica | Descripción |
|---|---|
| `total_transacciones` | 37 (= registros del dataset) |
| `total_items_unicos` | Número de items únicos identificados |
| `frequent_itemsets_count` | Número de itemsets que superan min_support |
| `reglas_generadas` | Total de reglas de asociación con min_confidence |
| `regla_max_lift` | La regla con mayor lift (items más co-ocurrentes) |
| `regla_max_confianza` | La regla con mayor confianza |
| `regla_max_soporte` | El itemset con mayor soporte (más común) |
| `coverage` | % de transacciones cubiertas por al menos una regla |

---

## RESUMEN ARQUITECTURAL

```
data/
├── processed/
│   ├── dataset/
│   │   ├── Dataset_ML.xlsx              ← INPUT ORIGINAL
│   │   ├── dataset_limpio.xlsx          ← OUTPUT NB01
│   │   ├── dataset_mensual.xlsx         ← OUTPUT NB01
│   │   └── metricas_preprocesamiento.xlsx ← OUTPUT NB01
│   ├── augmented/
│   │   ├── dataset_smote.xlsx           ← OUTPUT NB02
│   │   ├── dataset_bootstrap.xlsx       ← OUTPUT NB02
│   │   ├── dataset_sliding_window.xlsx  ← OUTPUT NB02
│   │   └── reporte_augmentation.xlsx    ← OUTPUT NB02
│   └── resultados/
│       ├── comparativa_modelos.xlsx     ← OUTPUT NB03
│       ├── predicciones_todos_modelos.xlsx ← OUTPUT NB03
│       ├── reglas_asociacion.xlsx       ← OUTPUT NB04
│       └── itemsets_frecuentes.xlsx     ← OUTPUT NB04

notebooks/
└── prediction/
    ├── 01_preprocesamiento.ipynb
    ├── 02_data_augmentation.ipynb
    ├── 03_modelos_temporales.ipynb
    ├── 04_apriori_asociacion.ipynb
    └── graficas/
        ├── comparativa_mae_rmse.png
        ├── predicciones_prophet.png
        ├── predicciones_sarima.png
        ├── predicciones_xgboost.png
        ├── predicciones_lgbm.png
        ├── predicciones_lstm.png
        ├── predicciones_ets.png
        └── apriori_heatmap.png
```

---

## DEPENDENCIAS PYTHON (requirements completos)

```
# Core
pandas>=2.0
numpy>=1.24
openpyxl>=3.1
matplotlib>=3.7
seaborn>=0.12

# NB02 - Augmentation
imbalanced-learn>=0.11
scikit-learn>=1.3

# NB03 - Modelos
statsmodels>=0.14      # SARIMA, ETS
prophet>=1.1           # Prophet
xgboost>=1.7           # XGBoost
lightgbm>=4.0          # LightGBM
tensorflow>=2.13       # LSTM
pmdarima>=2.0          # auto_arima para SARIMA (opcional)

# NB04 - Apriori
mlxtend>=0.22

# Tiempo
time  # built-in
```

---

*Fin del Plan de Ejecución Modular v1.0*
*Generado por análisis directo del dataset: 37 registros, 18 columnas, rango temporal Jul-Oct 2025 con 3 registros históricos anteriores.*
