### **🎯 Propósito del documento**

Este documento que el estudiante entrega **no es la tesis**. Es un *Technical Design & Development Report* (TDDR) que captura todo el proceso de diseño, desarrollo y validación de su solución tecnológica..

### **📐 ESTRUCTURA DEL DOCUMENTO**

### **SECCIÓN 0 — PORTADA Y METADATOS DEL PROYECTO**

| Campo | Descripción |
| --- | --- |
| Tipo de solución | Web / ML / IA Generativa |
| Dominio de aplicación | Industria (gestión de inventario en sector funerario) |
| Palabras clave | Handwriting Recognition, Inventory Management, Time Series Forecasting, Machine Learning, Data Digitization, Demand Prediction, Web Platform |
| Repositorio del código |   • URL Backend: https://github.com/Fabrix265/Funeraria_Inventario_Inteligente
  • URL Frontend: https://github.com/Fabrix265/funeraria-frontend/tree/main
  • URL Modelo: https://github.com/Fabrix265/Funeraria_Aranzabal_modelo.git |
| Dataset | Este dataset contiene el registro histórico digitalizado de servicios funerarios de la Funeraria Máximo Aranzabal, ubicada en Trujillo, Perú. Los datos fueron extraídos manualmente a partir de contratos físicos manuscritos mediante el módulo de extracción de inteligencia artificial desarrollado en el proyecto, con revisión y corrección manual posterior para garantizar la integridad de cada registro. El dataset fue construido con el propósito de entrenar y evaluar modelos de predicción de demanda de inventario (ataúdes, capillas y vehículos) y constituye el primer conjunto de datos estructurado disponible del sector funerario peruano con este nivel de detalle operativo. |

### **SECCIÓN 1 — PROBLEMA Y MOTIVACIÓN TÉCNICA**

**1.1 Descripción del problema real**

- **Contexto del dominio donde existe el problema**
    
    El proyecto se desarrolla en el sector de servicios funerarios, un entorno operativo en el que la gestión de suministros e inventario constituye un proceso crítico para garantizar la continuidad del negocio. Actualmente, dicha gestión se sustenta en registros físicos manuscritos, cuya administración recae principalmente en el personal administrativo (secretaria) de la empresa. Esta dependencia de procesos manuales representa un cuello de botella operativo que compromete tanto la eficiencia administrativa como la disponibilidad oportuna de productos esenciales.
    
- **Evidencia cuantitativa del problema (estadísticas, reportes, datos reales)**
    - Pérdida estimada de **S/ 800.00 mensuales** por quiebres de stock que impiden concretar servicios funerarios.
    - Costos adicionales de **S/ 300.00 mensuales** por compras de urgencia y errores en pedidos manuales.
    - Inversión de aproximadamente **40 horas mensuales** del personal administrativo en tareas de digitalización manual, con un impacto económico estimado de **S/ 420.00**.
- **¿Por qué las soluciones actuales son insuficientes?**
    
    El modelo operativo vigente presenta dos deficiencias estructurales. En primer lugar, la transcripción manual de registros manuscritos es un proceso lento y propenso a errores de digitación, lo que imposibilita contar con datos estructurados y confiables en tiempo real. En segundo lugar, las decisiones de reposición de stock se basan en criterios empíricos e intuitivos, sin respaldo de análisis histórico ni proyecciones de demanda, lo que deriva en ciclos recurrentes de sobrestock y quiebre de inventario. En conjunto, ambas deficiencias evidencian que el enfoque manual no escala ni responde a las necesidades analíticas del negocio.
    

**1.2 Brecha tecnológica identificada**

- **¿Qué gap técnico específico aborda esta solución?**
    
    El gap técnico central que aborda este trabajo es la inexistencia de una solución que integre de forma operativa el reconocimiento automático de escritura manuscrita con la predicción de demanda por series temporales en el contexto específico del sector funerario. El análisis del estado del arte (Sección 2.3) evidenció que de los 15 trabajos revisados, solo uno (Chen et al., 2023) combina componentes de HTR y predicción de demanda en una plataforma web, pero orientado a retail y servicios de salud sin considerar las particularidades del dominio funerario: contratos con campos de alta variabilidad caligráfica, relaciones complejas entre recursos (ataúdes, capillas, vehículos), modalidades de pago mixtas y la necesidad de validación legal de identidad de fallecidos y contratantes. Ningún trabajo revisado aborda simultáneamente la digitalización de contratos manuscritos, la predicción de reposición de inventario, el procesamiento de pagos y el control de accesos en un único sistema desplegado en producción, representando un gap técnico concreto y no cubierto por el estado del arte.
    
- **Justificación de por qué se necesita una solución computacional**
    
    La gestión operativa de la Funeraria Máximo Aranzabal de Trujillo, Perú, depende en su totalidad de registros físicos manuscritos cuya transcripción manual consume aproximadamente 40 horas mensuales del personal administrativo y genera errores de digitación que comprometen la integridad de los datos de contratos con implicaciones legales y económicas directas. La ausencia de datos estructurados impide cualquier análisis de demanda histórica, lo que obliga a basar las decisiones de reposición de inventario en criterios empíricos, derivando en quiebres de stock estimados en S/ 800 mensuales en servicios no concretados y S/ 300 mensuales en gastos de compras de urgencia. Una solución computacional es la única alternativa viable para romper este ciclo por tres razones técnicas concretas: primero, el volumen de contratos manuscritos (340 registros en 46 meses) supera la capacidad de digitación manual sin errores en el tiempo disponible del personal; segundo, la extracción de patrones de demanda y estacionalidad sobre ese volumen de datos requiere modelos estadísticos y de machine learning que no pueden ejecutarse manualmente; y tercero, la coordinación en tiempo real de inventario, pagos y validación de identidad entre múltiples usuarios con distintos niveles de acceso exige una arquitectura de sistema que solo una plataforma computacional puede garantizar con la consistencia y trazabilidad requeridas por el negocio.
    

**1.3 Pregunta de investigación técnica**

¿En qué medida la integración de un modelo de reconocimiento de escritura manuscrita con un sistema de predicción de series temporales permite automatizar la gestión y reposición de inventario en el contexto de una empresa de servicios funerarios?

**1.4 Objetivo general y objetivos específicos**

- Objetivo General:
    
    Desarrollar una plataforma web que integre un módulo de reconocimiento de escritura manuscrita y un módulo de predicción de demanda basado en series temporales, para automatizar la digitalización y gestión inteligente del inventario en una empresa del sector funerario.
    
- Objetivos Específicos:
    - Construir y etiquetar un dataset de registros manuscritos propios del dominio funerario, garantizando una tasa de imágenes aptas suficiente para el entrenamiento de modelos de reconocimiento.
    - Seleccionar, entrenar y ajustar un modelo de Handwriting Recognition que alcance una exactitud superior al 90%, con un CER inferior al 15% y un WER inferior al 20% sobre los formularios del negocio.
    - Seleccionar, entrenar y ajustar un modelo de predicción de series temporales que genere proyecciones de stock con un MAPE inferior al 20%, capturando correctamente la estacionalidad de la demanda.
    - Desarrollar e integrar las APIs de extracción y predicción en una plataforma web que permita la carga masiva de imágenes, la validación de datos extraídos y la visualización de proyecciones de inventario.
    - Validar el sistema integrado en el entorno real del negocio, midiendo la reducción del tiempo de digitalización manual y la eliminación de quiebres de stock respecto a la línea base actual.

**1.5 Alcance y limitaciones declaradas**

La solución comprende el desarrollo de una plataforma web con dos componentes principales: un módulo de extracción automatizada de datos a partir de imágenes de registros manuscritos, y un módulo de predicción de demanda mediante series temporales. Ambos módulos se exponen a través de APIs desarrolladas en Python y se integran en una interfaz web que permite la carga de imágenes, la corrección de datos extraídos y la consulta de proyecciones de inventario. La solución incluye además la base de datos PostgreSQL para el almacenamiento del historial digitalizado y el despliegue de la infraestructura en un servidor en la nube (Digital Ocean).

- **Limitaciones declaradas:**
    - El sistema no contempla el procesamiento de documentos con daños físicos severos que impidan su lectura.
    - No se desarrollará una aplicación móvil nativa; el acceso es exclusivamente vía navegador web estándar.
    - La solución no incluye integración con sistemas externos de gestión ni adquisición de hardware especializado.
    - No se desarrollarán módulos de gestión administrativa más allá del control de inventario.

**1.6 Contribución técnica principal** *(research contribution)*

La contribución central de este proyecto reside en la construcción de un pipeline end-to-end que integra, por primera vez en el contexto del sector funerario local, dos capacidades de inteligencia artificial previamente independientes: el reconocimiento automático de escritura manuscrita y la predicción de demanda mediante series temporales. 

A diferencia de soluciones genéricas existentes, esta propuesta genera un dataset etiquetado propio del dominio, lo que permite adaptar y ajustar los modelos a las particularidades léxicas y de formato de los registros reales del negocio.

 La combinación de ambos módulos en una única plataforma web operativa constituye una solución integral que transforma un proceso completamente empírico y manual en un flujo de toma de decisiones basado en evidencia analítica, aportando una arquitectura replicable para negocios de servicios con características operativas similares.

### **SECCIÓN 2 — REVISIÓN DE LITERATURA TÉCNICA**

*(Equivale a Related Work / Background)*

**2.1 Marco conceptual técnico**

- **Reconocimiento de Escritura Manuscrita (HTR)**
    
    El reconocimiento de texto manuscrito (Handwritten Text Recognition, HTR) se define como la tarea de convertir imágenes de escritura a mano en texto digital legible por máquina, apoyándose en modelos de aprendizaje profundo capaces de manejar la gran variabilidad de la caligrafía humana en contraste con el OCR tradicional para texto impreso. Según Li et al. (2021), los modelos HTR basados en arquitecturas transformer como TrOCR integran un encoder de visión y un decoder de lenguaje para realizar la transcripción de forma end‑to‑end a nivel de subpalabras, logrando resultados de estado del arte en texto manuscrito.
    
- **Modelos de Lenguaje Visual (VLM) para Extracción Estructurada**
    
    Los modelos de lenguaje visual (Vision‑Language Models, VLM) extienden las capacidades de los LLM al procesar conjuntamente imágenes y texto, permitiendo extraer de forma directa estructuras de datos a partir de documentos como facturas, formularios y contratos. Según Bai et al. (2025), Qwen2.5‑VL incorpora un transformer de visión de resolución dinámica capaz de localizar objetos con bounding boxes y realizar parsing robusto de documentos, extrayendo campos estructurados en formatos como JSON sin necesidad de un pipeline separado de detección de regiones.
    
- **Detección y Etiquetado de Regiones de Texto**
Previo al entrenamiento del modelo HTR, se requiere segmentar las imágenes en regiones de interés correspondientes a cada campo del formulario. Para ello se empleó Label Studio, una herramienta de anotación que permite definir etiquetas personalizadas y dibujar *bounding boxes* sobre las imágenes, generando pares imagen‑transcripción para entrenamiento supervisado. Según Heartex Labs (2023), Label Studio ofrece flujos de trabajo de etiquetado para visión por computador que incluyen la creación de cajas delimitadoras rotadas y rectangulares, así como la gestión de proyectos de anotación colaborativa, lo que la hace adecuada para construir datasets de reconocimiento de texto manuscrito en formularios estructurados
- **Fine-Tuning de Modelos Preentrenados**
    
    El ajuste fino (fine‑tuning) consiste en continuar el entrenamiento de un modelo preentrenado sobre un conjunto de datos específico del dominio para adaptar sus pesos al nuevo vocabulario, estilo de escritura y distribución de ejemplos. Li et al. (2021) señalan que los modelos basados en TrOCR pueden preentrenarse con grandes volúmenes de datos sintéticos y posteriormente afinarse con datos anotados manualmente, mejorando significativamente métricas como la tasa de error por carácter (CER) y la precisión de reconocimiento en textos manuscritos.
    
- **Series Temporales y Predicción de Demanda**
    
    Una serie temporal se define como una secuencia de observaciones ordenadas cronológicamente, que puede analizarse para identificar patrones de tendencia, estacionalidad y ciclos con el objetivo de realizar pronósticos de demanda en contextos como la gestión de inventarios. Modelos como SARIMA, Prophet, redes LSTM y métodos de suavizado exponencial se han utilizado ampliamente entre 2021 y 2026 para la predicción de series temporales de ventas y servicios, integrando componentes lineales y no lineales para capturar la dinámica temporal (Gusev, 2021).
    
- **Data Augmentation para Series Temporales**
    
    El data augmentation en series temporales consiste en incrementar el tamaño efectivo del conjunto de entrenamiento mediante modificaciones controladas a las observaciones originales, preservando la estructura temporal subyacente. Según Gusev (2021), técnicas como el bootstrapping temporal con ruido gaussiano y la construcción de ventanas deslizantes permiten mejorar la robustez de modelos de predicción al exponerlos a múltiples realizaciones sintéticas de la misma dinámica. En este contexto, enfoques como SMOTE y variantes para datos mixtos (por ejemplo, SMOTENC) se utilizan para balancear clases en problemas supervisados con variables categóricas, generando nuevos ejemplos sintéticos que reducen el sesgo hacia las clases mayoritarias.
    
- **Reglas de Asociación (Apriori)**
El algoritmo Apriori es una técnica de minería de datos que identifica conjuntos de ítems que coocurren frecuentemente en un conjunto de transacciones, expresando las relaciones encontradas como reglas de la forma antecedente → consecuente y evaluando su utilidad mediante métricas de soporte, confianza y *lift*. Según IBM (2022), Apriori se formula como un proceso en dos etapas: primero se obtienen los conjuntos de ítems frecuentes que superan un umbral mínimo de soporte y luego, a partir de ellos, se generan reglas de asociación que cumplen un umbral mínimo de confianza, lo que permite descubrir patrones de compra conjunta o contratación simultánea de recursos útiles para la toma de decisiones.
- **Arquitectura de la Plataforma Web**
    
    La solución se estructura como una aplicación web de tres capas: un frontend desarrollado en Angular que gestiona la interfaz de usuario; un backend desarrollado en Python con FastAPI que expone los endpoints REST para los módulos de extracción y predicción; y una base de datos PostgreSQL que almacena el historial de servicios digitalizados. Este enfoque arquitectónico modular de tres capas permite desacoplar la lógica de presentación de la lógica de negocio y el almacenamiento, optimizando la escalabilidad y el rendimiento en sistemas basados en microservicios y APIs REST (Nunes et al., 2023). La autenticación se gestiona mediante tokens JWT con expiración configurable, y el sistema de autorización utiliza roles y permisos dinámicos almacenados en base de datos para controlar el acceso granular a cada funcionalidad.
    
- **2.2 Estado del arte de soluciones similares**
    
    
    | Ref | Año | Tipo de solución | Técnica/Tecnología | Dataset/Contexto | Métrica principal | Limitación reportada | Referencias |
    | --- | --- | --- | --- | --- | --- | --- | --- |
    | [1] | 2022 | Pipeline de extracción estructurada desde formularios manuscritos | Preprocesamiento, alineación, deep learning y extracción de entidades clave-valor | Formularios manuscritos reales en escenarios variados | Accuracy alta reportada, orientada a conversión de texto manuscrito a datos estructurados | Aunque es muy útil para tu proyecto, el porcentaje exacto no aparece en el extracto recuperado | Rahman, T., Ahmed, F., & Hossain, M. (2024). Efficient data extraction from handwritten forms: A structured pipeline solution. *Proceedings of the 2024 2nd International Conference on Artificial Intelligence Trends and Pattern Recognition (ICAITPR)*. IEEE. https://doi.org/10.1109/ICAITPR63242.2024.10959837 |
    | [2] | 2022 | App/Servicio ML para HTR | CRNN (CNN + RNN / CTC) | Formularios comerciales y registros de almacén (dataset propio y IAM) | Acc: 92.1% | Rendimiento cae en manuscritos con trazos muy irregulares y fondos ruidosos. | Sánchez, G., Pérez, J., & Ramos, L. (2022). Handwritten text recognition for inventory forms using convolutional recurrent neural networks. IEEE Access, 10, 75432–75444. https://doi.org/10.1109/ACCESS.2022.3187654 |
    | [3] | 2021 | Modelo HTR optimizado para datos escasos | Transformer-based encoder–decoder con preprocesamiento de imagen | Colecciones de documentos históricos y cuadernos (conjunto propio) | CER : 11.4% (equivalente a 88.6% de exactitud de caracteres) | Necesidad de anotaciones manuales para dominios nuevos; problemas con abreviaturas locales. | Kumar, R., & Li, H. (2021). End-to-end deep learning approach for offline handwritten document transcription in low-resource settings. Pattern Recognition Letters, 150, 162–170. https://doi.org/10.1016/j.patrec.2021.06.012 |
    | [4] | 2020 | Modelos de series temporales para predicción de demanda | Prophet, LSTM, and Temporal Convolutional Networks (TCN) comparados | Datos históricos de ventas de retail (varias cadenas) | MAPE: LSTM obtuvo 17.6% | Modelos requieren suficientes históricos; menor desempeño en productos con ventas muy esporádicas. | Zhao, Y., Wang, X., & Fernández, M. (2020). Deep learning for demand forecasting in retail supply chains: A comparative study. European Journal of Operational Research, 283(3), 1038–1051. https://doi.org/10.1016/j.ejor.2020.05.012 |
    | [5] | 2021 | Sistema de forecast para inventario multivariante | N-BEATS, DeepAR, y modelos híbridos | Retail and product-level demand datasets (M4/M5 competitions subsets) | MAPE: N-BEATS alcanzó 15.9% | Necesidad de escalado y ajuste por estacionalidades locales; complejidad computacional. | Bandara, K., Bergmeir, C., & Smyl, S. (2021). Forecasting across time series databases with global and local deep learning models. International Journal of Forecasting, 37(3), 1428–1447. https://doi.org/10.1016/j.ijforecast.2020.10.005 |
    | [6] | 2023 | Plataforma web integrada (HTR + forecast) | HTR (CRNN) + Prophet/LSTM para forecasting; API REST para integración | Pequeñas empresas (incluye sector salud y servicios), dataset propio | Reducción de Tiempo de Digitación: 78% promedio; MAPE forecasting: 18.3% | Integración dependiente de calidad de imagen de entrada; necesidad de correcciones manuales en 9% de casos. | Chen, J., Xu, L., & Sun, K. (2023). An integrated web platform combining OCR/HTR extraction and time-series forecasting for small business inventory management. ACM Transactions on Management Information Systems, 14(2), Article 9. https://doi.org/10.1145/3581234 |
    | [7] | 2024 | Modelo de pronóstico integrado a inventario con componente de serie temporal | Forecasting robusto para series intermitentes + optimización de stock | Inventario real de repuestos en una empresa industrial china | Accuracy 92.1% | Está orientado a repuestos industriales; la generalización a entornos funerarios requiere adaptación del dominio. | Fan, L., Song, Z., Mao, W., Tiejun, L., Wang, W., Yang, K., & Cao, F. (2024). Change is safer: A dynamic safety stock model for inventory management of large manufacturing enterprise based on intermittent time series forecasting. *Journal of Intelligent Manufacturing*. https://doi.org/10.1007/s10845-024-02442-y |
    | [8] | 2024 | Reconocimiento de escritura a mano de extremo a extremo | Document Attention Network for Computationally Efficient Recognition (DANCER) | Reconocimiento de documentos manuscritos | CER 14.8% | El enfoque está más centrado en eficiencia y arquitectura que en formularios de inventario específicos | Alshahrani, A., & Al-Amri, A. (2024). An end-to-end approach for handwriting recognition. En *2024 International Conference on Artificial Intelligence and Smart Systems (ICAISS)* (pp. 412–417). IEEE. https://doi.org/10.1109/ICAISS61165.2024.10678189 |
    | [9] | 2023 | Revisión y comparación de sistemas de reconocimiento de escritura | Análisis de enfoques offline y online, incluyendo deep learning | Revisión de 422 artículos indexados | WER 18.6% | Al ser una revisión, no propone un solo modelo listo para implementar, sino criterios de comparación | A comprehensive and comparative study of handwriting recognition system. (2023). *IEEE Access*. https://ieeexplore.ieee.org/document/10236301 |
    | [10] | 2023 | OCR/HTR para digitalización de texto manuscrito | Algoritmos de reconocimiento de texto + machine learning | Texto manuscrito en lenguas nativa e inglés | MAPE 19.4% | El trabajo es más general y no está centrado en formularios de inventario | Advancing optical character recognition for handwritten text: Enhancing efficiency and streamlining document management. (2023). *Proceedings of the 2023 14th International Conference on Computing Communication and Networking Technologies*. IEEE. https://doi.org/10.1109/ICCCNT56998.2023.10307143 |
    | [11] | 2021 | Base de datos y evaluación para reconocimiento de texto manuscrito | Métodos CTC y basados en atención para reconocimiento de líneas y palabras | Más de 1,500 formularios manuscritos y 715,699 símbolos | F1-score 91.3% | El corpus está en ruso y kazajo, por lo que requiere adaptación lingüística para otros contextos | Handwritten Kazakh and Russian (HKR) database for text recognition. (2021). *Neural Computing and Applications*. https://doi.org/10.1007/s11042-021-11399-6 |
    | [12] | 2024 | Benchmark comparativo de motores OCR | PaddleOCR, EasyOCR, KerasOCR, Tesseract y otros motores de OCR | 200 reportes clínicos escaneados con formatos diversos | Accuracy 67.28% | El mejor desempeño sigue siendo moderado y presenta errores elevados en documentos complejos | Khan, M. A., Ali, S., & Iqbal, M. (2024). Benchmarking performance analysis of optical character recognition engines on clinical reports. *Proceedings of the 2024 26th International Multi-Topic Conference (INMIC)*. IEEE. https://doi.org/10.1109/INMIC64792.2024.11004392 |
    | [13] | 2025 | Modelo de reconocimiento de escritura a mano de extremo a extremo | Vision Transformer (ViT) + CNN para extracción de características, con SAM y span masking | IAM, READ2016 y LAM; el trabajo también menciona que LAM es el dataset más grande usado en su evaluación | CER 8.6% y WER 18.4% | Su desempeño depende de la disponibilidad de datos etiquetados y puede variar en manuscritos con estilos muy irregulares o recursos limitados | Li, Y., Chen, D., Tang, T., & Shen, X. (2025). HTR-VT: Handwritten text recognition with vision transformer. *Pattern Recognition, 157*, 110857. |
    | [14] | 2024 | HTR sobre imágenes manuscritas | LSTM + Pixel Shifting Optimization (PSO) | Imágenes de caracteres y números manuscritos | Accuracy 97.14% | El artículo se enfoca en reconocimiento de caracteres y dígitos, no en formularios completos con estructura compleja | Kumar, P., Singh, D., & Rao, S. (2024). Handwritten text recognition from image using LSTM integrated with pixel shifting optimization algorithm. *Proceedings of the 2024 International Conference on Advancement in Renewable Energy and Intelligent Systems (AREIS)*. IEEE. https://doi.org/10.1109/AREIS62559.2024.10893651 |
    | [15] | 2024 | Reconocimiento de texto manuscrito/semiestructurado | LSTM para reconocimiento de texto | Texto profesional en inglés | Accuracy 88.10% | Presenta WER y CER altos, lo que indica que aún requiere ajuste para uso documental exigente | Y. Fan, "Professional English Text Recognition Based on Long Short Term Memory Approach," *2024 International Conference on Data Science and Network Security (ICDSNS)*, Tiptur, India, 2024, pp. 1-4, doi: 10.1109/ICDSNS62112.2024.10691174.  |

**2.3 Análisis comparativo de gaps**

- **Tabla o mapa de calor mostrando qué aspectos NO han sido abordados**
    
    
    | Ref | Año | HTR/OCR manuscrito | Predicción de demanda | Dataset dominio propio | Integración web completa | Pagos integrados | Validación de identidad | Dominio funerario | Roles y permisos dinámicos |
    | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | Rahman, T., Ahmed, F., & Hossain, M. (2024). Efficient data extraction from handwritten forms: A structured pipeline solution. *Proceedings of the 2024 2nd International Conference on Artificial Intelligence Trends and Pattern Recognition (ICAITPR)*. IEEE. https://doi.org/10.1109/ICAITPR63242.2024.10959837 | 2022 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Sánchez, G., Pérez, J., & Ramos, L. (2022). Handwritten text recognition for inventory forms using convolutional recurrent neural networks. IEEE Access, 10, 75432–75444. https://doi.org/10.1109/ACCESS.2022.3187654 | 2022 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Kumar, R., & Li, H. (2021). End-to-end deep learning approach for offline handwritten document transcription in low-resource settings. Pattern Recognition Letters, 150, 162–170. https://doi.org/10.1016/j.patrec.2021.06.012 | 2021 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Zhao, Y., Wang, X., & Fernández, M. (2020). Deep learning for demand forecasting in retail supply chains: A comparative study. European Journal of Operational Research, 283(3), 1038–1051. https://doi.org/10.1016/j.ejor.2020.05.012 | 2020 | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Bandara, K., Bergmeir, C., & Smyl, S. (2021). Forecasting across time series databases with global and local deep learning models. International Journal of Forecasting, 37(3), 1428–1447. https://doi.org/10.1016/j.ijforecast.2020.10.005 | 2021 | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Chen, J., Xu, L., & Sun, K. (2023). An integrated web platform combining OCR/HTR extraction and time-series forecasting for small business inventory management. ACM Transactions on Management Information Systems, 14(2), Article 9. https://doi.org/10.1145/3581234 | 2023 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
    | Fan, L., Song, Z., Mao, W., Tiejun, L., Wang, W., Yang, K., & Cao, F. (2024). Change is safer: A dynamic safety stock model for inventory management of large manufacturing enterprise based on intermittent time series forecasting. *Journal of Intelligent Manufacturing*. https://doi.org/10.1007/s10845-024-02442-y | 2024 | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Alshahrani, A., & Al-Amri, A. (2024). An end-to-end approach for handwriting recognition. En *2024 International Conference on Artificial Intelligence and Smart Systems (ICAISS)* (pp. 412–417). IEEE. https://doi.org/10.1109/ICAISS61165.2024.10678189 | 2024 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | A comprehensive and comparative study of handwriting recognition system. (2023). *IEEE Access*. https://ieeexplore.ieee.org/document/10236301 | 2023 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Advancing optical character recognition for handwritten text: Enhancing efficiency and streamlining document management. (2023). *Proceedings of the 2023 14th International Conference on Computing Communication and Networking Technologies*. IEEE. https://doi.org/10.1109/ICCCNT56998.2023.10307143 | 2023 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Handwritten Kazakh and Russian (HKR) database for text recognition. (2021). *Neural Computing and Applications*. https://doi.org/10.1007/s11042-021-11399-6 | 2021 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Khan, M. A., Ali, S., & Iqbal, M. (2024). Benchmarking performance analysis of optical character recognition engines on clinical reports. *Proceedings of the 2024 26th International Multi-Topic Conference (INMIC)*. IEEE. https://doi.org/10.1109/INMIC64792.2024.11004392 | 2024 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Li, Y., Chen, D., Tang, T., & Shen, X. (2025). HTR-VT: Handwritten text recognition with vision transformer. *Pattern Recognition, 157*, 110857. | 2025 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Kumar, P., Singh, D., & Rao, S. (2024). Handwritten text recognition from image using LSTM integrated with pixel shifting optimization algorithm. *Proceedings of the 2024 International Conference on Advancement in Renewable Energy and Intelligent Systems (AREIS)*. IEEE. https://doi.org/10.1109/AREIS62559.2024.10893651 | 2024 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | Y. Fan, "Professional English Text Recognition Based on Long Short Term Memory Approach," *2024 International Conference on Data Science and Network Security (ICDSNS)*, Tiptur, India, 2024, pp. 1-4, doi: 10.1109/ICDSNS62112.2024.10691174.  | 2024 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
    | **Este trabajo** | **2026** | **✅** | **✅** | **✅** | **✅** | **✅** | **✅** | **✅** | **✅** |
    | **Trabajos que lo abordan** |  | **12/15** | **4/15** | **12/15** | **1/15** | **0/15** | **0/15** | **0/15** | **0/15** |
- **Posicionamiento explícito de la solución propuesta frente al estado del arte**
    
    El análisis de los 15 trabajos revisados permite identificar cuatro gaps no abordados de forma conjunta por ningún trabajo previo.
    
    El primer gap es la ausencia de soluciones orientadas al dominio funerario. Ninguno de los 15 trabajos revisados aborda el reconocimiento de escritura manuscrita ni la predicción de demanda en el contexto de empresas de servicios funerarios. Los trabajos más cercanos (Chen et al. (2023), Fan et al., (2024)) se orientan a retail, salud e industria manufacturera, cuyos patrones de demanda y estructura de formularios difieren significativamente de los contratos funerarios, que incluyen campos como tipo de ataúd, capilla, vehículos de sepelio y modalidad de pago mixta.
    El segundo gap es la integración de HTR y predicción de demanda en una plataforma web operativa. Solo el trabajo (Chen et al., 2023) combina ambos componentes, pero sin plataforma web completa con gestión operativa del negocio, pagos ni control de accesos. Los 14 trabajos restantes abordan uno u otro componente de forma aislada, sin integración en un sistema unificado desplegado en producción.
    
    El tercer gap, el más crítico, es la ausencia total de integración de pasarelas de pago y validación de identidad en sistemas HTR o de predicción de demanda. Ninguno de los 15 trabajos incorpora procesamiento de pagos ni verificación de identidad de los involucrados en el servicio, funcionalidades que en el contexto funerario son operativamente indispensables dado que cada contrato implica un pago y la identificación legal del fallecido y el contratante.
    
    El cuarto gap es la ausencia de sistemas de autorización con roles y permisos dinámicos en soluciones HTR integradas. Todos los trabajos revisados se concentran en la precisión del modelo o en la arquitectura del sistema de predicción, sin considerar el control de acceso granular necesario para que una plataforma de gestión empresarial sea operativamente segura en un entorno con múltiples usuarios con distintos niveles de responsabilidad.
    
    La solución propuesta en este trabajo es la única que aborda simultáneamente los ocho aspectos evaluados, constituyendo una plataforma documentada que integra extracción de datos manuscritos, predicción de demanda por series temporales, gestión operativa completa, procesamiento de pagos, validación de identidad y control de accesos dinámico en el contexto específico del sector funerario.
    

**2.4 Justificación de la elección tecnológica**

FastAPI como framework de backend se justifica a partir de la brecha identificada en integración de sistemas completos. El único trabajo que abordó la integración de HTR con predicción de demanda en una plataforma web (Chen et al., 2023) reportó una dependencia crítica de la calidad de imagen de entrada y necesidad de correcciones manuales en el 9% de casos, sin documentar la arquitectura de su API ni su capacidad de respuesta ante múltiples solicitudes concurrentes. FastAPI responde a esta limitación mediante su soporte nativo para operaciones asíncronas, permitiendo procesar múltiples imágenes de contratos en paralelo sin bloquear el servidor, y su generación automática de documentación Swagger, ausente en todos los trabajos revisados y necesaria para la trazabilidad técnica de los endpoints de extracción y predicción.

Angular como framework de frontend se justifica a partir del gap de integración web completa. Ninguno de los 14 trabajos que abordaron HTR o predicción de forma aislada consideró la interfaz de usuario como componente del sistema. El trabajo de Chen et al. (2023), el único con plataforma integrada, no detalla la tecnología de frontend ni su capacidad para gestionar flujos complejos de usuario. Angular fue seleccionado por su sistema de componentes tipados en TypeScript y su manejo de estado reactivo mediante Observables, necesarios para implementar la interfaz de validación lado a lado (imagen + campos editables) que mitiga la limitación de precisión reportada por Sánchez et al. (2022), Según Kumar y Li (2021) y Alshahrani y Al-Amri (2024), donde los errores residuales del modelo requieren intervención del usuario.

PostgreSQL como motor de base de datos se justifica a partir de la complejidad relacional del dominio funerario, no abordada por ningún trabajo previo. Los trabajos de predicción de demanda revisados (Zhao et al. (2020), Bandara et al. (2021), Fan et al. (2024)) trabajaron sobre datasets tabulares simples de retail e industria manufacturera sin relaciones entre entidades. El dominio funerario introduce relaciones complejas entre servicios, fallecidos, contratantes, ataúdes, capillas, vehículos, pasajeros y pagos, que requieren un motor relacional con soporte para integridad referencial, transacciones ACID y consultas con múltiples joins, características que PostgreSQL garantiza de forma nativa y que motores NoSQL o relacionales ligeros no ofrecen con la misma robustez.

Digital Ocean como proveedor de infraestructura se justifica a partir del gap de despliegue en producción identificado en el estado del arte. Ninguno de los 15 trabajos revisados documenta el despliegue de su solución en un entorno de producción real accesible por usuarios finales; todos reportan resultados sobre entornos de laboratorio o datasets de evaluación. Digital Ocean permite cerrar este gap dentro del presupuesto disponible del proyecto (S/ 84.40), ofreciendo soporte para PostgreSQL administrado, despliegue de APIs Python y servidor de inferencia Ollama en el mismo entorno de infraestructura, algo que ningún trabajo previo había implementado de forma conjunta en el sector funerario.

Modelos de series temporales (ETS, LightGBM, Prophet, SARIMA, LSTM, XGBoost) se justifican a partir de los resultados reportados en el estado del arte para predicción de demanda. Los trabajos Zhao et al. (2020) y Bandara et al. (2021) reportaron MAPE de 17.6% y 15.9% respectivamente con LSTM y N-BEATS sobre datasets de retail con historial amplio, mientras que Chen et al. (2023) reportó MAPE de 18.3% con Prophet/LSTM sobre pequeñas empresas de servicios. Dado que el sector funerario presenta demanda más esporádica e irregular que el retail (condición identificada como limitante en Zhao et al. (2020): "menor desempeño en productos con ventas muy esporádicas"), se optó por evaluar un conjunto amplio de seis modelos en lugar de seleccionar uno a priori, incluyendo tanto modelos estadísticos clásicos robustos ante datasets pequeños (ETS, SARIMA) como modelos supervisados que aprovechan features adicionales mediante sliding window (XGBoost, LightGBM).

Multicentury-HTR y Qwen2.5-VL-3B como modelos de extracción se justifican a partir de las limitaciones reportadas en los trabajos de HTR revisados. Los trabajos Sánchez et al. (2022) y Kumar et al. (2024) reportaron Accuracy de 92.1% y 97.14% respectivamente, pero sobre datasets de caracteres aislados o formularios con estructura regular, condición que no se cumple en los contratos manuscritos de la funeraria con escritura ligada y vocabulario específico del dominio. El trabajo de Kumar y Li (2021) reportó CER de 11.4% sobre documentos históricos complejos usando un transformer encoder-decoder, señalando como limitación la necesidad de anotaciones manuales para dominios nuevos, lo que justifica el proceso de etiquetado en Label Studio y el fine-tuning sobre el dataset propio implementado en este trabajo. Qwen2.5-VL-3B se incorpora como complemento dado que ninguno de los trabajos revisados exploró modelos VLM para extracción estructurada directa de formularios manuscritos, representando una contribución diferencial respecto al estado del arte.

**SECCIÓN 3 — DISEÑO DE LA SOLUCIÓN TECNOLÓGICA**

*(Sección central — equivale a Proposed Method / System Design)*

**3.1 Visión general de la arquitectura**

- Diagrama de arquitectura de alto nivel
    
    !DA2-2026-07-07-071832.png
    
    SVG: 
    
    !ATAÚDES and CAPILLAS-2026-07-07-072304 (1).svg.svg)
    
- Descripción de cada componente y su responsabilidad
    
    ### ACTORES DEL SISTEMA
    
    | Componente | Descripción |
    | --- | --- |
    | **Administrador** | Usuario con privilegios máximos. Accede a todos los módulos del sistema incluyendo gestión de usuarios, roles, inventario completo, servicios, IA y predicciones. |
    | **Trabajador** | Empleado operativo. Accede a módulos operacionales: servicios, inventario, personas, IA y predicciones. No puede gestionar usuarios ni roles. Dependiendo del rol asignado |
    
    ---
    
    ### FRONTEND — funeraria-frontend
    
    | Componente | Descripción |
    | --- | --- |
    | **Angular 19 (SPA + TypeScript)** | Aplicación de página única construida con Angular 19 y TypeScript. Funciona como cliente del sistema, consumiendo las APIs del backend y de la API ML. Se despliega como recurso estático. |
    | **Módulo Auth** | Maneja autenticación OAuth2 con tokens JWT, expiración de sesión automática (8 horas), y protección de rutas con guards (authGuard, roleGuard, permisoGuard). |
    | **Módulo Servicios** | CRUD completo de servicios funerarios con formulario multi-sección: datos del servicio, verificación RENIEC, selección de inventario, vehículos y pasajeros. |
    | **Módulo Inventario** | Gestión de ataudes, capillas y vehículos con control de stock, activar/desactivar y filtros por modelo, color y estado. |
    | **Módulo IA** | Subida de imágenes de contratos, procesamiento asíncrono con polling (POST 202 + GET cada 3s), revisión de datos extraídos y guardado como servicio. |
    | **Módulo Predicciones** | Dashboards con gráficos ApexCharts: ejecución de predicciones temporales, comparación de métricas de 6 modelos y cálculo de necesidades de inventario. |
    
    ---
    
    ### BACKEND — Inventario Inteligente
    
    | Componente | Descripción |
    | --- | --- |
    | **FastAPI v1.0 (Puerto 8000)** | Framework web Python que expone la REST API principal. Maneja autenticación, autorización, CRUD de entidades y integraciones externas. Se despliega en Render. |
    | **Autenticación (OAuth2 + JWT)** | Genera tokens JWT con roles y permisos del usuario. Verifica credenciales con bcrypt. Token expira en 8 horas. |
    | **RBAC (28 permisos granulares)** | Sistema de control de acceso basado en roles. Cada usuario tiene un array de permisos como servicios:crear, ataudes:actualizar_stock, etc. El rol define un conjunto de permisos. |
    | **Servicios CRUD (Transacciones ACID)** | CRUD transaccional de servicios funerarios: crea fallecido, contratante, gestiona stock de ataud y capilla, asigna vehículos y pasajeros en una sola transacción PostgreSQL. |
    | **Pagos (Stripe SDK)** | Crear intenciones de pago con PaymentIntents, procesar cobros con tarjeta y recibir notificaciones de estado vía webhooks (completado/fallido). |
    | **RENIEC (Decolecta API)** | Proxy que consulta el servicio externo de Decolecta para validar y obtener datos de una persona por DNI (8 dígitos). Retorna nombre completo y apellidos. |
    | **Seeding (Roles + Admin)** | Al iniciar la aplicación, crea automáticamente los 28 permisos, los roles base (Administrador con todos los permisos, Trabajador con permisos limitados) y el usuario admin por defecto. |
    
    ---
    
    ### API ML — Aranzabal Modelo
    
    | Componente | Descripción |
    | --- | --- |
    | **FastAPI v3.0 (Puerto 9000)** | Framework web Python que expone la API de inteligencia artificial y predicciones. Se despliega en Digital Ocean con Cloudflare Tunnel para acceso público. |
    | **Servicio IA (Extracción Contratos)** | Recibe imágenes de contratos escaneados, las preprocesa (grayscale, crop, resize, sharpen), las envía a Ollama VLM con un prompt estructurado, parsea la respuesta JSON y normaliza los 13 campos extraídos. |
    | **Servicio Predicciones (6 modelos ML)** | Ejecuta 6 modelos de predicción temporal: SARIMA, ETS, Prophet, XGBoost, LightGBM y LSTM. Predice servicios totales y monto total mensual (1-24 meses). Carga los modelos serializados (.pkl y .keras) en memoria al primer request. |
    | **Background Tasks (Polling asíncrono)** | Patrón de procesamiento asíncrono: el POST retorna inmediatamente con un UUID de tarea (202 Accepted), el procesamiento corre en segundo plano, y el cliente consulta el resultado con GET cada 3 segundos. Resuelve el timeout de Cloudflare Tunnel (~100s). |
    | **Modelos Serializados (.pkl + .keras)** | 15 archivos guardados en disco: 12 modelos (6 modelos × 2 targets), 2 scalers MinMaxScaler y 1 archivo de metadata JSON con métricas comparativas, distribuciones históricas y valores históricos. |
    
    ---
    
    ### SISTEMAS EXTERNOS
    
    | Componente | Descripción |
    | --- | --- |
    | **PostgreSQL (Supabase)** | Base de datos relacional que almacena todas las entidades de negocio. ORM SQLModel con relaciones FK, tabla pivote servicio_vehiculo para relación N:M, y constraints de unicidad. Se ejecuta en Supabase (producción). |
    | **Stripe (PaymentIntents + Webhooks)** | Pasarela de pagos externa. Crea PaymentIntents en el backend, procesa cobros con tarjeta en el frontend vía Stripe.js, y recibe notificaciones de estado vía webhooks POST a /pagos/webhook. |
    | **RENIEC (Decolecta API)** | Servicio externo de validación de identidad por DNI. Consultado al crear o editar servicios funerarios. Retorna nombres, apellidos y nombre completo de la persona. |
    
    ---
    
    ### DESPLIEGUE
    
    | Componente | Descripción |
    | --- | --- |
    | **Digital Ocean (Droplet 8GB RAM)** | Servidor en la nube (Ubuntu 22.04, 4 vCPU, 160 GB SSD, ~$24/mes) que aloja la API ML, los modelos de predicción serializados y el servidor Ollama. Región: New York. |
    | **Cloudflare Tunnel** | Túnel HTTPS que expone el puerto 9000 del droplet a través de una URL pública (trycloudflare.com). Permite que el frontend consuma la API ML sin abrir puertos ni configurar SSL. URL temporal que cambia al reiniciar. |

**3.2 Especificación de requerimientos técnicos**

*3.2.1 Requerimientos funcionales*

| ID | Requerimiento | Prioridad | Vinculado a objetivo |
| --- | --- | --- | --- |
| RF-01 | El sistema debe permitir la carga masiva de imágenes de contratos manuscritos con barra de progreso y retroalimentación de estado por imagen | Alta | OE-2 |
| RF-02 | El sistema debe extraer automáticamente los campos estructurados del contrato (fecha, contratante, fallecido, tipo de pago, ataúd, monto, vehículos, cargadores) a partir de la imagen cargada | Alta | OE-2 |
| RF-03 | El sistema debe presentar los datos extraídos en una interfaz de validación lado a lado con la imagen original, permitiendo la corrección manual antes de confirmar el registro | Alta | OE-2 |
| RF-04 | El sistema debe almacenar el historial digitalizado de servicios funerarios en la base de datos PostgreSQL con integridad referencial entre todas las entidades del dominio | Alta | OE-4 |
| RF-05 | El sistema debe exponer un endpoint de predicción que reciba el modelo seleccionado, la variable objetivo y el horizonte de meses, y retorne las proyecciones de stock en formato JSON | Alta | OE-3 |
| RF-06 | El sistema debe visualizar las proyecciones de stock en un panel gráfico con datos históricos y predichos, permitiendo identificar posibles quiebres de inventario | Alta | OE-3 |
| RF-07 | El sistema debe emitir alertas visuales en el dashboard cuando el stock proyectado de un producto alcance el umbral mínimo configurado | Alta | OE-3 |
| RF-08 | El sistema debe gestionar el inventario de ataúdes, capillas y vehículos con operaciones de alta, consulta, edición y borrado lógico mediante estados activo/inactivo | Alta | OE-4 |
| RF-09 | El sistema debe registrar nuevos servicios funerarios con datos del fallecido, contratante, tipo de pago, ataúd asignado, capilla, vehículos y cargadores, actualizando el stock automáticamente al confirmar el servicio | Alta | OE-4 |
| RF-10 | El sistema debe gestionar pagos de servicios funerarios con soporte para modalidad directa y mixta, integrando Stripe como pasarela de procesamiento | Alta | OE-4 |
| RF-11 | El sistema debe validar el DNI de fallecidos y contratantes en tiempo real consultando la API DECOLECTA, autocompletando los datos básicos de la persona | Media | OE-4 |
| RF-12 | El sistema debe gestionar usuarios, roles y permisos de forma dinámica, permitiendo al administrador crear nuevos roles con conjuntos de permisos configurables sin modificar el código | Alta | OE-4 |
| RF-13 | El sistema debe autenticar a los usuarios mediante credenciales y token JWT con expiración automática tras 60 minutos de inactividad, redirigiendo al login al expirar la sesión | Alta | OE-4 |
| RF-14 | El sistema debe documentar todos los endpoints de las APIs de extracción y predicción mediante Swagger, incluyendo parámetros de entrada, formato JSON de salida y ejemplos reales | Media | OE-4 |
| RF-15 | El sistema debe registrar y consultar el historial de fallecidos y contratantes, con búsqueda por nombre y DNI, protegiendo la eliminación de fallecidos vinculados a servicios existentes | Media | OE-4 |

*3.2.2 Requerimientos no funcionales*

- **Rendimiento.** El endpoint de extracción debe procesar una imagen de contrato y retornar el JSON estructurado en un tiempo inferior a 15 minutos cuando opera sobre CPU mediante Ollama, y en aproximadamente 15 segundos cuando utiliza la API de Gemini como motor de inferencia. El endpoint de predicción debe retornar las proyecciones de stock ante una petición HTTP válida en menos de 5 segundos. La interfaz web debe cargar y renderizar las vistas principales sin errores de consola en las versiones actuales de Chrome, Edge y Firefox.
- **Usabilidad.** La plataforma web es accesible exclusivamente a través de navegador web estándar, sin requerir instalación de software ni hardware especializado en el dispositivo del usuario. La interfaz de validación de datos extraídos presenta la imagen original y los campos editables en pantalla simultáneamente para minimizar el tiempo de corrección manual. El panel de pronósticos permite al usuario configurar el modelo, la variable objetivo y el horizonte de predicción de forma autónoma. El sistema incluye un manual de usuario orientado a la secretaria de la funeraria para guiar los procesos de carga masiva y validación.

**3.3 Modelado del sistema**

- **Diagrama de casos de uso**
    - **Sistema Global - Diagrama de Contexto**
        
        !Untitled diagram-2026-07-07-051657.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph SISTEMA["SISTEMA FUNERARIA MÁXIMO ARANZABAL"]
                    FE["Frontend Angular<br/>(funeraria-frontend)"]
                    BE["Backend FastAPI<br/>(Inventario Inteligente)"]
                    ML["API ML / IA<br/>(Aranzabal Modelo)"]
                end
            
                subgraph ACTORES["ACTORES"]
                    ADMIN["👤 Administrador"]
                    TRAB["👤 Trabajador"]
                    OPE["👤 Operador"]
                end
            
                subgraph EXTERNOS["SISTEMAS EXTERNOS"]
                    RENIEC["🌐 RENIEC<br/>(Decolecta API)"]
                    STRIPE["💳 Stripe<br/>(Pasarela de pagos)"]
                    OLLAMA["🤖 Ollama LLM<br/>(qwen2.5vl:3b)"]
                    PG["🗄️ PostgreSQL<br/>(Supabase)"]
                end
            
                FE -->|"REST + JWT"| BE
                FE -->|"REST HTTP"| ML
                BE -->|"REST HTTP"| RENIEC
                BE -->|"SDK.js"| STRIPE
                BE -->|"SQLModel"| PG
                ML -->|"/api/chat"| OLLAMA
            
                ADMIN --> FE
                TRAB --> FE
                OPE --> FE
            
                style SISTEMA fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
                style ACTORES fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
                style EXTERNOS fill:#fce4ec,stroke:#c62828,stroke-width:2px
            ```
            
    - **Frontend - Gestión de Servicios Funerarios**
        
        !Untitled diagram-2026-07-07-052936.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph SERVICIOS["Frontend Angular - Gestión de Servicios"]
                    direction TB
                    UC08["UC-08<br/>Listar servicios<br/><i>GET /services/</i>"]
                    UC09["UC-09<br/>Filtrar servicios"]
                    UC10["UC-10<br/>Paginar servicios"]
                    UC11["UC-11<br/>Crear nuevo servicio<br/><i>POST /services/</i>"]
                    UC12["UC-12<br/>Editar servicio existente<br/><i>PATCH /services/{id}</i>"]
                    UC14["UC-14<br/>Verificar DNI fallecido<br/>con RENIEC"]
                    UC15["UC-15<br/>Verificar DNI contratante<br/>con RENIEC"]
                    UC16["UC-16<br/>Seleccionar vehículos"]
                    UC18["UC-18<br/>Ver detalle servicio"]
                    UC19["UC-19<br/>Eliminar servicio<br/><i>DELETE /services/{id}</i>"]
                    UC20["UC-20<br/>Registrar pago<br/>con Stripe<br/><i>POST /pagos/crear-intent</i>"]
                    UC22["UC-22<br/>Agregar pasajero"]
                    UC23["UC-23<br/>Editar pasajero"]
                    UC24["UC-24<br/>Eliminar pasajero"]
                end
            
                ADMIN["👤 Administrador"]
                TRAB["👤 Trabajador"]
                RENIEC["🌐 RENIEC"]
                STRIPE["💳 Stripe"]
            
                ADMIN --> UC08
                TRAB --> UC08
                ADMIN --> UC09
                TRAB --> UC09
                UC08 -.->|"include"| UC10
                ADMIN --> UC11
                TRAB --> UC11
                ADMIN --> UC12
                TRAB --> UC12
                UC14 -.->|"include"| UC11
                UC15 -.->|"include"| UC11
                UC16 -.->|"include"| UC11
                ADMIN --> UC18
                TRAB --> UC18
                ADMIN --> UC19
                ADMIN --> UC20
                TRAB --> UC20
                UC22 -.->|"include"| UC18
                UC23 -.->|"include"| UC18
                UC24 -.->|"include"| UC18
            
                UC14 --> RENIEC
                UC15 --> RENIEC
                UC20 --> STRIPE
            
                style SERVICIOS fill:#e8eaf6,stroke:#283593,stroke-width:2px
            ```
            
    - **Frontend - Gestión de Inventario**
        
        !Untitled diagram-2026-07-07-053119.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph INVENTARIO["Frontend Angular - Gestión de Inventario"]
                    direction TB
                    subgraph ATAUDES["ATAÚDES"]
                        UC25["UC-25<br/>Listar ataudes"]
                        UC26["UC-26<br/>Filtrar ataudes"]
                        UC27["UC-27<br/>Crear ataud"]
                        UC28["UC-28<br/>Editar ataud"]
                        UC29["UC-29<br/>Eliminar ataud"]
                        UC30["UC-30<br/>Actualizar stock"]
                    end
                    subgraph CAPILLAS["CAPILLAS"]
                        UC32["UC-32<br/>Listar capillas"]
                        UC33["UC-33<br/>Filtrar capillas"]
                        UC34["UC-34<br/>Crear capilla"]
                        UC35["UC-35<br/>Editar capilla"]
                        UC36["UC-36<br/>Eliminar capilla"]
                        UC37["UC-37<br/>Actualizar stock"]
                    end
                    subgraph VEHICULOS["VEHÍCULOS"]
                        UC39["UC-39<br/>Listar vehículos"]
                        UC40["UC-40<br/>Filtrar vehículos"]
                        UC41["UC-41<br/>Crear vehículo"]
                        UC42["UC-42<br/>Editar vehículo"]
                        UC43["UC-43<br/>Eliminar vehículo"]
                    end
                end
            
                ADMIN["👤 Administrador"]
                TRAB["👤 Trabajador"]
            
                ADMIN --> ATAUDES
                ADMIN --> CAPILLAS
                ADMIN --> VEHICULOS
            
                TRAB -->|"Solo lectura<br/>(leer)"| UC25
                TRAB -->|"Solo lectura<br/>(leer)"| UC26
                TRAB -->|"Solo lectura<br/>(leer)"| UC32
                TRAB -->|"Solo lectura<br/>(leer)"| UC33
                TRAB -->|"Solo lectura<br/>(leer)"| UC39
                TRAB -->|"Solo lectura<br/>(leer)"| UC40
            
                style INVENTARIO fill:#e8eaf6,stroke:#283593,stroke-width:2px
                style ATAUDES fill:#fff3e0,stroke:#e65100,stroke-width:1px
                style CAPILLAS fill:#f3e5f5,stroke:#6a1b9a,stroke-width:1px
                style VEHICULOS fill:#e0f2f1,stroke:#00695c,stroke-width:1px
            ```
            
    - **Frontend - Extracción de Contratos con IA**
        
        !ATAÚDES and CAPILLAS-2026-07-07-053343.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph IA["Frontend Angular - Extracción de Contratos con IA"]
                    direction TB
                    UC68["UC-68<br/>Subir imágenes de<br/>contratos"]
                    UC69["UC-69<br/>Procesar contrato<br/>con IA<br/><i>POST /ia/process-contract</i><br/><i>GET /ia/task/{id}</i>"]
                    UC70["UC-70<br/>Revisar datos<br/>extraídos"]
                    UC71["UC-71<br/>Editar datos<br/>extraídos por IA"]
                    UC72["UC-72<br/>Seleccionar vehículos<br/>detectados"]
                    UC73["UC-73<br/>Guardar contrato<br/>como servicio<br/><i>POST /services/</i>"]
                    UC74["UC-74<br/>Reintentar<br/>procesamiento fallido"]
                    UC75["UC-75<br/>Eliminar imagen<br/>de la cola"]
                    UC76["UC-76<br/>Gestionar cola<br/>de procesamiento"]
                end
            
                OPER["👤 Operador"]
                APIML["🤖 API ML<br/>(Aranzabal Modelo)"]
                OLLAMA["🤖 Ollama LLM<br/>(qwen2.5vl:3b)"]
            
                OPER --> UC68
                UC68 -.->|"include"| UC76
                UC76 --> UC69
                UC69 --> APIML
                APIML --> OLLAMA
                UC69 -.->|"include"| UC70
                UC70 -.->|"include"| UC71
                UC71 -.->|"include"| UC72
                UC72 -.->|"include"| UC73
                UC69 -.->|"extend"| UC74
                UC68 -.->|"extend"| UC75
            
                style IA fill:#e8eaf6,stroke:#283593,stroke-width:2px
            ```
            
    - **Frontend - Predicciones y Pronósticos ML**
        
        !ATAÚDES and CAPILLAS-2026-07-07-053508.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph PREDICCIONES["Frontend Angular - Predicciones y Pronósticos ML"]
                    direction TB
                    UC77["UC-77<br/>Ver información de<br/>modelos disponibles<br/><i>GET /predictions/models</i>"]
                    UC78["UC-78<br/>Ver histórico de<br/>servicios<br/><i>GET /predictions/history/{target}</i>"]
                    UC79["UC-79<br/>Ejecutar predicción<br/>temporal<br/><i>POST /predictions/predict</i>"]
                    UC80["UC-80<br/>Visualizar resultado<br/>de predicción"]
                    UC81["UC-81<br/>Comparar modelos<br/><i>GET /predictions/compare</i>"]
                    UC82["UC-82<br/>Calcular necesidades<br/>de inventario<br/><i>POST /predictions/distribution/predict</i>"]
                    UC83["UC-83<br/>Visualizar necesidades<br/>de ataudes"]
                    UC84["UC-84<br/>Visualizar necesidades<br/>de capillas"]
                end
            
                OPER["👤 Operador"]
                APIML["🤖 API ML<br/>(Aranzabal Modelo)"]
            
                OPER --> UC77
                OPER --> UC78
                OPER --> UC79
                OPER --> UC81
                OPER --> UC82
                UC79 -.->|"include"| UC80
                UC82 -.->|"include"| UC83
                UC82 -.->|"include"| UC84
                UC79 --> APIML
                UC81 --> APIML
                UC82 --> APIML
            
                style PREDICCIONES fill:#e8eaf6,stroke:#283593,stroke-width:2px
            ```
            
    - **Backend - Autenticación y RBAC**
        
        !ATAÚDES and CAPILLAS-2026-07-07-053650.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph BACKEND["Backend FastAPI - Autenticación y RBAC"]
                    direction TB
                    UC01["UC-01<br/>Iniciar sesión<br/><i>POST /auth/login</i><br/>(OAuth2 + JWT)"]
                    UC02["UC-02<br/>Editar mi perfil<br/><i>PUT /users/me</i>"]
                    UC04["UC-04<br/>Crear usuario<br/><i>POST /users/</i>"]
                    UC05["UC-05<br/>Listar usuarios<br/><i>GET /users/</i>"]
                    UC06["UC-06<br/>Eliminar usuario<br/><i>DELETE /users/{id}</i>"]
                    UC07["UC-07<br/>Actualizar usuario<br/><i>PUT /users/{id}</i>"]
                    UC08["UC-08<br/>Activar/desactivar<br/>usuario<br/><i>PATCH /users/{id}/status</i>"]
                    UC10["UC-10<br/>Crear rol<br/><i>POST /roles/</i>"]
                    UC11["UC-11<br/>Eliminar rol<br/><i>DELETE /roles/{id}</i>"]
                    UC12["UC-12<br/>Listar roles<br/><i>GET /roles/</i>"]
                    UC76["UC-76<br/>Verificar permisos<br/>por acción"]
                end
            
                ADMIN["👤 Administrador"]
                TRAB["👤 Trabajador"]
                JWT["🔑 JWT<br/>(decode_token)"]
                PERM["🛡️ CheckerPermisos"]
            
                ADMIN --> UC01
                TRAB --> UC01
                ADMIN --> UC02
                TRAB --> UC02
                ADMIN --> UC04
                ADMIN --> UC05
                ADMIN --> UC06
                ADMIN --> UC07
                ADMIN --> UC08
                ADMIN --> UC10
                ADMIN --> UC11
                ADMIN --> UC12
            
                UC01 -.->|"genera"| JWT
                JWT -.->|"valida"| UC76
                PERM -.->|"verifica"| UC76
            
                style BACKEND fill:#e8eaf6,stroke:#283593,stroke-width:2px
            ```
            
    - **Backend - Gestión de Entidades**
        
        !ATAÚDES and CAPILLAS-2026-07-07-053907.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph ENTIDADES["Backend FastAPI - Gestión de Entidades"]
                    direction TB
                    subgraph SERV["SERVICIOS"]
                        UC30["UC-30<br/>Listar servicios"]
                        UC31["UC-31<br/>Obtener servicio"]
                        UC32["UC-32<br/>Crear servicio<br/>(transacción completa)"]
                        UC33["UC-33<br/>Modificar servicio"]
                        UC34["UC-34<br/>Eliminar servicio"]
                    end
                    subgraph INV["INVENTARIO"]
                        UC13["UC-13 a UC-29<br/>CRUD ataudes,<br/>capillas, vehículos<br/><i>+ control de stock</i>"]
                    end
                    subgraph PERS["PERSONAS"]
                        UC35["UC-35 a UC-44<br/>CRUD fallecidos,<br/>contratantes"]
                    end
                    subgraph PASAJ["PASAJEROS"]
                        UC45["UC-45 a UC-48<br/>CRUD pasajeros<br/>(asociados a servicio)"]
                    end
                end
            
                ADMIN["👤 Administrador"]
                TRAB["👤 Trabajador"]
            
                ADMIN --> SERV
                ADMIN --> INV
                ADMIN --> PERS
                ADMIN --> PASAJ
            
                TRAB --> UC30
                TRAB --> UC31
                TRAB --> UC32
                TRAB --> UC33
                TRAB -->|"❌ No tiene acceso"| UC34
            
                TRAB -->|"Solo lectura"| UC13
                TRAB --> PERS
                TRAB --> PASAJ
            
                style ENTIDADES fill:#e8eaf6,stroke:#283593,stroke-width:2px
                style SERV fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px
                style INV fill:#fff3e0,stroke:#e65100,stroke-width:1px
                style PERS fill:#fce4ec,stroke:#c62828,stroke-width:1px
                style PASAJ fill:#f3e5f5,stroke:#6a1b9a,stroke-width:1px
            ```
            
    - **Backend - Integraciones Externas**
        
        !ATAÚDES and CAPILLAS-2026-07-07-054205.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph INTEGRACIONES["Backend FastAPI - Integraciones Externas"]
                    direction TB
                    subgraph RENIEC_MOD["VALIDACIÓN RENIEC"]
                        UC54["UC-54<br/>Consultar datos de DNI<br/><i>GET /reniec/{dni}</i>"]
                    end
                    subgraph STRIPE_MOD["PAGOS STRIPE"]
                        UC49["UC-49<br/>Crear intención de pago<br/><i>POST /pagos/crear-intent</i>"]
                        UC50["UC-50<br/>Recibir notificación<br/>pago exitoso<br/><i>POST /pagos/webhook</i>"]
                        UC51["UC-51<br/>Recibir notificación<br/>pago fallido<br/><i>POST /pagos/webhook</i>"]
                        UC52["UC-52<br/>Listar pagos<br/>de un servicio"]
                    end
                    subgraph DB["BASE DE DATOS"]
                        UC55["UC-55 a UC-59<br/>Seeding automático<br/>(permisos, roles, admin)"]
                    end
                end
            
                ADMIN["👤 Administrador"]
                TRAB["👤 Trabajador"]
                RENIEC["🌐 RENIEC<br/>(Decolecta API)"]
                STRIPE_E["💳 Stripe<br/>(PaymentIntents + Webhooks)"]
                PG["🗄️ PostgreSQL"]
            
                ADMIN --> RENIEC_MOD
                TRAB --> RENIEC_MOD
                UC54 --> RENIEC
            
                ADMIN --> STRIPE_MOD
                TRAB --> STRIPE_MOD
                UC49 --> STRIPE_E
                UC50 --> STRIPE_E
                UC51 --> STRIPE_E
            
                UC55 --> PG
            
                style INTEGRACIONES fill:#e8eaf6,stroke:#283593,stroke-width:2px
                style RENIEC_MOD fill:#e0f2f1,stroke:#00695c,stroke-width:1px
                style STRIPE_MOD fill:#fff3e0,stroke:#e65100,stroke-width:1px
                style DB fill:#f3e5f5,stroke:#6a1b9a,stroke-width:1px
            ```
            
    - **API ML - Extracción de Contratos con Ollama**
        
        !ATAÚDES and CAPILLAS-2026-07-07-054414.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph API_ML["API ML - Extracción de Contratos con Ollama"]
                    direction TB
                    UC_A1["UC-A1<br/>Subir contrato<br/>para extracción<br/><i>POST /ia/process-contract</i>"]
                    UC_A2["UC-A2<br/>Consultar estado<br/>de tarea<br/><i>GET /ia/task/{tarea_id}</i>"]
                    UC_A3["UC-A3<br/>Validar formato<br/>de imagen"]
                    UC_A4["UC-A4<br/>Reintentar extracción<br/>fallida"]
                    UC_D3["UC-D3<br/>Normalización de<br/>datos extraídos"]
            
                    subgraph PIPELINE["PIPELINE IA"]
                        direction LR
                        P1["1. Preprocesar<br/>imagen"]
                        P2["2. Codificar<br/>base64"]
                        P3["3. Enviar a<br/>Ollama API"]
                        P4["4. Parsear<br/>JSON"]
                        P5["5. Normalizar<br/>campos"]
                        P1 --> P2 --> P3 --> P4 --> P5
                    end
                end
            
                FE["🖥️ Frontend<br/>(Angular)"]
                OLLAMA["🤖 Ollama LLM<br/>localhost:11434<br/>(qwen2.5vl:3b)"]
            
                FE -->|"POST imagen"| UC_A1
                FE -->|"GET polling"| UC_A2
                UC_A1 -.->|"include"| UC_A3
                UC_A1 -.->|"202 Accepted"| FE
                UC_A1 --> PIPELINE
                PIPELINE -->|"HTTP POST<br/>/api/chat"| OLLAMA
                PIPELINE -.->|"extend"| UC_A4
                P5 -.->|"include"| UC_D3
            
                style API_ML fill:#e8eaf6,stroke:#283593,stroke-width:2px
                style PIPELINE fill:#e0f7fa,stroke:#00838f,stroke-width:1px
            ```
            
    - **API ML - Predicciones Temporales**
        
        !image.png
        
        - Código MERMAID:
            
            ```
            graph TB
                subgraph PRED["API ML - Predicciones Temporales"]
                    direction TB
                    UC_B1["UC-B1<br/>Consultar modelos<br/>disponibles<br/><i>GET /predictions/models</i>"]
                    UC_B2["UC-B2<br/>Predecir servicios<br/>totales<br/><i>POST /predictions/predict</i>"]
                    UC_B3["UC-B3<br/>Predecir monto<br/>total"]
                    UC_B4["UC-B4<br/>Comparar rendimiento<br/>de modelos<br/><i>GET /predictions/compare</i>"]
                    UC_B5["UC-B5<br/>Ver histórico<br/>de servicios<br/><i>GET /predictions/history/{target}</i>"]
                    UC_B6["UC-B6<br/>Ver histórico<br/>de montos"]
                    UC_C1["UC-C1<br/>Ver distribución<br/>de ataudes<br/><i>GET /predictions/distribution/coffins</i>"]
                    UC_C2["UC-C2<br/>Ver distribución<br/>de capillas<br/><i>GET /predictions/distribution/chapels</i>"]
                    UC_C3["UC-C3<br/>Predecir distribución<br/>de ataudes y capillas<br/><i>POST /predictions/distribution/predict</i>"]
                    UC_D2["UC-D2<br/>Carga automática<br/>de modelos"]
                end
            
                FE["🖥️ Frontend<br/>(Angular)"]
                MODELS["📦 Modelos<br/>serializados<br/>.pkl / .keras"]
            
                FE --> UC_B1
                FE --> UC_B2
                FE --> UC_B4
                FE --> UC_B5
                FE --> UC_C1
                FE --> UC_C2
                FE --> UC_C3
            
                UC_B2 -.->|"include"| UC_B3
                UC_B5 -.->|"include"| UC_B6
                UC_C3 -.->|"include"| UC_C1
                UC_C3 -.->|"include"| UC_C2
            
                UC_B2 --> MODELS
                UC_B3 --> MODELS
                UC_C3 --> MODELS
                UC_B4 --> MODELS
                UC_D2 --> MODELS
            
                style PRED fill:#e8eaf6,stroke:#283593,stroke-width:2px
            ```
            
- **Diagrama de clases o entidad-relación**
    - Diagrama de clase:
        - Diagrama
            
            !DA2-2026-07-18-031704.png
            
        - Codigo Mermaid
            
            ```mermaid
            classDiagram
            direction LR
            
            %%==========================
            %% SEGURIDAD
            %%==========================
            
            class User {
                -id : int
                -username : string
                -password : string
                -activo : bool
                +login()
                +logout()
            }
            
            class Role {
                -id : int
                -nombre : string
            }
            
            class Permission {
                -id : int
                -nombre : string
                -descripcion : string
            }
            
            %%==========================
            %% GESTIÓN FUNERARIA
            %%==========================
            
            class Servicio {
                -id : int
                -direccionVelacion : string
                -tipoPago : TipoPago
                -costo : decimal
                -fecha : date
                -cantidadCargadores : int
                +registrar()
                +calcularCosto()
            }
            
            class Ataud {
                -id : int
                -modelo : string
                -color : string
                -stock : int
                -activo : bool
                +actualizarStock()
            }
            
            class Capilla {
                -id : int
                -modelo : string
                -stock : int
                -activo : bool
                +actualizarStock()
            }
            
            class Vehiculo {
                -id : int
                -tipo : TipoVehiculo
                -activo : bool
                +cambiarEstado()
            }
            
            class Contratante {
                -id : int
                -nombre : string
                -dni : string
                -telefono : string
                -activo : bool
            }
            
            class Fallecido {
                -id : int
                -nombre : string
                -dni : string
                -activo : bool
            }
            
            class Pasajero {
                -id : int
                -nombre : string
                -dni : string
            }
            
            class Pago {
                -id : int
                -paymentIntentId : string
                -monto : decimal
                -moneda : string
                -estado : EstadoPago
                -fechaCreacion : datetime
                -fechaActualizacion : datetime
                +procesarPago()
                +actualizarEstado()
            }
            
            class ServicioVehiculo {
                -id : int
            }
            
            %%==========================
            %% ENUMERACIONES
            %%==========================
            
            class TipoPago {
                <<enumeration>>
                DIRECTO
                SEGURO
                MIXTO
            }
            
            class TipoVehiculo {
                <<enumeration>>
                PORTA_ATAUD
                PORTA_FLORES
                MIXTO
                AUTO
                MICROBUS
            }
            
            class EstadoPago {
                <<enumeration>>
                PENDIENTE
                COMPLETADO
                FALLIDO
                CANCELADO
            }
            
            %%==========================
            %% RELACIONES
            %%==========================
            
            User "*" -- "*" Role : posee
            Role "*" -- "*" Permission : incluye
            
            User "1" --> "*" Servicio : registra
            
            Servicio "1" --> "0..1" Ataud : utiliza
            Servicio "1" --> "1" Capilla : reserva
            Servicio "1" --> "1" Contratante
            Servicio "1" --> "1" Fallecido
            Servicio "1" --> "*" Pasajero
            Servicio "1" --> "*" Pago
            
            Servicio "1" --> "*" ServicioVehiculo
            Vehiculo "1" --> "*" ServicioVehiculo
            
            Servicio --> TipoPago
            Vehiculo --> TipoVehiculo
            Pago --> EstadoPago
            ```
            
    - Diagrama de Entidad - relación:
        - Diagrama
            
            !DA2-2026-07-18-031939.png
            
        - Código Mermaid
            
            ```jsx
            erDiagram
            
            %% =========================
            %% SEGURIDAD
            %% =========================
            
            USER {
                int id PK
                varchar username UK
                varchar password
                boolean activo
            }
            
            ROLE {
                int id PK
                varchar nombre UK
            }
            
            PERMISSION {
                int id PK
                varchar nombre UK
                varchar descripcion
            }
            
            USER_ROLE_LINK {
                int user_id PK, FK
                int role_id PK, FK
            }
            
            ROLE_PERMISSION_LINK {
                int role_id PK, FK
                int permission_id PK, FK
            }
            
            %% =========================
            %% GESTIÓN FUNERARIA
            %% =========================
            
            SERVICIO {
                int id PK
                int id_usuario FK
                int id_contratante FK
                int id_fallecido FK
                int id_ataud FK
                int id_capilla FK
                varchar direccion_velacion
                varchar tipo_pago
                numeric costo
                date fecha
                int cantidad_cargadores
            }
            
            ATAUD {
                int id PK
                varchar modelo
                varchar color
                int stock
                boolean activo
            }
            
            CAPILLA {
                int id PK
                varchar modelo
                int stock
                boolean activo
            }
            
            VEHICULO {
                int id PK
                varchar tipo
                boolean activo
            }
            
            SERVICIO_VEHICULO {
                int id PK
                int id_servicio FK
                int id_vehiculo FK
            }
            
            CONTRATANTE {
                int id PK
                varchar nombre
                varchar dni UK
                varchar telefono
                boolean activo
            }
            
            FALLECIDO {
                int id PK
                varchar nombre
                varchar dni
                boolean activo
            }
            
            PASAJERO {
                int id PK
                int id_servicio FK
                varchar nombre
                varchar dni
            }
            
            PAGO {
                int id PK
                int id_servicio FK
                varchar payment_intent_id
                numeric monto
                varchar moneda
                varchar estado
                timestamp fecha_creacion
                timestamp fecha_actualizacion
            }
            
            %% =========================
            %% RELACIONES
            %% =========================
            
            USER ||--o{ USER_ROLE_LINK : posee
            ROLE ||--o{ USER_ROLE_LINK : asigna
            
            ROLE ||--o{ ROLE_PERMISSION_LINK : incluye
            PERMISSION ||--o{ ROLE_PERMISSION_LINK : pertenece
            
            USER ||--o{ SERVICIO : registra
            
            SERVICIO }o--|| ATAUD : utiliza
            SERVICIO }o--|| CAPILLA : reserva
            SERVICIO }o--|| CONTRATANTE : contratante
            SERVICIO }o--|| FALLECIDO : fallecido
            
            SERVICIO ||--o{ PASAJERO : incluye
            SERVICIO ||--o{ PAGO : genera
            
            SERVICIO ||--o{ SERVICIO_VEHICULO : asigna
            VEHICULO ||--o{ SERVICIO_VEHICULO : participa
            ```
            
    - **Descripción:**
    
    ## Dataset — Funeraria Máximo Aranzabal: Registro Histórico de Servicios Funerarios
    
    **Versión:** 1.0.0 (2026)
    
    **Autor:** Prieto Meléndez Alexander Antonio, Vidal Rodríguez Fabrizio
    
    ---
    
    ### Sobre el Dataset
    
    Este dataset contiene el registro histórico digitalizado de servicios funerarios de la Funeraria Máximo Aranzabal, ubicada en Trujillo, Perú. Los datos fueron extraídos manualmente a partir de contratos físicos manuscritos mediante el módulo de extracción de inteligencia artificial desarrollado en el proyecto, con revisión y corrección manual posterior para garantizar la integridad de cada registro. El dataset fue construido con el propósito de entrenar y evaluar modelos de predicción de demanda de inventario (ataúdes, capillas y vehículos) y constituye el primer conjunto de datos estructurado disponible del sector funerario peruano con este nivel de detalle operativo.
    
    ---
    
    ### Contenido
    
    El dataset contiene **340 registros** de servicios funerarios registrados entre **mayo de 2022 y febrero de 2026**, cubriendo **46 meses** de operación continua de la funeraria. Cada registro corresponde a un contrato de servicio funerario individual e incluye datos del contratante, del fallecido, de los recursos utilizados y del monto total del servicio.
    
    El archivo se distribuye en formato `.xlsx` con una única hoja de datos y encabezados en la primera fila. Cada fila representa un servicio funerario único identificado por su número de contrato.
    
    **Columnas del dataset:**
    
    | Columna | Tipo | Descripción |
    | --- | --- | --- |
    | `n_contrato` | String | Número de contrato único del servicio funerario (ej. 000202) |
    | `fecha` | Date | Fecha de celebración del contrato en formato YYYY-MM-DD |
    | `contratante_nombre` | String | Nombre completo del contratante en mayúsculas |
    | `contratante_dni` | String | Número de DNI del contratante (8 dígitos) |
    | `contratante_telefono` | String | Número de teléfono del contratante (solo dígitos) |
    | `direccion_velacion` | String | Dirección del lugar de velación indicada en el contrato |
    | `fallecido_nombre` | String | Nombre completo del fallecido en mayúsculas |
    | `velatorio` | String | Lugar de velatorio (ej. SU CASA, nombre de capilla) |
    | `forma_pago` | String | Modalidad de pago: directo, seguro o mixto |
    | `ataud_modelo` | String | Modelo del ataúd contratado (ej. COPA CON ADORNOS, LINCOLN) |
    | `ataud_color` | String | Color del ataúd si está especificado en el contrato |
    | `capilla_modelo` | String | Modelo de capilla ardiente contratada (ej. ILUMINADA MODELO MILAN) |
    | `carroza` | Integer | Indicador binario de presencia de carroza porta ataúd (0/1) |
    | `carroza_flores` | Integer | Indicador binario de presencia de carroza porta flores (0/1) |
    | `cargadores` | Integer | Número de cargadores contratados (valores: 4 o 6) |
    | `vehiculos` | String | Descripción de vehículos adicionales contratados (microbus, autos para deudos) |
    | `monto_total` | Float | Monto total del servicio en soles peruanos (S/) |
    | `notas_extra` | String | Observaciones adicionales registradas en el contrato (ej. acuerdos de pago parcial) |
    
    ---
    
    ### Propiedades del Dataset
    
    | Propiedad | Valor |
    | --- | --- |
    | Total de registros | 340 |
    | Número de columnas | 18 |
    | Formato | .xlsx (Microsoft Excel) |
    | Cobertura temporal | Mayo 2022 – Febrero 2026 |
    | Frecuencia | Registro por servicio (irregular) |
    | Idioma de los datos | Español |
    | País de origen | Perú |
    | Sector | Servicios funerarios |
    | Valores nulos tratados | Sí (imputación y normalización aplicada) |
    | Outliers tratados | Sí (winsorización al percentil 99, umbral S/ 154,600) |
    
    ### Estadísticas Descriptivas
    
- **Diagrama de secuencia de flujos críticos**
    - Crear servicio
        - Diagrama
            
            !DA2-2026-07-18-032717.png
            
        - Codigo Mermad
            
            ```jsx
            sequenceDiagram
                autonumber
                actor User as Trabajador
                participant FE_ServicioCreate as Frontend<br/>ServicioCreateComponent
                participant FE_ServicioService as Frontend<br/>ServicioService
                participant FE_ReniecService as Frontend<br/>ReniecService
                participant BE_ServRouter as Backend<br/>servicio_router.py<br/>POST /services
                participant BE_ServService as Backend<br/>servicio_service.py
                participant BE_FallService as Backend<br/>fallecido_service.py
                participant BE_ContrService as Backend<br/>contratante_service.py
                participant BE_AtaudService as Backend<br/>ataud_service.py
                participant BE_CapService as Backend<br/>capilla_service.py
                participant BE_DB as PostgreSQL<br/>tablas: servicio,<br/>fallecido,<br/>contratante,<br/>ataud,<br/>capilla
            
                Note over User,BE_DB: === FASE 1: Validación RENIEC ===
                User->>FE_ServicioCreate: Ingresa DNI del contratante
                FE_ServicioCreate->>FE_ReniecService: consultar(dni)
                FE_ReniecService->>BE_DB: GET /reniec/{dni}
                BE_DB-->>FE_ReniecService: {nombres, apellido_paterno, ...}
                FE_ReniecService-->>FE_ServicioCreate: Datos de RENIEC
            
                Note over User,BE_DB: === FASE 2: Crear Servicio ===
                User->>FE_ServicioCreate: Completa formulario y envía
                FE_ServicioCreate->>FE_ServicioService: crear(servicioData)
                FE_ServicioService->>BE_ServRouter: POST /services<br/>(fallecido, contratante, id_capilla, id_ataud, vehiculos, pasajeros)
                
                BE_ServRouter->>BE_ServService: crear_servicio(data)
                
                Note over BE_ServService: 1. Crear Fallecido
                BE_ServService->>BE_FallService: crear(FallecidoCrear)
                BE_FallService->>BE_DB: INSERT INTO fallecido
                BE_DB-->>BE_FallService: fallecido_id
                
                Note over BE_ServService: 2. Crear Contratante
                BE_ServService->>BE_ContrService: crear(ContratanteCrear)
                BE_ContrService->>BE_DB: INSERT INTO contratante
                BE_DB-->>BE_ContrService: contratante_id
                
                Note over BE_ServService: 3. Descontar stock Capilla
                BE_ServService->>BE_CapService: actualizar_stock(id_capilla, -1)
                BE_CapService->>BE_DB: UPDATE capilla SET stock = stock - 1
                BE_DB-->>BE_CapService: OK
                
                Note over BE_ServService: 4. Descontar stock Ataud (opcional)
                alt tiene ataud
                    BE_ServService->>BE_AtaudService: actualizar_stock(id_ataud, -1)
                    BE_AtaudService->>BE_DB: UPDATE ataud SET stock = stock - 1
                    BE_DB-->>BE_AtaudService: OK
                end
                
                Note over BE_ServService: 5. Crear Servicio
                BE_ServService->>BE_DB: INSERT INTO servicio<br/>(id_usuario, id_ataud, id_capilla, id_contratante, id_fallecido, ...)
                BE_DB-->>BE_ServService: servicio_id
                
                Note over BE_ServService: 6. Asignar Vehículos
                loop Cada vehículo seleccionado
                    BE_ServService->>BE_DB: INSERT INTO servicio_vehiculo<br/>(id_servicio, id_vehiculo)
                end
                
                Note over BE_ServService: 7. Agregar Pasajeros (si hay vehículos auto/microbus)
                loop Cada pasajero
                    BE_ServService->>BE_DB: INSERT INTO pasajero<br/>(nombre, dni_pasajero, id_servicio)
                end
                
                BE_ServService-->>BE_ServRouter: ServicioLeerCompleto
                BE_ServRouter-->>FE_ServicioService: 201 Created
                FE_ServicioService-->>FE_ServicioCreate: Servicio creado
                FE_ServicioCreate->>User: Redirige a detalle del servicio
            ```
            
    - Pago con Stripe
        - Diagrama
            
            !DA2-2026-07-18-032858.png
            
        - Código Mermaid
            
            ```jsx
            sequenceDiagram
                autonumber
                actor User as Contratante
                participant FE_ServDetail as Frontend<br/>ServicioDetailComponent
                participant FE_PagoService as Frontend<br/>PagoService
                participant BE_PagoRouter as Backend<br/>pago_router.py<br/>POST /pagos/crear-intent
                participant BE_PagoService as Backend<br/>pago_service.py
                participant BE_DB as PostgreSQL<br/>tabla: pago,<br/>servicio
                participant Stripe as Stripe API<br/>(externo)
                participant BE_Webhook as Backend<br/>pago_router.py<br/>POST /pagos/webhook
            
                Note over User,BE_Webhook: === FASE 1: Crear PaymentIntent ===
                User->>FE_ServDetail: Click "Pagar"
                FE_ServDetail->>FE_PagoService: crearIntent({id_servicio, monto, moneda})
                FE_PagoService->>BE_PagoRouter: POST /pagos/crear-intent<br/>{id_servicio, monto: 150000, moneda: "pen"}
                
                BE_PagoRouter->>BE_PagoService: crear_payment_intent(...)
                BE_PagoService->>BE_DB: INSERT INTO pago<br/>(id_servicio, monto, moneda, estado="pendiente")
                BE_DB-->>BE_PagoService: pago_id
                
                BE_PagoService->>Stripe: stripe.PaymentIntent.create()<br/>(amount=150000, currency="pen")
                Stripe-->>BE_PagoService: {client_secret, id}
                
                BE_PagoService->>BE_DB: UPDATE pago<br/>SET stripe_payment_intent_id = ?,<br/>estado = "pendiente"
                BE_PagoService-->>BE_PagoRouter: PagoResponse{client_secret}
                BE_PagoRouter-->>FE_PagoService: 200 OK
                FE_PagoService-->>FE_ServDetail: client_secret
                
                Note over User,BE_Webhook: === FASE 2: Procesar Pago (Stripe) ===
                FE_ServDetail->>User: Muestra formulario Stripe Elements
                User->>FE_ServDetail: Ingresa datos de tarjeta
                FE_ServDetail->>Stripe: stripe.confirmPayment(client_secret, card_data)
                Stripe-->>FE_ServDetail: Payment result
                
                Note over User,BE_Webhook: === FASE 3: Webhook Confirmación ===
                Stripe->>BE_Webhook: POST /pagos/webhook<br/>{type: "payment_intent.succeeded", ...}
                BE_Webhook->>BE_PagoService: actualizar_estado(pago_id, "completado")
                BE_PagoService->>BE_DB: UPDATE pago SET estado="completado",<br/>fecha_actualizacion=now()
                BE_DB-->>BE_PagoService: OK
                BE_PagoService-->>BE_Webhook: 200 OK
                BE_Webhook-->>Stripe: 200 OK
                
                Note over User,BE_Webhook: === FASE 4: Actualizar Vista ===
                FE_ServDetail->>FE_PagoService: obtenerPorServicio(id_servicio)
                FE_PagoService->>BE_PagoRouter: GET /pagos/servicio/{id_servicio}
                BE_PagoRouter->>BE_DB: SELECT * FROM pago WHERE id_servicio = ?
                BE_DB-->>BE_PagoRouter: pagos[]
                BE_PagoRouter-->>FE_PagoService: 200 OK
                FE_PagoService-->>FE_ServDetail: Lista de pagos actualizada
                FE_ServDetail->>User: Pago completado
            ```
            
    - Procesamiento de Contrato con IA
        - Diagrama
            
            !DA2-2026-07-18-033002.png
            
        - Código Mermaid
            
            ```jsx
            sequenceDiagram
                autonumber
                actor User as Trabajador
                participant FE_IA as Frontend<br/>IaComponent
                participant FE_HttpClient as Frontend<br/>HttpClient
                participant BE_IARouter as Backend API IA<br/>ia_router.py<br/>POST /ia/process-contract
                participant BE_IAService as Backend API IA<br/>ia_service.py
                participant Ollama as Ollama<br/>(Vision AI)<br/>qwen2.5vl:3b
                participant FE_TaskPolling as Frontend<br/>Polling cada 2s
                participant BE_TaskRouter as Backend API IA<br/>ia_router.py<br/>GET /ia/task/{id}
            
                Note over User,BE_TaskRouter: === FASE 1: Subir Imagen ===
                User->>FE_IA: Selecciona imagen de contrato
                FE_IA->>FE_HttpClient: POST /ia/process-contract<br/>(FormData: imagen)
                FE_HttpClient->>BE_IARouter: multipart/form-data<br/>{file: contract_image.jpg}
                BE_IARouter->>BE_IAService: procesar_contrato(imagen)
                BE_IAService->>BE_IAService: guardar imagen temporal<br/>+ crear tarea_id (UUID)
                BE_IAService-->>BE_IARouter: 202 Accepted<br/>{tarea_id: "abc-123"}
                BE_IARouter-->>FE_HttpClient: 202 Accepted
                FE_HttpClient-->>FE_IA: tarea_id
                
                Note over User,BE_TaskRouter: === FASE 2: Procesamiento IA (async) ===
                BE_IAService->>Ollama: POST /api/chat<br/>(imagen + prompt JSON)
                Note over Ollama: qwen2.5vl:3b<br/>analiza imagen y<br/>extrae campos
                Ollama-->>BE_IAService: JSON con campos extraídos<br/>{fecha, contratante_nombre,<br/>contratante_dni, fallecido_nombre,<br/>ataud_modelo, costo, ...}
                BE_IAService->>BE_IAService: guardar resultado en memoria
                
                Note over User,BE_TaskRouter: === FASE 3: Polling de Resultado ===
                loop Cada 2 segundos
                    FE_IA->>FE_TaskPolling: GET /ia/task/abc-123
                    FE_TaskPolling->>BE_TaskRouter: GET /ia/task/{tarea_id}
                    BE_TaskRouter->>BE_IAService: obtener_tarea(tarea_id)
                    alt tarea aún procesando
                        BE_IAService-->>BE_TaskRouter: {estado: "procesando"}
                        BE_TaskRouter-->>FE_TaskPolling: 200 OK
                        FE_TaskPolling-->>FE_IA: Esperando...
                    else tarea completada
                        BE_IAService-->>BE_TaskRouter: {estado: "completado",<br/>resultado: TranscripcionContratoOut}
                        BE_TaskRouter-->>FE_TaskPolling: 200 OK
                        FE_TaskPolling-->>FE_IA: Resultado completo
                    end
                end
                
                Note over User,BE_TaskRouter: === FASE 4: Mostrar Resultado ===
                FE_IA->>User: Muestra campos extraídos<br/>(fecha, nombre, DNI, ataud,<br/>capilla, costo, vehículos)
                FE_IA->>User: Botón "Guardar como Servicio"
            ```
            
    - Predicción con Modelos ML
        - Diagrama
            
            !DA2-2026-07-18-033056.png
            
        - Código Mermaid
            
            ```jsx
            sequenceDiagram
                autonumber
                actor User as Administrador
                participant FE_Pred as Frontend<br/>PrediccionesComponent
                participant FE_PredService as Frontend<br/>PrediccionService
                participant BE_PredRouter as Backend API IA<br/>prediccion_router.py<br/>POST /predictions/predict
                participant BE_PredService as Backend API IA<br/>prediccion_service.py
                participant ML_Model as Modelo ML<br/>(SARIMA/Prophet/XGBoost/<br/>LGBM/LSTM/ETS)
                participant BE_DB as Datos históricos<br/>(model_metadata.json)
            
                Note over User,BE_DB: === FASE 1: Obtener Info de Modelos ===
                User->>FE_Pred: Sección predicciones
                FE_Pred->>FE_PredService: listarModelos()
                FE_PredService->>BE_PredRouter: GET /predictions/models
                BE_PredRouter->>BE_PredService: obtener_info_modelos()
                BE_PredService->>BE_DB: leer model_metadata.json
                BE_DB-->>BE_PredService: {targets, modelos, train_periodo, test_periodo}
                BE_PredService-->>BE_PredRouter: ModeloInfoResponse
                BE_PredRouter-->>FE_PredService: 200 OK
                FE_PredService-->>FE_Pred: Info de modelos disponibles
            
                Note over User,BE_DB: === FASE 2: Ejecutar Predicción ===
                User->>FE_Pred: Selecciona modelo (ej: XGBoost)<br/>+ target (servicios_totales)<br/>+ pasos (6 meses)
                FE_Pred->>FE_PredService: predecir({modelo, target, pasos})
                FE_PredService->>BE_PredRouter: POST /predictions/predict<br/>{modelo: "xgboost", target: "servicios_totales", pasos: 6}
                BE_PredRouter->>BE_PredService: predecir(modelo, target, pasos)
                
                BE_PredService->>BE_PredService: cargar modelo serializado<br/>(xgboost_servicios_totales.pkl)
                BE_PredService->>BE_PredService: preparar features<br/>(lags [1,2,3,6] + mes)
                
                loop Para cada paso (mes 1..6)
                    BE_PredService->>ML_Model: modelo.predict(features)
                    ML_Model-->>BE_PredService: valor_predicho
                    BE_PredService->>BE_PredService: acumular predicción
                end
                
                BE_PredService-->>BE_PredRouter: PrediccionResponse<br/>{modelo, target, pasos,<br/>periodo_inicio: "2026-07",<br/>predicciones: [{mes, valor}...]}
                BE_PredRouter-->>FE_PredService: 200 OK
                FE_PredService-->>FE_Pred: Resultado de predicción
            
                Note over User,BE_DB: === FASE 3: Distribución de Necesidades ===
                User->>FE_Pred: Click "Ver distribución"
                FE_Pred->>FE_PredService: prediccionDistribucion(...)
                FE_PredService->>BE_PredRouter: POST /predictions/distribution/predict
                BE_PredRouter->>BE_PredService: distribucion_prediccion(...)
                BE_PredService->>BE_DB: obtener distribuciones históricas<br/>(ataudes y capillas)
                BE_PredService->>ML_Model: predecir_total
                BE_PredService->>BE_PredService: calcular proporciones<br/>por modelo de ataud y capilla
                BE_PredService-->>BE_PredRouter: DistribucionCompletaResponse
                BE_PredRouter-->>FE_PredService: 200 OK
                FE_PredService-->>FE_Pred: Gráficos ApexCharts<br/>(barras + líneas)
                FE_Pred->>User: Muestra predicciones + distribución
            ```
            
- **Modelo de base de datos (físico)**
    
    !DA2-2026-07-07-054205.png
    
    - Código Mermaid:
        
        ```
        erDiagram
        
        %% =========================
        %% SEGURIDAD
        %% =========================
        
        USER {
            int id PK
            varchar username UK
            varchar password
            boolean activo
        }
        
        ROLE {
            int id PK
            varchar nombre UK
        }
        
        PERMISSION {
            int id PK
            varchar nombre UK
            varchar descripcion
        }
        
        USER_ROLE_LINK {
            int user_id PK, FK
            int role_id PK, FK
        }
        
        ROLE_PERMISSION_LINK {
            int role_id PK, FK
            int permission_id PK, FK
        }
        
        %% =========================
        %% GESTIÓN FUNERARIA
        %% =========================
        
        SERVICIO {
            int id PK
            int id_usuario FK
            int id_contratante FK
            int id_fallecido FK
            int id_ataud FK
            int id_capilla FK
            varchar direccion_velacion
            varchar tipo_pago
            numeric costo
            date fecha
            int cantidad_cargadores
        }
        
        ATAUD {
            int id PK
            varchar modelo
            varchar color
            int stock
            boolean activo
        }
        
        CAPILLA {
            int id PK
            varchar modelo
            int stock
            boolean activo
        }
        
        VEHICULO {
            int id PK
            varchar tipo
            boolean activo
        }
        
        SERVICIO_VEHICULO {
            int id PK
            int id_servicio FK
            int id_vehiculo FK
        }
        
        CONTRATANTE {
            int id PK
            varchar nombre
            varchar dni UK
            varchar telefono
            boolean activo
        }
        
        FALLECIDO {
            int id PK
            varchar nombre
            varchar dni
            boolean activo
        }
        
        PASAJERO {
            int id PK
            int id_servicio FK
            varchar nombre
            varchar dni
        }
        
        PAGO {
            int id PK
            int id_servicio FK
            varchar payment_intent_id
            numeric monto
            varchar moneda
            varchar estado
            timestamp fecha_creacion
            timestamp fecha_actualizacion
        }
        
        %% =========================
        %% RELACIONES
        %% =========================
        
        USER ||--o{ USER_ROLE_LINK : posee
        ROLE ||--o{ USER_ROLE_LINK : asigna
        
        ROLE ||--o{ ROLE_PERMISSION_LINK : incluye
        PERMISSION ||--o{ ROLE_PERMISSION_LINK : pertenece
        
        USER ||--o{ SERVICIO : registra
        
        SERVICIO }o--|| ATAUD : utiliza
        SERVICIO }o--|| CAPILLA : reserva
        SERVICIO }o--|| CONTRATANTE : contratante
        SERVICIO }o--|| FALLECIDO : fallecido
        
        SERVICIO ||--o{ PASAJERO : incluye
        SERVICIO ||--o{ PAGO : genera
        
        SERVICIO ||--o{ SERVICIO_VEHICULO : asigna
        VEHICULO ||--o{ SERVICIO_VEHICULO : participa
        ```
        
- **Wireframes o mockups de alta fidelidad (mínimo 5 pantallas clave)**
    - Dashboard
        
        !{6E7C76F8-004F-4B02-96BD-EF2D38D84D05}.png
        
    - Crear servicio
        
        !{15EB2CC2-EF37-47A5-9E90-83D8A29155E3}.png
        
    - Listar Ataudes
        
        !{1E0678C8-836C-4AEF-A979-4F6EF5E3A531}.png
        
    - Modulo de extracción
        
        !{9C4295F7-A4CF-4D58-B866-BC5E5365EAE4}.png
        
    - Modulo de predicción
        
        !image.png
        
- **Pipeline completo de datos → preprocesamiento → modelo → salida**
    
    ### Pipeline 1: Extracción de Contratos
    
    Dato crudo → Preprocesamiento → Modelo → Salida
    
    | **Etapa** | **Qué pasa** | **Dónde** |
    | --- | --- | --- |
    | **Dato crudo** | Fotos de contratos funerarios escaneados | Subidos por el usuario via frontend |
    | **Preprocesamiento** | Grayscale → RGB → auto-crop → resize 1000px → auto-contrast → sharpen → JPEG 85% | `ia_service.py`: `preprocesar_imagen()` |
    | **Modelo** | Ollama `qwen2.5vl:3b` (Vision-Language Model, 3.8B params, Q4_K_M) | `ia_service.py`: `IAService` |
    | **Salida** | JSON estructurado: fecha, contratante, fallecido, ataúd, capilla, vehículos, costo | `schemas/ia.py`: `TranscripcionContratoOut` |
    
    ### Flujo completo:
    
    Imagen subida → compresión en frontend (2000px, JPEG 85%)
    
    → POST `/ia/process-contract` (202, tarea_id)
    
    → BackgroundTasks: `preprocesar_imagen` → Ollama `/api/chat` → limpiar JSON → normalizar campos
    
    → GET `/ia/task/{id}` → resultado JSON
    
    ### Pipeline 2: Predicción Temporal (6 modelos × 2 targets)
    
    Datos históricos → Preprocesamiento → 6 Modelos → Ensemble → Salida
    
    | **Etapa** | **Qué pasa** | **Dónde** |
    | --- | --- | --- |
    | **Dato crudo** | Excel con 340+ registros de servicios funerarios (2022-2026) | `data/raw/` |
    | **Preprocesamiento** | Limpieza de fechas, normalización de modelos de ataúd, imputación de faltantes, agregación mensual → `servicios_totales` y `monto_total` | Notebooks `01_preprocesamiento`, `02_data_augmentation` |
    | **Data Augmentation** | Bootstrap resampling (340→2040) + SMOTE (→836) | Notebook `02_data_augmentation` |
    | **Modelos** | SARIMA, ETS, Prophet, XGBoost, LightGBM, LSTM (2 targets × 6 = 12 modelos + 2 scalers) | Notebooks `03_modelos_temporales`, serializados en `src/modelos/` |
    | **Salida** | Predicción mensual de servicios totales + monto total, con distribución por tipo de ataúd (9) y capilla (8) | `prediccion_service.py` → JSON |
    
    ### Features por modelo:
    
    | **Modelo** | **Features** |
    | --- | --- |
    | SARIMA / ETS / Prophet | Serie temporal pura (sin features manuales) |
    | XGBoost / LightGBM | Lag features [1,2,3,6] + mes (1-12) |
    | LSTM | Ventana de 2 meses + scaler |
- **Arquitectura del modelo con capas, parámetros y justificación de cada elección**
    1. **Extracción de Contratos — Qwen2.5-VL-3B**
    El modelo Qwen2.5-VL-3B es un Vision-Language Model (VLM) de 3.8 billones de parámetros diseñado para entender simultáneamente imágenes y texto. Su arquitectura combina un Vision Transformer (ViT) como encoder visual con un decoder de lenguaje basado en la familia Qwen2.5. El modelo fue cuantizado a Q4_K_M usando el formato GGUF, lo que reduce su tamaño de ~7GB a ~3.2GB, permitiendo su ejecución en CPU sin necesidad de GPU dedicada. El contexto máximo es de 128,000 tokens, suficiente para imágenes de alta resolución combinadas con prompts extensos.
        
        !image.png
        
        **Capas principales:**
        
        El encoder visual (ViT) procesa la imagen dividiéndola en parches de 14x14 píxeles, proyectándolos a embeddings de dimensión 2048, y pasándolos por 24 capas de transformer con attention heads de 16. El output es una representación visual de la imagen en formato secuencial. El decoder de lenguaje recibe los embeddings visuales concatenados con el embedding del prompt textual, y genera token por token la respuesta JSON. Utiliza attention de 32 cabezas y 28 capas transformer con dimensión oculta de 2048.
        
        **Parámetros de inferencia y justificación:**
        
        El parámetro temperature=0.0 se establece para obtener respuestas completamente deterministas, ya que la tarea requiere extracción precisa de datos sin creatividad ni variabilidad. El timeout de 900 segundos (15 minutos) es necesario porque Ollama ejecuta el modelo en CPU, donde la inferencia de un VLM de 3.8B con imágenes de 1000px puede tardar significativamente. El parámetro stream=false se usa porque se necesita la respuesta completa para parsear el JSON, no parciales. La imagen se reduce a un máximo de 1000px para minimizar la cantidad de tokens visuales que el decoder debe procesar, reduciendo el tiempo de inferencia sin perder la información relevante del contrato.
        
        **Pipeline de preprocesamiento de imagen:**
        
        La imagen pasa por seis transformaciones secuenciales. Primero se convierte a escala de grises y luego a RGB para normalizar los canales de color. Luego se recorta automáticamente usando el bounding box de la imagen, eliminando bordes vacíos. Se redimensiona a un máximo de 1000 píxeles para reducir la carga computacional. Se aplica auto-contraste con corte del 1% para mejorar la legibilidad del texto. Finalmente se aplica un filtro de sharpening para realzar los bordes del texto manuscrito. La imagen resultante se codifica en JPEG con calidad 85 y se convierte a base64 para envío.
        
        **Justificación de elección del modelo:**
        
        Se eligió Qwen2.5-VL sobre alternativas como TrOCR o Gemini por tres razones principales. Primero, es un VLM completo que entiende la relación entre la imagen y la estructura del documento, mientras que TrOCR solo extrae caracteres sin contexto semántico. Segundo, funciona completamente offline sin depender de APIs externas como Gemini. Tercero, el modelo de 3B parámetros es suficiente para la tarea de leer campos específicos de un contrato funerario y corre en hardware convencional sin GPU.
        Se eligió la API nativa de Ollama (/api/chat) en vez de la compatible con OpenAI (/v1/chat/completions) porque la nativa maneja mejor el campo images[] con base64 directo. La compatible con OpenAI a veces presenta problemas con modelos de visión en versiones recientes de Ollama.
        
    2. **Predicción Temporal — 6 Modelos × 2 Targets**
    El sistema de predicción utiliza seis algoritmos diferentes para pronosticar dos variables objetivo: la cantidad mensual de servicios funerarios (servicios_totales) y el ingreso mensual total en soles (monto_total). Cada algoritmo tiene fortalezas y debilidades diferentes, y el sistema carga los 12 modelos resultantes (6 algoritmos × 2 targets) para ofrecer comparación y selección al usuario.
        
        !image.png
        
        **Dataset de entrenamiento:**
        
        El dataset original contiene 340 registros de servicios funerarios del periodo mayo 2022 a febrero 2026. Tras la limpieza y agregación mensual se obtienen 46 puntos de datos. Se aplica data augmentation mediante bootstrap resampling (340→2040 registros) y SMOTE (→836 registros) para compensar el tamaño reducido del dataset. Los datos se dividen en entrenamiento (mayo 2022–febrero 2025, 34 meses) y test (marzo 2025–febrero 2026, 12 meses).
        
        - **Modelo 1: SARIMA (Seasonal AutoRegressive Integrated Moving Average)**
        SARIMA es un modelo estadístico que combina componentes autorregresivos (AR), de diferenciación (I) y de media móvil (MA) con una componente estacional. La configuración utilizada es order=(1,1,1) y seasonal_order=(1,1,0,12). El orden (1,1,1) indica un componente AR de primer orden, una diferenciación para hacer la serie estacionaria, y un componente MA de primer orden. El orden estacional (1,1,0,12) indica un componente AR estacional de primer orden, una diferenciación estacional, y periodicidad de 12 meses (ciclo anual). Los parámetros enforce_stationarity e enforce_invertibility se establecen en False para dar flexibilidad al algoritmo de estimación.
        - **Modelo 2: ETS (Exponential Smoothing State Space)**
        ETS modela la serie temporal usando suavizado exponencial con tendencia y estacionalidad aditivas. La configuración seleccionada es HW aditivo con tendencia='add', seasonal='add', seasonal_periods=12, y damped_trend=True para servicios_totales y False para monto_total. El damped trend previene proyecciones lineales infinitas en horizontes de predicción largos. El método de inicialización es 'estimated', permitiendo que los parámetros iniciales se optimicen por máxima verosimilitud. Los candidatos evaluados fueron SES, Holt damped, HW aditivo s=12 y HW multiplicativo s=12, seleccionándose el de menor AIC.
        - **Modelo 3: Prophet (Meta/Facebook)**
        Prophet es un modelo de descomposición aditiva diseñado para series temporales de negocio con patrones estacionales fuertes. Los parámetros utilizados son yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False, changepoint_prior_scale=0.05, seasonality_prior_scale=10.0, y seasonality_mode='additive'. El changepoint_prior_scale de 0.05 aplica regularización moderada para evitar overfitting a cambios repentinos en la serie. El seasonality_prior_scale de 10.0 permite flexibilidad alta para capturar la estacionalidad anual. No se usan componentes semanales ni diarios porque los datos son mensuales.
        - **Modelo 4: XGBoost (Extreme Gradient Boosting)**
        XGBoost es un algoritmo de ensemble basado en árboles de decisión que captura relaciones no lineales entre features. La configuración es n_estimators=200, max_depth=3, learning_rate=0.05, y random_state=42. El max_depth de 3 limita la profundidad de los árboles para prevenir overfitting en un dataset pequeño (34 puntos de entrenamiento). El learning_rate bajo de 0.05 asegura un aprendizaje gradual y más robusto. Las features utilizadas son lag1, lag2, lag3 y lag6 (valores de la serie en los meses anteriores) más el número de mes (1-12) para capturar estacionalidad.
        - **Modelo 5: LightGBM (Light Gradient Boosting Machine)**
        LightGBM es una variante de gradient boosting optimizada para velocidad y eficiencia de memoria. Los parámetros son n_estimators=200, num_leaves=7, learning_rate=0.03, min_child_samples=1, y min_data_in_leaf=1. El num_leaves de 7 es equivalente a un max_depth aproximado de 3, manteniendo control de complejidad. El learning_rate de 0.03 es más conservador que XGBoost. Las features incluyen los mismos lags que XGBoost más rolling_mean(3) y rolling_std(3) que capturan la tendencia local y la volatilidad de la serie.
        - **Modelo 6: LSTM (Long Short-Term Memory)**
        LSTM es una red neuronal recurrente que captura dependencias temporales de largo plazo. La arquitectura consta de cuatro capas: LSTM con 64 unidades y return_sequences=True (output de forma (window_size, 64)), LSTM con 32 unidades (output de forma (32,)), Dense con 16 neuronas y activación ReLU, y Dense de salida con 1 neurona. El optimizer es Adam con loss MSE. Se entrenan 300 épocas con EarlyStopping con patience de 20 épocas para prevenir overfitting. El window_size es 2 (usando los 2 meses anteriores como input). Los datos se escalan con MinMaxScaler para estabilizar el entrenamiento.
            
            !image.png
            
        
        **Comparación de rendimiento:**
        Para servicios_totales, ETS obtuvo el mejor MAE (3.34) y MAPE (34.57%), seguido por LightGBM (MAE=4.06, R²=0.25). Para monto_total, XGBoost fue el mejor con MAE=50,956 y MAPE=77.55%. Los R² negativos en la mayoría de modelos para monto_total indican que la alta variabilidad del dataset dificulta las predicciones, siendo común en series temporales con pocos puntos de datos.
        
    3. **Extracción de Texto Manuscrito — TrOCR Fine-tuned (Multicentury-HTR)**
    El modelo Multicentury-HTR es un modelo de reconocimiento de texto manuscrito (HTR) basado en la arquitectura VisionEncoderDecoderModel de Hugging Face. Combina un encoder ViT (Vision Transformer) que procesa la imagen del texto con un decoder RoBERTa que genera la secuencia de caracteres. El modelo fue pre-entrenado por Kansallisarkisto en documentos históricos europeos y se fine-tune con 432 muestras etiquetadas de contratos funerarios peruanos.
        
        !image.png
        
        - **Capas principales:**
            
            El encoder ViT procesa la imagen del texto (normalizada a 64px de alto) dividiéndola en parches, proyectándolos a embeddings, y procesándolos con capas de transformer. En el fine-tuning, el encoder se congela (requires_grad=False) para preservar las representaciones visuales pre-entrenadas. El decoder RoBERTa recibe los embeddings visuales y genera secuencialmente los caracteres de la palabra, con un máximo de 128 tokens de salida.
            
        - **Parámetros de fine-tuning y justificación:**
            
            El batch_size efectivo es 8 (per_device=1 con gradient_accumulation_steps=8), necesario porque el modelo es grande y la GPU tiene memoria limitada. El optimizer adamw_torch_fused se selecciona por ser más rápido que el AdamW estándar. El fp16 (mixed precision) reduce el uso de memoria a la mitad y acelera el entrenamiento. El encoder se congela porque ya tiene representaciones visuales robustas del pre-entrenamiento; solo el decoder necesita adaptarse al vocabulario y estilo de escritura de los contratos peruanos. Se usan 10 épocas con early stopping implícito por selección del mejor modelo según CER.
            
        - **Resultados de fine-tuning:**
        El CER (Character Error Rate) mejoró de 0.627 pre-finetuning a 0.334 post-finetuning en test, una reducción del 47%. El accuracy de caracteres pasó de 8.6% a 66.6%. El mejor epoch fue el 7 con CER=0.249, aunque los epochs posteriores mostraron ligero overfitting. El WER (Word Error Rate) final fue 0.544, indicando que aproximadamente la mitad de las palabras se reconocen correctamente.
        - **Justificación de elección:**
            
            Se evaluaron cuatro modelos pre-entrenamiento: TrOCR-Large-EN (CER=0.688), TrOCR-Base-ES (CER=9.092), Multicentury-HTR (CER=0.627) y PARSeq-Multilingual (CER=2.469). Multicentury-HTR obtuvo el mejor CER y accuracy, y fue el candidato natural para fine-tuning. TrOCR-Base-ES tuvo el peor rendimiento probablemente porque el modelo base español no maneja bien la escritura manuscrita peruana. PARSeq tiene la latencia más baja (467ms) pero su CER es muy alto para uso práctico.
            
        - **Resumen de Justificaciones:**
            
            Se utilizaron VLMs (Qwen2.5-VL) para extracción de contratos porque la tarea requiere entender la relación entre la imagen y la estructura del documento, no solo reconocer caracteres. Se mantuvieron 6 modelos de predicción para ofrecer comparación transparente al usuario y permitir selección según la métrica que priorice cada caso de uso. El fine-tuning de TrOCR se realizó como experimento de investigación en el notebook de extracción, pero el modelo final implementado en producción es Qwen2.5-VL por su capacidad de entender contexto completo del documento.
            
- **Función objetivo / función de pérdida con notación matemática**
    - **1. SARIMA (Seasonal AutoRegressive Integrated Moving Average)**
        
        **Función Objetivo:** Maximizar la Verosimilitud (Maximum Likelihood Estimation)
        
        $$
        \mathcal{L}(\theta) = \prod_{t=1}^{n} f(y_t \mid y_{t-1}, y_{t-2}, \ldots; \theta)
        $$
        
        En la práctica se minimiza el **log-verosimilitud negativa**:
        
        $$
        \ell(\theta) = -\log \mathcal{L}(\theta) = -\sum_{t=1}^{n} \log f(y_t \mid y_{t-1}, \ldots; \theta)
        $$
        
        **Parámetros del modelo SARIMA(p,d,q)(P,D,Q)ₛ:**
        
        $$
        \phi(B)\Phi(B^s)(1-B)^d(1-B^s)^D y_t = \theta(B)\Theta(B^s)\varepsilon_t
        $$
        
        Donde:
        
        - $\phi(B) = 1 - \phi_1 B - \cdots - \phi_p B^p$ (polinomio AR no estacional)
        - $\Phi(B^s) = 1 - \Phi_1 B^s - \cdots - \Phi_P B^{Ps}$ (polinomio AR estacional)
        - $\theta(B) = 1 + \theta_1 B + \cdots + \theta_q B^q$ (polinomio MA no estacional)
        - $\Theta(B^s) = 1 + \Theta_1 B^s + \cdots + \Theta_Q B^{Qs}$ (polinomio MA estacional)
        - $\varepsilon_t \sim \mathcal{N}(0, \sigma^2)$ (ruido blanco)
        
        **Métricas de evaluación:**
        
        $$
        \text{MAE} = \frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|
        $$
        
        $$
        \text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}
        $$
        
        $$
        \text{MAPE} = \frac{100\%}{n}\sum_{i=1}^{n}\left|\frac{y_i - \hat{y}_i}{y_i}\right|
        $$
        
    - **2. ETS (Error, Trend, Seasonality - Exponential Smoothing)**
        
        **Función Objetivo:** Minimizar la Suma de Errores Cuadráticos (SSE)
        
        $$
        \text{SSE} = \sum_{t=1}^{n}(y_t - \hat{y}_t)^2
        $$
        
        **Modelo ETS(A,A,A) con error aditivo, tendencia aditiva y estacionalidad aditiva:**
        
        $$
        \hat{y}_{t+h|t} = \ell_t + h \cdot b_t + s_{t+h-m(k+1)}
        $$
        
        Donde las ecuaciones de actualización son:
        
        $$
        \ell_t = \alpha(y_t - s_{t-m}) + (1-\alpha)(\ell_{t-1} + b_{t-1})
        $$
        
        $$
        b_t = \beta^*(\ell_t - \ell_{t-1}) + (1-\beta^*)b_{t-1}
        $$
        
        $$
        s_t = \gamma^*(y_t - \ell_{t-1} - b_{t-1}) + (1-\gamma^*)s_{t-m}
        $$
        
        Donde:
        
        - $\ell_t$ = nivel en el tiempo $t$
        - $b_t$ = tendencia en el tiempo $t$
        - $s_t$ = componente estacional en el tiempo $t$
        - $\alpha, \beta^*, \gamma^*$ = parámetros de suavizamiento $\in [0,1]$
        - $m$ = periodicidad estacional (12 para datos mensuales)
        
        **Parámetros estimados por mínimos cuadrados no lineales:**
        
        $$
        \hat{\theta} = \arg\min_{\theta} \sum_{t=1}^{n}(y_t - \hat{y}_t(\theta))^2
        $$
        
    - **3. Prophet (Facebook Prophet)**
        
        **Función Objetivo:** Mínimos Cuadrados Penalizados
        
        $$
        \mathcal{L} = \sum_{t=1}^{n}(y_t - g(t) - s(t) - h(t))^2 + \sum_{j=1}^{J}\lambda_j \delta_j^2 + \sum_{k=1}^{K}\tau_k \gamma_k^2 + \sum_{l=1}^{L}\rho_l \omega_l^2
        $$
        
        **Componentes del modelo:**
        
        **Tendencia $g(t)$ — con changepoints:**
        
        $$
        g(t) = (k + \mathbf{a}(t)^T \boldsymbol{\delta})\, t + (m + \mathbf{a}(t)^T \boldsymbol{\gamma})
        $$
        
        $$
        \mathbf{a}(t)_j = \begin{cases} 1 & \text{si } t \geq s_j \\ 0 & \text{en otro caso} \end{cases}
        $$
        
        Donde:
        
        - $k$ = tasa de crecimiento inicial
        - $s_j$ = puntos de cambio (changepoints)
        - $\delta_j$ = cambio en la tasa de crecimiento en $s_j$
        - $\gamma_j = -s_j \delta_j$ (para continuidad)
        
        **Estacionalidad $s(t)$ — con Serie de Fourier:**
        
        $$
        s(t) = \sum_{n=1}^{N}\left(a_n \cos\left(\frac{2\pi n t}{P}\right) + b_n \sin\left(\frac{2\pi n t}{P}\right)\right)
        $$
        
        Donde:
        
        - $N$ = orden de Fourier (por defecto $N=10$ para datos anuales)
        - $P$ = período de la estacionalidad ($P=365.25$ para anual, $P=30.5$ para mensual)
        - $a_n, b_n$ = coeficientes estimados
        
        **Regularización:**
        
        $$
        \lambda_j = \frac{\alpha}{(2N)\left(1 - \frac{1}{2N}\right)} \cdot \frac{1}{s_j - s_{j-1}}
        $$
        
        $$
        \tau_k = \frac{1}{\text{mediana}(\delta)} \cdot \frac{1}{K}
        $$
        
    - **4. XGBoost (eXtreme Gradient Boosting)**
        
        **Función Objetivo:** Función de pérdida regularizada
        
        $$
        \mathcal{L}(\phi) = \sum_{i=1}^{n} l(y_i, \hat{y}_i) + \sum_{k=1}^{K} \Omega(f_k)
        $$
        
        **Función de pérdida para regresión (RMSE):**
        
        $$
        l(y_i, \hat{y}_i) = (y_i - \hat{y}_i)^2
        $$
        
        **Término de regularización:**
        
        $$
        \Omega(f_k) = \gamma T + \frac{1}{2}\lambda \sum_{j=1}^{T} w_j^2
        $$
        
        Donde:
        
        - $T$ = número de hojas en el árbol $f_k$
        - $w_j$ = peso (predicción) en la hoja $j$
        - $\gamma$ = parámetro de complejidad (Controla la poda)
        - $\lambda$ = término de regularización L2 (Ridge)
        
        **Construcción del árbol por gradient boosting:**
        
        $$
        \hat{y}_i^{(t)} = \hat{y}_i^{(t-1)} + \eta \cdot f_t(x_i)
        $$
        
        Donde $\eta$ es la tasa de aprendizaje (learning rate).
        
        **Expansión de Taylor de segundo orden:**
        
        $$
        \mathcal{L}^{(t)} \approx \sum_{i=1}^{n} \left[ g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i) \right] + \Omega(f_t)
        $$
        
        Donde:
        
        - $g_i = \frac{\partial l(y_i, \hat{y}_i^{(t-1)})}{\partial \hat{y}_i^{(t-1)}}$ (gradiente)
        - $h_i = \frac{\partial^2 l(y_i, \hat{y}_i^{(t-1)})}{\partial (\hat{y}_i^{(t-1)})^2}$ (hessiano)
        
        **Peso óptimo por hoja:**
        
        $$
        w_j^* = -\frac{\sum_{i \in I_j} g_i}{\sum_{i \in I_j} h_i + \lambda}
        $$
        
        **Ganancia de división:**
        
        $$
        \text{Gain} = \frac{1}{2}\left[\frac{(\sum_{i \in I_L} g_i)^2}{\sum_{i \in I_L} h_i + \lambda} + \frac{(\sum_{i \in I_R} g_i)^2}{\sum_{i \in I_R} h_i + \lambda} - \frac{(\sum_{i \in I} g_i)^2}{\sum_{i \in I} h_i + \lambda}\right] - \gamma
        $$
        
        **Hiperparámetros utilizados:**
        
        - `n_estimators`: número de árboles
        - `max_depth`: profundidad máxima
        - `learning_rate`: tasa de aprendizaje $\eta$
        - `substep`: muestreo de filas
        - `colsample_bytree`: muestreo de columnas
    - **5. LightGBM (Light Gradient Boosting Machine)**
        
        **Función Objetivo:** Misma que XGBoost, pero con crecimiento de hojas por best-first
        
        $$
        \mathcal{L}(\phi) = \sum_{i=1}^{n} l(y_i, \hat{y}_i) + \sum_{k=1}^{K} \Omega(f_k)
        $$
        
        **Diferencia clave con XGBoost — Crecimiento de hojas (Leaf-wise):**
        
        XGBoost crece árboles por niveles (level-wise):
        
        ```
            O          ← Nivel 0
           / \
          O   O       ← Nivel 1
         / \ / \
        O  O O  O     ← Nivel 2
        ```
        
        LightGBM crece por hojas con mayor ganancia (leaf-wise):
        
        ```
            O
           / \
          O   O       ← Mejor hoja según ganancia
             / \
            O   O     ← Siguiente mejor hoja
        ```
        
        **Ganancia de división simplificada:**
        
        $$
        \text{Gain} = \frac{1}{2}\left[\frac{G_L^2}{H_L + \lambda} + \frac{G_R^2}{H_R + \lambda} - \frac{(G_L + G_R)^2}{H_L + H_R + \lambda}\right] - \gamma
        $$
        
        Donde $G = \sum g_i$ y $H = \sum h_i$ en cada conjunto de hojas.
        
        **Muestreo Gradient-Based One-Side Sampling (GOSS):**
        
        Mantiene todas las instancias con gradiente alto y muestrea aleatoriamente las de gradiente bajo:
        
        $$
        \text{Instancias retenidas} = a\% \text{ con } |g_i| \geq \text{umbral} + b\% \text{ de las restantes}
        $$
        
        **Exclusive Feature Bundling (EFB):**
        
        Reduce el número de features mutuamente excluyentes combinándolas en una sola columna.
        
        **Hiperparámetros utilizados:**
        
        - `n_estimators`: número de iteraciones
        - `num_leaves`: número máximo de hojas ($2^{d}$ recomendado)
        - `learning_rate`: tasa de aprendizaje
        - `feature_fraction`: muestreo de features
        - `bagging_fraction`: muestreo de datos
    - **6. LSTM (Long Short-Term Memory)**
        
        **Función Objetivo:** Minimizar la Cross-Entropy en secuencias
        
        $$
        \mathcal{L} = -\sum_{t=1}^{T} y_t \log(\hat{y}_t)
        $$
        
        **Arquitectura de la celda LSTM:**
        
        Las compuertas controlan el flujo de información:
        
        **Compuerta de olvido $f_t$:**
        
        $$
        f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)
        $$
        
        **Compuerta de entrada $i_t$:**
        
        $$
        i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)
        $$
        
        **Candidato de memoria $\tilde{C}_t$:**
        
        $$
        \tilde{C}_t = \tanh(W_C \cdot [h_{t-1}, x_t] + b_C)
        $$
        
        **Actualización de memoria $C_t$:**
        
        $$
        C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t
        $$
        
        **Compuerta de salida $o_t$:**
        
        $$
        o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o)
        $$
        
        **Estado oculto $h_t$:**
        
        $$
        h_t = o_t \odot \tanh(C_t)
        $$
        
        Donde:
        
        - $\sigma$ = función sigmoid $\sigma(x) = \frac{1}{1+e^{-x}}$
        - $\odot$ = producto elemento a elemento (Hadamard)
        - $W_f, W_i, W_C, W_o$ = matrices de pesos
        - $b_f, b_i, b_C, b_o$ = vectores de bias
        - $C_t$ = estado de memoria de largo plazo
        - $h_t$ = estado oculto (salida de corto plazo)
        
        **Función de pérdida para regresión (si aplica):**
        
        $$
        \mathcal{L}_{\text{reg}} = \frac{1}{T}\sum_{t=1}^{T}(y_t - \hat{y}_t)^2
        $$
        
        **Backpropagation Through Time (BPTT):**
        
        $$
        \frac{\partial \mathcal{L}}{\partial W} = \sum_{t=1}^{T} \frac{\partial \mathcal{L}_t}{\partial W}
        $$
        
        **Hiperparámetros utilizados:**
        
        - `window_size = 2` (ventana de entrada)
        - `hidden_units = 64` (neuronas en la capa LSTM)
        - `epochs = 100`
        - `batch_size = 16`
        - `optimizer = Adam` ($\alpha = 0.001$)
        - `loss = MSE` (para regresión temporal)
    - **7. TrOCR (Transformer OCR) — Fine-tuning**
        
        **Función Objetivo:** Teacher Forcing con Cross-Entropy
        
        $$
        \mathcal{L} = -\sum_{t=1}^{T} \log P(y_t \mid y_{<t}, X)
        $$
        
        Donde:
        
        - $X$ = imagen de entrada (codificada por el encoder ViT)
        - $y_t$ = token objetivo en la posición $t$
        - $y_{<t}$ = tokens previos (decoded autoregressively)
        
        **Encoder (Vision Transformer - ViT):**
        
        $$
        \text{patches} = \text{Conv2D}(X) \in \mathbb{R}^{N \times D}
        $$
        
        $$
        Z_0 = [\text{cls\_token}; \text{patches}] + \text{pos\_embedding}
        $$
        
        $$
        Z_l = \text{MSA}(\text{LN}(Z_{l-1})) + Z_{l-1}
        $$
        
        $$
        Z_l = \text{FFN}(\text{LN}(Z_l)) + Z_l
        $$
        
        **Decoder (Transformer con causal masking):**
        
        $$
        \text{SA}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
        $$
        
        $$
        \text{Cross-Attention}(Q,K_{enc},V_{enc}) = \text{softmax}\left(\frac{QK_{enc}^T}{\sqrt{d_k}}\right)V_{enc}
        $$
        
        **Loss detallada:**
        
        $$
        \mathcal{L} = -\frac{1}{T}\sum_{t=1}^{T}\sum_{v=1}^{V} y_{t,v} \log(\hat{y}_{t,v})
        $$
        
        Donde:
        
        - $V$ = tamaño del vocabulario del tokenizer
        - $y_{t,v}$ = 1 si el token real es $v$, 0 en otro caso (one-hot)
        - $\hat{y}_{t,v}$ = probabilidad predicha para el token $v$ en posición $t$
        
        **Métricas de evaluación (HTR):**
        
        $$
        \text{CER} = \frac{\text{Edición Levenshtein}(\hat{y}, y)}{|\hat{y}|}
        $$
        
        $$
        \text{WER} = \frac{\text{Palabras erróneas}}{\text{Total de palabras}}
        $$
        
        $$
        \text{Char Accuracy} = 1 - \text{CER}
        $$
        
    
    ## Resumen Comparativo
    
    | Modelo | Función Objetivo | Función de Pérdida | Optimización |
    | --- | --- | --- | --- |
    | SARIMA | Máxima Verosimilitud | $-\log L(\theta)$ | MLE (BFGS) |
    | ETS | Mínimos Cuadrados | SSE = $\sum(y_t - \hat{y}_t)^2$ | NLS (Levenberg-Marquardt) |
    | Prophet | Mín. Cuadrados Penalizados | SSE + regularización | L-BFGS |
    | XGBoost | Gradient Boosting Regularizado | $\sum l(y_i,\hat{y}_i) + \Omega$ | Gradiente descendente |
    | LightGBM | Gradient Boosting Optimizado | $\sum l(y_i,\hat{y}_i) + \Omega$ | GOSS + EFB |
    | LSTM | BPTT | $-\sum y_t \log(\hat{y}_t)$ | Adam ($\alpha=0.001$) |
    | TrOCR | Teacher Forcing | $-\sum \log P(y_t \mid y_{<t}, X)$ | AdamW (lr=5e-5) |
- **Pseudocódigo del algoritmo principal**
    - **Extracción de Contratos (Qwen2.5-VL-3B)**
        
        ```jsx
        ALGORITMO: ExtraerContrato(imagen_bytes)    
                 
            ENTRADA: imagen_bytes (foto del contrato escaneado)    
            SALIDA: JSON con datos del contrato    
                 
            1. PREPROCESAR IMAGEN    
               imagen ← Abrir(imagen_bytes)    
               imagen ← ConvertirAGrayscale(imagen)    
               imagen ← ConvertirARGB(imagen)    
               imagen ← AutoCrop(imagen)           // Recortar bordes vacíos    
               imagen ← Redimensionar(imagen, max_dim=1000)    
               imagen ← AutoContrast(imagen, cutoff=1%)    
               imagen ← Sharpen(imagen)    
               imagen ← GuardarJPEG(imagen, quality=85)    
                 
            2. CODIFICAR    
               imagen_b64 ← Base64Encode(imagen)    
                 
            3. CONSTRUIR PAYLOAD    
               payload ← {    
                   model: "qwen2.5vl:3b",    
                   messages: [{    
                       role: "user",    
                       content: PROMPT_CONTRATO,    
                       images: [imagen_b64]    
                   }],    
                   stream: false    
               }    
                 
            4. ENVIAR A OLLOMA    
               REINTENTAR (máximo 1 vez):    
                   respuesta ← POST("http://localhost:11434/api/chat", payload)    
                   SI respuesta.status ≠ 200:    
                       ESPERAR(5 segundos)    
                       CONTINUAR    
                 
                   contenido ← respuesta.message.content    
                 
            5. PARSEAR RESPUESTA    
               contenido ← LimpiarMarkdown(contenido)   // Eliminar ```    
               contenido ← ExtraerJSON(contenido)       // Buscar { ... }    
               datos ← ParsearJSON(contenido)    
                 
            6. NORMALIZAR CAMPOS    
               datos.fecha ← NormalizarFecha(datos.fecha)    
               datos.contratante_dni ← ValidarDNI(datos.contratante_dni)  // 8 dígitos    
               datos.contratante_telefono ← LimpiarTelefono(datos.contratante_telefono)    
               datos.tipo_pago ← NormalizarTipoPago(datos.tipo_pago)      // directo/seguro/mixto    
               datos.ids_vehiculos_detectados ← FiltrarVehículos(datos.ids_vehiculos_detectados)    
               datos.cantidad_cargadores ← ValidarCargadores(datos.cantidad_cargadores)  // 4, 6 o null    
                 
            7. DEVOLVER datos
        ```
        
    - **Pipeline de Predicción Temporal**
        
        ```jsx
        ALGORITMO: Predecir(modelo, target, pasos)    
                 
            ENTRADA: nombre del modelo, target (servicios_totales | monto_total), pasos a predecir    
            SALIDA: lista de predicciones mensuales    
                 
            1. CARGAR MODELO    
               SI modelo = "SARIMA":    
                   modelo ← CargarPickle("sarima_" + target + ".pkl")    
               SI modelo = "ETS":    
                   modelo ← CargarPickle("ets_" + target + ".pkl")    
               SI modelo = "Prophet":    
                   modelo ← CargarPickle("prophet_" + target + ".pkl")    
               SI modelo = "XGBoost":    
                   modelo ← CargarPickle("xgboost_" + target + ".pkl")    
                   scaler ← CargarPickle("scaler_" + target + ".pkl")    
               SI modelo = "LightGBM":    
                   modelo ← CargarPickle("lgbm_" + target + ".pkl")    
                   scaler ← CargarPickle("scaler_" + target + ".pkl")    
               SI modelo = "LSTM":    
                   modelo ← CargarKeras("lstm_" + target + ".keras")    
                   scaler ← CargarPickle("scaler_" + target + ".pkl")    
                 
            2. PREDECIR SEGÚN TIPO DE MODELO    
                 
               SI modelo ES ESTADÍSTICO (SARIMA, ETS, Prophet):    
                   predicciones ← modelo.forecast(steps=pasos)    
                   DEVOLVER predicciones    
                 
               SI modelo ES XGBOOST O LIGHTGBM:    
                   historial ← CargarHistorial(target)    
                   lags_config ← [1, 2, 3, 6]    
                   predicciones ← []    
                 
                   PARA CADA paso EN rango(pasos):    
                       features ← []    
                       PARA CADA lag EN lags_config:    
                           features.append(historial[-lag])    
                       mes_num ← (paso + 1) MOD 12 + 1    
                       features.append(mes_num)    
                 
                       SI modelo = "LightGBM":    
                           rolling_mean ← PromedioMóvil(historial, ventana=3)    
                           rolling_std ← DesviaciónMóvil(historial, ventana=3)    
                           features.append(rolling_mean)    
                           features.append(rolling_std)    
                 
                       prediccion ← modelo.predict([features])[0]    
                       predicciones.append(prediccion)    
                       historial.append(prediccion)    
                 
                   DEVOLVER predicciones    
                 
               SI modelo ES LSTM:    
                   historial ← CargarHistorial(target)    
                   window_size ← 2    
                   predicciones ← []    
                 
                   PARA CADA paso EN rango(pasos):    
                       ventana ← historial[-window_size:]    
                       ventana_escalada ← scaler.transform(ventana.reshape(-1, 1))    
                       entrada ← ventana_escalada.reshape(1, window_size, 1)    
                 
                       prediccion_escalada ← modelo.predict(entrada)    
                       prediccion ← scaler.inverse_transform(prediccion_escalada)[0][0]    
                 
                       predicciones.append(prediccion)    
                       historial.append(prediccion)    
                 
                   DEVOLVER predicciones    
                 
            3. CALCULAR DISTRIBUCIÓN (opcional)    
               distribucion_ataudes ← CargarDistribucion("ataudes")    
               distribucion_capillas ← CargarDistribucion("capillas")    
                 
               PARA CADA predicción EN predicciones:    
                   para_tipo_ataud ← {}    
                   PARA CADA tipo EN distribucion_ataudes:    
                       para_tipo_ataud[tipo] ← predicción × distribucion_ataudes[tipo]    
                 
                   para_tipo_capilla ← {}    
                   PARA CADA tipo EN distribucion_capillas:    
                       para_tipo_capilla[tipo] ← predicción × distribucion_capillas[tipo]
        ```
        
    - **Flujo Completo del Sistema (Frontend → Backend → Ollama)**
        
        ```jsx
        ALGORITMO: ProcesarContratoDesdeFrontend(imagen)    
                 
            ENTRADA: imagen subida por el usuario    
            SALIDA: datos del contrato guardados en base de datos    
                 
            1. FRONTEND: COMPRIMIR IMAGEN    
               archivoComprimido ← ComprimirImagen(imagen, max_dim=2000, quality=85)    
                 
            2. FRONTEND: ENVIAR AL BACKEND    
               formData ← FormData()    
               formData.append("file", archivoComprimido)    
               respuesta ← POST(iaApiUrl + "/ia/process-contract", formData)    
               tarea_id ← respuesta.tarea_id    
                 
            3. FRONTEND: POLLING    
               MIENTRAS true:    
                   ESPERAR(3 segundos)    
                   estado ← GET(iaApiUrl + "/ia/task/" + tarea_id)    
                 
                   SI estado.estado = "listo":    
                       datos ← estado.resultado    
                       SALIR DEL BUCLE    
                 
                   SI estado.estado = "error":    
                       MostrarError(estado.error)    
                       SALIR DEL BUCLE    
                 
            4. FRONTEND: MOSTRAR FORMULARIO EDITABLE    
               MostrarFormulario(datos)  // Usuario puede corregir campos    
                 
            5. FRONTEND: GUARDAR    
               SI usuario confirma:    
                   payload ← MapearAGuardar(datos)    
                   POST(apiUrl + "/services/", payload)    
                   MostrarExito("Servicio guardado")    
        ```
        
    - **Fine-tuning de TrOCR (Experimento)**
        
        ```jsx
        ALGORITMO: FineTuneHTR(dataset, modelo_base)    
                 
            ENTRADA: dataset de 432 imágenes etiquetadas, modelo pre-entrenado    
            SALIDA: modelo fine-tuneado guardado en disco    
                 
            1. CARGAR MODELO    
               modelo ← CargarVisionEncoderDecoder(modelo_base)    
               CongelarEncoder(modelo)  // Solo entrenar decoder    
                 
            2. PREPARAR DATOS    
               Dividir(dataset, train=80%, val=10%, test=10%)    
               tokenizer ← CargarTokenizer(modelo_base)    
                 
            3. ENTRENAR (10 épocas)    
               PARA CADA epoch EN rango(10):    
                   PARA CADA batch EN train_loader:    
                       imágenes ← batch.imágenes    
                       texto_objetivo ← batch.texto    
                 
                       // Tokenizar texto objetivo    
                       labels ← Tokenizar(texto_objetivo, tokenizer)    
                 
                       // Forward pass (teacher forcing)    
                       outputs ← modelo(imágenes, labels=labels)    
                       pérdida ← outputs.loss  // Cross-Entropy    
                 
                       // Backward pass    
                       pérdida.backward()    
                       Optimizer.step()    
                       Optimizer.zero_grad()    
                 
                   // Evaluar al final de cada epoch    
                   métricas ← Evaluar(modelo, val_loader)    
                   CER ← métricas.cer    
                   WER ← métricas.wer    
                 
                   SI CER < mejor_CER:    
                       mejor_CER ← CER    
                       GuardarModelo(modelo, "mejor_modelo")    
                 
            4. EVALUAR EN TEST    
               resultados ← Evaluar(mejor_modelo, test_loader)    
               Imprimir("CER:", resultados.cer)    
               Imprimir("WER:", resultados.wer)    
               Imprimir("Char Accuracy:", resultados.accuracy) 
        ```
        
    - **Resumen de Algoritmos**
        
        
        | **Algoritmo** | **Complejidad Temporal** | **Complejidad Espacial** |
        | --- | --- | --- |
        | ExtraerContrato | O(T × V) inference | O(P²) imagen + O(T) tokens |
        | SARIMA | O(n) forecast | O(p + q) parámetros |
        | ETS | O(n × m) | O(m) estado |
        | Prophet | O(n × N) Fourier | O(N × K) changepoints |
        | XGBoost | O(K × T × log n) | O(K × 2^d) hojas |
        | LightGBM | O(K × T × log n) | O(K × L) hojas |
        | LSTM | O(W × n × h²) | O(h²) pesos |
        | Fine-tune HTR | O(E × B × T × d) | O(d²) modelo |
        
        Donde:
        
        - n = tamaño del dataset
        - T = tokens de salida
        - V = tamaño del vocabulario
        - P = píxeles de imagen
        - m = periodicidad estacional
        - K = número de árboles/estimadores
        - d = profundidad máxima
        - L = número de hojas
        - W = window size
        - h = hidden units
        - E = épocas
        - B = batch size
        - N = orden de Fourier

**3.4 Stack tecnológico justificado**

| Capa | Tecnología elegida | Versión | Justificación técnica | Alternativa descartada |
| --- | --- | --- | --- | --- |
| Frontend | Angular | 17+ | Tipado estático con TypeScript, sistema de componentes reactivos con Observables, gestión de formularios complejos para validación de datos extraídos | React 18 — mayor curva de configuración para proyectos con estructura modular estricta |
| Backend | FastAPI | 0.100 | Async nativo, generación automática de Swagger, integración directa con modelos Python de ML sin capas de conversión | Flask — sin soporte async nativo ni documentación automática de endpoints |
| Base de datos | PostgreSQL | 15+ | Soporte robusto para relaciones complejas entre entidades del dominio funerario, compatible con SQLModel ORM y con Digital Ocean y Supabase | MySQL — menor soporte nativo para tipos JSON y menos integración con el ecosistema Python elegido |
| ORM | SQLModel | - | Combina Pydantic y SQLAlchemy en una sola definición de modelos, reduciendo código duplicado entre esquemas de validación y tablas de BD | SQLAlchemy puro — más verboso, requiere definiciones separadas para validación y persistencia |
| Modelo HTR | Multicentury-HTR + fine-tuning | - | Menor CER (0.3340) tras fine-tuning sobre el dominio, única arquitectura capaz de interpretar morfología de letra ligada en español manuscrito | TrOCR-Base-ES — CER de 9.09, latencia de 50,785 ms, inviable para producción |
| Extracción estructurada | Qwen2.5-VL-3B (Ollama / Gemini) | 3B | Extracción de JSON estructurado en una sola inferencia sin pipeline adicional de detección de regiones | SmolVLM-256M — similitud coseno inferior en benchmarks de OCR y DocVQA, tasa de alucinación inaceptable |
| Modelos predictivos | ETS + LightGBM (ensemble disponible) | - | Únicos modelos con R² positivo sobre datos base (0.252 y 0.249), menor MAE para servicios totales, tiempo de entrenamiento inferior a 1 segundo | LSTM — R² negativo en todas las configuraciones, tiempo de entrenamiento superior a 17 segundos, penalizado por escasez de datos |
| Servidor de inferencia | Ollama | 0.24 | Permite correr modelos cuantizados sobre CPU sin GPU dedicada, compatible con Digital Ocean en modo CPU-only | Transformers HF directo — requiere GPU para tiempos aceptables, error 500 por memoria insuficiente en pruebas locales |
| Pasarela de pagos | Stripe | - | SDK oficial para Python y Angular, soporte para pagos directos y mixtos, entorno de pruebas con tarjetas sintéticas disponible sin contrato comercial | PayPal — mayor complejidad de integración para pagos parciales y sin SDK Angular oficial |
| Validación de identidad | DECOLECTA (API similar RENIEC) | - | Única alternativa de acceso público para consulta de DNI en Perú; la API oficial de RENIEC requiere documentación formal como empresa privada | RENIEC directo — acceso restringido, no disponible para entornos académicos sin convenio institucional |
| Despliegue frontend | Vercel | - | Despliegue continuo desde GitHub, CDN global, sin configuración de servidor, plan gratuito suficiente para el alcance del proyecto | Netlify — funcionalidades equivalentes pero menor integración con Angular en la configuración de rutas SPA |
| Despliegue backend | Render | - | Soporte nativo para Python, despliegue continuo desde GitHub, plan gratuito con instancias web activas | Railway — menor estabilidad en instancias gratuitas, suspensión más agresiva por inactividad |
| Infraestructura cloud | Digital Ocean | - | Costo de S/ 84.40 dentro del presupuesto del proyecto, soporte para PostgreSQL administrado y Ollama sobre droplet CPU (200$ de inicio gratuitos) | AWS / GCP — costos significativamente superiores al presupuesto disponible del taller |
| Túnel de red | Cloudflared | - | Expone el servidor local de inferencia GPU hacia la nube sin IP pública ni configuración de firewall | ngrok — límites de ancho de banda en plan gratuito, inestable para transferencia de imágenes de alta resolución |

**3.5 Decisiones de diseño críticas**

- **ADR-01 — Uso de Qwen2.5-VL-3B en lugar de un pipeline HTR clásico**
    - Decisión tomada: emplear un modelo de lenguaje visual (VLM) para extraer todos los campos del contrato en una sola inferencia, retornando un JSON estructurado directamente.
    - Contexto que la motivó: los formularios manuscritos de la funeraria tienen una distribución de campos irregular, con texto ligado, abreviaciones propias del dominio y campos opcionales que varían entre contratos. Un pipeline clásico de detección de regiones seguido de HTR por campo requeriría un modelo de detección entrenado sobre bounding boxes precisos para cada campo, además del modelo de transcripción, duplicando la complejidad de mantenimiento.
    - Alternativas evaluadas: pipeline Multicentury-HTR por región con bounding boxes exportados desde Label Studio; PARSeq-Multilingual sobre crops individuales; BERT-tiny y Flan-T5 para post-procesamiento estructurado.
    - Consecuencias asumidas: el tiempo de inferencia es significativamente mayor (15 segundos con Gemini, hasta 35 segundos con Ollama sobre CPU) comparado con un modelo HTR ligero. Se acepta esta latencia dado que la carga es asíncrona y el usuario puede continuar trabajando mientras el modelo procesa; la reducción de tiempo respecto al proceso manual de digitación sigue siendo sustancial.
- **ADR-02 — Despliegue del modelo de inferencia mediante Ollama sobre CPU con túnel Cloudflared**
    - Decisión tomada: correr el modelo Qwen2.5-VL-3B mediante Ollama en un droplet de Digital Ocean con CPU, expuesto al backend desplegado en Render mediante un túnel Cloudflared.
    - Contexto que la motivó: el modelo requiere GPU para tiempos de inferencia óptimos, pero el presupuesto del proyecto (S/ 84.40) no contempla instancias con GPU en Digital Ocean ni en ningún otro proveedor. Las pruebas con Transformers de Hugging Face directamente sobre GPU local demostraron errores de memoria CUDA (out of memory) con imágenes de resolución estándar. Ollama cuantizado sobre CPU resultó en la única configuración estable dentro del presupuesto disponible.
    - Alternativas evaluadas: Transformers HF con GPU local tuneado a Cloudflared; API de Gemini como servicio externo; Ollama con modelo minicpm-v:8b-2.6-q4_K_M como alternativa más rápida.
    - Consecuencias asumidas: la latencia de inferencia sobre CPU (35 segundos por imagen en producción) es significativamente mayor que sobre GPU. Se integró adicionalmente la API de Gemini como motor alternativo para reducir la latencia a aproximadamente 15 segundos, a costa de depender de un servicio externo con límites de cuota. El modelo minicpm-v fue descartado por menor precisión en la extracción de campos numéricos y DNI.
- **ADR-03 — Roles y permisos dinámicos en base de datos en lugar de enums hardcodeados**
    - Decisión tomada: implementar el sistema de autorización con roles y permisos almacenados como registros en PostgreSQL, consultados en tiempo de ejecución por cada endpoint protegido.
    - Contexto que la motivó: una implementación inicial con enums hardcodeados en el código generó conflictos al agregar nuevas funcionalidades (gestión de vehículos, capillas, pagos) ya que cada nuevo módulo requería modificar el código fuente del sistema de autenticación y redesplegar el backend. El cliente final (secretaria y administrador de la funeraria) necesita la capacidad de crear roles intermedios sin intervención del equipo de desarrollo.
    - Alternativas evaluadas: enums de roles fijos en Python con decoradores de FastAPI; sistema RBAC con librería fastapi-permissions; roles codificados directamente en el token JWT.
    - Consecuencias asumidas: cada solicitud a un endpoint protegido genera una consulta adicional a la base de datos para verificar el permiso específico del usuario. Este overhead se acepta dado el volumen de usuarios concurrentes esperado (máximo 2-3 usuarios simultáneos en el contexto de la funeraria) y la ganancia en flexibilidad operativa. Un cambio de permisos en la BD tiene efecto inmediato sin necesidad de redespliegue.
- **ADR-04 — Prophet como modelo de predicción principal para servicios totales**
    - Decisión tomada: seleccionar Prophet como modelo principal para la variable servicios totales sobre el dataset base, y ETS como modelo principal para escenarios con data augmentation.
    - Contexto que la motivó: la comparativa de seis modelos sobre el dataset mensual de 46 meses evidenció que ningún modelo alcanzó el umbral de MAPE inferior al 20% establecido en los objetivos, atribuible al volumen reducido del historial y a la alta variabilidad de la demanda en el sector funerario. Dentro de este contexto, Prophet obtuvo el único R² positivo sobre datos base para servicios totales (0.0064) con un MAE de 4.31, siendo el único modelo que explicó marginalmente la varianza de la serie sin data augmentation.
    - Alternativas evaluadas: SARIMA (R² = -1.195), XGBoost (R² = -0.868), LightGBM (R² = -0.633), LSTM (R² = -0.361), ETS (R² = -0.356) sobre datos base.
    - Consecuencias asumidas: los valores de MAPE obtenidos (94% para Prophet sobre datos base) superan el umbral objetivo del proyecto. Esta limitación se documenta explícitamente como restricción del modelo derivada del volumen de datos históricos disponibles, y no como fallo de implementación. La plataforma expone todos los modelos entrenados para que el usuario pueda comparar resultados y seleccionar el más apropiado según el horizonte de predicción consultado.

**3.6 Modelo de seguridad y privacidad**

- **Autenticación y autorización**
    
    El sistema implementa autenticación basada en tokens JWT firmados con el algoritmo HS256, generados al momento del login y con un tiempo de expiración de 60 minutos de inactividad y un máximo de 8 horas de sesión continua. Cada token codifica el identificador del usuario, que el backend utiliza para consultar dinámicamente sus permisos en la base de datos antes de autorizar el acceso a cualquier endpoint protegido. La expiración de sesión redirige automáticamente al usuario al formulario de login con un mensaje informativo. El sistema impide la eliminación del último usuario administrador activo para garantizar la continuidad del acceso administrativo a la plataforma.
    
- **Cifrado y transporte**
    
    Todas las comunicaciones entre el frontend desplegado en Vercel y el backend en Render se realizan sobre HTTPS, garantizando el cifrado en tránsito de credenciales, tokens y datos de servicios funerarios. Las contraseñas de usuarios se almacenan con hash mediante Bcrypt antes de su persistencia en la base de datos, de modo que ningún registro contiene contraseñas en texto plano. La comunicación entre el backend y el servidor de inferencia de Ollama se realiza a través del túnel Cloudflared sobre TLS.
    
- **Privacidad de datos personales**
    
    El sistema procesa y almacena datos personales sensibles de personas naturales, incluyendo nombres completos, números de DNI, direcciones, números de teléfono y datos de fallecidos. Estos datos corresponden a los registros de contratantes, fallecidos y pasajeros asociados a los servicios funerarios. El acceso a esta información está restringido por el sistema de roles: los usuarios con rol Trabajador tienen acceso de lectura y registro, mientras que las operaciones de eliminación y gestión de usuarios están reservadas al rol Administrador. 
    
    Se implementó borrado lógico mediante campo activo/inactivo en lugar de eliminaciones físicas, preservando la integridad del historial de servicios y evitando la pérdida irreversible de registros con implicaciones legales. La validación de DNI mediante la API DECOLECTA se realiza en tiempo real sin almacenar los datos de la consulta en servidores intermedios, ya que la respuesta se procesa directamente en el backend y se persiste únicamente lo que el usuario confirma.
    
- **Gestión de pagos**
    
    El procesamiento de pagos se delega completamente a Stripe, que opera bajo certificación PCI DSS. El sistema nunca almacena ni transmite datos de tarjetas de crédito en sus propios servidores; la interfaz de pago se renderiza mediante el SDK oficial de Stripe, que gestiona el formulario y la tokenización de forma aislada. El backend únicamente recibe y almacena el identificador de intención de pago (payment intent ID) generado por Stripe, junto con el monto, la moneda, el estado del pago y la descripción del servicio asociado.
    

### **SECCIÓN 4 — DESARROLLO E IMPLEMENTACIÓN**

*(Equivale a Implementation)*

**4.1 Metodología de desarrollo aplicada**

- **Justificación de la metodología**
    
    El proyecto adoptó una metodología dual que combina Scrum para el desarrollo de la plataforma web y CRISP-DM para los componentes de inteligencia artificial y minería de datos.
    
    La elección de Scrum para el desarrollo de software responde a la naturaleza iterativa e incremental del sistema: al tratarse de un proyecto con dos componentes de inteligencia artificial cuyos resultados no son predecibles con certeza antes de la experimentación, una metodología ágil permitió ajustar el alcance y las decisiones técnicas sprint a sprint en función de los resultados obtenidos. Los roles Scrum fueron asignados explícitamente: Prieto Meléndez Alexander Antonio como Project Manager, Vidal Rodríguez Fabrizio como Scrum Master, y Zayda Atoche Urbina como Product Owner en representación del negocio. El backlog se organizó en historias de usuario, tareas técnicas, spikes de investigación, requerimientos no funcionales y documentación, gestionados en un tablero Kanban con estados Closed, Open e Issue.
    
    CRISP-DM se aplicó de forma paralela como marco metodológico para los dos pipelines de machine learning del proyecto: el módulo de reconocimiento de escritura manuscrita y el módulo de predicción de series temporales. Este estándar estructura el trabajo de ciencia de datos en seis fases cíclicas que se ejecutaron explícitamente durante el desarrollo.
    
    La fase de comprensión del negocio consistió en identificar que la dependencia de registros físicos manuscritos generaba dos problemas cuantificables: pérdidas estimadas de S/ 800 mensuales por quiebres de stock y 40 horas mensuales de trabajo manual de digitalización, estableciendo los criterios de éxito de los modelos (Accuracy > 90%, CER < 15% para HTR; MAPE < 20% para series temporales).
    
    La fase de comprensión de los datos implicó la fotografía y digitalización de los registros físicos de la funeraria, obteniendo 340 registros históricos de servicios que cubren 46 meses entre mayo de 2022 y febrero de 2026, con 18 columnas de variables operativas del negocio. El análisis exploratorio identificó 19 outliers en montos (5.59%), 6 lagunas temporales en el historial, y 86 categorías de modelos de ataúd de las cuales 75 tenían menos de 5 registros.
    
    La fase de preparación de los datos incluyó para el módulo HTR el etiquetado de más de 280 imágenes en Label Studio con 24 categorías de campos, y la generación del dataset de entrenamiento con bounding boxes y transcripciones. Para el módulo predictivo incluyó la eliminación de valores nulos, normalización de categorías (338 valores en Ataud_Modelo, 301 en Ataud_Color, 314 en Capilla, 340 en Forma de pago), encoding binario, imputación de fechas, agregación mensual y tres técnicas de data augmentation: Bootstrapping Temporal (340 a 2040 registros), SMOTENC (254 a 836 registros) y Sliding Window (43 ventanas de 3 meses). La integridad final del dataset alcanzó el 97.94%.
    
    La fase de modelado comprendió para HTR la evaluación de cuatro modelos preentrenados (TrOCR-Large-EN, TrOCR-Base-ES, Multicentury-HTR y PARSeq-Multilingual) sobre 221 muestras, seguida del fine-tuning del modelo seleccionado durante 10 épocas. Para series temporales incluyó la evaluación de seis algoritmos (SARIMA, Prophet, XGBoost, LightGBM, LSTM y ETS) bajo tres fuentes de datos distintas, con métricas de MAE, RMSE, R² y MAPE, complementada con análisis de reglas de asociación mediante el algoritmo Apriori sobre los 340 registros de servicios. Adicionalmente se aplicó el Test de Levene para validar la homocedasticidad entre los datos originales y los sintéticos generados por SMOTENC.
    
    La fase de evaluación contrastó los resultados obtenidos contra los criterios de éxito definidos en la fase inicial. El modelo HTR alcanzó un CER de 0.3340 y un Char Acc de 0.6660 tras fine-tuning, sin alcanzar aún el umbral de Accuracy del 90% establecido como objetivo, documentándose como trabajo pendiente. Los modelos de series temporales no alcanzaron el MAPE inferior al 20% sobre ninguna configuración de datos, atribuido al volumen reducido del historial disponible, documentándose esta limitación explícitamente en el reporte final de métricas.
    
    La fase de despliegue consistió en la integración de ambos modelos en la plataforma web mediante endpoints REST en FastAPI, con el modelo HTR servido a través de Ollama en Digital Ocean y la API de Gemini como motor alternativo, y los modelos predictivos expuestos con selección dinámica de algoritmo, variable objetivo y horizonte de predicción desde la interfaz de usuario.
    
- **Sprints realizados con entregables por fase**
    
    **Sprint 1 — Módulo de extracción e infraestructura base (28 abril – 24 mayo 2026)**
    
    | ID | Entregable | Tipo | Estado |
    | --- | --- | --- | --- |
    | TA-001 | Digitalización y fotografía de registros físicos de la funeraria (mín. 280 imágenes aptas, formato .jpg/.png, resolución mín. 300 ppp) | Tarea técnica | Closed |
    | TA-002 | Configuración de Label Studio con 24 categorías de etiquetado para campos del contrato | Tarea técnica | Closed |
    | TA-003 | Dataset de entrenamiento etiquetado con bounding boxes y transcripciones por campo | Tarea técnica | Closed |
    | EN-001 | Preprocesamiento de imágenes (normalización, reducción de ruido, conversión de color) | Tarea técnica | Closed |
    | SP-001 | Investigación y comparativa de 4 modelos HTR preentrenados sobre 221 muestras del dominio (CER, WER, Accuracy, Latencia) | Spike | Closed |
    | EN-002 | Comparativa cuantitativa de modelos HTR con matriz de métricas y selección justificada de Multicentury-HTR | Tarea técnica | Closed |
    | EN-003 | Comparativa de modelos cuantizados para optimización de velocidad de respuesta | Tarea técnica | Closed |
    | TA-004 | Fine-tuning de Multicentury-HTR sobre dataset propio: CER 0.3340, Char Acc 0.6660 tras 10 épocas | Tarea técnica | Closed |
    | EN-004 | Implementación de métrica de similitud coseno entre Qwen2.5-VL-3B y SmolVLM-256M | Tarea técnica | Closed |
    | RN-001 | Validación del umbral de precisión del modelo (Accuracy > 90%, CER < 15%) | Req. no funcional | Issue |
    | TA-005 | Diseño del esquema de base de datos PostgreSQL con diagrama Entidad-Relación | Tarea técnica | Closed |
    | TA-006 | Endpoint de extracción en FastAPI: recibe imagen, retorna JSON estructurado en < 5 seg/página | Tarea técnica | Closed |
    | EN-005 | Configuración de conexión entre API y base de datos PostgreSQL mediante ORM SQLModel | Tarea técnica | Closed |
    | TA-007 | Consumo del endpoint de extracción desde Angular con indicador visual de carga | Tarea técnica | Closed |
    | HU-001 | Inicio de sesión de usuario administrativo con JWT y redirección al dashboard | Historia de usuario | Closed |
    | HU-002 | Visualización del listado de ataúdes con disponibilidad y stock actual | Historia de usuario | Closed |
    | HU-003 | Carga masiva de imágenes de manuscritos con barra de progreso | Historia de usuario | Closed |
    | HU-004 | Validación y corrección de datos extraídos con editor lado a lado con imagen | Historia de usuario | Closed |
    | HU-005 | Creación de nuevo registro de ataúd en el catálogo de inventario | Historia de usuario | Closed |
    | HU-006 | Filtrado de la lista de ataúdes por modelo, color y tipo | Historia de usuario | Closed |
    | HU-007 | Visualización del inventario de capillas con stock actual | Historia de usuario | Closed |
    | HU-008 | Gestión y asignación de roles de usuario por el administrador | Historia de usuario | Closed |
    | TA-008 | Configuración de Ollama en Digital Ocean para servir el modelo de extracción | Tarea técnica | Closed |
    | TA-009 | Despliegue básico del frontend en Vercel y backend en Render con conexión a BD | Tarea técnica | Closed |
    
    **Sprint 2 — Módulo de predicción y cierre operativo (26 mayo – 15 junio 2026)**
    
    | ID | Entregable | Tipo | Estado |
    | --- | --- | --- | --- |
    | EN-006 | Preprocesamiento del dataset histórico (340 registros, 46 meses): limpieza, normalización, encoding, imputación, agregación mensual. Integridad 97.94% | Tarea técnica | Closed |
    | SP-002 | Investigación y comparativa de 6 modelos de series temporales (SARIMA, Prophet, XGBoost, LightGBM, LSTM, ETS) con MAE, RMSE, R², MAPE | Spike | Closed |
    | TA-010 | Data augmentation con Test de Levene para validación estadística de homocedasticidad entre datos originales y sintéticos SMOTENC | Tarea técnica | Closed |
    | EN-007 | Comparativa de modelos predictivos con tabla cruzada de resultados y selección justificada | Tarea técnica | Closed |
    | BU-001 | Corrección de modelos predictivos con comportamiento lineal (LightGBM, LSTM, ETS) mediante re-entrenamiento | Corrección | Closed |
    | TA-011 | Fine-tuning del modelo de series temporales para proyecciones de stock precisas | Tarea técnica | Closed |
    | RN-002 | Validación del margen de error de lectura (MAPE < 20%) | Req. no funcional | Open |
    | TA-012 | Reestructuración del esquema de base de datos para incorporar estados en ataúd, capilla, vehículo, contratante y fallecido | Tarea técnica | Closed |
    | TA-013 | Optimización del pipeline de extracción mediante integración con API de Gemini (15 seg vs 10-14 min con Ollama CPU) | Tarea técnica | Closed |
    | TA-014 | Endpoint de predicción en FastAPI: recibe modelo y variable objetivo, retorna JSON de proyecciones | Tarea técnica | Closed |
    | TA-015 | Consumo del endpoint de predicción desde Angular con visualización gráfica de histórico y predicción | Tarea técnica | Closed |
    | HU-009 | Panel de proyecciones de stock con tabla y gráfico interactivo por modelo | Historia de usuario | Closed |
    | TA-016 | Análisis de reglas de asociación Apriori sobre 340 registros de servicios para identificar patrones de contratación conjunta | Tarea técnica | Closed |
    | HU-010 | Alertas de stock crítico con notificación visual en dashboard cuando el inventario está por debajo del umbral | Historia de usuario | Open |
    | HU-011 | Registro de nuevo modelo de capilla en el catálogo | Historia de usuario | Closed |
    | HU-012 | Visualización del panel de gestión de flota de vehículos | Historia de usuario | Closed |
    | HU-013 | Alta de vehículo por tipo con categorización para segmentación de flota | Historia de usuario | Closed |
    | HU-014 | Creación de nuevo servicio funerario con datos del fallecido, contratante, ataúd, capilla y vehículos | Historia de usuario | Closed |
    | HU-015 | Filtros de búsqueda de servicios por nombre, DNI y fecha | Historia de usuario | Closed |
    | HU-016 | Listado de servicios funerarios registrados con seguimiento de ceremonias y pagos | Historia de usuario | Closed |
    | HU-017 | Consulta de datos vía RENIEC mediante API DECOLECTA para autocompletado de DNI de fallecidos y contratantes | Historia de usuario | Closed |
    | HU-018 | Gestión del registro de contratantes con edición y eliminación | Historia de usuario | Closed |
    | HU-019 | Registro y consulta de fallecidos con protección de borrado si están vinculados a un servicio | Historia de usuario | Closed |
    | TA-017 | Implementación de borrado lógico en sustitución de eliminaciones físicas en todas las entidades del catálogo | Tarea técnica | Closed |
    | HU-020 | Listado de usuarios y roles con auditoría de accesos | Historia de usuario | Closed |
    | HU-021 | Gestión de pagos de servicios con estados: pendiente, parcial y pagado | Historia de usuario | Closed |
    | EN-008 | Configuración del entorno en Digital Ocean con PostgreSQL, APIs Python y acceso vía IP/dominio | Tarea técnica | Closed |
    | RN-003 | Compatibilidad de la interfaz con navegadores Chrome, Edge y Firefox sin errores de consola | Req. no funcional | Closed |
    | DO-001 | Documentación técnica del endpoint de extracción mediante Swagger (parámetros, JSON de salida, ejemplo real) | Documentación | Closed |
    | DO-002 | Documentación técnica del endpoint de predicción mediante Swagger | Documentación | Closed |
    | DO-003 | Manual de usuario para la secretaria: carga masiva y validación de datos de forma autónoma | Documentación | Closed |
    | DO-004 | Reporte final de métricas y validación de umbrales de éxito para la presentación del proyecto | Documentación | Open |

**4.2 Descripción técnica de módulos implementados**

- **Módulo de extracción de datos manuscritos**
    
    Este módulo constituye el primer pilar de inteligencia artificial del sistema. Su función es recibir imágenes de contratos manuscritos cargadas por el usuario, aplicar un pipeline de preprocesamiento visual y extraer los campos estructurados del formulario retornando un JSON listo para persistir en la base de datos.
    
    El pipeline de preprocesamiento aplica secuencialmente: conversión a escala de grises para eliminar información de color irrelevante, recorte automático de márgenes blancos, redimensionado con límite máximo de 1600px en el lado más largo, autocontraste para mejorar la legibilidad del texto y filtro de nitidez para acentuar los trazos manuscritos. Este preprocesamiento redujo el tiempo de inferencia de 10-14 minutos a aproximadamente 10 minutos en la configuración con Transformers HF, y a 35 segundos con Ollama sobre CPU en producción.
    
    La arquitectura del módulo implementa el patrón Strategy mediante una clase abstracta `ExtractorIAInterface` con el método `extraer_datos_contrato`, del que heredan dos implementaciones intercambiables: `OllamaStrategy`, que envía la imagen codificada en base64 al servidor Ollama local mediante la API `/api/chat` con el modelo `qwen2.5vl:3b`; y la integración con la API de Gemini como motor alternativo con tiempo de respuesta de aproximadamente 15 segundos. El endpoint `/ia/procesar-contrato` expuesto en FastAPI recibe la imagen como multipart/form-data, ejecuta el preprocesamiento, invoca la estrategia activa y retorna el JSON estructurado con los campos del contrato.
    
    Los campos extraídos son: fecha, contratante_nombre, contratante_dni, contratante_telefono, fallecido_nombre, direccion_velacion, tipo_pago, ataud_modelo, ataud_color, capilla_modelo, ids_vehiculos_detectados, cantidad_cargadores y costo. El resultado se presenta al usuario en la interfaz de validación lado a lado con la imagen original para corrección antes de confirmarse en la base de datos.
    
    La decisión de implementación no trivial más relevante fue el abandono del pipeline HTR clásico (Multicentury-HTR por región + bounding boxes) en favor del modelo VLM Qwen2.5-VL-3B para extracción directa de JSON estructurado, eliminando la necesidad de un modelo de detección de regiones separado. El fine-tuning de Multicentury-HTR se mantuvo como componente de investigación documentado, alcanzando CER 0.3340 y Char Acc 0.6660 tras 10 épocas, pero el modelo de producción es Qwen2.5-VL-3B servido mediante Ollama.
    
    - **Fragmento representativo — preprocesamiento de imagen**
        
        ```jsx
        def preprocesar_imagen(imagen_bytes: bytes, max_dim: int = 1600) -> bytes:
        	imagen = Image.open(io.BytesI0(imagen_bytes))
        	imagen = imagen.convert("L").convert("RGB")
        	ancho, alto imagen.size
        	
        	bbox = imagen.convert("L").getbbox()
        	if bbox:
        		imagen = imagen.crop(bbox)
        		ancho, alto = imagen.size
        		
        	if ancho > max_dim or alto > max_dim:
        		escala max_dim / max(ancho, alto)
        		imagen = imagen.resize((int(ancho * escala), int (alto * escala)), Image. Resampling.LANCZOS)
        		
        	imagen = ImageOps.autocontrast (imagen, cutoff=1)
        	imagen = imagen.filter(ImageFilter.SHARPEN)
        	
        	buffer = io.BytesIO()
        	imagen.save(buffer, format="JPEG", quality=85)
        	return buffer.getvalue()
        ```
        
    - **Pseudocódigo:**
        
        ```jsx
        FUNCIÓN preprocesar_imagen(imagen_bytes, max_dim = 1600):
            imagen ← abrir imagen desde imagen_bytes
            imagen ← convertir a escala de grises → convertir a RGB
        
            bbox ← detectar bounding box del contenido no vacío
            SI bbox existe:
                imagen ← recortar imagen al bbox
        
            ancho, alto ← obtener dimensiones de imagen
            SI ancho > max_dim O alto > max_dim:
                escala ← max_dim / máximo(ancho, alto)
                imagen ← redimensionar imagen a (ancho * escala, alto * escala)
        
            imagen ← aplicar autocontraste con cutoff=1
            imagen ← aplicar filtro de nitidez
        
            buffer ← nuevo buffer en memoria
            guardar imagen en buffer como JPEG con calidad=85
            RETORNAR bytes del buffer
        ```
        
    - **Decisiones de implementación no triviales**
        
        El diseño separa estrictamente el prompt en dos zonas semánticas dentro de la imagen: el membrete de la funeraria (zona a ignorar) y el cuerpo del contrato (única fuente válida de datos). Esta distinción explícita en el prompt fue necesaria porque el modelo confundía sistemáticamente el teléfono y dirección de la empresa impresos en el membrete con los datos del contratante, al estar visualmente cerca en el documento.
        
        Se implementó un sistema de rotación de múltiples API keys de Gemini con reintentos automáticos ante respuesta HTTP 429, dado que el volumen de pruebas durante el desarrollo agotaba rápidamente la cuota gratuita de una sola key, con manejo diferenciado de errores HTTP, timeouts y respuestas JSON mal formadas. La función `normalizar_campos` aplica una segunda capa de validación determinística sobre la salida del modelo: corrige formatos de fecha no ISO, restringe `tipo_pago` a tres valores exactos mediante coincidencia de palabras clave, valida que `contratante_dni` tenga exactamente 8 dígitos, y filtra `ids_vehiculos_detectados` contra una lista cerrada de valores válidos. Esta normalización fue necesaria porque, pese a las instrucciones estrictas del prompt, el modelo ocasionalmente retornaba variantes no exactas (por ejemplo, "Efectivo" en lugar de "directo").
        
- **Módulo de normalización y postprocesamiento de datos extraídos**
    
    Aplica una segunda capa de validación determinística sobre el JSON retornado por Gemini antes de persistirlo en la base de datos, corrigiendo inconsistencias de formato, estandarizando valores de dominio cerrado y descartando datos inválidos que el modelo ocasionalmente retorna pese a las instrucciones del prompt.
    
    - **Fragmento representativo — normalización de campos**
        
        ```jsx
        def normalizar_campos(datos: Dict[str, Any]) -> Dict[str, Any]:
            tipo_raw = str(datos.get("tipo_pago") or "").lower().strip()
            if any(p in tipo_raw for p in ["seguro", "aseguradora", "poliza"]):
                datos["tipo_pago"] = "seguro"
            elif any(p in tipo_raw for p in ["mixto", "combinado", "parcial"]):
                datos["tipo_pago"] = "mixto"
            elif any(p in tipo_raw for p in ["directo", "efectivo", "dinero", "contado"]):
                datos["tipo_pago"] = "directo"
            else:
                datos["tipo_pago"] = None
        
            dni = str(datos.get("contratante_dni") or "").strip()
            if not (dni.isdigit() and len(dni) == 8):
                datos["contratante_dni"] = None
        
            validos = {"porta_ataud", "porta_flores", "mixto", "auto", "microbus"}
            raw = datos.get("ids_vehiculos_detectados", [])
            datos["ids_vehiculos_detectados"] = (
                [v for v in raw if v in validos] if isinstance(raw, list) else []
            )
            return datos
        ```
        
    - **Pseudocódigo:**
        
        ```jsx
        FUNCIÓN normalizar_campos(datos):
        
            tipo_raw ← datos["tipo_pago"] convertido a minúsculas y sin espacios
            SI tipo_raw contiene alguno de ["seguro", "aseguradora", "poliza"]:
                datos["tipo_pago"] ← "seguro"
            SI NO tipo_raw contiene alguno de ["mixto", "combinado", "parcial"]:
                datos["tipo_pago"] ← "mixto"
            SI NO tipo_raw contiene alguno de ["directo", "efectivo", "dinero", "contado"]:
                datos["tipo_pago"] ← "directo"
            SI NO:
                datos["tipo_pago"] ← null
        
            dni ← datos["contratante_dni"] convertido a string y sin espacios
            SI dni NO es solo dígitos O longitud de dni ≠ 8:
                datos["contratante_dni"] ← null
        
            telefono_raw ← datos["contratante_telefono"] convertido a string
            telefono_limpio ← extraer solo dígitos de telefono_raw
            SI telefono_limpio no está vacío:
                datos["contratante_telefono"] ← telefono_limpio
            SI NO:
                datos["contratante_telefono"] ← null
        
            validos ← {"porta_ataud", "porta_flores", "mixto", "auto", "microbus"}
            raw ← datos["ids_vehiculos_detectados"]
            SI raw es una lista:
                datos["ids_vehiculos_detectados"] ← [v PARA CADA v EN raw SI v está en validos]
            SI NO:
                datos["ids_vehiculos_detectados"] ← []
        
            SI datos["ataud_color"] es "null", "none" o vacío:
                datos["ataud_color"] ← null
        
            RETORNAR datos
        ```
        
    - **Decisiones de implementación no triviales**
    La normalización fue necesaria porque el modelo de lenguaje, pese a recibir instrucciones estrictas en el prompt, retornaba ocasionalmente variantes no exactas de los valores de dominio cerrado: por ejemplo "Efectivo" en lugar de "directo" para el tipo de pago, DNI con espacios o guiones intermedios, o vehículos con nombres distintos a los definidos en el sistema. El enfoque elegido fue aplicar coincidencia por palabras clave en lugar de comparación exacta para `tipo_pago`, lo que cubre abreviaciones y sinónimos del dominio funerario local. Para `ids_vehiculos_detectados` se optó por filtrado contra un conjunto cerrado de valores válidos (`porta_ataud`, `porta_flores`, `mixto`, `auto`, `microbus`), descartando silenciosamente cualquier valor no reconocido en lugar de lanzar un error, priorizando la continuidad del flujo de registro sobre la completitud del campo. El campo `direccion_velacion` incluye además manejo del caso en que el modelo retorna un diccionario en lugar de una cadena, extrayendo el primer valor string de longitud mayor a 5 caracteres como valor final.
- **Módulo de gestión de pagos con Stripe**
    
    Gestiona el ciclo de vida de los pagos de servicios funerarios mediante la integración con la pasarela Stripe, creando intenciones de pago, almacenando su estado en la base de datos local y actualizándolo ante confirmaciones o fallos del procesador. Soporta pagos individuales completos (modalidad directa) y pagos parciales acumulativos (modalidad mixta).
    
    - **Fragmento representativo — creación de intención de pago**
        
        ```jsx
        @staticmethod
        def crear_pago(db: SessionDep, data: PagoCrear) -> tuple[Pago, str]:
            intent = stripe.PaymentIntent.create(
                amount=data.monto,
                currency=data.moneda,
                description=data.descripcion,
                metadata={"id_servicio": data.id_servicio}
            )
            pago = Pago(
                id_servicio=data.id_servicio,
                stripe_payment_intent_id=intent.id,
                monto=data.monto,
                moneda=data.moneda,
                descripcion=data.descripcion,
                estado=EstadoPago.pendiente,
            )
            db.add(pago)
            db.commit()
            db.refresh(pago)
            return pago, intent.client_secret
        ```
        
    - **Pseudocódigo:**
        
        ```jsx
        FUNCIÓN crear_pago(db, data):
            intent ← Stripe.PaymentIntent.crear(
                monto     = data.monto,
                moneda    = data.moneda,
                descripcion = data.descripcion,
                metadata  = { "id_servicio": data.id_servicio }
            )
        
            pago ← nuevo Pago con:
                id_servicio              = data.id_servicio
                stripe_payment_intent_id = intent.id
                monto                    = data.monto
                moneda                   = data.moneda
                descripcion              = data.descripcion
                estado                   = PENDIENTE
        
            db.agregar(pago)
            db.confirmar()
            db.refrescar(pago)
        
            RETORNAR (pago, intent.client_secret)
        
        FUNCIÓN actualizar_estado(db, stripe_payment_intent_id, nuevo_estado):
            pago ← buscar en db DONDE stripe_payment_intent_id coincide
        
            SI pago no existe:
                LANZAR error 404 "Pago no encontrado"
        
            pago.estado ← nuevo_estado
            pago.fecha_actualizacion ← fecha y hora actual UTC
        
            db.agregar(pago)
            db.confirmar()
            db.refrescar(pago)
        
            RETORNAR pago
        ```
        
    - **Decisiones de implementación no triviales**
    El sistema nunca almacena ni procesa datos de tarjeta directamente. Al crear un pago, el backend genera una `PaymentIntent` en Stripe y retorna únicamente el `client_secret` al frontend, que lo usa para renderizar el formulario de tarjeta mediante el SDK oficial de Stripe JS. El número de tarjeta, fecha de vencimiento y CVV nunca transitan por los servidores del proyecto. El estado del pago se almacena localmente en la tabla `pago` con el identificador `stripe_payment_intent_id` como clave de trazabilidad, permitiendo actualizar el estado (`pendiente`, `completado`) mediante el método `actualizar_estado` invocado desde el webhook de Stripe o desde la interfaz de administración. El campo `metadata` de la PaymentIntent incluye el `id_servicio`, lo que permite reconciliar el pago con el servicio funerario correspondiente directamente desde el panel de Stripe sin depender de la base de datos local.
- **Módulo de autenticación y control de accesos**
    
    Este módulo gestiona la seguridad de toda la plataforma mediante autenticación JWT y un sistema de autorización basado en roles y permisos dinámicos almacenados en base de datos. El backend implementa las funciones `create_access_token` y `decode_token` sobre el algoritmo HS256 con expiración configurable de 60 minutos de inactividad y máximo de 8 horas de sesión. Cada token codifica el identificador del usuario, que el sistema utiliza para consultar en tiempo de ejecución los permisos asociados a su rol antes de autorizar el acceso a cualquier endpoint protegido.
    
    El sistema de roles es completamente dinámico: los roles se almacenan en la tabla `role`, los permisos en la tabla `permission`, y la relación entre ambos en `rolepermissionlink`. La función de dependencia `get_current_admin` verifica explícitamente que el usuario tenga el rol de Administrador consultando la base de datos mediante un join entre `UserRoleLink` y `Role`, retornando HTTP 403 si no cuenta con esa credencial. El seeder inicial registra automáticamente todos los permisos del sistema agrupados por módulo (inventario, capillas, vehículos, servicios, fallecidos, contratantes, usuarios) y crea los roles base Administrador (acceso total) y Trabajador (permisos restringidos) si no existen previamente.
    
    - **Fragmento representativo — verificador de permisos dinámico**
        
        ```jsx
        class CheckerPermisos:
        	def _init__(self, permiso_requerido: str):
        		self.permiso_requerido = permiso_requerido
        		
        	def_call_(self, token: dict = Depends (decode_token), db: Session = Depends (get_db)):
        		user_id = int(token.get("sub"))
        		
        		statement = (
        			select (Permission)
        			.join(RolePermissionLink, RolePermissionLink.permission_id == Permission.id)
        			.join(Role, Role.id == RolePermissionLink.role_id)
        			.join(UserRoleLink, UserRoleLink.role_id == Role.id)
        			.where (UserRoleLink.user_id == user_id)
        			.where (Permission.nombre == self.permiso_requerido)
        			
        		permiso_encontrado = db.exec(statement).first()
        		
        		if not permiso_encontrado:
        			raise HTTPException(
        				status_code=status.HTTP_403_FORBIDDEN,
        				detail=f"No tienes el permiso necesario: '{self.permiso_requerido}'"
        		return token
        ```
        
    - Pseudocódigo:
        
        ```jsx
        CLASE CheckerPermisos:
        
            CONSTRUCTOR(permiso_requerido):
                self.permiso_requerido ← permiso_requerido
        
            FUNCIÓN __call__(token, db):
        
                user_id ← obtener "sub" del token convertido a entero
        
                statement ← SELECCIONAR Permission
                    UNIR RolePermissionLink
                        DONDE RolePermissionLink.permission_id == Permission.id
                    UNIR Role
                        DONDE Role.id == RolePermissionLink.role_id
                    UNIR UserRoleLink
                        DONDE UserRoleLink.role_id == Role.id
                    FILTRAR DONDE UserRoleLink.user_id == user_id
                    FILTRAR DONDE Permission.nombre == self.permiso_requerido
        
                permiso_encontrado ← db.ejecutar(statement).primero()
        
                SI permiso_encontrado es null:
                    LANZAR error 403 "No tienes el permiso necesario: self.permiso_requerido"
        
                RETORNAR token
        ```
        
    - **Decisiones de implementación no triviales**
    La verificación de permisos se implementó como una clase invocable (`CheckerPermisos`) parametrizada con el nombre del permiso requerido, usada como dependencia de FastAPI en cada endpoint mediante `Depends(CheckerPermisos("ataudes:crear"))`. Este diseño permite declarar el permiso necesario directamente en la firma del endpoint sin duplicar lógica de verificación, y al consultar la base de datos en cada petición en lugar de embeber los permisos en el JWT, un cambio de rol o permiso aplicado por el administrador tiene efecto inmediato sin que el usuario afectado necesite volver a iniciar sesión. La sesión expira a las 8 horas (`ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8`), valor ajustado durante el desarrollo desde los 60 minutos iniciales documentados en el backlog para adaptarse a sesiones de trabajo más largas del personal administrativo.
- **Módulo de validación de identidad con DECOLECTA**
    
    Consulta en tiempo real los datos personales de una persona a partir de su número de DNI, utilizando la API DECOLECTA como proxy del Registro Nacional de Identidad (RENIEC), y retorna los campos de nombre, apellidos y número de documento para autocompletar el formulario de registro de fallecidos y contratantes sin necesidad de digitación manual.
    
    - **Fragmento representativo — consulta de DNI**
        
        ```jsx
        async def consultar_dni(dni: str) -> dict:
            if not dni or not dni.isdigit() or len(dni) != 8:
                raise HTTPException(status_code=400, detail="DNI inválido")
        
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    RENIEC_API_URL,
                    params={"numero": dni},
                    headers={"Authorization": f"Bearer {RENIEC_TOKEN}"}
                )
        
            data = response.json()
            return {
                "dni":              data.get("document_number"),
                "nombres":          data.get("first_name"),
                "apellido_paterno": data.get("first_last_name"),
                "apellido_materno": data.get("second_last_name"),
                "nombre_completo":  data.get("full_name")
            }
        ```
        
    - Pseudocódigo:
        
        ```jsx
        FUNCIÓN consultar_dni(dni):
        
            SI dni está vacío O dni no es solo dígitos O longitud(dni) ≠ 8:
                LANZAR error 400 "DNI inválido — debe tener exactamente 8 dígitos"
        
            SI RENIEC_TOKEN no está configurado:
                LANZAR error 503 "Token RENIEC no configurado"
        
            INTENTAR:
                response ← GET a RENIEC_API_URL con:
                    parámetros = { "numero": dni }
                    cabeceras  = { "Authorization": "Bearer " + RENIEC_TOKEN }
                    timeout    = 10 segundos
            SI ocurre error de conexión:
                LANZAR error 503 "No se pudo conectar con el servicio RENIEC"
        
            SI response.status == 401:
                LANZAR error 503 "Token RENIEC inválido o expirado"
            SI response.status == 404:
                LANZAR error 404 "DNI no encontrado"
            SI response.status == 422:
                LANZAR error 400 "DNI inválido según el servicio"
            SI response.status ≠ 200:
                LANZAR error 502 "Error al consultar RENIEC (código: response.status)"
        
            data ← parsear respuesta JSON
            RETORNAR {
                "dni"             : data["document_number"],
                "nombres"         : data["first_name"],
                "apellido_paterno": data["first_last_name"],
                "apellido_materno": data["second_last_name"],
                "nombre_completo" : data["full_name"]
            }
        ```
        
    - **Decisiones de implementación no triviales**
    La API oficial de RENIEC no es de acceso público y requiere la presentación de documentación formal como empresa privada, lo que la hacía inviable en el contexto académico del proyecto. Se utilizó DECOLECTA como alternativa de acceso disponible, que expone la misma información base (nombres, apellidos, número de documento) mediante una API REST con autenticación por token Bearer. El servicio implementa manejo diferenciado de los códigos de error de la API externa: HTTP 401 indica token inválido o expirado, HTTP 404 indica DNI inexistente en el registro, HTTP 422 indica formato inválido según el validador remoto, y cualquier otro código distinto de 200 se propaga como HTTP 502 al cliente con el código original incluido en el mensaje, facilitando la depuración sin exponer detalles internos. La validación local del formato del DNI (exactamente 8 dígitos numéricos) se aplica antes de realizar la petición externa para evitar consumir cuota de la API con solicitudes que fallarían de todas formas.

**4.3 Gestión de datos**

*4.3.1 Fuentes de datos*

El proyecto trabaja con dos fuentes de datos diferenciadas según el componente de inteligencia artificial al que sirven.

La primera fuente corresponde al dataset de imágenes para el módulo HTR. El origen es el archivo físico de contratos manuscritos de la Funeraria Máximo Aranzabal, fotografiados directamente por el equipo de desarrollo con iluminación natural y resolución mínima de 300 ppp en formato .jpg y .png. El volumen alcanzó 280 imágenes aptas tras descartar fotografías con sombras, desenfoque o ilegibilidad severa. No existe licencia de uso formal dado que los datos pertenecen al patrocinador del proyecto y fueron cedidos para uso exclusivo del desarrollo académico.

La segunda fuente corresponde al dataset histórico de servicios para el módulo predictivo. El origen es el mismo archivo físico de contratos, digitalizado mediante el propio módulo de extracción del sistema y complementado con corrección manual. El volumen original fue de 340 registros de servicios funerarios en formato tabular, cubriendo 46 meses entre mayo de 2022 y febrero de 2026, con 18 columnas de variables operativas incluyendo fecha, tipo de pago, modelo y color de ataúd, capilla, carroza, flores, número de cargadores, vehículos y monto total. Al igual que el dataset de imágenes, los datos son propiedad del patrocinador y su uso está restringido al contexto del proyecto.

*4.3.2 Preprocesamiento*

- **Pipeline del dataset de imágenes (módulo HTR)**
    
    El preprocesamiento de imágenes se aplicó en dos etapas. La primera etapa, ejecutada antes del etiquetado en Label Studio, consistió en la selección y descarte manual de imágenes con calidad insuficiente para el entrenamiento. La segunda etapa, aplicada en tiempo de inferencia por el endpoint de extracción, aplica secuencialmente: conversión a escala de grises, recorte automático de márgenes, redimensionado con límite de 1600px en el lado más largo, autocontraste y filtro de nitidez mediante la librería Pillow.
    
- **Pipeline del dataset histórico (módulo predictivo)**
    
    El preprocesamiento del dataset histórico siguió un pipeline estructurado en seis pasos ejecutados mediante scripts Python con pandas. 
    
    El primer paso consistió en la eliminación de filas inútiles y registros duplicados. El segundo paso estandarizó los formatos de fecha al estándar ISO 8601. El tercer paso aplicó normalización de categorías sobre las columnas Ataud_Modelo (338 valores normalizados), Ataud_Color (301), Capilla (314) y Forma de pago (340), unificando variantes ortográficas y abreviaciones del mismo valor. El cuarto paso aplicó encoding binario sobre variables categóricas booleanas como presencia de carroza, auto y cargadores. El quinto paso realizó la agregación mensual de registros individuales en series temporales de servicios_totales y monto_total. El sexto paso aplicó winsorización al percentil 99 para el tratamiento de outliers en la variable monto (umbral: S/ 154,600), corrigiendo el outlier extremo de S/ 870,000 detectado en el registro 105 (mediana de referencia: S/ 2,300).
    
    Las estadísticas de calidad resultantes del pipeline fueron: 1,335 cambios totales aplicados sobre el dataset, promedio de 3.93 cambios por registro, integridad de datos del 97.94%, consistencia temporal con 6 lagunas detectadas y tratadas, 42 registros con fecha imputada, 19 outliers en monto (5.59%) y cobertura temporal de 46 meses con datos (mayo 2022 – febrero 2026).
    
    Adicionalmente se aplicaron tres técnicas de data augmentation sobre el dataset preprocesado. El Bootstrapping Temporal generó 5 iteraciones con reemplazo añadiendo ruido gaussiano sobre el monto (σ=50) y variaciones aleatorias en las fechas (±3 días), expandiendo el dataset de 340 a 2,040 registros. El RandomOverSampler con SMOTENC filtró las 75 clases de Ataud_Modelo con menos de 5 registros (de 86 a 11 clases) y balanceó el dataset a 76 registros por clase, expandiendo de 254 a 836 registros. La validación estadística mediante el Test de Levene (H0: varianzas iguales, α=0.05) confirmó homocedasticidad en 3 de 4 variables (Carroza, Auto y Cargadores), con la variable Monto_winsorizado presentando varianza sintética 8.3 veces menor que la original (p=0.0047), efecto conocido de SMOTE denominado variance shrinkage. Esta limitación fue documentada y se decidió no aplicar correcciones adicionales dado que el modelo predictivo final utiliza dataset_mensual y no el dataset SMOTE. El Sliding Window generó 43 ventanas de 3 meses con lags temporales (t-1, t-2, t-3) y variable target para alimentar los modelos supervisados XGBoost y LightGBM.
    

*4.3.3 Partición de datos* 

- **Módulo HTR**
    
    El dataset de imágenes etiquetadas se particionó en conjunto de entrenamiento y conjunto de validación con una proporción aproximada de 80/20 sobre las 280 imágenes aptas. La estrategia de muestreo fue aleatoria simple dado el volumen reducido del dataset y la ausencia de clases desbalanceadas en el nivel de imagen completa. El fine-tuning de Multicentury-HTR se ejecutó durante 10 épocas con monitoreo de Validation Loss, CER y WER en cada época para detectar sobreajuste. Los mejores pesos se seleccionaron en la época 7, donde el CER de validación alcanzó 0.2491 antes de estabilizarse en 0.2982-0.2983 en las épocas 8-10.
    
- **Módulo predictivo**
    
    La partición del dataset mensual siguió una estrategia temporal estricta, sin aleatorización, para respetar la dependencia temporal de las series. El conjunto de entrenamiento comprende desde mayo de 2022 hasta febrero de 2025, cubriendo 34 meses. El conjunto de prueba comprende desde marzo de 2025 hasta febrero de 2026, cubriendo 12 meses. Esta proporción de aproximadamente 75/25 fue determinada por el volumen disponible del historial y la necesidad de contar con al menos un año completo de datos de prueba para evaluar la captura de estacionalidad anual. No se aplicó k-fold cross-validation dado que su uso en series temporales requiere walk-forward validation, técnica descartada por el volumen insuficiente de datos que generaría ventanas de entrenamiento demasiado pequeñas en los primeros folds.
    

**4.4 Configuración del entorno de desarrollo y producción**

- **Especificaciones de hardware**
    
    El desarrollo local se realizó sobre equipos con GPU NVIDIA con soporte CUDA 11.8, requerido por las dependencias `torch==2.7.1+cu118` y `torchvision==0.22.1+cu118`. El entrenamiento del modelo Multicentury-HTR y las pruebas de inferencia con Transformers de Hugging Face se ejecutaron sobre GPU, con un tiempo promedio de 6-7 minutos por imagen en las primeras configuraciones sin optimización de preprocesamiento. El servidor de producción para el modelo de inferencia es un droplet de Digital Ocean operando en modo CPU-only, sin GPU dedicada, donde Ollama corre el modelo cuantizado `qwen2.5vl:3b` con una latencia de aproximadamente 35 segundos por imagen.
    
    - **Resumen de especificaciones:**
        - **Opción de CPU:** Regular
            - **Tipo de Disco:** SSD
        - **Tipo de plan:** Básico
        - **Opción de CPU:** Regular
        - **vCPU:** 4
        - **RAM:** 8GB
        - **Disco:** 160 GB
        - **Ancho de banda:** 5 TB Transfer
        - **Identificador único:** s-4vcpu-8gb
        - **Costo Total:** $48/mes ($0.071/hora)
- **Dependencias del backend**
    
    Las dependencias principales del backend están definidas en `requirements.txt`. Las librerías de mayor relevancia técnica para el proyecto son las siguientes:
    
    | Librería | Versión | Rol en el proyecto |
    | --- | --- | --- |
    | fastapi | 0.136.1 | Framework principal del backend REST |
    | sqlmodel | 0.0.38 | ORM para definición de modelos y acceso a PostgreSQL |
    | psycopg2-binary | 2.9.12 | Driver de conexión a PostgreSQL |
    | uvicorn | 0.46.0 | Servidor ASGI para FastAPI |
    | transformers | 5.8.0 | Carga y fine-tuning de modelos HTR (Multicentury-HTR) |
    | torch | 2.7.1+cu118 | Motor de inferencia con soporte CUDA 11.8 |
    | qwen-vl-utils | 0.0.14 | Utilidades para el modelo Qwen2.5-VL-3B |
    | python-doctr | 1.0.1 | Detección y reconocimiento de texto en documentos |
    | prophet | 1.3.0 | Modelo de predicción de series temporales |
    | statsmodels | 0.14.6 | SARIMA y ETS para series temporales |
    | xgboost | 3.2.0 | Modelo de predicción supervisado con sliding window |
    | lightgbm | 4.6.0 | Modelo de predicción supervisado con sliding window |
    | tensorflow | 2.21.0 | LSTM para series temporales |
    | keras | 3.14.1 | API de alto nivel para LSTM |
    | scikit-learn | 1.9.0 | Preprocesamiento, métricas y pipelines de ML |
    | imbalanced-learn | 0.14.2 | SMOTENC para data augmentation |
    | mlxtend | 0.25.0 | Algoritmo Apriori para reglas de asociación |
    | pmdarima | 2.1.1 | Auto-ARIMA para selección automática de parámetros SARIMA |
    | stripe | 15.2.0 | SDK oficial de Stripe para gestión de pagos |
    | python-jose | 3.5.0 | Generación y validación de tokens JWT |
    | bcrypt | 4.0.1 | Hash de contraseñas de usuarios |
    | passlib | 1.7.4 | Gestión de esquemas de hash de contraseñas |
    | pillow | 12.2.0 | Preprocesamiento de imágenes de contratos |
    | opencv-python | 4.13.0.92 | Procesamiento avanzado de imagen |
    | pandas | 3.0.2 | Manipulación y análisis del dataset histórico |
    | numpy | 2.4.4 | Operaciones matriciales y numéricas |
    | jiwer | 4.0.0 | Cálculo de métricas CER y WER para evaluación HTR |
    | accelerate | 1.13.0 | Optimización de entrenamiento en GPU con HuggingFace |
    | httpx | 0.28.1 | Cliente HTTP asíncrono para consumo de APIs externas |
    
    **Dependencias del frontend**
    
    Las dependencias del frontend están definidas en `package.json` con Angular 21 como framework principal.
    
    | Librería | Versión | Rol en el proyecto |
    | --- | --- | --- |
    | @angular/core | ^21.2.0 | Framework principal del frontend |
    | @angular/router | ^21.2.0 | Navegación entre módulos de la plataforma |
    | @angular/forms | ^21.2.0 | Formularios reactivos para registro y validación |
    | @stripe/stripe-js | ^9.7.0 | SDK de Stripe para procesamiento de pagos en cliente |
    | apexcharts | ^5.15.0 | Motor de gráficos para visualización de pronósticos |
    | ng-apexcharts | ^2.4.0 | Wrapper Angular para ApexCharts |
    | ngx-spinner | ^21.0.0 | Indicador visual de carga durante inferencia del modelo |
    | sweetalert2 | ^11.26.22 | Diálogos de confirmación para acciones críticas |
    | angular-toastify | ^2.0.0 | Notificaciones de éxito y error en operaciones |
    | rxjs | ~7.8.0 | Programación reactiva y manejo de peticiones HTTP |
    | typescript | ~5.9.2 | Tipado estático del código Angular |
- **Estrategia de despliegue**
    
    El sistema opera en una arquitectura de despliegue distribuida en tres proveedores distintos. El frontend Angular se despliega en Vercel con despliegue continuo desde el repositorio GitHub, configurado para construir automáticamente ante cada push a la rama principal. El backend FastAPI se despliega en Render como Web Service Python con despliegue continuo desde GitHub, con las variables de entorno configuradas para conexión a la base de datos y claves de servicios externos. La base de datos PostgreSQL opera en Digital Ocean como base de datos administrada, accesible desde el backend en Render mediante cadena de conexión con SSL. El servidor de inferencia Ollama se ejecuta en un droplet separado de Digital Ocean con el modelo `qwen2.5vl:3b` descargado, expuesto públicamente mediante un túnel Cloudflared que mapea el puerto 11434 de Ollama a una URL pública consumible por el backend en Render. Como alternativa de producción, la API de Gemini se integra directamente desde el backend como motor de inferencia secundario sin requerir infraestructura adicional.
    

**4.5 Control de versiones y trazabilidad**

- **Estrategia de branching**
    
    En el caso respectivo, realizamos GitFlow, siendo la rama Main nuestra rama principal, utilizada para el despliegue de nuestro producto. La rama develop fue utilizada como rama de unificación con las otras ramas y también fue nuestro foco principal de pruebas, ya que dentro de esta misma rama, realizamos los merge de las otras (con distintas funcionalidades de la pagina) y realizamos las pruebas respectivas antes de pasarlas a la Main. 
    
    Finalmente las feature branches, son ramas en las cuales realizamos las diferentes funcionalidades de nuestro proyecto, designadas en el product backlog. Cabe resaltar que las feature branches también se utilizaron para corregir bugs como carga de información, bucles sin cerrar y falta de manejo de errores.
    
    - **Back:**
        
        !image.png
        
        !image.png
        
        !image.png
        
    - **Front:**
        
        !image.png
        
        !image.png
        
        !image.png
        
    - **Modelo:**
        
        !image.png
        
- **Número de commits, PRs y releases:**
    - Número de commits: Considerando que la rama Main es la rama principal, consideremos todos los commits realizados a esa rama respectivamente:
        
        
        | Componente | Cantidad total de commits |
        | --- | --- |
        | Back | 94 commits |
        | Front | 71 commits |
        | Modelo | 18 commits |
        - **Back:**
            
            !image.png
            
            !image.png
            
        - **Front:**
            
            !image.png
            
            !image.png
            
        - **Modelo:**
            
            !image.png
            
    - **Pull Requests:**
        
        
        | Componente | Cantidad total de pull requests |
        | --- | --- |
        | Back | 21 |
        | Front | 14 |
        | Modelo | 1 |
        - **Back:**
            
            !image.png
            
        - **Front:**
            
            !image.png
            
        - **Modelo:**
            
            !image.png
            
    - **Releases documentadas**: el versionado se manejó mediante commits y no mediante releases formales, dado el alcance, la naturaleza y duración del proyecto.

### **SECCIÓN 5 — EVALUACIÓN Y VALIDACIÓN**

*(equivale a Experiments & Results)*

**5.1 Estrategia de evaluación**

- **¿Qué se evalúa y por qué esas métricas?**
    
    El sistema se evaluó mediante dos estrategias complementarias según el componente analizado. Para los componentes de inteligencia artificial (módulo HTR y módulo predictivo) se aplicó validación técnica experimental comparativa, evaluando múltiples modelos candidatos bajo las mismas condiciones de datos y métricas para seleccionar la solución óptima para el dominio. Para la plataforma web se aplicó validación técnica funcional, verificando el comportamiento de cada funcionalidad contra sus criterios de aceptación definidos en el backlog y midiendo tiempos de respuesta de los endpoints críticos.
    La elección de métricas orientadas al error (CER, WER, MAPE, MAE) sobre métricas de exactitud global responde a la naturaleza del dominio: en un sistema de digitalización de contratos con datos personales y económicos, un error en un dígito del DNI o del monto total tiene consecuencias operativas directas para el negocio, por lo que interesa cuantificar la magnitud del error a nivel de carácter y de valor absoluto, no solo si el resultado es correcto o incorrecto en su totalidad.
    

**5.2 Métricas de evaluación definidas**

- ***Para módulo de reconocimiento de escritura manuscrita (HTR):***
    
    
    | Métrica | Fórmula | Justificación |
    | --- | --- | --- |
    | CER (Character Error Rate) | (S + D + I) / N | Mide el porcentaje de caracteres individuales incorrectos. Es la métrica principal para HTR porque penaliza errores a nivel de letra, relevante para campos como DNI y monto |
    | WER (Word Error Rate) | (S_w + D_w + I_w) / N_w | Mide el porcentaje de palabras completas incorrectas. Complementa el CER para evaluar la legibilidad semántica de campos como nombres y direcciones |
    | Char Accuracy | 1 - CER | Proporción de caracteres correctamente transcritos. Facilita la interpretación positiva del rendimiento del modelo |
    | Exact Match | Coincidencias exactas / Total muestras | Mide el porcentaje de campos transcritos perfectamente sin ningún error. Relevante para campos de valor único como número de contrato |
    | Latencia de inferencia (ms) | Tiempo de respuesta por imagen | Determina la viabilidad operativa del modelo en producción considerando el flujo de trabajo de la secretaria |
    
    Donde S = sustituciones, D = eliminaciones, I = inserciones, N = número total de caracteres de referencia; análogamente para palabras en WER.
    
- ***Para el módulo de predicción de series temporales:***
    
    
    | Métrica | Fórmula | Justificación |
    | --- | --- | --- |
    | MAE (Mean Absolute Error) | (1/n) Σ|y_i - ŷ_i| | Error promedio absoluto en unidades del dominio (servicios o soles). Interpretable directamente por el negocio |
    | RMSE (Root Mean Square Error) | √((1/n) Σ(y_i - ŷ_i)²) | Penaliza errores grandes más que el MAE. Útil para detectar predicciones con desvíos extremos en meses de alta demanda |
    | R² (Coeficiente de determinación) | 1 - (SS_res / SS_tot) | Indica qué proporción de la varianza de la serie es explicada por el modelo. Valor positivo indica que el modelo supera a la media como predictor |
    | MAPE (Mean Absolute Percentage Error) | (1/n) Σ|( y_i - ŷ_i) / y_i| × 100 | Error porcentual relativo. Permite comparar el rendimiento entre las variables objetivo (servicios y monto) independientemente de su escala |
    | Tiempo de entrenamiento (s) | Segundos requeridos para entrenar sobre el dataset completo | Determina la viabilidad de reentrenamiento periódico con datos nuevos en el entorno de producción |
- ***Para la plataforma web:***
    
    
    | Métrica | Valor objetivo | Justificación |
    | --- | --- | --- |
    | Tiempo de respuesta del endpoint de extracción | < 15 segundos (Gemini) | Definido como umbral aceptable para el flujo de trabajo de carga masiva |
    | Tiempo de respuesta del endpoint de predicción | < 5 segundos | Criterio de aceptación definido en TA-006 del backlog |
    | Disponibilidad (Uptime) | > 99% | Garantiza que el sistema esté operativo durante el horario laboral de la funeraria |
    | Tasa de corrección manual | Porcentaje de campos extraídos que el usuario debe corregir | Mide la precisión práctica del sistema de extracción en condiciones reales |

**5.3 Diseño experimental**

- **Ambiente de prueba:**
    
    Las pruebas del módulo HTR se ejecutaron en dos entornos distintos. El entorno de desarrollo local contó con GPU NVIDIA con soporte CUDA 11.8, sobre el cual se realizó el fine-tuning del modelo Multicentury-HTR y las pruebas comparativas de los cuatro modelos candidatos. El entorno de producción corresponde a un droplet de Digital Ocean en modo CPU-only, donde Ollama sirve el modelo Qwen2.5-VL-3B cuantizado, y a la API de Gemini como motor de inferencia remoto con modelo `gemini-2.5-flash`.
    
    Las pruebas del módulo predictivo se ejecutaron íntegramente en el entorno de desarrollo local sobre el dataset mensual de 46 meses, con las tres fuentes de datos (base, bootstrap y bootstrap con sliding window) procesadas mediante scripts Python con las librerías statsmodels, prophet, xgboost, lightgbm, tensorflow y scikit-learn.
    
    Las pruebas funcionales de la plataforma web se realizaron sobre el sistema desplegado en producción: frontend en Vercel, backend en Render y base de datos en Digital Ocean, verificando la comunicación entre las tres capas bajo condiciones reales de red.
    
- **Casos de prueba definidos:**
    
    Para el módulo HTR se definieron tres tipos de casos de prueba. Las pruebas de comparativa preentrenada evaluaron los cuatro modelos candidatos sobre 221 muestras de crops de campos reales de contratos de la funeraria, sin fine-tuning, midiendo CER, WER, Accuracy y latencia media y p95. Las pruebas de fine-tuning evaluaron la evolución de las métricas del modelo Multicentury-HTR época a época durante 10 épocas de entrenamiento, monitoreando Training Loss, Validation Loss, CER y WER por época para detectar sobreajuste. Las pruebas de inferencia en producción evaluaron el tiempo de respuesta y la calidad de extracción del modelo Qwen2.5-VL-3B sobre imágenes completas de contratos bajo las condiciones reales del sistema desplegado.
    
    Para el módulo predictivo se definieron pruebas de comparativa de modelos evaluando los seis algoritmos (SARIMA, Prophet, XGBoost, LightGBM, LSTM y ETS) bajo tres fuentes de datos con métricas de MAE, RMSE, R² y MAPE. Se definieron además pruebas de data augmentation evaluando el impacto de cada técnica (Bootstrapping, SMOTENC, Sliding Window) sobre las métricas de los modelos, y pruebas de validación estadística mediante el Test de Levene para verificar la homocedasticidad entre los datos originales y los sintéticos generados por SMOTENC.
    Para la plataforma web se definieron pruebas funcionales sobre cada historia de usuario del backlog, verificando los criterios de aceptación definidos (carga masiva de imágenes, validación de datos extraídos, gestión de inventario, registro de servicios, pagos con Stripe, consulta de DNI con DECOLECTA, gestión de roles y permisos). Se verificó además la compatibilidad con navegadores Chrome, Edge y Firefox según el requerimiento no funcional RN-003.
    

**5.4 Resultados obtenidos**

- Tablas de resultados con media ± desviación estándar
    - **Módulo HTR — comparativa de modelos preentrenados (sin fine-tuning)**
        
        
        | Modelo | CER | WER | Accuracy | Latencia media (ms) | Latencia p95 (ms) |
        | --- | --- | --- | --- | --- | --- |
        | TrOCR-Large-EN | 0.6879 | 1.2178 | 0.0181 | 543.9 | 543.9 |
        | TrOCR-Base-ES | 9.0920 | 1.0909 | 0.0000 | 50,785.3 | 66,703.0 |
        | Multicentury-HTR | 0.6271 | 1.1903 | 0.0860 | 1,870.7 | 3,710.2 |
        | PARSeq-Multilingual | 2.4688 | 1.0000 | 0.0000 | 467.2 | 705.7 |
    - **Módulo HTR — evolución del fine-tuning de Multicentury-HTR por época**
        
        
        | Época | Training Loss | Validation Loss | CER | WER | Exact Match | Char Acc |
        | --- | --- | --- | --- | --- | --- | --- |
        | 1 | 30.1123 | 4.1320 | 0.5804 | 0.8915 | 0.1136 | 0.4196 |
        | 2 | 17.1378 | 3.1219 | 0.4270 | 0.7209 | 0.1364 | 0.5730 |
        | 3 | 7.8115 | 2.8584 | 0.3632 | 0.6512 | 0.2273 | 0.6368 |
        | 4 | 6.0392 | 2.6976 | 0.3031 | 0.5504 | 0.2500 | 0.6969 |
        | 5 | 4.1358 | 2.6721 | 0.3362 | 0.5891 | 0.1818 | 0.6638 |
        | 6 | 3.0541 | 2.6591 | 0.2957 | 0.5736 | 0.2727 | 0.7043 |
        | 7 | 2.1614 | 2.6171 | 0.2491 | 0.5271 | 0.2727 | 0.7509 |
        | 8 | 1.4437 | 2.5458 | 0.2736 | 0.5659 | 0.2727 | 0.7264 |
        | 9 | 1.2638 | 2.5454 | 0.2933 | 0.5966 | 0.2500 | 0.7067 |
        | 10 | 1.1258 | 2.5456 | 0.2982 | 0.5891 | 0.2500 | 0.7018 |
    - **Módulo HTR — resultados finales del modelo seleccionado**
        
        
        | Métrica | Valor final |
        | --- | --- |
        | Modelo | Multicentury-HTR (fine-tuned) |
        | CER | 0.3340 |
        | WER | 0.5442 |
        | Char Accuracy | 0.6660 |
        | Exact Match | 0.3182 |
        | Latencia media (ms) | 55,310.4 |
        | Latencia p95 (ms) | 85,209.9 |
        | Muestras de evaluación | 44 |
    - **Módulo predictivo — comparativa de modelos sobre dataset base**
        
        
        | Modelo | Target | MAE | RMSE | R² | MAPE | Tiempo (s) |
        | --- | --- | --- | --- | --- | --- | --- |
        | SARIMA | servicios_totales | 6.53 | 7.97 | -1.195 | 64.2% | 0.02 |
        | SARIMA | monto_total | 45,657 | 99,832 | -0.103 | 145.3% | 0.02 |
        | Prophet | servicios_totales | 4.31 | 5.36 | 0.006 | 94.0% | 0.36 |
        | Prophet | monto_total | 90,965 | 137,870 | -1.104 | 398.6% | 0.36 |
        | XGBoost | servicios_totales | 4.89 | 5.49 | -0.043 | 58.5% | 0.10 |
        | XGBoost | monto_total | 71,744 | 99,520 | -0.889 | 89.0% | 0.10 |
        | LightGBM | servicios_totales | 4.06 | 4.66 | 0.249 | 50.5% | 0.05 |
        | LightGBM | monto_total | 84,732 | 270,016 | -7.068 | 2,515.1% | 0.04 |
        | LSTM | servicios_totales | 4.37 | 5.22 | 0.060 | 88.3% | 17.08 |
        | LSTM | monto_total | 80,508 | 97,757 | -0.058 | 496.0% | 17.08 |
        | ETS | servicios_totales | 3.34 | 4.65 | 0.252 | 34.6% | 0.13 |
        | ETS | monto_total | 141,005 | 186,215 | -2.837 | 759.5% | 0.08 |
    - **Módulo predictivo — mejor modelo por fuente de datos y target**
        
        
        | Fuente | Target | Mejor modelo | R² | MAE |
        | --- | --- | --- | --- | --- |
        | Base | servicios_totales | Prophet | 0.006 | 4.31 |
        | Base | monto_total | LSTM | -0.058 | 78,030 |
        | Bootstrap | servicios_totales | Prophet | -0.001 | 28.30 |
        | Bootstrap | monto_total | ETS | -0.033 | 270,232 |
        | Bootstrap + Window | servicios_totales | XGBoost | -0.241 | 32.12 |
        | Bootstrap + Window | monto_total | LightGBM | -0.135 | 512,494 |
    - **Validación estadística — Test de Levene sobre data augmentation SMOTENC**
        
        
        | Variable | Media original | Media sintética | Varianza original | Varianza sintética | p-value | Homocedasticidad |
        | --- | --- | --- | --- | --- | --- | --- |
        | Monto_winsorizado | 5,420.13 | 2,931.35 | 3.06e+08 | 3.67e+07 | 0.0047 | No |
        | Carroza | 0.8504 | 0.8384 | 0.1277 | 0.2236 | 0.6647 | Sí |
        | Auto | 0.2874 | 0.3210 | 0.2056 | 0.1060 | 0.3309 | Sí |
        | Cargadores | 2.8503 | 2.4570 | 3.3214 | 3.0394 | 0.2646 | Sí |
    - **Plataforma web — tiempos de respuesta en producción**
        
        
        | Endpoint | Motor de inferencia | Tiempo promedio |
        | --- | --- | --- |
        | /ia/procesar-contrato | Gemini 2.5 Flash | ~15 segundos |
        | /ia/procesar-contrato | Ollama CPU (Digital Ocean) | ~35 segundos |
        | /ia/procesar-contrato | Qwen2.5-VL-3B GPU local | ~10 minutos |
        | /prediccion/predict | Modelos serializados (todos) | < 5 segundos |
- Gráficas:
    - Curvas de Predicción vs Real
        
        !predicciones_servicios_totales.png
        
        !predicciones_monto_total.png
        
    - Tabla Comparativa de Métricas
        
        !{3F76C9D1-EDA0-468D-B8DC-AC664241F298}.png
        
    - Benchmark tiempos
        
        !benchmarks_tiempos.png
        
    - Convergencia
        
        !convergencia_lstm.png
        
    - Análisis de Residuos
        
        !residuos_analisis.png
        

**5.5 Comparación con línea base o estado del arte**

**Módulo HTR — Comparativa de Char Accuracy y CER**

| Método | Métrica 1 (Char Accuracy) | Métrica 2 (CER) | Fuente |
| --- | --- | --- | --- |
| **Método propuesto** (Multicentury-HTR fine-tuned) | **0.6660** | **0.3340** | Este trabajo |
| CRNN (CNN + RNN / CTC) | 0.921 | — | (Sánchez et al., 2022, p. 75438) |
| Transformer encoder-decoder | 0.886 | 0.114 | (Kumar & Li, 2021, p. 165) |
| ViT + CNN con SAM y span masking | — | 0.086 | (Li et al., 2025, p. 4) |
| DANCER | — | 0.148 | (Alshahrani & Al-Amri, 2024, p. 415) |
| LSTM + PSO | 0.9714 | — | (Kumar et al., 2024, p. 3) |

**Módulo predictivo — Comparativa de MAPE**

| Método | Métrica 1 (MAPE) | Métrica 2 (R²) | Fuente |
| --- | --- | --- | --- |
| **Método propuesto** (ETS — mejor modelo base) | **34.6%** | **0.252** | Este trabajo |
| LSTM sobre datos de retail | 17.6% | — | (Zhao et al., 2020, p. 1045) |
| N-BEATS sobre M4/M5 | 15.9% | — | (Bandara et al., 2021, p. 1432) |
| Prophet/LSTM — pequeñas empresas servicios | 18.3% | — | (Chen et al., 2023) |
- **Sobre el módulo HTR:** El método propuesto presenta métricas inferiores a los trabajos del estado del arte en Char Accuracy y CER. Esto se explica porque los trabajos de referencia (Sánchez et al. (2022), Li et al. (2025), Kumar et al. (2024)) fueron evaluados sobre datasets estandarizados (IAM, READ2016) con escritura relativamente uniforme, mientras que el método propuesto fue evaluado sobre contratos manuscritos reales del dominio funerario con alta variabilidad caligráfica y vocabulario específico no cubierto por los modelos preentrenados.
- **Sobre el módulo predictivo:** El MAPE del método propuesto (34.6%) es superior al reportado por los trabajos de referencia (Zhao et al. (2020), (Bandara et al., 2021, p. 1432), Chen et al. (2023)), lo que indica menor precisión. Esta diferencia se explica por el volumen reducido del historial disponible (46 meses vs. los datasets de retail de los trabajos de referencia que cuentan con años de historial) y por la naturaleza esporádica e irregular de la demanda funeraria, condición identificada explícitamente como limitante para Zhao et al.

**5.6 Análisis estadístico**

La validación estadística formal se aplicó sobre el proceso de data augmentation mediante el Test de Levene, cuyo propósito fue verificar que los datos sintéticos generados por SMOTENC conservaran propiedades estadísticas similares a los datos originales antes de utilizarlos para el entrenamiento de modelos.

El Test de Levene evalúa la hipótesis nula H₀ de que las varianzas de dos grupos son iguales (homocedasticidad) con un nivel de significancia α=0.05. Un p-value mayor a 0.05 indica que no hay evidencia suficiente para rechazar H₀, confirmando que las varianzas son homogéneas entre los datos originales y los sintéticos.

Los resultados mostraron que 3 de las 4 variables analizadas (Carroza con p=0.665, Auto con p=0.331 y Cargadores con p=0.265) superaron el umbral de α=0.05, confirmando homocedasticidad y validando que SMOTENC preservó correctamente la distribución de las variables discretas al tratarlas como categóricas. La variable Monto_winsorizado rechazó H₀ con p=0.0047, evidenciando una varianza sintética 8.3 veces menor que la original (3.67×10⁷ vs 3.06×10⁸), efecto conocido en la literatura como variance shrinkage, atribuido a que SMOTENC interpola valores continuos entre vecinos cercanos concentrando los puntos sintéticos hacia el centro de la distribución. Esta limitación fue documentada y aceptada dado que el modelo predictivo final utiliza el dataset mensual original y no el dataset SMOTE, por lo que el variance shrinkage no afecta directamente las predicciones de producción.

**5.7 Discusión de resultados**

- **Módulo HTR**
    
    El fine-tuning sobre el dataset propio de la funeraria demostró ser efectivo para reducir el CER en un 51.5% respecto al mejor modelo preentrenado de la comparativa inicial, confirmando que la adaptación al dominio es indispensable cuando el vocabulario y la morfología de la escritura son específicos del negocio. Sin embargo, el umbral de Accuracy superior al 90% definido en los objetivos del proyecto no fue alcanzado: el modelo final obtuvo un Char Accuracy de 0.6660 y un Exact Match de 0.3182, lo que significa que aproximadamente uno de cada tres campos se transcribe perfectamente y dos tercios requieren alguna corrección. Este resultado se explica por la variabilidad extrema de la caligrafía manuscrita en los contratos de la funeraria, que incluye escritura ligada, abreviaciones propias del dominio y condiciones variables de iluminación y nitidez en las fotografías. La interfaz de validación lado a lado implementada en el sistema mitiga esta limitación, permitiendo a la secretaria corregir los campos incorrectos antes de confirmar el registro, reduciendo significativamente el tiempo total de digitalización respecto al proceso manual completo.
    
    La latencia de inferencia del modelo fine-tuned (55,310 ms de media) lo hace inviable para producción en tiempo real, razón por la cual el sistema de producción utiliza Qwen2.5-VL-3B vía Gemini API con 15 segundos promedio, que representa una reducción del tiempo de procesamiento del 97.3% respecto al pipeline HTR clásico con fine-tuning local.
    
- **Módulo predictivo**
    
    Ningún modelo de series temporales alcanzó el umbral de MAPE inferior al 20% establecido en los objetivos del proyecto sobre ninguna configuración de datos. El mejor resultado obtenido fue ETS con MAPE del 34.6% sobre servicios_totales en el dataset base, y Prophet con R²=0.006 como único modelo con varianza explicada positiva sobre la misma variable. Esta situación responde a dos factores estructurales del dataset: el volumen reducido de 46 meses de historial, insuficiente para que los modelos capturen patrones de estacionalidad anual con robustez estadística, y la alta variabilidad de la demanda en el sector funerario, cuya naturaleza estocástica hace inherentemente difícil la predicción precisa a corto plazo.
    
    Las técnicas de data augmentation no mejoraron consistentemente las métricas de los modelos: el bootstrapping temporal degradó el rendimiento de Prophet y ETS al distorsionar la estructura temporal de la serie con ruido gaussiano, y el sliding window benefició a XGBoost y LightGBM en la captura de patrones locales pero a costa de un MAPE superior al 50%. El análisis de reglas de asociación Apriori aportó valor complementario al revelar patrones de contratación conjunta de recursos (Carroza aparece en el 84.7% de los servicios, y su contratación conjunta con Cargadores_4 y Carroza_flores alcanza un soporte del 52.9%), información útil para anticipar necesidades de inventario de forma cualitativa cuando los modelos cuantitativos tienen limitaciones.
    
- **Plataforma web**
    
    El sistema cumplió los requerimientos funcionales definidos en el backlog con todos los ítems marcados como Closed a excepción de HU-009 (alertas de stock crítico) y DO-004 (reporte final de métricas), que quedaron en estado Open al cierre del Sprint 2. El endpoint de predicción cumplió el criterio de respuesta inferior a 5 segundos. El módulo de extracción con Gemini cumplió el criterio operativo de menos de 15 segundos por imagen en producción. La integración con Stripe y DECOLECTA funcionó correctamente en el entorno de producción desplegado, con la limitación de que la API de DECOLECTA opera bajo cuota de plan gratuito con un límite de 24 solicitudes por hora, lo que restringe el uso intensivo de la validación de DNI en escenarios de carga masiva de registros.
    
- **Comparación entre alternativas evaluadas**
    
    En el módulo HTR, Multicentury-HTR superó a los tres modelos alternativos por su entrenamiento original sobre manuscritos históricos complejos, que le otorgó una capacidad previa para interpretar letra ligada que los demás modelos no tienen. TrOCR-Base-ES, pese a estar entrenado en español, colapsó con un CER de 9.09 al no haber sido expuesto a escritura manuscrita durante su preentrenamiento. PARSeq-Multilingual, aunque el más rápido con 467 ms, generó alucinaciones sistemáticas retornando texto inventado sin relación con el contenido de la imagen, lo que lo descarta completamente para extracción de datos críticos. TrOCR-Large-EN ofreció un comportamiento estable pero sesgado al inglés, confundiendo palabras españolas frecuentes en los contratos.
    
    En el módulo predictivo, ETS y LightGBM superaron a los demás modelos sobre datos base porque ambos son robustos ante datasets pequeños: ETS por su naturaleza paramétrica que requiere pocos datos para estimar sus componentes de nivel, tendencia y estacionalidad, y LightGBM por su regularización que evita el sobreajuste en conjuntos reducidos. SARIMA obtuvo los peores R² por la dificultad de identificar correctamente sus parámetros (p,d,q)(P,D,Q) sobre una serie tan corta y ruidosa. LSTM, pese a su capacidad teórica para capturar dependencias temporales largas, quedó penalizado por la escasez de datos, ya que las redes recurrentes requieren volúmenes significativamente mayores para generalizar correctamente.
    
- **Casos de fallo y menor rendimiento**
    
    El módulo HTR falla con mayor frecuencia en campos numéricos con dígitos similares visualmente (1/7, 6/0, 3/8) escritos con caligrafía muy ligada, en contratos con manchas de tinta o deterioro físico del papel, y en campos donde el contratante omitió información dejando la línea en blanco pero con trazos residuales que el modelo interpreta como texto. El campo `contratante_dni` presentó la mayor tasa de error en las pruebas, dado que un único dígito incorrecto invalida el campo completo por la validación de 8 dígitos exactos aplicada en la normalización.
    
    El módulo predictivo tiene menor rendimiento en los meses con demanda atípica alta (picos de fallecimientos por causas estacionales como invierno o epidemias locales), ya que el historial disponible no contiene suficientes eventos de este tipo para que los modelos los capturen como patrón recurrente. La variable monto_total es consistentemente más difícil de predecir que servicios_totales en todos los modelos evaluados, dado que su varianza es significativamente mayor por la diferencia de precio entre tipos de servicio (seguro vs. directo vs. mixto) y por la presencia del outlier extremo de S/ 870,000 que, aunque winsorizado, sigue afectando la distribución del conjunto de entrenamiento.
    

### **SECCIÓN 6 — DISCUSIÓN INTEGRADORA**

**6.1 Respuesta a la pregunta de investigación**

El módulo de extracción demostró que la integración de un modelo VLM (Qwen2.5-VL-3B vía Gemini API) con un pipeline de preprocesamiento de imágenes y normalización determinística permite automatizar la digitalización de contratos manuscritos con un tiempo de procesamiento de 15 segundos por imagen, frente a la digitación manual que consumía aproximadamente 40 horas mensuales del personal administrativo. El modelo fine-tuned Multicentury-HTR alcanzó un Char Accuracy de 0.6660 y un CER de 0.3340, resultado que, aunque no alcanza el umbral del 90% establecido como objetivo, es suficiente para reducir drásticamente el esfuerzo de corrección manual gracias a la interfaz de validación implementada.

El módulo de predicción demostró que es técnicamente viable construir un sistema de pronóstico de demanda sobre el historial digitalizado, pero con limitaciones significativas derivadas del volumen de datos disponibles. El mejor modelo (ETS sobre servicios_totales) obtuvo un MAPE de 34.6% y un R² de 0.252, sin alcanzar el umbral del 20% de MAPE definido en los objetivos. Esta limitación no invalida la contribución del sistema: el análisis de reglas de asociación Apriori identificó patrones de contratación conjunta con soporte superior al 50% que permiten anticipar necesidades de inventario de forma complementaria a los modelos cuantitativos.

En conjunto, la integración de ambos módulos en una plataforma web operativa en producción demuestra que la automatización de la gestión de inventario en el sector funerario es alcanzable con el stack tecnológico implementado, con la condición de que el volumen del historial digitalizado continúe creciendo para mejorar progresivamente la precisión de los modelos predictivos.

**6.2 Contribuciones técnicas verificadas**

- **Contribución 1 — Dataset etiquetado de contratos funerarios manuscritos en español**
    
    Se construyó un dataset de más de 280 imágenes de contratos manuscritos reales del sector funerario peruano, etiquetadas con 24 categorías de campos mediante bounding boxes en Label Studio. Este dataset constituye un recurso de dominio específico no existente previamente, utilizado para el fine-tuning de Multicentury-HTR y la evaluación comparativa de cuatro modelos HTR. Evidencia: reducción del CER de 0.6271 a 0.3340 tras fine-tuning sobre este dataset.
    
- **Contribución 2 — Pipeline de extracción estructurada de contratos manuscritos mediante VLM**
    
    Se implementó un pipeline end-to-end que combina preprocesamiento de imagen (escala de grises, recorte de márgenes, redimensionado, autocontraste, nitidez), inferencia con Qwen2.5-VL-3B mediante prompt especializado con separación semántica de zonas del documento, y normalización determinística post-inferencia para corrección de valores de dominio cerrado. El pipeline opera en producción con 15 segundos de latencia promedio vía Gemini API. Evidencia: sistema desplegado en producción en Vercel y Render, funcional para carga masiva de imágenes con validación de datos.
    
- **Contribución 3 — Comparativa empírica de seis modelos de series temporales sobre historial funerario**
    
    Se realizó la primera evaluación comparativa documentada de SARIMA, Prophet, XGBoost, LightGBM, LSTM y ETS sobre datos reales de demanda de servicios funerarios, bajo tres fuentes de datos distintas (base, bootstrapping temporal y bootstrapping con sliding window), con métricas de MAE, RMSE, R² y MAPE. Evidencia: tablas de resultados completas en la Sección 5.4, con identificación de ETS y LightGBM como los modelos con mejor R² positivo sobre datos base.
    
- **Contribución 4 — Validación estadística del data augmentation mediante Test de Levene**
    
    Se aplicó el Test de Levene para verificar la homocedasticidad entre datos originales y sintéticos generados por SMOTENC, confirmando que 3 de 4 variables preservan la distribución de varianza original y documentando el efecto de variance shrinkage sobre la variable continua Monto_winsorizado. Evidencia: resultados del Test de Levene en la Sección 5.6 con p-values por variable.
    
- **Contribución 5 — Plataforma web integral para la gestión digitalizada de una funeraria**
    
    Se desarrolló e implementó una plataforma web con módulos de extracción IA, predicción de demanda, gestión de inventario, registro de servicios funerarios, procesamiento de pagos con Stripe, validación de identidad con DECOLECTA y control de accesos con roles y permisos dinámicos. Evidencia: sistema desplegado y operativo en producción al cierre del Sprint 2, con 23 de 25 ítems del backlog en estado Closed.
    

**6.3 Limitaciones del trabajo**

- **Volumen insuficiente del historial para predicción confiable:**
    
    El dataset de 340 registros distribuidos en 46 meses es insuficiente para que los modelos de series temporales capturen patrones de estacionalidad anual con robustez estadística. Ningún modelo alcanzó el MAPE objetivo del 20%, y la mayoría obtuvo R² negativo, indicando que el predictor naïve de media histórica supera a los modelos entrenados en varias configuraciones. Esta limitación es estructural y no resoluble mediante cambios de algoritmo sin incrementar el volumen de datos históricos disponibles.
    
- **Precisión del módulo HTR por debajo del umbral objetivo:**
    
    El modelo fine-tuned alcanzó un Char Accuracy de 0.6660, significativamente por debajo del 90% establecido como objetivo en el Project Charter. La variabilidad de la caligrafía manuscrita en los contratos reales, que incluye escritura ligada, deterioro físico del papel y condiciones de iluminación variables, impone un techo de rendimiento que no puede superarse únicamente con fine-tuning sobre el dataset disponible sin un proceso de recolección y etiquetado más extenso.
    
- **Dependencia de servicios externos con restricciones de cuota:**
    
    El sistema de producción depende de la API de Gemini para la extracción de datos (sujeta a límites de cuota y cambios de precio) y de DECOLECTA para la validación de DNI (limitada a 24 solicitudes por hora en el plan gratuito). Ambas dependencias externas introducen riesgos de disponibilidad y costo que no son controlables por el equipo de desarrollo.
    
- **Ausencia de webhook de Stripe en producción:**
    
    La lógica de actualización automática del estado de pago ante confirmaciones asíncronas de Stripe (webhook) no fue implementada completamente en el entorno de producción al cierre del proyecto. Los pagos requieren actualización manual del estado desde la interfaz de administración, lo que representa una brecha operativa en el flujo de pagos mixtos.
    
- **Alcance geográfico y sectorial acotado:**
    
    El sistema fue diseñado y validado exclusivamente sobre los contratos de la Funeraria Máximo Aranzabal de Trujillo, Perú. El modelo de extracción está entrenado sobre la estructura específica de ese formulario y el modelo predictivo sobre los patrones de demanda de ese negocio particular, lo que limita la generalización directa a otras funerarias u otros formatos de contrato sin un proceso de re-etiquetado y fine-tuning específico.
    

**6.4 Amenazas a la validez**

- **Validez interna:**
    
    La principal amenaza a la validez interna es el tamaño reducido del conjunto de evaluación del módulo HTR, con 44 muestras para el fine-tuning y 221 para la comparativa preentrenada. Este volumen introduce alta varianza en las métricas CER y WER, de modo que pequeñas diferencias entre modelos podrían no ser estadísticamente significativas. No se realizó prueba de significancia formal entre los modelos HTR comparados. Para el módulo predictivo, la partición temporal estricta (34 meses entrenamiento / 12 meses prueba) sin validación cruzada limita la capacidad de detectar sobreajuste en modelos como XGBoost y LightGBM.
    
- **Validez externa:**
    
    Los resultados del módulo HTR son válidos únicamente para el formato de contrato de la Funeraria Máximo Aranzabal. La generalización a otros documentos manuscritos del sector funerario o a otros sectores requeriría reentrenamiento con datos del nuevo dominio. Los resultados del módulo predictivo son válidos únicamente para el patrón de demanda de esta funeraria específica, condicionado por factores demográficos y económicos locales de Trujillo que no son transferibles directamente a otras regiones o contextos.
    
- **Validez de constructo:**
    
    El MAPE como métrica principal del módulo predictivo presenta limitaciones cuando la variable objetivo contiene valores cercanos a cero, ya que pequeños errores absolutos generan MAPE desproporcionadamente alto. En el dataset de la funeraria, los meses con uno o dos servicios registrados inflan artificialmente el MAPE de todos los modelos, lo que podría estar subestimando el rendimiento real en meses de demanda normal. El Char Accuracy como métrica del módulo HTR no captura la severidad operativa de los errores: un error en el DNI tiene mayor impacto que un error en el modelo de ataúd, pero ambos se ponderan igual en la métrica.
    
- **Validez estadística:**
    
    La única validación estadística formal aplicada fue el Test de Levene sobre el proceso de data augmentation. No se aplicaron pruebas de significancia estadística para comparar los modelos HTR entre sí ni para comparar los modelos predictivos, lo que limita la capacidad de afirmar con rigor estadístico que las diferencias observadas en las métricas son significativas y no producto de la variabilidad del muestreo.
    

**6.5 Trabajo futuro**

- **Expansión del dataset de entrenamiento HTR con técnicas de data augmentation de imagen:**
    
    El Char Accuracy de 0.6660 puede mejorarse incrementando el volumen del dataset de entrenamiento más allá de las 280 imágenes actuales, aplicando técnicas de augmentation específicas para documentos manuscritos: rotaciones leves, variaciones de brillo y contraste, adición de ruido gaussiano y simulación de degradación de papel. Esto permitiría que el modelo generalice mejor ante las variaciones de caligrafía e iluminación que actualmente generan mayor tasa de error.
    
- **Implementación del webhook de Stripe para actualización automática de estados de pago:**
    
    La integración completa del flujo de pagos requiere configurar un endpoint de webhook en el backend que reciba y procese los eventos `payment_intent.succeeded`, `payment_intent.payment_failed` y `payment_intent.canceled` de Stripe, eliminando la necesidad de actualización manual del estado y habilitando la lógica de pagos parciales acumulativos para la modalidad mixta de forma completamente automatizada.
    
- **Reentrenamiento periódico de los modelos predictivos con datos acumulados:**
    
    A medida que el sistema digitalice nuevos contratos y el historial crezca más allá de los 46 meses actuales, los modelos de series temporales dispondrán de mayor volumen para capturar patrones de estacionalidad anual. Se recomienda establecer un proceso de reentrenamiento trimestral automatizado que incorpore los nuevos registros al dataset de entrenamiento y actualice los modelos serializados en producción, con validación automática de las métricas antes de reemplazar el modelo activo.
    
- **Generalización del sistema a otras funerarias mediante transferencia de dominio:**
    
    El pipeline de extracción puede adaptarse a otros formatos de contrato funerario mediante un proceso de re-etiquetado mínimo en Label Studio y fine-tuning incremental sobre el nuevo formato, reutilizando los pesos del modelo actual como punto de partida. Esto abriría la posibilidad de ofrecer el sistema como solución replicable para otras funerarias de la región con estructuras de contrato similares.
    
- **Integración de la API oficial de RENIEC:**
    
    Una vez que el proyecto cuente con personería jurídica formal, la sustitución de DECOLECTA por la API oficial de RENIEC eliminaría las restricciones de cuota del plan gratuito actual y garantizaría mayor disponibilidad y precisión en la validación de identidad de fallecidos y contratantes.
    

### **SECCIÓN 7 — CONCLUSIONES**

El presente trabajo desarrolló una plataforma web integral que automatiza la gestión de inventario de una empresa de servicios funerarios mediante dos componentes de inteligencia artificial: un módulo de reconocimiento de escritura manuscrita para la digitalización de contratos físicos y un módulo de predicción de demanda basado en series temporales para la reposición inteligente de stock.

El módulo de extracción, basado en el modelo Qwen2.5-VL-3B servido mediante la API de Gemini con un pipeline de preprocesamiento de imagen y normalización post-inferencia, opera en producción con una latencia de 15 segundos por contrato, frente a las 40 horas mensuales de digitación manual que demandaba el proceso anterior, representando una reducción del tiempo de digitalización superior al 95%. El modelo fine-tuned Multicentury-HTR, entrenado sobre 280 imágenes etiquetadas del dominio, alcanzó un CER de 0.3340 y un Char Accuracy de 0.6660 tras 10 épocas de entrenamiento, sin alcanzar el umbral del 90% establecido como objetivo pero proporcionando una base funcional complementada por la interfaz de validación manual implementada en la plataforma.

El módulo de predicción evaluó seis modelos de series temporales (SARIMA, Prophet, XGBoost, LightGBM, LSTM y ETS) sobre 46 meses de historial de servicios bajo tres estrategias de data augmentation. El mejor resultado obtenido fue ETS con MAPE de 34.6% y R² de 0.252 sobre la variable servicios_totales en el dataset base, sin alcanzar el umbral del 20% de MAPE definido en los objetivos debido al volumen reducido del historial disponible. El análisis complementario de reglas de asociación Apriori identificó patrones de contratación conjunta con soporte superior al 84% para recursos como carroza y cargadores, aportando inteligencia de negocio cualitativa para la gestión del inventario.
La plataforma web desplegada en producción (Angular en Vercel, FastAPI en Render, PostgreSQL en Digital Ocean) integra además módulos de gestión de servicios funerarios, control de inventario con borrado lógico, procesamiento de pagos con Stripe, validación de identidad con la API DECOLECTA y un sistema de roles y permisos dinámicos, cerrando el Sprint 2 con 23 de 25 ítems del backlog en estado Closed.

El impacto potencial del sistema en el dominio funerario local es significativo: la eliminación del proceso manual de digitación reduce el riesgo de errores en datos personales y económicos de los contratos, la disponibilidad de historial digitalizado y estructurado habilita por primera vez la toma de decisiones basada en datos para la reposición de inventario, y la integración con Stripe formaliza el registro y seguimiento de pagos que anteriormente se gestionaban de forma completamente manual. A medida que el historial digitalizado crezca, la precisión de los modelos predictivos mejorará progresivamente, consolidando el sistema como una herramienta de inteligencia operativa para el negocio.
El código fuente del proyecto está disponible en los repositorios de GitHub del equipo de desarrollo, con el backend en Python/FastAPI y el frontend en Angular documentados mediante Swagger y manual de usuario respectivamente, garantizando la reproducibilidad técnica de la solución implementada.

### **SECCIÓN 8 — REFERENCIAS**

- A comprehensive and comparative study of handwriting recognition system. (2023). *IEEE Access*. https://ieeexplore.ieee.org/document/10236301
- Advancing optical character recognition for handwritten text: Enhancing efficiency and streamlining document management. (2023). *Proceedings of the 2023 14th International Conference on Computing Communication and Networking Technologies*. IEEE. https://doi.org/10.1109/ICCCNT56998.2023.10307143
- Alshahrani, A., & Al-Amri, A. (2024). An end-to-end approach for handwriting recognition. En *2024 International Conference on Artificial Intelligence and Smart Systems (ICAISS)* (pp. 412–417). IEEE. https://doi.org/10.1109/ICAISS61165.2024.10678189
- Bai, S., Chen, K., Liu, X., Wang, J., Ge, W., Song, S., Dang, K., Wang, P., Wang, S., Tang, J., Zhong, H., Zhu, Y., Yang, M., Li, Z., Wan, J., Wang, P., Ding, W., Fu, Z., Xu, Y., . . . Lin, J. (2025, 19 febrero). *QWen2.5-VL Technical Report*. arXiv.org. https://doi.org/10.48550/arXiv.2502.13923
- Bandara, K., Bergmeir, C., & Smyl, S. (2021). Forecasting across time series databases with global and local deep learning models. International Journal of Forecasting, 37(3), 1428–1447. https://doi.org/10.1016/j.ijforecast.2020.10.005
- Chen, J., Xu, L., & Sun, K. (2023). An integrated web platform combining OCR/HTR extraction and time-series forecasting for small business inventory management. ACM Transactions on Management Information Systems, 14(2), Article 9. https://doi.org/10.1145/3581234
- Fan, L., Song, Z., Mao, W., Tiejun, L., Wang, W., Yang, K., & Cao, F. (2024). Change is safer: A dynamic safety stock model for inventory management of large manufacturing enterprise based on intermittent time series forecasting. *Journal of Intelligent Manufacturing*. https://doi.org/10.1007/s10845-024-02442-y
- Gupta, R. (29 de noviembre de 2021). *Data Augmentation for Time Series Application*. Water Programming: A Collaborative Research Blog. https://waterprogramming.wpcomstaging.com/2021/11/29/data-augmentation-for-time-series-application/
- Handwritten Kazakh and Russian (HKR) database for text recognition. (2021). *Neural Computing and Applications*. https://doi.org/10.1007/s11042-021-11399-6
- Heartex. (2023). *Label Studio Documentation*. https://labelstud.io/guide/
- IBM. (s.f.). *Apriori de Oracle*. IBM Documentation. https://www.ibm.com/docs/es/spss-modeler/saas?topic=mining-oracle-apriori
- Kumar, P., Singh, D., & Rao, S. (2024). Handwritten text recognition from image using LSTM integrated with pixel shifting optimization algorithm. *Proceedings of the 2024 International Conference on Advancement in Renewable Energy and Intelligent Systems (AREIS)*. IEEE. https://doi.org/10.1109/AREIS62559.2024.10893651
- Kumar, R., & Li, H. (2021). End-to-end deep learning approach for offline handwritten document transcription in low-resource settings. Pattern Recognition Letters, 150, 162–170. https://doi.org/10.1016/j.patrec.2021.06.012
- Khan, M. A., Ali, S., & Iqbal, M. (2024). Benchmarking performance analysis of optical character recognition engines on clinical reports. *Proceedings of the 2024 26th International Multi-Topic Conference (INMIC)*. IEEE. https://doi.org/10.1109/INMIC64792.2024.11004392
- Li, M., Lv, T., Chen, J., Cui, L., Lu, Y., Florencio, D., Zhang, C., Li, Z., & Wei, F. (2021). TrOCR: Transformer-based optical character recognition with pre-trained models. *arXiv preprint arXiv:2109.10282v5*. https://doi.org/10.48550/arXiv.2109.10282
- Li, Y., Chen, D., Tang, T., & Shen, X. (2025). HTR-VT: Handwritten text recognition with vision transformer. *Pattern Recognition, 157*, 110857.https://www.sciencedirect.com/science/article/abs/pii/S0031320324007180
- Nunes, M., Santos, N., & Silva, J. (2023). Modern web architectures: Evaluating performance and scalability of FastAPI and PostgreSQL in three-tier systems. *Journal of Software Engineering and Applications*, *16*(4), 112-128. https://doi.org/10.4236/jsea.2023.164006
- Rahman, T., Ahmed, F., & Hossain, M. (2024). Efficient data extraction from handwritten forms: A structured pipeline solution. *Proceedings of the 2024 2nd International Conference on Artificial Intelligence Trends and Pattern Recognition (ICAITPR)*. IEEE. https://doi.org/10.1109/ICAITPR63242.2024.10959837
- Sánchez, G., Pérez, J., & Ramos, L. (2022). Handwritten text recognition for inventory forms using convolutional recurrent neural networks. IEEE Access, 10, 75432–75444. https://doi.org/10.1109/ACCESS.2022.3187654
- Y. Fan, "Professional English Text Recognition Based on Long Short Term Memory Approach," *2024 International Conference on Data Science and Network Security (ICDSNS)*, Tiptur, India, 2024, pp. 1-4, doi: 10.1109/ICDSNS62112.2024.10691174.
- Zhao, Y., Wang, X., & Fernández, M. (2020). Deep learning for demand forecasting in retail supply chains: A comparative study. European Journal of Operational Research, 283(3), 1038–1051. https://doi.org/10.1016/j.ejor.2020.05.012

### **SECCIÓN 9 — ANEXOS TÉCNICOS *(obligatorios)***

| Anexo | Contenido |
| --- | --- |
| A | Diagrama de arquitectura completo en alta resolución |
| B | Especificación completa de la API (endpoints, parámetros, respuestas) |
| C | Diccionario de datos / esquema de base de datos |
| D | Manual de instalación y reproducibilidad  |
| E | Dataset o enlace de acceso con descripción |
| F | Resultados completos de pruebas (incluyendo los negativos) |
| G | Consentimiento informado si hubo participantes humanos |
- **ANEXO A: Diagrama de arquitectura completo en alta resolución**
    
    !ATAÚDES and CAPILLAS-2026-07-07-072204.png
    
- **ANEXO B: Especificación completa de la API (endpoints, parámetros, respuestas)**
    - Back: https://funeraria-inventario-inteligente-wv7g.onrender.com/docs
    - Modelo: https://cgi-amber-yet-shelter.trycloudflare.com/docs
- **ANEXO C: Diccionario de datos / esquema de base de datos**
    
    ## Dataset — Funeraria Máximo Aranzabal: Registro Histórico de Servicios Funerarios
    
    **Versión:** 1.0.0 (2026)
    
    **Autor:** Prieto Meléndez Alexander Antonio, Vidal Rodríguez Fabrizio
    
    ---
    
    ### About Dataset
    
    Este dataset contiene el registro histórico digitalizado de servicios funerarios de la Funeraria Máximo Aranzabal, ubicada en Trujillo, Perú. Los datos fueron extraídos manualmente a partir de contratos físicos manuscritos mediante el módulo de extracción de inteligencia artificial desarrollado en el proyecto, con revisión y corrección manual posterior para garantizar la integridad de cada registro. El dataset fue construido con el propósito de entrenar y evaluar modelos de predicción de demanda de inventario (ataúdes, capillas y vehículos) y constituye el primer conjunto de datos estructurado disponible del sector funerario peruano con este nivel de detalle operativo.
    
    ---
    
    ### Content
    
    El dataset contiene **340 registros** de servicios funerarios registrados entre **mayo de 2022 y febrero de 2026**, cubriendo **46 meses** de operación continua de la funeraria. Cada registro corresponde a un contrato de servicio funerario individual e incluye datos del contratante, del fallecido, de los recursos utilizados y del monto total del servicio.
    
    El archivo se distribuye en formato `.xlsx` con una única hoja de datos y encabezados en la primera fila. Cada fila representa un servicio funerario único identificado por su número de contrato.
    
    **Columnas del dataset:**
    
    | Columna | Tipo | Descripción |
    | --- | --- | --- |
    | `n_contrato` | String | Número de contrato único del servicio funerario (ej. 000202) |
    | `fecha` | Date | Fecha de celebración del contrato en formato YYYY-MM-DD |
    | `contratante_nombre` | String | Nombre completo del contratante en mayúsculas |
    | `contratante_dni` | String | Número de DNI del contratante (8 dígitos) |
    | `contratante_telefono` | String | Número de teléfono del contratante (solo dígitos) |
    | `direccion_velacion` | String | Dirección del lugar de velación indicada en el contrato |
    | `fallecido_nombre` | String | Nombre completo del fallecido en mayúsculas |
    | `velatorio` | String | Lugar de velatorio (ej. SU CASA, nombre de capilla) |
    | `forma_pago` | String | Modalidad de pago: directo, seguro o mixto |
    | `ataud_modelo` | String | Modelo del ataúd contratado (ej. COPA CON ADORNOS, LINCOLN) |
    | `ataud_color` | String | Color del ataúd si está especificado en el contrato |
    | `capilla_modelo` | String | Modelo de capilla ardiente contratada (ej. ILUMINADA MODELO MILAN) |
    | `carroza` | Integer | Indicador binario de presencia de carroza porta ataúd (0/1) |
    | `carroza_flores` | Integer | Indicador binario de presencia de carroza porta flores (0/1) |
    | `cargadores` | Integer | Número de cargadores contratados (valores: 4 o 6) |
    | `vehiculos` | String | Descripción de vehículos adicionales contratados (microbus, autos para deudos) |
    | `monto_total` | Float | Monto total del servicio en soles peruanos (S/) |
    | `notas_extra` | String | Observaciones adicionales registradas en el contrato (ej. acuerdos de pago parcial) |
    
    ---
    
    ### Dataset Properties
    
    | Propiedad | Valor |
    | --- | --- |
    | Total de registros | 340 |
    | Número de columnas | 18 |
    | Formato | .xlsx (Microsoft Excel) |
    | Cobertura temporal | Mayo 2022 – Febrero 2026 |
    | Frecuencia | Registro por servicio (irregular) |
    | Idioma de los datos | Español |
    | País de origen | Perú |
    | Sector | Servicios funerarios |
    | Valores nulos tratados | Sí (imputación y normalización aplicada) |
    | Outliers tratados | Sí (winsorización al percentil 99, umbral S/ 154,600) |
    
    ---
    
    ### Estadísticas Descriptivas
    
    | Variable | Valores únicos | Observaciones |
    | --- | --- | --- |
    | `forma_pago` | 3 | directo, seguro, mixto — 340 valores normalizados |
    | `ataud_modelo` | - | 338 valores normalizados tras limpieza de variantes ortográficas |
    | `ataud_color` | - | 301 valores normalizados |
    | `capilla_modelo` | - | 314 valores normalizados |
    | `carroza` | 2 | Binario: 0 o 1 |
    | `carroza_flores` | 2 | Binario: 0 o 1 |
    | `cargadores` | 2 | 4 o 6 cargadores |
    | `monto_total` | — | Rango: S/ 0 – S/ 870,000 (outlier extremo winsorizado a S/ 154,600) |
    | Registros con fecha imputada | 42 | Fechas faltantes reconstruidas por continuidad temporal |
    | Lagunas temporales detectadas | 6 | Meses sin registros en la serie histórica |
    | Outliers en monto | 19 (5.59%) | Detectados por método IQR y tratados por winsorización |
    | Integridad de datos final | 97.94% | Tras aplicar el pipeline completo de preprocesamiento |
- **ANEXO D: Manual de instalación y reproducibilidad**
    
    Manual de Instalación y Reproducibilidad
    
- **ANEXO E: Dataset o enlace de acceso con descripción**
    
    **Google Drive - Datos en crudo y Etiquetados:** https://drive.google.com/drive/folders/1MlczECvdiw4yebJjiTITwm0jEXgb47WW?usp=sharing
    
- **ANEXO F: Resultados completos de pruebas (incluyendo los negativos)**
    - Pruebas de Funcionales
        
        Pruebas G11.xlsx
        
    - Pruebas unitarias
        
        Pruebas unitarias
        
    - Pruebas de caja negra
        
        Pruebas de caja negra
        
    - Pruebas End to End
        
        Pruebas End-to-End (E2E)
        
    - Pruebas de integración
        
        **Plan de Pruebas de Integración - Frontend**
        
        **Plan de Pruebas de Integración - Backend**
        

**ANEXO G: Consentimiento informado si hubo participantes humanos**

### **📋 Checklist**

Antes de entregar, el estudiante autoevalúa con esta rúbrica:

| Criterio | Insuficiente (0) | Aceptable (1) | Sólido (2) |
| --- | --- | --- | --- |
| Problema con evidencia cuantitativa | Descripción vaga | Datos citados sin fuente primaria | Datos con fuente y análisis |
| Gap tecnológico explícito | No identificado | Mencionado vagamente | Tabla comparativa con literatura |
| Arquitectura documentada | Solo descripción | Diagrama básico | Diagrama + ADRs justificados |
| Stack justificado técnicamente | Solo listado | Con razones generales | Comparativa con alternativas |
| Métricas apropiadas al tipo de solución | Métricas genéricas | 2–3 métricas estándar | ≥4 métricas con justificación estadística |
| Comparación con estado del arte | Ausente | 1 trabajo comparado | Tabla ≥5 trabajos con análisis |
| Análisis estadístico | Ausente | Solo medias | Test de significancia + p-value |
| Reproducibilidad | Sin código ni datos | Código parcial | Repositorio + instrucciones completas |
| Referencias Q1 (≥60%) | <40% | 40–60% | >60% |
| Limitaciones y amenazas | Ausentes | Superficiales | Detalladas y honestas |