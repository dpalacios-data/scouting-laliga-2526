# Scouting LaLiga 2025/26

Herramienta de scouting de los **jugadores de campo de LaLiga 2025/26**, con un panel en Power BI y otro en
Tableau. Este repositorio contiene la capa de datos: un modelo en estrella con métricas por 90 minutos y
percentiles por grupo de posición, listo para conectar a los dos paneles.

Es un proyecto separado de mi TFM sobre el descenso del RCD Mallorca, del que reutiliza los datos ya procesados.
El TFM no se modifica.

**Paneles**

- Power BI: _[enlace pendiente]_
- Tableau: _[enlace pendiente]_

---

## De dónde vienen los datos

| Fuente | Qué aporta |
|---|---|
| **Understat** | Minutos, partidos, goles, xG, asistencias, xA, tiros, pases clave, xGChain y xGBuildup de cada jugador. Puntos y puntos esperados de cada equipo |
| **Eventos Opta de WhoScored** | Alineaciones con el identificador de cada jugador, y acciones del partido con su resultado: entradas intentadas y exitosas, intercepciones, despejes, pases bloqueados, duelos aéreos disputados y ganados, centros y toques en el área |
| **Fichero propio de posiciones** | La posición de 637 jugadores, asignada a mano y validada en el TFM contra las alineaciones de WhoScored |

En el TFM también usé FBref, pero ninguna columna de este modelo sale de FBref.

Todos los ficheros de origen se copiaron del TFM sin modificarlos:

| Fichero (`data/origen/`) | SHA-256 | Uso |
|---|---|---|
| `posiciones_laliga_2526.csv` | `d49b47fc82e486a9e1d6c5cc1695c7cd20dd48734f4b1d2aec58c15b96caa985` | posición de cada jugador |
| `jugadores_laliga_2526.csv` | `645e7c0730a694b3aee18b449e6a4b8bd76f086a693d6a3fa0f963c9fa35f402` | Understat: minutos, partidos y métricas |
| `alineaciones_laliga_2526.csv` | `a357179f0c5ae48ecea8b3850af5e4c5c56081b7b5f9923d698e3b3daa06ebee` | identificador de WhoScored y puesto en cada alineación |
| `metricas_jugadores_laliga_2526.csv` | `6b8ea02ab17baad5119c8dd6f05e2d41804e8b8dda91d07c70254c5654b54b54` | cruce posiciones-Understat del TFM y auditoría |
| `altura_defensiva_laliga_2526.csv` | `4bb0d9f3578c0e3b97738a4bfe2d9e85c6c1f7c0ae8b86dc932f9ae3fef57797` | altura defensiva de cada equipo |
| `clasificacion_xpts_laliga_2526.csv` | `f6cbe1b0889644bef4ac526f2b1351e468a9b580932c9a5b45188a4e0ba8bd35` | puntos y puntos esperados |
| `disparos_laliga_2526_limpio.csv` | `23f52e01c5fe60b6aa66c6786295cf0100505d7b5669135c182f06a3d2eec427` | solo auditoría (modelos del TFM) |
| `equipos_largo_laliga_2526.csv` | `4e7e92d08b5a91520253aa602c632b80da28ff83f4332a3c1430750e7834cf1a` | solo auditoría (modelos del TFM) |

**`data/bruto/` no está versionado.** Contiene `eventos_laliga_2526.parquet` (16 MB, SHA-256
`8bcb04eeacb42d93d242ca735e080a86475b9d57aa5ee82fa267d7f997989d61`), que se copia a mano desde
`tfm-mallorca/data/`. Solo lo necesita el cuaderno 00. El modelo se reconstruye con el cuaderno 01 sin él,
porque las acciones de Opta ya agregadas están versionadas en `data/eventos_por_jugador.csv`.

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
  necesita paradas, salidas y goles esperados a puerta, y esos datos no los tengo completos. El panel cubre
  jugadores de campo y lo dice de forma visible.

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
| `dim_equipo` | 20 | equipo, altura defensiva, puntos, puntos esperados y fichero del escudo |
| `dim_posicion` | 9 | posición y grupo de comparación |
| `dim_jugador` | 561 | jugador, equipo, posición, minutos, partidos y de dónde sale su posición |
| `hechos_jugador` | 561 | 19 métricas por 90 minutos y 2 porcentajes de éxito, con su percentil por grupo, `percentil_fiable`, `n_grupo_referencia` y `muestra_reducida` |

**Claves.** Todas las claves son numéricas y propias. La clave del jugador nunca es el nombre: hay dos David
López, uno en el Mallorca y otro en el Girona. Los eventos de Opta se cruzan por el identificador de WhoScored,
no por nombre. Así los dos David López no se mezclan, y los traspasados suman los eventos de sus dos clubes.

**Percentiles.**

- Se calculan dentro del grupo de posición, contra los jugadores de ese grupo con **600 minutos o más**.
- Fórmula: % del grupo de referencia con un valor estrictamente menor. Ningún jugador del grupo de referencia
  llega a 100: el mejor de los 71 centrales sale en 98,59.
- Los jugadores con menos de 600 minutos tienen percentil, pero con `percentil_fiable` en falso.
- **368 jugadores** tienen percentil fiable.
- El grupo mediapunta solo tiene 28 jugadores de referencia, y el panel lo avisa.

Las fórmulas, unidades y fuentes de cada columna están en [docs/diccionario_datos.md](docs/diccionario_datos.md).

## Cuadernos

| Cuaderno | Qué hace | Necesita `data/bruto/` |
|---|---|---|
| `notebooks/00_cruces_nombres.ipynb` | Decide qué jugador es quién en cada fuente. Todas las decisiones de cruce están escritas como listas en el cuaderno. Genera los ficheros de `data/` | sí |
| `notebooks/01_modelo_datos.ipynb` | Construye el modelo de `data/modelo/`, imprime el cuadre y ejecuta las comprobaciones de calidad | no |
| `notebooks/02_auditoria_david_lopez.ipynb` | Mide cuánto afecta al TFM el fallo de los dos David López, que en el TFM compartían eventos | no |

Entorno: conda `tfm`. Cada cuaderno se ejecuta desde la raíz del proyecto o desde `notebooks/`, con rutas
relativas.

## Qué se va a construir encima

- **Ficha de jugador:** métricas por 90 y percentiles dentro de su grupo, con `n_grupo_referencia` siempre
  visible y aviso de muestra reducida en mediapunta.
- **Comparador** de jugadores del mismo grupo de posición.
- **Buscador por perfil:** filtros de percentil, minutos y equipo, con `percentil_fiable` como filtro por defecto.
- **Contexto de equipo:** altura defensiva y puntos frente a puntos esperados.
