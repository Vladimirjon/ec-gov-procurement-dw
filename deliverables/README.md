# deliverables/

Versiones finales de los entregables calificados, tal como se suben al
curso. El contenido se escribe y revisa antes en `docs/` (ver
[PLAN.md](../docs/PLAN.md#cómo-se-producen-los-entregables)).

## Organización

```
deliverables/
├─ plantilla/       # plantilla-entregable.docx: base en APA 7 con el encabezado del curso
├─ fase0/
├─ fase1/
├─ fase2/
├─ fase3/
├─ fase4/
├─ fase5/
└─ final/           # presentación y documento final
```

## Cómo usar la plantilla

1. Copia `plantilla/plantilla-entregable.docx`; no la edites en su sitio.
2. Rellena el encabezado del curso (ver abajo).
3. Escribe el contenido con los estilos de la plantilla: Título 1 a 3, Normal,
   listas, Tabla entregable, Referencia. No cambies fuentes ni sangrías a mano.
4. Borra el contenido de ejemplo y la página de guía, que viene marcada para
   borrar, y conserva el encabezado.
5. Revisa el límite de páginas de la entrega, exporta a PDF desde Word y
   guarda el archivo con el nombre que indica la sección siguiente.

La página de guía de la propia plantilla repite estas indicaciones y el formato
con ejemplos. Si algo difiere, manda este archivo. Las entregas F1-E2 y F2-E2
usan la plantilla que da el curso, con el mismo encabezado.

## Formato (APA 7)

La plantilla aplica la séptima edición de las normas APA, en español:

| Elemento | Norma aplicada |
|---|---|
| Página y letra | A4, márgenes de 2,54 cm, Times New Roman de 12 puntos. |
| Interlineado | Sencillo y sin espacio entre párrafos. Ajuste del equipo: APA pide doble, pero las entregas tienen de 1 a 3 páginas. Si una entrega no tiene límite de páginas, se cambia a doble. |
| Alineación y sangría | Texto justificado (ajuste del equipo; APA recomienda alinear a la izquierda). Sangría de primera línea de 1,27 cm. |
| Número de página | Arriba a la derecha. |
| Títulos | Nivel 1 centrado y en negrita; nivel 2 a la izquierda y en negrita; nivel 3 a la izquierda, en negrita y cursiva. Solo la primera palabra lleva mayúscula inicial. |
| Tablas y figuras | Epígrafe encima: «Tabla 1» o «Figura 1» en negrita y, en la línea siguiente, el título en cursiva. Debajo, la línea «Nota.» con la fuente. Las tablas llevan solo líneas horizontales. |
| Citas | Autor y año en el texto: (Kimball y Ross, 2013); sin fecha, (s. f.). Cada cita tiene su entrada en la sección Referencias. |
| Referencias | Orden alfabético por el primer autor, con sangría francesa y el título de la obra en cursiva. |
| Números | Coma decimal y punto para los miles (190.619; 15,33 %). |

## Encabezado obligatorio

Todos los entregables comienzan con:

```
Título: <título exacto del entregable>
Equipo #: <número>
Nombres: <nombre y apellido de cada integrante>
Fecha: <dd/mm/aa>
```

## Nombre de archivo

`<Apellidos>.<sufijo>.<extensión>`, donde `<Apellidos>` son los apellidos
de los integrantes separados por puntos, siempre en el mismo orden, y el
sufijo es el que pide el curso para cada entrega:

| Entrega | Sufijo y extensión |
|---|---|
| E0 · Contextualización | `.E1.pdf` |
| F1-E1 · Requerimientos | `.E1.pdf` |
| F1-E2 · Guía de Diseño Inicial | `.E2.pdf` |
| F2-E1 · Modelo en Estrella | `.E3.pdf` |
| F2-E2 · Diccionario de Datos | `.E3.doc` |
| F3-E1 · Diseño Físico | `.E1.pdf` + script `.sql` |
| F3-E2 · Proceso ETL | `.E2.pdf` + notebook `.ipynb` |
| F3-E3 · Flujo ETL | `.E3.pdf` |
| F4 · Carga y pruebas | `.DW.zip` |
| F5 · Dashboard | `.DashDW.zip` |
| Presentación | `.Pre.PDF` |
| Documento final | `.PDW.PDF` |

**Orden de los apellidos (decidido el 17/10/2026):** alfabético por apellido,
es decir `Bravo.Freire.Guajan.Pasquel.Torres`. En «Nombres» se escribe nombre y
apellido en el mismo orden, separados por comas y con «y» antes del último.
La fecha del encabezado va como `dd/mm/aa`, porque la fecha de entrega puede
cambiar.

**Tamaño del equipo:** el enunciado de los entregables pide equipos de 3
integrantes y el equipo es de 5 ([PLAN.md](../docs/PLAN.md#4-equipo)). Los
cinco figuran en «Nombres» y en el nombre del archivo.

**[PENDIENTE]** Número de equipo, y si la composición de 5 se mantiene en los
entregables o se declara de otra forma. Lo decide el líder.

En `fase0/` está el Word editable de E0, desde el que se exporta. El PDF final
se agrega por PR cuando el líder lo integre **[PENDIENTE]**.

## Reglas

- Aquí no se guardan datos reales ni datasets.
- Un archivo final solo entra por PR aprobado por el líder.
