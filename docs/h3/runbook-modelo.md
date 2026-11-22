# Modelo en Power BI: relaciones, claves ocultas y página de prueba

Pasos 8 a 10 de la guía del Hito 3, ejecutados por el líder en Power BI Desktop el 22/11/2026 sobre `H3MD-BravoFreireGuajanPasquelTorres.pbix` (el archivo no se versiona; se entrega por el aula virtual). Las consultas M se construyen antes con [runbook-transformaciones.md](runbook-transformaciones.md) y [runbook-construccion.md](runbook-construccion.md). Este documento registra lo que se hizo, el resultado observado y los desvíos reales.

## 1. Carga del modelo

1. En **Transformar datos** solo cuatro consultas tienen **Habilitar carga** activado: `DimTiempo`, `DimEntidad`, `DimMetodo` y `FactContratacion`. Las intermedias (`Procesos_SERCOP`, `Licitaciones_SERCOP`, `Adjudicaciones_SERCOP`, `Semilla_Entidades`, `Origen_Modelo`, `ControlAlcance`) y las consultas auxiliares de control quedan sin carga (guía, paso 8).
2. **Cerrar y aplicar**.

Resultado observado (22/11/2026), igual al esperado de `evidencia/modelo-esperado.csv`:

| Tabla | Filas observadas | Filas esperadas |
|---|---:|---:|
| `FactContratacion` | 275.100 | 275.100 |
| `DimTiempo` | 60 | 60 |
| `DimEntidad` | 587 | 587 |
| `DimMetodo` | 28 | 28 |

### Desvíos reales de la carga

- La primera versión de las consultas no terminó de cargar en más de 40 minutos. Causas: las guardas de control volvían a leer los CSV, la clasificación se hacía fila por fila sobre 1.007.920 procesos y los importes se combinaban con todo el conjunto nacional. Corrección (misma lógica y mismos totales): `Table.Buffer` antes de las guardas, clasificación sobre los compradores distintos con una sola combinación hacia los procesos, e importes combinados solo con los 275.100 procesos del alcance.
- Power BI limitaba cada evaluación a 432 MB. Se ajustó en **Archivo > Opciones y configuración > Opciones > Global > Carga de datos**: 2 evaluaciones simultáneas y 7.000 MB por evaluación. El cambio solo surte efecto tras **reiniciar Power BI Desktop**. Con ambos cambios la carga terminó.
- Con la vista previa en segundo plano desactivada, el Editor muestra `?` o un aviso «Preview refresh was canceled» al cambiar de consulta; no es un error y no afecta a la carga.

## 2. Relaciones (guía, paso 9)

En la vista de **Modelo** se borran las relaciones detectadas automáticamente y se crean tres, cada una **uno a varios (1:\*)** desde la dimensión hacia el hecho, con **dirección de filtro única**:

| Desde (lado 1) | Hacia (lado varios) |
|---|---|
| `DimTiempo[IdTiempo]` | `FactContratacion[IdTiempo]` |
| `DimEntidad[IdEntidad]` | `FactContratacion[IdEntidad]` |
| `DimMetodo[IdMetodo]` | `FactContratacion[IdMetodo]` |

No hay relaciones de varios a varios, bidireccionales ni inactivas. Cada clave de dimensión es única (las guardas de las consultas lo comprueban y la carga se detiene si no).

## 3. Claves ocultas y descripciones

- **Ocultar en la vista de informe**: `IdTiempo`, `IdEntidad` e `IdMetodo` en el hecho y en su dimensión, y `RucRaiz` en `DimEntidad` (guía, paso 10).
- Descripción de cada tabla (panel **Propiedades**), con su grano según el diseño dimensional:
  - `FactContratacion`: «Un proceso de contratación (ocid) del gobierno central con fecha entre enero de 2021 y diciembre de 2025».
  - `DimTiempo`: «Un mes, de enero de 2021 a diciembre de 2025».
  - `DimEntidad`: «Una entidad compradora por raíz de RUC».
  - `DimMetodo`: «Un método y procedimiento de contratación».

## 4. Medida y página de prueba

Medida simple en `FactContratacion` (las tasas y la desviación porcentual quedan para el segundo bimestre):

```DAX
Monto adjudicado = SUM(FactContratacion[MontoAdjudicado])
```

Página «Prueba del modelo»:

- **Matriz**: filas `DimMetodo[Procedimiento]`, columnas `DimTiempo[Anio]`, valores `Monto adjudicado`. Responde parcialmente P1 (cómo se reparte el monto adjudicado del gobierno central por procedimiento y año).
- **Tarjeta**: `Monto adjudicado`.

Resultado observado, comparado con el grupo `control_alcance` («En el hecho») de `evidencia/modelo-esperado.csv`:

| Año | Power BI (USD) | Esperado, Python (USD) |
|---|---:|---:|
| 2021 | 463.293.502,34 | 463.293.502,34 |
| 2022 | 986.513.949,66 | 986.513.949,66 |
| 2023 | 1.519.235.226,34 | 1.519.235.226,34 |
| 2024 | 1.307.798.881,05 | 1.307.798.881,05 |
| 2025 | 1.234.957.603,19 | 1.234.957.603,19 |
| Total | 5.511.799.162,58 | 5.511.799.162,58 |

Sin diferencias. La tarjeta muestra el total abreviado («5,51bn»).

## 5. Capturas

En [evidencia/capturas/](evidencia/capturas/):

- `modelo.png`: vista de modelo con las cuatro tablas, las tres relaciones 1:\* y las claves ocultas.
- `pagina-prueba.png`: matriz procedimiento × año y tarjeta del total.

## 6. Parámetros y rutas

Las consultas M versionadas no contienen rutas absolutas: solo usan los parámetros `RutaDerivados` y `RutaSemillas` (comprobación estática de los `.pq` el 22/11/2026). No se exige la prueba de actualización en otra carpeta (decisión del líder, 21/11/2026).
