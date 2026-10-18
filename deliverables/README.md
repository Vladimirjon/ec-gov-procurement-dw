# deliverables/

Versiones finales de los entregables calificados, tal como se suben al
curso. El contenido se escribe y revisa antes en `docs/` (ver
[PLAN.md](../docs/PLAN.md#cómo-se-producen-los-entregables)).

## Organización

```
deliverables/
├─ plantilla/       # plantilla-entregable.docx: documento base con el encabezado del curso
├─ fase0/
├─ fase1/
├─ fase2/
├─ fase3/
├─ fase4/
├─ fase5/
└─ final/           # presentación y documento final
```

## Encabezado obligatorio

Todos los entregables comienzan con:

```
Título: <título exacto del entregable>
Equipo #: <número>
Nombres: <integrantes>
Fecha: <fecha de entrega>
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

En `fase0/` se conserva, además del PDF final, el Word editable desde el que
se exporta.

## Reglas

- Aquí no se guardan datos reales ni datasets.
- Un archivo final solo entra por PR aprobado por el líder.
