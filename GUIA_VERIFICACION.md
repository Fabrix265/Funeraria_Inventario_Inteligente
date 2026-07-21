# Guía de Verificación: Excel vs Imágenes Raw

## Objetivo
Verificar que los datos del Excel `Dataset_crudo.xlsx` coincidan con las imágenes raw de contratos escaneados en `data/raw/`.

## Archivos involucrados
| Archivo | Ubicación |
|---------|-----------|
| Excel a verificar | `Dataset_crudo.xlsx` (raíz del proyecto) |
| Imágenes raw | `data/raw/0.png` a `data/raw/339.png` |

## Mapeo Excel ↔ Imagen
```
Fila 1 del Excel (Nro 000301) → data/raw/0.png
Fila 2 del Excel (Nro 000302) → data/raw/1.png
Fila 3 del Excel (Nro 000305) → data/raw/2.png
...
Fila N del Excel → data/raw/(N-1).png
```

## Columnas a actualizar en el Excel

| Columna | Letra | Valores posibles |
|---------|-------|------------------|
| Estado | T | "Completo" / "Incompleto" |
| Revisado | U | "SI" / "NO" |

## Criterios de Estado

| Estado | Condición |
|--------|-----------|
| **Completo** | Todos los campos tienen datos válidos y legibles en la imagen |
| **Incompleto** | Hay campos vacíos, ilegibles o con valor "Vacío" en la imagen |

## Campos clave a verificar
1. **Fecha**
2. **Ataud_Modelo**
3. **Ataud_Color**
4. **Capilla**
5. **Monto**

## Proceso por lote

1. Abrir imagen raw correspondiente a la fila
2. Leer visualmente los 5 campos clave
3. Comparar contra el valor del Excel
4. **Si hay diferencia:** Corregir el Excel directamente con el valor correcto de la imagen
5. **Si campo vacío/ilegible:** Marcar Estado como "Incompleto"
6. **Si todo OK:** Marcar Estado como "Completo"
7. Marcar Revisado como "SI"
8. Guardar progreso
9. Continuar con siguiente imagen

## Distribución de lotes (15 imágenes c/u)

| Lote | Filas Excel | Imágenes |
|------|-------------|----------|
| 1 | 1-15 | 0.png - 14.png |
| 2 | 16-30 | 15.png - 29.png |
| 3 | 31-45 | 30.png - 44.png |
| 4 | 46-60 | 45.png - 59.png |
| 5 | 61-75 | 60.png - 74.png |
| 6 | 76-90 | 75.png - 89.png |
| 7 | 91-105 | 90.png - 104.png |
| 8 | 106-120 | 105.png - 119.png |
| 9 | 121-135 | 120.png - 134.png |
| 10 | 136-150 | 135.png - 149.png |
| 11 | 151-165 | 150.png - 164.png |
| 12 | 166-180 | 165.png - 179.png |
| 13 | 181-195 | 180.png - 194.png |
| 14 | 196-210 | 195.png - 209.png |
| 15 | 211-225 | 210.png - 224.png |
| 16 | 226-240 | 225.png - 239.png |
| 17 | 241-255 | 240.png - 254.png |
| 18 | 256-270 | 255.png - 269.png |
| 19 | 271-285 | 270.png - 284.png |
| 20 | 286-300 | 285.png - 299.png |
| 21 | 301-315 | 300.png - 314.png |
| 22 | 316-330 | 315.png - 329.png |
| 23 | 331-340 | 330.png - 339.png |

## Ejemplo de ejecución

```
Fila 1: Nro 000301
├── Abrir: data/raw/0.png
├── Leer: fecha=24/07/2025, ataud_modelo=LINCOLN BIBLIA, ataud_color=Vacío, capilla=ILUMINADA, monto=4500
├── Excel dice: fecha=24/07/2025, ataud_modelo=LINCOLN BIBLIA, ataud_color=Vacío, capilla=ILUMINADA, monto=4500
├── Resultado: Todo coincide → Estado = "Completo"
└── Revisado = "SI"
```

## Notas importantes
- El Excel tiene 340 filas con datos (filas 2-341)
- Hay 659 filas vacías que se ignoran
- Si la imagen está completamente vacía → Estado = "Incompleto"
- Si un campo es ilegible → Estado = "Incompleto"
- Las correcciones se hacen directamente en el Excel (no en un archivo separado)
