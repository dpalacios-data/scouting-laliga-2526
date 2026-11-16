# Scouting LaLiga 2025/26

Modelo de datos de los **jugadores de campo de LaLiga 2025/26**: métricas por 90 minutos y percentiles por grupo
de posición, organizados en un modelo en estrella pensado para alimentar un panel de scouting en Power BI y otro
en Tableau.

## Estado

Hoy este repositorio es la capa de datos de un panel de scouting. Los paneles de Power BI y Tableau todavía no
existen; cuando se publiquen, se enlazarán aquí.

Es un proyecto separado de mi TFM sobre el descenso del RCD Mallorca
([analisis-mallorca-2025-26](https://github.com/dpalacios-data/analisis-mallorca-2025-26)), del que reutiliza los
datos ya procesados. El TFM no se modifica.

---

## Reproducibilidad

- **El cuaderno 00 no se puede ejecutar desde fuera, porque los eventos de WhoScored no están versionados en
  ningún sitio.** Necesita `data/bruto/eventos_laliga_2526.parquet` (16 MB), que no está en este repositorio
  ni en el del TFM. Se generó en el cuaderno 01 del TFM a partir de los eventos de WhoScored descargados con la librería `soccerdata`. Su SHA-256 es
  `8bcb04eeacb42d93d242ca735e080a86475b9d57aa5ee82fa267d7f997989d61`.
- **El cuaderno 01 sí se puede ejecutar, porque todo lo que lee está en el repositorio.** Las acciones de Opta
  ya agregadas por jugador están versionadas en `data/eventos_por_jugador.csv`, y el resto son ficheros de
  `data/origen/` y de `data/`.
- **El cuaderno 02 también se puede ejecutar** con lo que hay en el repositorio.
- **El cuaderno 05 también se puede ejecutar sin conexión.** Lo que leyó de Wikipedia está versionado en
  `data/wikitexto_equipaciones.json`.
- **El cuaderno 06 no se puede ejecutar desde fuera sin volver a descargar** las 20 páginas de plantilla de
  Transfermarkt, que se guardan en `data/bruto/transfermarkt/` y no se versionan. Su resultado sí está
  versionado, en `data/fotos_transfermarkt.csv`.
- **Los cuadernos 03 y 04 necesitan conexión a internet.** El 03 descarga los escudos de Wikimedia Commons y de
  las webs oficiales de los clubes, que pueden cambiar de dirección. El 04 consulta Wikidata; guarda una caché
  local (`data/cache_wikidata.json`, unos 8 MB) que no se versiona.

## De dónde vienen los datos

| Fuente | Qué aporta |
|---|---|
| **Understat** | Minutos, partidos, goles, xG, asistencias, xA, tiros, pases clave, xGChain y xGBuildup de cada jugador. Puntos y puntos esperados de cada equipo |
| **Eventos Opta de WhoScored** | Alineaciones con el identificador de cada jugador, y acciones del partido con su resultado: entradas intentadas y exitosas, intercepciones, despejes, pases bloqueados, duelos aéreos disputados y ganados, centros y toques en el área |
| **Fichero propio de posiciones** | La posición de 637 jugadores, asignada a mano y validada en el TFM contra las alineaciones de WhoScored |

En el TFM también usé FBref, pero ninguna columna de este modelo sale de FBref.

Los ficheros de origen se copiaron del TFM sin modificarlos. La tabla muestra los 16 primeros caracteres del
SHA-256 de cada uno; los completos están en `data/origen/SHA256SUMS`, y se comprueban con:

```bash
cd data/origen && sha256sum -c SHA256SUMS
```

| Fichero (`data/origen/`) | SHA-256 (inicio) | Uso |
|---|---|---|
| `posiciones_laliga_2526.csv` | `d49b47fc82e486a9` | posición de cada jugador |
| `jugadores_laliga_2526.csv` | `645e7c0730a694b3` | Understat: minutos, partidos y métricas |
| `alineaciones_laliga_2526.csv` | `a357179f0c5ae48e` | identificador de WhoScored y puesto en cada alineación |
| `metricas_jugadores_laliga_2526.csv` | `6b8ea02ab17baad5` | cruce posiciones-Understat del TFM y auditoría |
| `altura_defensiva_laliga_2526.csv` | `4bb0d9f3578c0e3b` | altura defensiva de cada equipo |
| `clasificacion_xpts_laliga_2526.csv` | `f6cbe1b0889644be` | puntos y puntos esperados |
| `disparos_laliga_2526_limpio.csv` | `23f52e01c5fe60b6` | solo auditoría (modelos del TFM) |
| `equipos_largo_laliga_2526.csv` | `4e7e92d08b5a9152` | solo auditoría (modelos del TFM) |

## Qué jugadores cubre

```
  jugadores en el fichero de posiciones           637
- no jugaron                                      112   data/sin_minutos.csv
- descartados por cruce dudoso                      2   data/cruces_descartados.csv
= jugadores del fichero de posiciones que entran  523
+ jugadores de campo recuperados de Understat      38
= total de jugadores del modelo                   561

  (aparte) porteros excluidos                      39
  comprobación: 561 + 39 = 600 jugadores en Understat
```

- **No jugaron (112):** están en el fichero de posiciones, pero no aparecen en Understat con ningún nombre
  parecido ni tienen un solo evento de Opta. La lista está en `data/sin_minutos.csv`.
- **Descartados por cruce dudoso (2):** Carlos Protesoni y Yago Santiago. Su posible pareja en Understat (Carlos
  Benavídez y Yago Alonso) solo comparte el nombre de pila. Esas dos filas de Understat entran en el modelo con
  su propio nombre, sin posición confirmada y sin eventos.
- **Porteros (39), fuera de esta versión.** Un portero no se mide con intercepciones ni duelos aéreos:
  necesita paradas, salidas y goles esperados a puerta, y esos datos no los tengo completos. El modelo cubre
  jugadores de campo, y el panel deberá decirlo de forma visible.

### Cómo se cruzó cada jugador

| Cruce | Jugadores |
|---|---|
| Directos: los cruzaba ya el TFM | 466 |
| Recuperados por nombre, eventos de Opta (estaban en el TFM con los eventos vacíos) | 15 |
| Recuperados por nombre, posiciones-Understat | 36 |
| Traspasados en invierno: Understat los pone en su club anterior | 6 |
| Recuperados por grafía: jugadores de Understat sin posición, con otra grafía en WhoScored | 2 |
| Recuperados de Understat sin posición | 36 |
| **Total** | **561** |

Todos los recuperados se comprobaron con el mismo equipo y los mismos partidos en las dos fuentes, y se
confirmaron a mano. Cada cruce está en `data/mapa_nombres.csv`, con el nombre del jugador en cada fuente.

### Posiciones

- **523** jugadores tienen la posición del fichero propio.
- **38** jugadores tienen la posición deducida de sus titularidades en las alineaciones de WhoScored:
  - **10** están confirmados.
  - **28** siguen **sin posición confirmada**: tienen menos de 3 titularidades, nunca fueron titulares o no
    tienen identificador de WhoScored. No tienen percentil y ninguno pasa de 320 minutos.

### Eventos de Opta

**5 jugadores** quedan con las métricas de Opta vacías (`tiene_eventos` = falso), porque su cruce con
WhoScored es dudoso: Carlos Benavídez, Yago Alonso, Adam El Mokhtari, Sergio Lozano y Rubén Iranzo. Todos
tienen menos de 600 minutos. Un hueco es "no tengo el dato" y nunca se rellena con cero: un cero significa
"no hizo la acción".

## Cómo está montado el modelo

```
dim_equipo ──┐
             ├── dim_jugador ── hechos_jugador
dim_posicion ┘
```

| Tabla | Filas | Contenido |
|---|---|---|
| `dim_equipo` | 20 | equipo, altura defensiva, puntos, puntos esperados, fichero y url del escudo, y colores primario y secundario de la camiseta |
| `dim_posicion` | 9 | posición y grupo de comparación |
| `dim_jugador` | 561 | jugador, equipo, posición, minutos, partidos, de dónde sale su posición, edad, altura, pie, nacionalidad, valor de mercado estimado y url de su retrato |
| `hechos_jugador` | 561 | 19 métricas por 90 minutos y 2 porcentajes de éxito, con su percentil por grupo, `percentil_fiable`, `n_grupo_referencia` y `muestra_reducida` |

**Claves.** Todas las claves son numéricas y propias. La clave del jugador nunca es el nombre: hay dos jugadores
que se llaman David López, uno en el Mallorca y otro en el Girona. Los eventos de Opta se cruzan por el
identificador de WhoScored, no por nombre. Así los homónimos no se mezclan, y los traspasados suman los eventos
de sus dos clubes.

**Percentiles.**

- Se calculan dentro del grupo de posición, contra los jugadores de ese grupo con **600 minutos o más**.
- Fórmula: % del grupo de referencia con un valor estrictamente menor. Ningún jugador del grupo de referencia
  llega a 100: el mejor de los 71 centrales sale en 98,59.
- Los jugadores con menos de 600 minutos tienen percentil, pero con `percentil_fiable` en falso.
- **368 jugadores** tienen percentil fiable.
- El grupo mediapunta solo tiene 28 jugadores de referencia. El modelo lo marca con `muestra_reducida` para que
  el panel pueda avisarlo.

**Diferencias con el TFM.** Los percentiles de este proyecto no coinciden con los del TFM para los mismos
jugadores, y es lo esperado: el grupo de centrales pasa de 65 a 71 jugadores, el cruce de eventos es por
identificador, y las entradas y los duelos aéreos separan volumen y éxito. El
[diccionario de datos](docs/diccionario_datos.md) explica cada diferencia.

## Escudos y fotos

**Escudos.** Los 20 están en `images/escudos/`, con el nombre de fichero que usa `dim_equipo.escudo`: PNG con
transparencia, 128 × 128 px y el mismo margen interior. El origen de cada uno está en `data/escudos.csv`.

Los 20 están versionados, porque el panel los carga por su dirección pública en este repositorio
(`dim_equipo.url_escudo`): sin fichero en el repositorio no hay url pública, y el escudo es lo que identifica al
equipo en todo el panel.

**Los escudos son marcas registradas de sus clubes.** Se usan solo con fines identificativos, en un proyecto
académico sin ánimo de lucro. Cada uno tiene su url de origen y su fecha de descarga en `data/escudos.csv`.

- 17 se descargaron de la web oficial de cada club.
- 3 vienen de Wikimedia Commons (propiedad P154 de Wikidata), con licencia libre:

| Escudo | Licencia | Autor en Commons | Fichero |
|---|---|---|---|
| Barcelona | CC0 | HAMDANI 72 | [Football Club Barcelona Color Update.png](https://commons.wikimedia.org/wiki/File:Football_Club_Barcelona_Color_Update.png) |
| Celta | CC BY-SA 3.0 | Elisardojm, a partir de ficheros de Madboy74, HansenBCN y WarX | [Escudo RC Celta de Vigo.svg](https://commons.wikimedia.org/wiki/File:Escudo_RC_Celta_de_Vigo.svg) |
| Getafe | CC BY-SA 4.0 | Yawen | [Getafe CF Logo.png](https://commons.wikimedia.org/wiki/File:Getafe_CF_Logo.png) |

Estos tres están reducidos a 128 × 128 px respecto al original.

**Colores.** `dim_equipo.color_primario` y `color_secundario` son los dos colores de la camiseta de la primera
equipación 2025/26, medidos sobre la plantilla de equipación de la ficha de cada club en la Wikipedia en inglés
(versión de cada artículo a 31 de mayo de 2026). El primario es el que no es blanco, porque el blanco solo
identifica al Real Madrid. Son colores aproximados de Wikipedia, no colores de marca oficiales.

**El color no identifica al equipo en este panel: lo hace el escudo.** Hay 7 equipos rojos y 5 azules, y varios
comparten exactamente el mismo `#ff0000`. El color servirá para acentuar la ficha del jugador seleccionado,
donde solo hay un equipo en pantalla. El detalle, con la revisión de cada artículo, está en el
[diccionario de datos](docs/diccionario_datos.md).

**Retratos de jugadores. Fuente: [Transfermarkt](https://www.transfermarkt.es).** Las imágenes de Transfermarkt
no se descargan ni se republican: `dim_jugador.url_foto` guarda la dirección del retrato en sus servidores, y
el panel la cargará desde allí. Los retratos son de Transfermarkt y de sus proveedores, y el panel citará la
fuente de forma visible.

- **539 de 561** jugadores tienen retrato enlazado, y **367 de los 368** con percentil fiable.
- Los otros **22** tienen un retrato de iniciales generado en este proyecto (`images/jugadores/`, cuaderno 07):
  un rectángulo de la misma proporción que los retratos de Transfermarkt (10:13), con el color primario de su
  equipo y sus iniciales. `url_foto` apunta a su dirección pública en
  este repositorio, así que **los 561 jugadores tienen una url de imagen**, y `foto_origen` dice de dónde sale
  cada una. Son: 18 que en
  Transfermarkt solo tienen la silueta genérica, 3 sin coincidencia y 1 con cruce dudoso.
- Todas las url responden fuera de la web de Transfermarkt, pesan entre 3 y 30 KB y tienen 85 caracteres como
  máximo, dentro de los límites de Tableau (128 KB y 255 caracteres).

**Datos de scouting. Fuente: Transfermarkt.** De las mismas páginas de plantilla salen la fecha de nacimiento,
la altura, el pie, la nacionalidad y el valor de mercado de 557 de los 561 jugadores (descargadas el 16/11/2026).

- **La edad está calculada a 31 de mayo de 2026**, último día de la temporada, no a día de hoy.
- **`valor_mercado_tm` es una estimación de Transfermarkt, no un precio real** ni una cifra de traspaso.
- La fecha de fin de contrato no está en el modelo: no aparece en las páginas de plantilla descargadas.
- 4 jugadores no tienen ninguno de estos datos, porque no están emparejados con Transfermarkt: Carlos
  Benavídez, Yago Alonso, Adam El Mokhtari y Sergio Lozano.

**Fuente evaluada y descartada: Wikimedia Commons.** Antes se midió la cobertura de fotos con licencia libre en
Wikidata (cuaderno 04, `data/fotos_wikidata.csv`): 218 de 561 jugadores (38,9 %) y 174 de los 368 con percentil
fiable (47,3 %). Con menos de la mitad de cobertura se cambió de fuente.

## Cuadernos

| Cuaderno | Qué hace | ¿Se puede ejecutar desde el repositorio? |
|---|---|---|
| `notebooks/00_cruces_nombres.ipynb` | Decide qué jugador es quién en cada fuente. Todas las decisiones de cruce están escritas como listas en el cuaderno. Genera los ficheros de `data/` | **no**: necesita los eventos de WhoScored, que no están versionados |
| `notebooks/01_modelo_datos.ipynb` | Construye el modelo de `data/modelo/`, imprime el cuadre y ejecuta las comprobaciones de calidad | sí |
| `notebooks/03_escudos.ipynb` | Descarga los 20 escudos, los normaliza a 128 × 128 px con el mismo margen y extrae su color dominante | con conexión a internet |
| `notebooks/04_fotos_wikidata.ipynb` | Mide qué jugadores tienen foto en Wikidata. No descarga ninguna imagen. Fuente descartada por cobertura | con conexión a internet |
| `notebooks/05_colores_equipacion.ipynb` | Mide los dos colores de la camiseta de cada equipo sobre la plantilla de equipación de Wikipedia y fija el color primario | sí |
| `notebooks/07_retratos_iniciales.ipynb` | Genera el retrato de iniciales de los jugadores sin retrato de Transfermarkt | sí, después del cuaderno 01 |
| `notebooks/06_fotos_transfermarkt.ipynb` | Empareja a los 561 jugadores con las plantillas de Transfermarkt y guarda la url de su retrato, sin descargar imágenes. Comprueba que las url responden y cumplen los límites de Tableau | **no** sin volver a descargar las plantillas |
| `notebooks/02_auditoria_cruce_eventos.ipynb` | Comprueba que el cruce por identificador reproduce las cifras de eventos publicadas en el TFM: 462 de 464 jugadores son idénticos. Identifica los dos que cambian (dos homónimos que el TFM sumaba al cruzar por nombre) y mide su efecto en los cálculos del TFM. Compara también volumen y éxito en duelos aéreos y entradas | sí |

Entorno: Python con pandas, numpy, pyarrow, unidecode y scikit-learn 1.9.1 (la versión con la que el cuaderno 02
reproduce los modelos del TFM). Cada cuaderno se ejecuta desde la raíz del proyecto o desde `notebooks/`, con
rutas relativas. Las fórmulas, unidades y fuentes de cada columna están en
[docs/diccionario_datos.md](docs/diccionario_datos.md).

## Próximos pasos

El panel se construirá sobre este modelo:

- **Ficha de jugador:** métricas por 90 y percentiles dentro de su grupo, con `n_grupo_referencia` siempre
  visible y aviso de muestra reducida en mediapunta.
- **Comparador** de jugadores del mismo grupo de posición.
- **Buscador por perfil:** filtros de percentil, minutos y equipo, con `percentil_fiable` como filtro por defecto.
- **Contexto de equipo:** altura defensiva y puntos frente a puntos esperados.
- **Cobertura visible:** el panel dirá que cubre jugadores de campo, y mostrará "Posición no confirmada" para el
  grupo `sin_confirmar`.
