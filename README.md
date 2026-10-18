# Sistema de Gestión y Predicción de Inventario - Funeraria Aranzabal

## 📋 Descripción
[cite_start]Este proyecto implementa una solución integral para la modernización de inventarios mediante la digitalización automatizada de registros manuscritos y la predicción de demanda basada en datos[cite: 5].

## 🚀 Módulos Principales
* [cite_start]**Extracción:** Reconocimiento de escritura manual con precisión objetivo > 90%[cite: 5].
* [cite_start]**Predicción:** Modelos de series temporales para reducción de quiebres de stock (MAPE < 20%)[cite: 5].

## 🛠️ Estructura del Proyecto
* `src/`: Código fuente de la API (FastAPI).
* `notebooks/`: Experimentación CRISP-DM y entrenamiento de modelos.
* `data/`: Datasets de entrenamiento y validación (locales).
* `models_weights/`: Pesos de los modelos entrenados.

## Inicio
* `python -m venv venv`
* `.\venv\Scripts\activate`

* `pip install --upgrade pip`
* `pip install -r requirements.txt`

## Levantar el backend
*  `uvicorn src.main:app --port 8000 --reload`  

## 🔐 Cifrado de archivos (Google Drive)
Todos los archivos que se suben a Google Drive (documentos de servicio, respaldos
`.sql` y manifiestos `.json`) se cifran con **Fernet antes de salir del backend** y
se descifran al descargarlos.

Antes de levantar el backend, define la clave en el `.env`:

* `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
* Copia el resultado en la variable `ENCRYPTION_KEY` del `.env`.

> Importante: los archivos subidos antes de activar el cifrado están en texto
> plano y deberán volver a subirse; el backend espera contenido cifrado.