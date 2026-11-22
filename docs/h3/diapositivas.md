# Diapositivas | Hito 3

## 1. Grupo 5: USD 5.511,80 millones adjudicados
- Gobierno central del Ecuador
- Hito 3 - Modelo dimensional y presentación de avance
- Francis Bravo, Ismael Freire, Harry Guajan, Johann Pasquel y Jorge Torres | 22/11/26
- **Apoya a:** P1
- **Visual:** cifra principal, tomada de `pagina-prueba.png` (total de la tarjeta y matriz).
- **Bloque y tiempo:** Sector y preguntas | 1:00

## 2. Tres preguntas, tres decisiones
- P1: evolución del monto adjudicado por método, año y tipo de entidad
- P2: desviación entre monto adjudicado y estimado por método y entidad
- P3: monto mensual esperado para el primer semestre de 2026
- **Apoya a:** P1/P2/P3
- **Visual:** esquema de preguntas y decisores, basado en `docs/requirements/hito1.md`; no requiere captura.
- **Bloque y tiempo:** Sector y preguntas | 1:00

## 3. De la fuente al diagnóstico
- Descargas abiertas de contratación pública, estructura OCDS
- 1.007.920 procesos nacionales; 993.425 dentro de 2021–2025
- H2 diagnostica: USD 30.952,88 millones adjudicados en el total nacional
- **Apoya a:** P1/P2/P3
- **Visual:** flujo fuente → diagnóstico H2 → modelo H3, con cifras de `docs/h2/calidad.csv` y `controles-esperados.csv`.
- **Bloque y tiempo:** Datos y calidad | 1:00

## 4. Calidad y límites de cobertura
- 14.495 procesos de 2026 quedan fuera de la ventana
- 9.495 procesos de institutos dudosos, USD 128,24 millones, excluidos y contabilizados
- H2 documenta faltantes, duplicados, monedas y cobertura antes de transformar
- **Apoya a:** P1/P2/P3
- **Visual:** tabla de ventana y exclusiones; cifras de `semilla-entidades.md`, `controles-esperados.csv` y `docs/h2/calidad.csv`.
- **Bloque y tiempo:** Datos y calidad | 1:00

## 5. Un hecho, tres dimensiones
- Grano: un proceso `ocid` aprobado del sector, por fecha del proceso
- `FactContratacion`: monto adjudicado, estimado y conteos aditivos
- `DimTiempo`, `DimEntidad` y `DimMetodo`
- **Apoya a:** P1/P2/P3
- **Visual:** captura `modelo.png`, vista de modelo de Power BI.
- **Bloque y tiempo:** Modelo dimensional | 1:00

## 6. Decisiones que protegen la medida
- Adjudicaciones múltiples se suman por proceso antes de relacionar
- Importes faltantes permanecen vacíos, no se convierten en cero
- Tres relaciones 1 a varios, con filtro en una dirección
- **Apoya a:** P1/P2
- **Visual:** diagrama `modelo.png`; las reglas de agregación y nulidad salen de `diseno-dimensional.md` y `runbook-modelo.md`.
- **Bloque y tiempo:** Modelo dimensional | 1:00

## 7. Conciliación del sector
- 275.100 procesos en el hecho; 0 institutos incorporados
- USD 5.511,80 millones en Power BI, conciliados con Python por año
- 14.495 procesos de 2026 quedan fuera del periodo analizado
- **Apoya a:** P1/P2/P3
- **Visual:** tabla de controles del modelo y captura `pagina-prueba.png`; filas y total salen de controles confirmados en Power BI el 22/11/26.
- **Bloque y tiempo:** Modelo dimensional | 1:00

## 8. Prueba interactiva: monto por procedimiento y año
- Medida: Monto adjudicado
- Filas: procedimiento; columnas: año
- Total de la página: USD 5.511.799.162,58
- **Apoya a:** P1
- **Visual:** captura `pagina-prueba.png`, página de prueba en Power BI Desktop.
- **Bloque y tiempo:** Demostración en Power BI | 1:00

## 9. Lectura de la prueba
- El monto cambia por procedimiento y año
- El total coincide con el cálculo independiente anual en Python
- La prueba describe el periodo; no es el pronóstico de P3
- **Apoya a:** P1/P3
- **Visual:** interacción en Power BI; respaldo visual `pagina-prueba.png`.
- **Bloque y tiempo:** Demostración en Power BI | 1:00

## 10. Recomendación: cerrar cobertura y validar P3
- Ratificar o resolver casos dudosos de entidades antes de ampliar el indicador
- Construir y validar el pronóstico mensual P3 con la ventana temporal definida
- Documentar límites y mantener controles de conciliación por año
- **Apoya a:** P1/P2/P3
- **Visual:** ruta de próximos pasos basada en `semilla-entidades.md`, `diseno-dimensional.md` y `docs/requirements/hito1.md`.
- **Bloque y tiempo:** Próximos pasos | 1:00
