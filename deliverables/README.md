# deliverables/

Versiones finales de los entregables de los seis hitos, tal como se suben al
aula virtual. El contenido se escribe y revisa antes en `docs/`; aquí solo
entra el archivo final.

**Vigencia:** el formato, el nombre y el contenido de cada entrega los fijan los
PDF del profesor (ver [PLAN.md](../docs/PLAN.md)). Si este archivo y un PDF
del profesor difieren, manda el PDF. Hoy solo el Hito 1 tiene guía detallada;
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
| H2 | Datos crudos o su script, esquema `stg`, diccionario en Excel, notebook de perfilado e informe de calidad | **[PENDIENTE]** guía del profesor |
| H3 | Matriz de bus, diagrama de la estrella, DDL del esquema `dw` y presentación de 10 minutos | **[PENDIENTE]** guía del profesor |
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

## Plantilla opcional

`plantilla/plantilla-entregable.docx` es una base en APA 7 con el encabezado
del curso anterior (Título, Equipo #, Nombres, Fecha). El profesor **no exige
APA**: exige citar cada fuente con enlace y fecha de consulta. Úsala solo si
ayuda; en el Hito 1 el encabezado debe llevar el nombre del equipo, el sector
y la fecha, y la plantilla hay que adaptarlo. **[PENDIENTE]** decidir si se
conserva o se reemplaza cuando haya más hitos con guía.

## Reglas

- Aquí no se guardan datos reales ni datasets.
- Un archivo final solo entra por PR aprobado por el líder.
- El uso de IA se declara en el informe del hito que lo pida (qué se pidió y
  cómo se verificó), según la guía general del proyecto.
