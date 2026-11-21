# Diagnóstico de calidad de datos de SERCOP (2021-2025)

**Fecha:** 21 de noviembre de 2026  
**Autor:** Integrante 4 (Calidad de datos)  
**Equipo:** Grupo 5  
**Hito:** Hito 2 — Perfilado de calidad de fuentes (Issue #62)  
**Entrada:** CSV descargados del portal oficial de SERCOP (`data/derivados/sercop-portal-csv-AAAA-<sello>/`), procesados bajo la **Ruta A** aprobada en [ADR 0005](../adr/0005-hitos-2-y-3-power-bi.md) y [Decisión Formato y Conexión](decision-formato-conexion.md).  
**Script generador:** `scripts/profile_h2_quality.py`  
**SHA-256 LF del script:** `19F8F2FA96AAAC657335B261D8FE29451787470CCCE400BF83119D8DDAD75608`  
**Evidencia reproducible:**  
- `docs/h2/evidencia/perfil-calidad-sercop-2021-v2.json` a `perfil-calidad-sercop-2025-v2.json`  
- `docs/h2/evidencia/perfil-calidad-sercop-resumen-v2.csv`  
- `docs/h2/evidencia/perfil-calidad-sercop-por-comprador-v2.csv`  

---

## 1. Resumen ejecutivo

Este diagnóstico presenta el perfilado cuantitativo de calidad de la contratación pública de SERCOP (2021–2025) a lo largo de las **seis dimensiones de calidad** exigidas por la guía académica (Completitud, Conformidad, Consistencia, Precisión, Unicidad y Temporalidad).

Se procesaron en streaming los cinco años de datos del portal de SERCOP, cubriendo **1.007.920 procesos** (`ocid` únicos en `releases` y `tender`) y **867.755 adjudicaciones** (`awards`), totalizando un importe estimado en convocatorias de **USD 67.873,43 millones** y un importe adjudicado de **USD 39.529,08 millones**.

### Hallazgos clave y su impacto en H2 y H3
1. **Unicidad de clave primaria de proceso garantizada (Q-06):** Hay exactamente 1 fila de `tender` por cada `ocid` en `releases` (cero duplicados de `ocid`), lo que garantiza la relación 1:1 entre convocatoria y proceso.
2. **Multiplicidad de adjudicaciones por proceso identificada (Q-11):** Se identificaron 10.827 pares `(ocid, release_id)` adicionales en `awards` correspondientes a procesos con múltiples lotes o ítems adjudicados. Cada fila tiene su propio identificador único de adjudicación; en H3 deben agregarse a nivel de proceso (`Table.Group` con `List.Sum([amount])`) antes de combinar con `tender` para no inflar métricas en hechos de proceso.
3. **Completitud y unicidad del identificador del comprador (Q-01):** El RUC del comprador (`buyer_id`) tiene 100 % de completitud en `releases` (0 nulos), 100 % de conformidad estructural (13 dígitos numéricos) y coincide exactamente con `tender.procuringEntity_id`. Esto asegura la unión sin pérdida con el catálogo de entidades públicas de la función ejecutiva.
4. **Fechas de negocio y cobertura temporal (Q-03):** La fecha `tenderPeriod_startDate` alcanza 99,88 % de completitud y `releases.date` tiene 100 %, mientras que `awards.date` solo está presente en el 13 % al 23 % de los procesos. Por tanto, para el Hito 3 se recomienda utilizar `tenderPeriod_startDate` como fecha primaria de proceso y `releases.date` como sustituto determinista ante nulos.
5. **Codificación de caracteres (Q-05):** El archivo `tender_2021.csv` contiene bytes en Windows-1252 (ANSI) no válidos en UTF-8 estricto. La importación en Power Query debe realizarse especificando la página de códigos 1252 (`Encoding=1252`).
6. **Brecha con informe oficial de SERCOP 2025 (Q-09):** La suma de adjudicaciones transaccionales en 2025 alcanza USD 6.223,59 millones frente a los USD 7.318,70 millones del informe oficial institucional de SERCOP, arrojando una diferencia no explicada de USD 1.095,11 millones (14,96 %). Se documenta el contexto transaccional y se plantean hipótesis de agregación institucional sin calificar causas de forma infundada.

---

## 2. Totales de control por año y periodo (2021-2025)

Las siguientes métricas fueron calculadas por el script `profile_h2_quality.py` procesando directamente los CSV de `data/derivados/`:

| Métrica de control | 2021 | 2022 | 2023 | 2024 | 2025 | Total 2021-2025 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Filas en `releases`** | 167.058 | 212.324 | 217.913 | 219.185 | 191.440 | **1.007.920** |
| **`ocid` únicos en `releases`** | 167.058 | 212.324 | 217.913 | 219.185 | 191.440 | **1.007.920** |
| **Filas en `tender`** | 167.058 | 212.324 | 217.913 | 219.185 | 191.440 | **1.007.920** |
| **Filas en `awards`** | 145.452 | 185.127 | 179.805 | 172.659 | 184.712 | **867.755** |
| **Filas en `contracts`** | 108.973 | 143.080 | 141.011 | 134.502 | 143.078 | **670.644** |
| **Suma estimada `tender.value_amount` (M USD)** | 11.233,48 | 13.914,02 | 14.542,56 | 13.565,96 | 14.617,42 | **67.873,43** |
| **Suma adjudicada `awards.amount` (M USD)** | 6.702,96 | 9.076,64 | 8.847,15 | 8.678,74 | 6.223,59 | **39.529,08** |
| **Procesos con adjudicación (`ocid` en awards)** | 142.735 | 182.680 | 178.030 | 170.385 | 183.098 | **856.928** |
| **Procesos con estimado y adjudicación** | 142.735 | 182.680 | 178.030 | 170.385 | 183.098 | **856.928** |
| **Procesos con estimado pero sin adjudicación** | 24.323 | 29.644 | 39.883 | 48.800 | 8.342 | **150.992** |
| **Procesos con adjudicación sin estimado** | 0 | 0 | 0 | 0 | 0 | **0** |
| **Pares duplicados en awards `(ocid, release_id)`** | 2.717 | 2.447 | 1.775 | 2.274 | 1.614 | **10.827** |
| **Pares duplicados en contracts `(ocid, release_id)`** | 2.378 | 2.113 | 1.547 | 1.960 | 1.360 | **9.358** |

*Nota:* Los conteos de releases coinciden exactamente con los totales observados y registrados en [docs/h2/adquisicion.md](adquisicion.md).

---

## 3. Matriz de hallazgos por dimensión de calidad (Plantilla H2 §6.3)

| ID | Dimensión | Tabla / Campo | Descripción del problema | Evidencia cuantitativa | Impacto en Power BI / DW | Acción en H3 (Limpieza / Transformación) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Q-01** | Completitud / Conformidad | `releases.buyer_id`, `tender.procuringEntity_id` | Identificador de la entidad compradora | 100 % de completitud en `releases` (0 nulos de 1.007.920). 100 % cumple formato RUC (13 dígitos numéricos). | Alto positivo: permite enlazar compras con el catálogo oficial de entidades del PGE sin pérdidas. | En Power Query, usar `buyer_id` como clave de búsqueda hacia `Dim_Entidad`. |
| **Q-02** | Completitud | `tender.value_amount`, `awards.amount` | Importes nulos o vacíos en convocatoria y adjudicación | `value_amount`: 0 nulos (100 % completo). `awards.amount`: solo 5 nulos en 2025 (0,0027 % en 2025, 0,0006 % total); 0 en 2021–2024. | Bajo: 5 adjudicaciones carecen de monto en 2025. | Reemplazar nulos en `awards.amount` por `0.0` o mantener bandera `flag_monto_nulo` en H3. |
| **Q-03** | Completitud / Temporalidad | Fechas del proceso: `tender.tenderPeriod_startDate`, `releases.date`, `awards.date`, `contracts.dateSigned` | Cobertura dispar de fechas para asociar al calendario | `tenderPeriod_startDate`: 99,88 % completo (1.205 nulos total). `releases.date`: 100 % completo. `awards.date`: solo presente en el 13 % al 23 % de los procesos. `contracts.dateSigned`: presente en ~66 % de procesos. | Crítico: usar `awards.date` como fecha del hecho `Fact_Proceso` dejaría fuera al 77 %–87 % de los procesos en los gráficos temporales. | En Power Query crear columna calculada `fecha_proceso`: `if [tenderPeriod_startDate] <> null then [tenderPeriod_startDate] else [date]`. |
| **Q-04** | Validez | `awards.amount`, `tender.value_amount` | Importes iguales o menores a cero | `awards.amount <= 0`: 1.258 en 2021, 1.340 en 2022, 1.258 en 2023, 1.488 en 2024, 1.034 en 2025 (Total: 6.378 filas, 0,73 % de awards). `value_amount <= 0`: 6.671 procesos (0,66 %). | Medio: procesos declarados en cero o adjudicaciones simbólicas distorsionan promedios. | Filtrar o categorizar con columna condicional en Power Query (`tipo_monto`: 'Normal', 'Cero'). |
| **Q-05** | Conformidad | Codificación de caracteres en `tender_2021.csv` | Caracteres no compatibles con UTF-8 estricto en descripciones y nombres | 380 filas con saltos de línea y presencia de secuencias Windows-1252 (ej. tildes y eñes ANSI). | Alto: rompe la carga en Power Query si se asume UTF-8 estricto sin tolerancia. | En Power Query, usar `Csv.Document(File.Contents(...), [Encoding=1252])` o importar especificando página de códigos 1252. |
| **Q-06** | Unicidad | `releases.ocid`, `tender.ocid` | Unicidad del identificador primario de proceso | 1.007.920 filas en `releases` con 1.007.920 `ocid` únicos. Exactamente 1 fila de `tender` por cada `ocid`. Cero duplicados de clave primaria de proceso. | Alto positivo: garantiza relación 1:1 estricta entre convocatoria y proceso. | Usar `ocid` como clave primaria de la tabla lógica `Procesos_SERCOP` en Power Query. |
| **Q-07** | Consistencia | `awards.amount` vs `tender.value_amount` | Importe adjudicado supera al importe referencial estimado | 7.971 procesos presentan monto adjudicado superior al referencial en 2021–2025 (0,93 % de procesos con adjudicación). | Medio: normal en subastas inversas o ampliaciones de ítem, pero requiere trazabilidad. | Crear columna calculada `flag_adjudicado_mayor_estimado` para auditoría y visualización. |
| **Q-08** | Consistencia | `tender.procuringEntity_id` vs Catálogo PGE | Entidades compradoras que no pertenecen a la Función Ejecutiva | Del total de 1.007.920 procesos, solo una fracción corresponde al Gobierno Central (Presidencia, Ministerios, Institutos); el resto pertenece a GADs, empresas públicas y otras funciones. | Crítico para el alcance: el proyecto delimita estrictamente Función Ejecutiva (ADR 0001). | Filtrar procesos en Power Query mediante combinación interna (`inner join`) con `Dim_Entidad`. |
| **Q-09** | Precisión | Suma de adjudicaciones 2025 vs Informe Oficial SERCOP | Brecha no explicada de USD 1.095,11 millones (14,96 %) entre datos transaccionales del portal y cifra institucional reportada | En datos: USD 6.223,59 M. Cifra oficial reportada: USD 7.318,70 M. Brecha sin explicar: USD 1.095,11 M. | Alto documental: debe revelarse explícitamente en el Hito 2 para transparencia analítica. | Documentar la brecha como no explicada a nivel transaccional y presentar factores de contexto como hipótesis (inferencia). |
| **Q-10** | Temporalidad | Distribución de años en fechas registradas | Presencia de fechas fuera del periodo esperado (fechas históricas o 2026) | En 2025: 4.376 adjudicaciones registradas con fecha en 2026. Fechas anteriores a 2015 en menos del 0,05 % de registros. | Medio: procesos convocados en 2025 con adjudicación o firma perfeccionada en 2026. | Mantener las fechas reales para análisis de ciclo de vida del proceso en `Dim_Tiempo`. |
| **Q-11** | Unicidad / Consistencia | `awards.(ocid, release_id)` | Múltiples adjudicaciones por proceso (lotes/ítems) | 10.827 pares `(ocid, release_id)` adicionales en `awards` (2.717 en 2021, 2.447 en 2022, 1.775 en 2023, 2.274 en 2024, 1.614 en 2025). | Crítico: un merge directo de `awards` con `tender` multiplicaría filas y distorsionaría montos a nivel proceso. | En Power Query, pre-agrupar `awards` por `ocid` sumando `amount` antes de consolidar `Fact_Proceso`, o modelar `Fact_Adjudicacion` a grano de adjudicación con clave `id`. |

---

## 4. Análisis detallado de las fechas de negocio (Decisión para H3)

El perfilado midió la completitud y distribución de las cuatro fechas presentes en los CSV de SERCOP para responder a la decisión de diseño dimensional ([ADR 0004](../adr/0004-modelo-dimensional.md)):

| Fecha evaluada | Tabla de origen | Completitud global | Ventajas | Limitaciones | Recomendación H3 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `tenderPeriod_startDate` | `tender` | **99,88 %** | Refleja el inicio real del proceso de contratación pública. | 1.205 procesos (0,12 %) carecen de este valor. | **Fecha primaria recomendada.** |
| `date` | `releases` | **100,00 %** | Siempre presente en todos los registros. | Representa la fecha de publicación del paquete OCDS, no necesariamente el evento de compra. | **Sustituto determinista (`fallback`)** cuando `tenderPeriod_startDate` sea nula. |
| `date` | `awards` | **13 % a 23 %** (de procesos) | Refleja la fecha formal del acta de adjudicación. | No aplica a procesos desiertos, cancelados o sin adjudicar (ausente en >77 % de procesos). | Uso restringido a la tabla de hechos a grano de adjudicación (`Fact_Adjudicacion`). |
| `dateSigned` | `contracts` | **~66 %** (de procesos) | Refleja el perfeccionamiento legal del contrato. | Ausente en procesos sin contrato formalizado o en fase precontractual. | Métrica de análisis de desfase temporal (tiempo entre convocatoria y contrato). |

---

## 5. Comparación de totales de control con Hito 1

Al comparar los datos del portal actualizados con el reconocimiento preliminar del Hito 1:

| Concepto | Año | Total Hito 1 | Total Hito 2 (Actual) | Diferencia | Explicación |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Releases totales** | 2021 | 167.058 | 167.058 | 0 | Coincidencia exacta confirmada. |
| **Releases totales** | 2022 | 212.324 | 212.324 | 0 | Coincidencia exacta confirmada. |
| **Releases totales** | 2023 | 217.913 | 217.913 | 0 | Coincidencia exacta confirmada. |
| **Releases totales** | 2024 | 219.185 | 219.185 | 0 | Coincidencia exacta confirmada. |
| **Releases totales** | 2025 | 191.440 | 191.440 | 0 | Coincidencia exacta confirmada. |
| **Filas de awards** | 2025 | 183.891 | 184.712 | +821 | Crecimiento de 821 adjudicaciones publicadas por SERCOP entre el corte preliminar de H1 y la descarga oficial analizada. |

---

## 6. Diagnóstico de la brecha de exactitud en 2025 (USD 1.095,11 millones)

En el ejercicio 2025, la cifra de adjudicación oficial reportada en el informe de gestión de SERCOP es de **USD 7.318,70 millones**. La suma obtenida a partir de las 184.712 filas del archivo transaccional `awards_2025.csv` es de **USD 6.223,59 millones**.

Esto arroja una **brecha sin explicar de USD 1.095,11 millones** (`unexplained_difference_usd`: USD 1.095,11 M, representativa del 14,96 % de la cifra institucional).

### Contexto transaccional medido en los datos:
- Existen **5 adjudicaciones con importe nulo o vacío** en 2025.
- Existen **32.244 adjudicaciones cuyo estado (`status`) no es activo** (`unsuccessful`, `cancelled`, etc.).
- Existen **4.376 adjudicaciones registradas en el archivo de 2025 con fecha de adjudicación en 2026** (procesos continuados).

### Hipótesis sobre la brecha (Inferencia sin fuente oficial):
Se plantea como hipótesis que el informe anual institucional de SERCOP podría agregar procedimientos especiales que no se publican bajo el estándar OCDS abierto, tales como adquisiciones de empresas públicas estratégicas, compras de emergencia con reserva, régimen especial de seguridad o ajustes presupuestarios posteriores. Al no disponerse de la metodología de agregación del informe oficial, la diferencia se declara formalmente como **sin explicar** a nivel transaccional.

---

## 7. Alcance y cobertura de anomalías de la fuente

- **Ruta A (CSV del Portal):** Este diagnóstico se basó íntegramente en los CSV generados por el portal oficial de SERCOP, conforme a lo establecido en la [Decisión de Formato y Conexión](decision-formato-conexion.md).
- **Anomalías de JSON no aplicables al CSV:** Las anomalías estructurales detectadas en las descargas JSON crudas (por ejemplo, `contracts` publicado como objeto singular en lugar de arreglo en un release de 2024, y un paquete OCDS con lista vacía de releases en 2023) corresponden a defectos de serialización del JSON crudo documentados en [docs/h2/adquisicion.md](adquisicion.md). En la exportación a CSV del portal, la plataforma SERCOP aplanó estas estructuras, por lo que dichas anomalías no están presentes en los archivos de datos analizados.

---

## 8. Pasos de reproducción

Para reproducir exactamente los archivos de evidencia y las tablas de este diagnóstico:

```powershell
python -I scripts/profile_h2_quality.py `
  --derived-dir "c:\Users\johan\Desktop\UNI\7 Semestre\Business Intelligence\ec-gov-procurement-dw\data\derivados" `
  --output-dir "c:\Users\johan\Desktop\UNI\7 Semestre\Business Intelligence\ec-gov-procurement-dw\docs\h2\evidencia" `
  --output-suffix=-v2 `
  --years 2021 2022 2023 2024 2025 `
  --reference-awarded-2025 7318.7
```
