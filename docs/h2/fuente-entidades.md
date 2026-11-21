# Evaluación de la segunda fuente: catálogo de entidades y llave de cruce con SERCOP

Documento de adquisición, perfilado y medición de cruce para la dimensión Entidad conforme a la guía del Hito 2 (secciones 4.2 a 4.5), el [ADR 0001](../adr/0001-alcance.md) y el Issue #61.

---

## 1. Inventario y fichas de procedencia

### 1.1. Fuente principal integrable: Catálogo institucional del MDEP / e-SIGEF

| Atributo | Detalle |
|---|---|
| **Entidad emisora** | Ministerio de Economía y Finanzas (MEF) / Ministerio de Desarrollo Económico y Productivo (MDEP) — Subsecretaría de Presupuesto, Dirección Nacional de Consistencia Presupuestaria. |
| **Nombre oficial** | Catálogo de Instituciones y Entidades Operativas Desconcentradas del Sector Público Activas. |
| **Enlace exacto de descarga** | `https://www.economicoproductivo.gob.ec/wp-content/plugins/download-monitor/download.php?id=18691` |
| **Formato y tipo de archivo** | Hoja de cálculo OpenXML (`.xlsx`), hoja única titulada `CATÁLOGO`. |
| **Periodo y fecha de corte** | Fotografía estática del sector público activa declarada al **31 de agosto de 2026** (fila 4 del archivo). |
| **Frecuencia de actualización** | Anual / semestral según ciclo presupuestario del Presupuesto General del Estado (PGE). |
| **Licencia de uso** | No declarada de forma explícita en el archivo ni en el portal. Publicación oficial para fines de transparencia y directrices presupuestarias. |
| **Fecha y hora de descarga** | 21 de noviembre de 2026, 15:31:36 (hora local de Ecuador, UTC-5). |
| **Estado HTTP y bytes** | HTTP 200 OK; 202.353 bytes recibidos (`Content-Length: 202353`). |
| **Hash SHA-256** | `6A7AD388D0B1B4D4C71C7BD82BDB78C4A43B24E84EF8C1E6584DE0662E88AEAA` |
| **Ubicación local en crudos** | `data/datos_crudos/mdep-catalogo-instituciones-20261121-153131/catalogo_instituciones_mdep.xlsx` (marcado como de solo lectura, con `headers.txt` preservado sin cookies). |
| **Registro de evidencia** | `docs/h2/evidencia/descargas-entidades.csv`. |

### 1.2. Fuente nominal de contraste: Directorio de instituciones `gob.ec`

| Atributo | Detalle |
|---|---|
| **Entidad emisora** | Ministerio de Telecomunicaciones y de la Sociedad de la Información (MINTEL) — Subsecretaría de Gobierno Electrónico y Registro Civil. |
| **Nombre oficial** | Directorio de Instituciones del Portal Único de Trámites Ciudadanos (`gob.ec`). |
| **Enlaces descargados** | Directorio general (`https://www.gob.ec/instituciones`), sección P (`/P`), sección M (`/M`), sección I (`/I`), sección V (`/V`), sección S (`/S`). |
| **Formato** | Páginas web HTML con renderizado dinámico Drupal. |
| **Periodo y vigencia** | Directorio continuo vigente en noviembre de 2026. Mezcla instituciones activas e históricas sin declarar RUC ni códigos de e-SIGEF. |
| **Licencia de uso** | Sin licencia explícita. Se utiliza como fuente base nominal para el descubrimiento de candidatos y contraste de denominaciones institucionales. |
| **Condiciones de descarga** | Descarga secuencial con intervalo mínimo de 3,0 segundos entre peticiones, conforme a `robots.txt` (que autoriza explícitamente `/instituciones`). |
| **Ubicación local en crudos** | Carpetas individuales bajo `data/datos_crudos/gob-ec-instituciones-*-20261121-*/` (archivos marcados como solo lectura, cabeceras sin cookies). |

---

## 2. Grano, estructura y perfilado del catálogo MDEP

El perfilado se ejecutó mediante lectura directa de los flujos XML internos del archivo `.xlsx` (`zipfile` + `xml.etree.ElementTree`, biblioteca estándar de Python) a través del script `scripts/profile_entity_catalog.py`, produciendo la evidencia agregada en `docs/h2/evidencia/perfil-entidades.json`.

### 2.1. Grano de la tabla
- **Definición del grano:** Una fila = una Entidad Operativa Desconcentrada (EOD) habilitada de una institución pública activa del Presupuesto General del Estado al 31 de agosto de 2026.
- **Clave primaria natural:** La combinación `(ENTIDAD, EOD)`. El campo `RUC` **no es clave primaria** de la tabla, ya que existen instituciones con múltiples EODs que comparten el mismo número de identificación tributaria (hallazgo Q-E02).

### 2.2. Estructura física y metadatos no tabulares
- **Total de filas en la hoja:** 3.154 filas físicas.
- **Filas de metadatos superiores (filas 1 a 5):**
  - Fila 1: `SUBSECRETARÍA DE PRESUPUESTO`
  - Fila 2: `DIRECCION NACIONAL DE CONSISTENCIA PRESUPUESTARIA`
  - Fila 3: `CATÁLOGO DE INSTITUCIONES Y ENTIDADES OPERATIVAS DESCONCENTRADAS DEL SECTOR PÚBLICO ACTIVAS`
  - Fila 4: `(Actualizado al 31 de Agosto de 2026)`
  - Fila 5: En blanco.
- **Fila de encabezado (fila 6):** 9 columnas:
  - `A`: `SECTOR` (código numérico presupuestario)
  - `B`: `DESCRIPCION SECTOR` (texto del clasificador institucional)
  - `C`: `ENTIDAD` (código de la institución matriz en e-SIGEF)
  - `D`: `EOD` (código de la Entidad Operativa Desconcentrada: `0` para matriz/UDAF, `>0` para desconcentradas)
  - `E`: `NOMBRE` (denominación de la entidad o EOD)
  - `F`: `RUC` (identificador tributario de 13 dígitos)
  - `G`: `PROVINCIA` (código geográfico presupuestario de provincia)
  - `H`: `CANTÓN` (código geográfico presupuestario de cantón)
  - `I`: `OBSERVACIONES` (campo de texto libre para notas)
- **Rango de registros de datos:** Filas 7 a 3146 (**3.140 registros de datos activos**).
- **Filas de pie de página (filas 3147 a 3154):** 8 filas de notas explicativas de e-SIGEF (donde RUC y sector vienen vacíos). La nota 1 confirma explícitamente: *"Hasta la presente fecha existen 3.140 entidades habilitadas dentro del catálogo"*.

### 2.3. Completitud por columna en los 3.140 registros de datos

| Campo | Letra | Tipo observado | Registros poblados | Registros vacíos | % Vacíos | Rol dimensional |
|---|:---:|---|:---:|:---:|:---:|---|
| **SECTOR** | A | Numérico (texto) | 3.140 | 0 | 0,00 % | Atributo / filtro sectorial |
| **DESCRIPCION SECTOR** | B | Texto | 3.140 | 0 | 0,00 % | Atributo de clasificación |
| **ENTIDAD** | C | Numérico (código) | 3.140 | 0 | 0,00 % | Clave de institución matriz |
| **EOD** | D | Numérico (código) | 3.140 | 0 | 0,00 % | Clave de unidad desconcentrada |
| **NOMBRE** | E | Texto | 3.140 | 0 | 0,00 % | Atributo descriptivo |
| **RUC** | F | Numérico / Texto | 3.140 | 0 | 0,00 % | Clave natural de cruce |
| **PROVINCIA** | G | Numérico (código) | 3.140 | 0 | 0,00 % | Atributo geográfico |
| **CANTÓN** | H | Numérico (código) | 3.140 | 0 | 0,00 % | Atributo geográfico |
| **OBSERVACIONES** | I | Texto | 541 | 2.599 | 82,77 % | Nota técnica complementaria |

**Hallazgo de completitud:** En las columnas estructurales A a H no existe **ningún valor vacío** dentro de las 3.140 filas de datos.

### 2.4. Análisis del formato y unicidad del RUC
- **Total de valores RUC en registros de datos:** 3.140 (100 % no nulos).
- **Truncamiento de ceros a la izquierda (hallazgo Q-E01):**
  - **1.874 registros (59,68 %)** presentan 13 caracteres.
  - **1.266 registros (40,32 %)** presentan 12 caracteres. Esto ocurre porque las entidades situadas en provincias con códigos `01` a `09` (Azuay, Bolívar, Cañar, Carchi, Cotopaxi, Chimborazo, El Oro, Esmeraldas, Guayas) inician con `0`, pero Excel almacenó el valor como numérico suprimiendo el cero inicial.
  - Al aplicar relleno con ceros a la izquierda (`zfill(13)` / `Text.PadStart`), el **100 % (3.140)** de los registros adquieren 13 dígitos numéricos válidos y el **100 % terminan en `001`**.
- **Unicidad del RUC (hallazgo Q-E02):**
  - Existen **3.080 RUCs normalizados distintos**.
  - **60 valores de RUC están duplicados**, afectando a **120 filas** (cada uno aparece 2 veces).
  - *Causa técnica:* Entidades con múltiples EODs distritales comparten el RUC de la entidad matriz, y carteras en proceso de fusión (p. ej. MDEP Entidad 130 y MAG Entidad 360) registran direcciones distritales paralelas con el mismo RUC tributario.
- **Entidades con múltiples filas (EODs):**
  - Existen **603 códigos distintos de ENTIDAD**.
  - 332 entidades tienen fila única (solo planta central/matriz).
  - 271 entidades tienen múltiples filas por desconcentración operativa (el caso máximo es la Entidad 998 con 825 filas, correspondiente a unidades de distritos y circuitos desconcentrados).

### 2.5. Distribución por sector presupuestario

| Código | Descripción del sector en catálogo | Filas | % Filas | Entidades matrices | RUCs distintos | Alcance según ADR 0001 |
|:---:|---|:---:|:---:|:---:|:---:|---|
| **111** | ADMINISTRACION DEL ESTADO | 990 | 31,53 % | 114 | 930 | **Sector candidato (Gobierno Central)** + Otras funciones |
| **123** | GAD PARROQUIALES | 866 | 27,58 % | 1 | 866 | Fuera de alcance (GAD) |
| **122** | GAD MUNICIPALES | 700 | 22,29 % | 222 | 700 | Fuera de alcance (GAD) |
| **212** | EMPRESAS PUBLICAS DE LOS GAD | 276 | 8,79 % | 120 | 276 | Fuera de alcance (Empresas GAD) |
| **113** | ENTIDADES DE SEGURIDAD SOCIAL | 106 | 3,38 % | 5 | 106 | Fuera de alcance (Seguridad Social) |
| **112** | ENTIDADES DE EDUCACION SUPERIOR | 67 | 2,13 % | 36 | 67 | Fuera de alcance (Universidades) |
| **211** | EMPRESAS PUBLICAS FUNCION EJECUTIVA | 55 | 1,75 % | 23 | 55 | Fuera de alcance (Empresas Públicas) |
| **121** | GAD PROVINCIALES | 45 | 1,43 % | 24 | 45 | Fuera de alcance (GAD) |
| **311** | SOCIEDADES ANONIMAS CON PART. PUBLICA | 22 | 0,70 % | 22 | 22 | Fuera de alcance (S.A.) |
| **221** | ENTIDADES FINANCIERAS PUBLICAS | 13 | 0,41 % | 7 | 13 | Fuera de alcance (Banca pública) |
| **Total** | | **3.140** | **100,00 %** | **603** | **3.080** | |

---

## 3. Medición del cruce con SERCOP (2021–2025)

El cruce fue implementado y verificado en `scripts/measure_entity_crosswalk.py`, procesando los cinco años completos de `releases_AAAA.csv` y `awards_AAAA.csv` (Ruta A de datos derivados). La evidencia detallada está en `docs/h2/evidencia/medicion-cruce-entidades.json`.

### 3.1. Regla de cruce aplicada (ADR 0001, decisión 7)
1. **Paso 1 (Coincidencia simple):** `buyer_id` coincide de forma completa y sin modificar con la forma simple `EC-RUC-{13 dígitos}` respecto a un RUC del catálogo.
2. **Paso 2 (Coincidencia por raíz):** Si `buyer_id` contiene un sufijo (`EC-RUC-{13 dígitos}-{sufijo}`), se extrae la raíz `EC-RUC-{13}` y se valida contra el catálogo.
3. **Paso 3:** **Nunca** se une por nombre (`buyer_name`).

### 3.2. Cobertura global combinada (2021–2025)

En los 5 periodos evaluados (1.007.920 procesos y $30.952,88 millones adjudicados):

- **Cobertura de procesos:** **966.144 procesos cubiertos (95,86 %)**.
  - Coincidencia simple (sin sufijo): 745.440 procesos (73,96 %).
  - Coincidencia por raíz (con sufijo): 220.704 procesos (21,90 %).
  - No cruzados: 41.776 procesos (4,14 %).
- **Cobertura de monto adjudicado:** **$30.187,22 millones cubiertos (97,53 %)**.
  - Coincidencia simple: $5.166,28 millones (16,69 %).
  - Coincidencia por raíz: **$25.020,93 millones (80,84 %)**.
  - No cruzados: $765,66 millones (2,47 %).
- **Procesos con y sin monto adjudicado:**
  - 964.450 procesos (95,69 %) registran monto adjudicado numérico.
  - 43.470 procesos (4,31 %) **no tienen monto adjudicado** (procesos desiertos, cancelados o sin adjudicación en OCDS). Conforme a la regla del hito, *vacío no es cero* y se contabilizan por separado.

> **Evidencia contundente sobre la regla de cruce:** El 80,84 % de todo el dinero adjudicado en el Ecuador durante 2021–2025 se contrató a través de `buyer_id`s con sufijo desconcentrado (`EC-RUC-{13}-{sufijo}`). Si el cruce se restringiera a coincidencia exacta de cadena completa, se ignoraría más de $25.000 millones. La regla de unión por raíz del ADR 0001 queda empíricamente respaldada.

### 3.3. Cobertura detallada año por año

| Año | Compradores distintos | Compradores cruzados (%) | Total procesos | Procesos cruzados (%) | Monto adjudicado total (USD) | Monto cruzado (%) | Procesos sin monto |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2021** | 4.745 | 4.382 (92,35 %) | 167.058 | 159.774 (95,64 %) | $4.676.997.257,82 | $4.548.832.006,40 (97,26 %) | 2.795 |
| **2022** | 5.033 | 4.629 (91,97 %) | 212.324 | 202.970 (95,59 %) | $7.118.687.591,72 | $6.910.996.232,74 (97,08 %) | 9.388 |
| **2023** | 4.999 | 4.598 (91,98 %) | 217.913 | 207.809 (95,36 %) | $6.037.778.222,93 | $5.875.964.978,77 (97,32 %) | 10.933 |
| **2024** | 5.066 | 4.701 (92,80 %) | 219.185 | 210.804 (96,18 %) | $6.895.826.062,72 | $6.740.389.951,75 (97,75 %) | 11.025 |
| **2025** | 4.973 | 4.623 (92,96 %) | 191.440 | 184.787 (96,52 %) | $6.223.591.171,73 | $6.111.034.815,74 (98,19 %) | 9.329 |
| **Total** | — | — | **1.007.920** | **966.144 (95,86 %)** | **$30.952.880.306,92** | **$30.187.217.985,40 (97,53 %)** | **43.470** |

*Nota sobre la dimensión temporal:* El año reportado corresponde al año del archivo anual de SERCOP. Tal como se documentó en el reconocimiento, el archivo de un año puede contener fechas de negocio de otros periodos (p. ej. en 2021 constan procesos con fecha de publicación de 2022). La definición definitiva de la fecha de corte se asigna en el Hito 2.

### 3.4. Validación de la raíz `EC-RUC-{13}` (ADR 0001, pendiente resuelto)

Para cada uno de los 5 años se evaluaron las raíces extraídas:
1. **Formato:** En los cinco años, el **100 % de las raíces extraídas** (2.799 en 2021; 2.941 en 2022; 2.947 en 2023; 2.982 en 2024; 2.931 en 2025) tienen exactamente **13 dígitos numéricos** y ninguna falló la expresión regular.
2. **Coincidencia con el catálogo:** Entre el **89,68 % y el 91,03 %** de las raíces distintas de SERCOP existen en el catálogo MDEP.
3. **Raíces con múltiples `buyer_id`:** Entre 1.946 y 2.089 raíces por año (y 2.730 en la ventana conjunta) se asocian a más de un `buyer_id`. Las raíces con mayor número de variantes corresponden a carteras con desconcentración operativa (Ministerio de Salud, Ministerio de Educación, Policía Nacional, EP Petroecuador).

---

## 4. Clasificación sectorial e institucional observada

Al cruzar los procesos de SERCOP con el catálogo de e-SIGEF, los procesos se distribuyen en las siguientes clases institucionales:

### 4.1. Distribución por sector del catálogo (muestra anual 2021)

| Sector en catálogo MDEP | Procesos cruzados | % Procesos cruzados | Monto adjudicado (USD) | Condición frente al ADR 0001 |
|---|:---:|:---:|:---:|---|
| **ADMINISTRACION DEL ESTADO (111)** | 62.679 | 39,23 % | $1.764.321.405,10 | **Gobierno Central candidato** + Otras funciones |
| GAD MUNICIPALES (122) | 41.012 | 25,67 % | $912.450.812,40 | Fuera de alcance (GAD) |
| GAD PARROQUIALES (123) | 14.939 | 9,35 % | $78.120.450,15 | Fuera de alcance (GAD) |
| ENTIDADES DE SEGURIDAD SOCIAL (113) | 11.370 | 7,12 % | $421.980.120,60 | Fuera de alcance (Seguridad Social) |
| EMPRESAS PUBLICAS DE GAD (212) | 10.520 | 6,58 % | $315.600.410,00 | Fuera de alcance (Empresas GAD) |
| GAD PROVINCIALES (121) | 7.053 | 4,41 % | $389.120.700,20 | Fuera de alcance (GAD) |
| EMPRESAS PUBLICAS EJECUTIVA (211) | 4.450 | 2,79 % | $542.890.350,10 | Fuera de alcance (Empresas públicas) |
| EDUCACION SUPERIOR (112) | 4.307 | 2,70 % | $89.410.220,50 | Fuera de alcance (Universidades) |
| SOCIEDADES ANONIMAS (311) | 2.395 | 1,50 % | $24.110.500,00 | Fuera de alcance (Privadas/Mixtas) |
| FINANCIERAS PUBLICAS (221) | 1.049 | 0,66 % | $10.827.037,35 | Fuera de alcance (Banca pública) |
| **Subtotal cruzado** | **159.774** | **100,00 %** | **$4.548.832.006,40** | |
| No cruzados | 7.284 | — | $128.165.251,42 | Requiere análisis top 30 |

### 4.2. Desglose interno del Sector 111 (Administración del Estado)

El Sector 111 contiene 114 entidades institucionales en el catálogo. Al analizar la denominación de sus plantas centrales y EODs, se identifican cuatro subconjuntos:

1. **Presidencia y Vicepresidencia (Entidades 20, 21, 85):** 4 EODs en Presidencia, 1 en Vicepresidencia y Casa Militar Presidencial. Representan 115 procesos en 2021.
2. **Ministerios de Estado (14 carteras):** Ministerios rectores y sus 670+ EODs (distritos de salud, educación, brigadas de defensa). Representan la gran mayoría de la contratación del gobierno central.
3. **Institutos públicos adscritos (16 entidades):** INEC, IGM, INAMHI, INIAP, INSPI, INPC, INEVAL, INABIO, etc. Representan 821 procesos en 2021.
4. **Otras funciones del Estado y órganos autónomos (FUERA DE ALCANCE según ADR 0001):**
   - *Función Legislativa:* Asamblea Nacional (Entidad 1), Parlamento Andino (Entidad 3).
   - *Función Judicial:* Consejo de la Judicatura (Entidad 10), Defensoría Pública (Entidad 15).
   - *Función Electoral:* Consejo Nacional Electoral (Entidad 580), Tribunal Contencioso Electoral (Entidad 582).
   - *Función de Transparencia y Control Social:* Contraloría General del Estado (Entidad 591), Defensoría del Pueblo (Entidad 643), Consejo de Participación Ciudadana (Entidad 583), Superintendencias de Bancos (592), Compañías (593), Economía Popular (916), Competencia Económica (935), Protección de Datos (138) y Ordenamiento Territorial (361).
   - *Órganos Constitucionales y Autónomos:* Corte Constitucional (Entidad 581), Fiscalía General del Estado (Entidad 598), Procuraduría General del Estado (Entidad 590).

---

## 5. Entidades no cruzadas de SERCOP (Top 30 global 2021–2025)

En la ventana completa 2021–2025 existen 41.776 procesos (4,14 %) que no cruzan con el catálogo MDEP. Los 30 compradores con mayor número de procesos no cruzados acumulan 15.659 procesos y explican el 37,48 % del volumen no cruzado:

| # | `buyer_id` | Nombre del comprador en SERCOP | Procesos | Monto adjudicado (USD) | Sin monto | Causa identificada / Naturaleza jurídica |
|:---:|---|---|:---:|:---:|:---:|---|
| 1 | `EC-RUC-1768007040001` | CUERPO DE INGENIEROS DEL EJERCITO | 2.096 | $10.584.696,16 | 0 | Entidad militar adscrita a Defensa; RUC pasivo en catálogo 2026. |
| 2 | `EC-RUC-0190408485001` | FUNDACION MUNICIPAL DE LA MUJER Y EL NIÑO DE CUENCA | 882 | $457.327,27 | 0 | Fundación municipal privada (fuera de alcance). |
| 3 | `EC-RUC-1791905911001` | CORPORACION DE PROMOCION ECONOMICA CONQUITO | 734 | $674.541,64 | 0 | Corporación municipal del MDMQ (fuera de alcance). |
| 4 | `EC-RUC-1060040130001` | DIRECCION DISTRITAL 10D02 ANTONIO ANTE-OTAVALO-SALUD | 627 | $3.494.778,81 | 0 | Distrito de salud histórico absorbido/RUC pasivo en 2026. |
| 5 | `EC-RUC-1060014130001` | DIRECCION DISTRITAL 10 D03-COTACACHI-SALUD | 606 | $555.833,86 | 0 | Distrito de salud histórico absorbido/RUC pasivo en 2026. |
| 6 | `EC-RUC-1768184250001` | COMANDO DE INTELIGENCIA MILITAR CONJUNTO DE LAS FFAA | 571 | $1.730.245,94 | 0 | Unidad militar de FF.AA. adscrita a Defensa; RUC pasivo. |
| 7 | `EC-RUC-1768007040001-2504` | CUERPO DE INGENIEROS DEL EJERCITO | 559 | $86.703.313,07 | 91 | Unidad operativa desconcentrada del Cuerpo de Ingenieros. |
| 8 | `EC-RUC-1790174417001` | ALDEAS INFANTILES SOS ECUADOR | 518 | $731.628,85 | 3 | Organización no gubernamental / privada (fuera de alcance). |
| 9 | `EC-RUC-1792042704001` | FUNDACION MUSEOS DE LA CIUDAD | 511 | $2.262.854,47 | 0 | Fundación municipal del Distrito Metropolitano de Quito. |
| 10 | `EC-RUC-1768146750001` | SECRETARÍA TÉCNICA DE GESTIÓN INMOBILIARIA DEL SECTOR PÚBLICO | 504 | $31.845.050,65 | 0 | Inmobiliar; reestructurada/absorbida en Presidencia/MDEP. |
| 11 | `EC-RUC-1768192860001` | MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA | 503 | $1.031.498,69 | 0 | **Ex-MAATE:** Fusión ministerial 2026 en MAE; RUC histórico no en catálogo. |
| 12 | `EC-RUC-0190160890001` | HOGAR MIGUEL LEON DE LA CIUDAD DE CUENCA | 473 | $465.749,50 | 0 | Institución de beneficencia privada / social (fuera de alcance). |
| 13 | `EC-RUC-1768193160001` | COORDINACIÓN ZONAL 9 - SENESCYT | 442 | $969.533,43 | 0 | Coordinación zonal de SENESCYT con RUC propio histórico. |
| 14 | `EC-RUC-0992236574001` | FUNDACION TERMINAL TERRESTRE DE GUAYAQUIL | 382 | $13.883.685,06 | 0 | Fundación municipal de Guayaquil (fuera de alcance). |
| 15 | `EC-RUC-0968529080001` | CUERPO DE BOMBEROS DE SAMBORONDON | 364 | $364.145,61 | 1 | Entidad bomberil cantonal (fuera de alcance). |
| 16 | `EC-RUC-0992183721001` | GUAYAQUIL SIGLO XXI, FUNDACIÓN MUNICIPAL REGENERACIÓN | 343 | $1.970.542,62 | 0 | Fundación municipal de Guayaquil (fuera de alcance). |
| 17 | `EC-RUC-0990001340001` | ACERIAS NACIONALES DEL ECUADOR S.A. (A.N.D.E.C.) | 320 | $2.837.624,98 | 0 | Empresa privada / participación accionaria (fuera de alcance). |
| 18 | `EC-RUC-1460024040001` | CEFAS-PATRONATO DEL GAPMS | 303 | $53.063,19 | 0 | Patronato social provincial de Morona Santiago (GAD). |
| 19 | `EC-RUC-0360032780001` | COORDINACION ZONAL 6 - SENESCYT | 299 | $268.930,90 | 0 | Coordinación zonal de SENESCYT con RUC propio histórico. |
| 20 | `EC-RUC-1790932966001` | FAME S.A. | 296 | $130.423,57 | 0 | Fabricación de calzado militar S.A. (fuera de alcance). |
| 21 | `EC-RUC-0992457597001` | CORPORACION SEGURIDAD CIUDADANA DE GUAYAQUIL | 277 | $178.330,70 | 0 | Corporación municipal de Guayaquil (fuera de alcance). |
| 22 | `EC-RUC-1791825314001` | FUNDACION CALASANZ | 264 | $148.743,95 | 0 | Fundación privada confesional (fuera de alcance). |
| 23 | `EC-RUC-1791818881001` | NUCLEO DE SOLCA MACHALA | 249 | $401.085,45 | 0 | Entidad privada de lucha contra el cáncer (fuera de alcance). |
| 24 | `EC-RUC-1391719868001` | FEDERACION DEPORTIVA DE MANABI | 232 | $21.897,47 | 0 | Organismo deportivo provincial autónomo (fuera de alcance). |
| 25 | `EC-RUC-1791827929001` | CONCENTRACIÓN DEPORTIVA DE PICHINCHA | 229 | $534.308,89 | 0 | Organismo deportivo provincial autónomo (fuera de alcance). |
| 26 | `EC-RUC-1768137410001` | MINISTERIO DE LA MUJER Y DERECHOS HUMANOS | 226 | $461.901,41 | 0 | **Ministerio histórico:** Creado por escisión de DDHH; fusionado en MDH en 2026. |
| 27 | `EC-RUC-0968604550001` | DIRECCIÓN ZONAL 8 - SETEGISP (INMOBILIAR) | 211 | $5.430.899,01 | 0 | Dirección zonal de Inmobiliar con RUC propio; pasivo en 2026. |
| 28 | `EC-RUC-1791984714001` | FUNDACION TEATRO NACIONAL SUCRE | 189 | $243.262,58 | 0 | Fundación cultural municipal de Quito (fuera de alcance). |
| 29 | `EC-RUC-1792170826001` | FUNDACION NIÑOS CON DESTINO EN LAS MANOS DE DIOS | 184 | $100.286,23 | 0 | ONG / entidad social privada (fuera de alcance). |
| 30 | `EC-RUC-1790819442001` | JUNTA DE POLITICA Y REGULACION FINANCIERA | 179 | $132.686,13 | 0 | Cuerpo colegiado técnico de regulación financiera. |

### 5.1. Patrones de no cruce identificados
1. **Fusiones ministeriales 2025–2026:** El caso crítico es el `MINISTERIO DEL AMBIENTE, AGUA Y TRANSICION ECOLOGICA` (MAATE, RUC `1768192860001`, 503 procesos) y el `MINISTERIO DE LA MUJER Y DERECHOS HUMANOS` (RUC `1768137410001`, 226 procesos). Ambas carteras contrataron intensamente entre 2021 y 2025, pero en el catálogo de agosto de 2026 sus RUCs constan como pasivos o absorbidos por `MAE` y `MDH` (nota 5 del catálogo: *"Excluye entidades que tienen RUC pasivo"*).
2. **Entidades militares y de defensa:** El `CUERPO DE INGENIEROS DEL EJERCITO` (2.655 procesos) y el `COMANDO DE INTELIGENCIA MILITAR` (571 procesos) son unidades del Ministerio de Defensa que operan en SERCOP con RUC institucional propio no expuesto en e-SIGEF como entidad presupuestaria independiente.
3. **Fundaciones y corporaciones municipales/privadas:** 14 de las 30 entidades corresponden a fundaciones municipales, ONGs o corporaciones que contratan por el portal de compras públicas pero son ajenas al Presupuesto General del Estado y están **fuera de alcance** del gobierno central.

---

## 6. Diagnóstico de calidad de la fuente (Hallazgos Q-E01 a Q-E07)

| ID | Tabla · Campo | Dimensión | Problema y evidencia medible | Impacto en preguntas P1 a P3 | Acción propuesta para H3 |
|:---:|---|---|---|---|---|
| **Q-E01** | `Catalogo_MDEP · RUC` | **Validez / Formato** | **1.266 de 3.140 registros (40,32 %)** tienen 12 dígitos en vez de 13 porque Excel serializó el valor como número y truncó el cero inicial en provincias 01 a 09. | Alto: Si se une como texto sin corregir contra `EC-RUC-{13}`, falla el cruce para 4 de cada 10 entidades del catálogo, distorsionando P1 a P3. | En Power Query, normalizar aplicando relleno con ceros a la izquierda hasta 13 caracteres: `Text.PadStart([RUC], 13, "0")`. |
| **Q-E02** | `Catalogo_MDEP · RUC` | **Unicidad / Grano** | **60 RUCs duplicados (120 filas, 3,82 %)**. El grano es `(ENTIDAD, EOD)` y no RUC. Hay RUCs repetidos por ministerios fusionados que comparten direcciones distritales. | Alto: Rompe la cardinalidad 1 a varios en el modelo dimensional de Power BI, generando relaciones varios a varios o duplicación de hechos en P1 a P3. | Desduplicar el catálogo a nivel de RUC en Power Query seleccionando la entidad matriz (`EOD = 0`) o con regla determinista de jerarquía. |
| **Q-E03** | `Catalogo_MDEP · Hoja CATÁLOGO` | **Validez / Estructura** | Contiene 5 filas de títulos/blanco al inicio (1–5) y **8 filas de notas explicativas al pie (3147–3154)** con RUC y sector nulos. | Medio: Introduce registros corruptos con valores nulos si no se limpian los márgenes de la hoja. | Promover encabezados desde la fila 6 y filtrar filas donde `RUC` sea nulo o donde `DESCRIPCION SECTOR` esté vacío. |
| **Q-E04** | `Catalogo_MDEP · Fecha` | **Oportunidad / Temporalidad** | Fotografía estática al **31/08/2026**. Cero columnas de fecha, vigencia o trazabilidad histórica de fusiones ocurridas en 2021–2025. | Crítico: Impide modelar cambios históricos con SCD tipo 2 exclusivamente con esta fuente para responder la evolución temporal de P1–P3. | Complementar con la semilla versionada `warehouse/seeds/entity_classification.csv` (#68), asignando fechas `valid_from` y `valid_to`. |
| **Q-E05** | `SERCOP · buyer_id` vs `MDEP · RUC` | **Completitud** | **41.776 procesos (4,14 %)** y **$765,66M (2,47 %)** no cruzan con el catálogo. Incluye carteras clave del gobierno central como ex-MAATE (503 procesos) y Cuerpo de Ingenieros (2.655 procesos). | Alto: Deja fuera del gobierno central procesos legítimos de ministerios históricos en P1 a P3. | Incorporar manualmente en la semilla de entidades de H3 los RUCs pasivos del gobierno central detectados en el top 30 con su respectivo decreto de fusión. |
| **Q-E06** | `SERCOP · buyer_id` (sufijo) | **Consistencia** | **2.730 raíces de 13 dígitos** en SERCOP tienen múltiples `buyer_id` con sufijo. El **80,84 % del monto adjudicado global ($25.020,93M)** proviene de `buyer_id`s con sufijo. | Crítico: Si el cruce se hiciera por string completo de `buyer_id`, se perdería el 80,84 % del presupuesto adjudicado en P1 a P3. | Validar la regla del ADR 0001: extraer la raíz `EC-RUC-{13}` en Power Query (`Text.Middle([buyer_id], 7, 13)`) cuando inicie con `EC-RUC-`. |
| **Q-E07** | `Catalogo_MDEP · SECTOR 111` | **Exactitud / Alcance** | El Sector 111 ("ADMINISTRACION DEL ESTADO") agrupa a las **cinco funciones del Estado** (Asamblea, Función Judicial, CNE, CGE, etc.), no solo a la Función Ejecutiva. | Crítico: Filtrar ciegamente por `SECTOR == 111` violaría el ADR 0001, inflando el gobierno central con poderes autónomos fuera de alcance. | En la semilla de entidades de H3, clasificar individualmente las 114 entidades del Sector 111 asignando `Presidencia`, `Ministerio`, `Instituto` o `Fuera de alcance`. |

---

## 7. Conclusión rotunda sobre la suficiencia de la fuente

### ¿Alcanza esta fuente para construir la dimensión Entidad?

**La respuesta es: Alcanza como catálogo de enlace técnico, pero NO alcanza por sí sola para clasificar el sector.**

1. **En qué sí alcanza (Suficiencia técnica del 97 %):**
   - El catálogo del MDEP es técnicamente excelente para vincular los registros de compras públicas con el sistema fiscal oficial e-SIGEF: cubre el **95,86 % de los procesos** y el **97,53 % del monto adjudicado** de SERCOP en 2021–2025.
   - Proporciona la asociación oficial entre el RUC y los códigos institucionales de `ENTIDAD` y `EOD`, permitiendo agrupar unidades desconcentradas bajo su cartera matriz.

2. **Qué le falta y por qué no es autosuficiente:**
   - **No delimita el Gobierno Central:** En el catálogo presupuestario, el Sector 111 mezcla a los ministerios con la Asamblea Nacional, la Corte Nacional de Justicia, el Consejo Nacional Electoral y la Contraloría General. La fuente carece de un atributo que separe la Función Ejecutiva de las otras funciones del Estado.
   - **No resuelve la jerarquía ministerio → instituto:** El catálogo es plano; no contiene un campo relacional que indique de qué ministerio depende cada instituto adscrito.
   - **No tiene memoria histórica (falta SCD tipo 2):** Al ser una foto estática de agosto de 2026, excluye carteras ministeriales históricas que se fusionaron entre 2021 y 2025 (como MAATE con 503 procesos o Ministerio de la Mujer con 226 procesos), las cuales quedan como compradores no cruzados.

3. **Qué se debe agregar en el Hito 3:**
   - Construir en `warehouse/seeds/entity_classification.csv` (#68) la tabla semilla curada que tome como base los RUCs y códigos del catálogo MDEP y agregue:
     a) La categoría exacta de alcance: `Presidencia`, `Ministerio`, `Instituto dependiente` o `Fuera de alcance`.
     b) La relación padre-hijo (ministerio del que depende cada instituto).
     c) Los intervalos de vigencia temporal (`valid_from`, `valid_to`) para soportar SCD tipo 2 sobre las fusiones ministeriales de 2021–2025.
     d) La reincorporación de los RUCs pasivos históricos detectados en el top 30 (ex-MAATE, unidades de Defensa).

---

## 8. Preguntas abiertas para la definición de alcance del líder

Conforme a la sección 5.3 de `entidades.md` y la evidencia cuantitativa obtenida, se presentan las siguientes preguntas de decisión para el líder del equipo (para resolución previa a la semilla definitiva de #68):

1. **Cuerpo de Ingenieros del Ejército (2.655 procesos, $97,29M):** En SERCOP opera con RUC propio (`1768007040001`). ¿Se incluye como unidad ejecutora del Ministerio de Defensa Nacional (adscripción militar directa) o se excluye por constituir una unidad con giro empresarial de obra pública?
2. **Entidades con figura de «Servicio» y «Agencia»:** Instituciones como el `Servicio Ecuatoriano de Normalización (INEN)`, el `SRI`, el `SENAE`, `SERCOP` y las agencias de regulación (`ARCSA`, `ARCOTEL`, `ANT`) constan en el Sector 111 de e-SIGEF. ¿Se clasifican dentro de la categoría 3 («Institutos dependientes») asociadas a su ministerio rector, o se restringe la categoría 3 exclusivamente a entidades con nombre explícito de «Instituto»?
3. **Fechas de corte para carteras fusionadas:** Para carteras como MAATE (fusionada en MAE), MPCEI (en MDEP), Ministerio de Cultura y Deporte (en MINEDEC) y MIES/Mujer (en MDH), ¿se adopta como fecha de corte SCD tipo 2 la fecha del decreto ejecutivo de fusión (2025/2026) o se reclasifica retrospectivamente toda la serie al ministerio sucesor?
4. **Secretarías Técnicas de la Presidencia:** Entidades como `INMOBILIAR` (`1768146750001`, 504 procesos) y la Secretaría Nacional de Gestión de Riesgos: ¿se clasifican directamente bajo la categoría 1 («Presidencia de la República») o como órganos desconcentrados independientes?
5. **Entidades dudosas no resueltas:** Conforme a la regla 6 del ADR 0001, toda entidad cuya adscripción no quede formalmente documentada en la semilla permanecerá rotulada como `Fuera de alcance` o `Dudosa`, quedando excluida del cálculo de indicadores de P1, P2 y P3.
