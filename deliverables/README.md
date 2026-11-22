# deliverables/

Versiones finales de los entregables de los seis hitos, tal como se suben al
aula virtual. El contenido se escribe y revisa antes en `docs/`; aquí solo
entra el archivo final.

**Vigencia:** el formato, el nombre y el contenido de cada entrega los fijan los
PDF del profesor (ver [PLAN.md](../docs/PLAN.md)). Si este archivo y un PDF
del profesor difieren, manda el PDF. Los hitos 1, 2 y 3 tienen guía detallada;
los demás se completan cuando el profesor la publique.

## Organización

```
deliverables/
├─ plantilla/       # plantilla-entregable.docx: base opcional del equipo
├─ h1/              # Perfil institucional y preguntas de negocio
├─ h2/              # Adquisición y calidad de datos
├─ h3/              # Modelo dimensional y presentación de avance
├─ h4/              # ETL e implementación del DW
├─ h5/              # Analítica OLAP, tablero y modelo analítico
└─ h6/              # Presentación final y defensa
```

## Qué pide cada hito

| Hito | Entregable según el profesor | Archivo |
|---|---|---|
| H1 | Documento con el perfil del sector y la matriz de 3 preguntas, máx. 6 páginas sin anexos. Al inicio: nombre del equipo, sector y fecha | `Hito1_Apellido1Apellido2ApellidoN.pdf` |
| H2 | `.pbix` con las fuentes conectadas y un libro de Excel (o Word/PDF) con Fuentes, Diccionario, Calidad y Cobertura. Vence el 21/11/2026 | `Proyecto_Grupo5_Hito2.pbix` y `h2/Proyecto_Grupo5_Hito2.xlsx` |
| H3 | `.pbix` con el modelo dimensional, documento de diseño en PDF (máx. 8 páginas sin anexos) y diapositivas en PDF; presentación de 10 min + 5 de preguntas. Vence el 22/11/2026 | `Proyecto_Grupo5_Hito3.pbix`, `h3/Proyecto_Grupo5_Hito3_Diseno.pdf` y `h3/Proyecto_Grupo5_Hito3_Presentacion.pdf` |
| H4 | Scripts ETL, carga inicial e incremental, bitácora de cargas y reporte de reconciliación | **[PENDIENTE]** guía del profesor |
| H5 | Consultas OLAP, tablero `.pbix`, notebook del modelo analítico y resumen de 1 página | **[PENDIENTE]** guía del profesor |
| H6 | Repositorio final, `.pbix`, informe técnico de 1 página, presentación de 20 min y coevaluación | **[PENDIENTE]** guía del profesor |

La columna «Entregable» resume la guía general del proyecto (sección 7). No
reemplaza la guía detallada de cada hito.

## Nombre del archivo del Hito 1

`Hito1_` seguido de los apellidos de los integrantes pegados, en orden
alfabético: `Hito1_BravoFreireGuajanPasquelTorres.pdf`. La guía general del
Hito 1 menciona también el nombre `Proyecto_EquipoX_Hito1` en su paso 10; se usa
el de la ficha del hito, que es la instrucción de formato de entrega.

## Word y PDF del Hito 1

`h1/Hito1_BravoFreireGuajanPasquelTorres.docx` es el documento que revisó y
retocó el líder en Word, y `h1/Hito1_BravoFreireGuajanPasquelTorres.pdf` es su
conversión, 6 páginas (perfil 3, cuerpo 4 con la Parte 2, anexos A, B y C). El
Word se generó primero desde `docs/requirements/hito1.md` con
`python -I scripts/build_hito1_docx.py` (solo biblioteca estándar, sin Word); el
Markdown quedó alineado con el texto final. Regenerar sobrescribe los retoques
hechos a mano en el Word, así que se hace solo si el Markdown cambia y se vuelve
a revisar el resultado. El script falla si queda una marca [VERIFICAR] o
[PENDIENTE] y no mide las páginas: se cuentan abriendo el Word.

## Archivos de los hitos 2 y 3

La guía escribe `Proyecto_EquipoX_Hito2` y `Proyecto_EquipoX_Hito3` sin definir
`X`: el profesor asignó al equipo el nombre **Grupo 5**, así que son
`Proyecto_Grupo5_Hito2` y `Proyecto_Grupo5_Hito3`. Las entregas vencen a las
23:59 del 21/11 (H2) y del 22/11 (H3). Los `.pbix` **sí se versionan** (decisión
del líder, ADR 0005): entran aquí por PR, y como GitHub rechaza archivos de más
de 100 MB se mide su tamaño antes de commitear y, si pasa de unos 50 MB, se
consulta al líder. Llevan datos embebidos (solo las columnas necesarias, nunca
datos de personas). Aquí entran también el libro de Excel de H2 y los PDF de H3,
cuando el líder los apruebe por PR. Las consultas M y los runbooks que producen
el modelo viven en `reports/powerbi/` y `docs/h2/`, `docs/h3/`.

### Libro de Excel del Hito 2

`h2/Proyecto_Grupo5_Hito2.xlsx` es el libro de cuatro partes (Fuentes, Diccionario,
Calidad y Cobertura, precedidas de la Portada institucional) generado desde los
archivos de contenido `docs/h2/fuentes.csv`, `diccionario.csv`, `calidad.csv` y
`cobertura.csv` con `python -I scripts/build_hito2_xlsx.py`.

- **Regeneración:** regenerar el libro sobrescribe cualquier retoque de formato hecho
  a mano en Excel; si se modifican los CSV o el script, se vuelve a generar y a revisar.
- **Apertura y verificación:** un entorno automatizado no puede abrir Excel; la apertura
  limpia y sin reparación la confirma el líder al abrir el archivo en Excel Desktop.
- **Plan B:** si por cualquier motivo el archivo `.xlsx` requiriese reparación en una
  versión específica de Excel, el plan de respaldo consiste en importar a un libro nuevo
  de Excel los cuatro archivos CSV fuente (`docs/h2/fuentes.csv`, `diccionario.csv`,
  `calidad.csv` y `cobertura.csv`), darles formato tabular a mano y añadir la portada.

## Plantilla opcional

`plantilla/plantilla-entregable.docx` es una base en APA 7 con el encabezado
del curso anterior (Título, Equipo #, Nombres, Fecha). El profesor **no exige
APA**: exige citar cada fuente con enlace y fecha de consulta. Úsala solo si
ayuda; en el Hito 1 el encabezado debe llevar el nombre del equipo, el sector
y la fecha, y la plantilla hay que adaptarlo. **[PENDIENTE]** decidir si se
conserva o se reemplaza cuando haya más hitos con guía.

## Reglas

- Aquí no se guardan datos reales ni datasets, salvo los datos embebidos en un
  `.pbix` entregable (ver arriba).
- Un archivo final solo entra por PR aprobado por el líder.
- El uso de IA se declara en el informe del hito que lo pida (qué se pidió y
  cómo se verificó), según la guía general del proyecto.
