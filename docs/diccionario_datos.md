# Diccionario de datos

Modelo en estrella de `data/modelo/`, construido por `notebooks/01_modelo_datos.ipynb` a partir de los ficheros
de cruce que genera `notebooks/00_cruces_nombres.ipynb`.

```
dim_equipo ──┐
             ├── dim_jugador ── hechos_jugador
dim_posicion ┘
```

- `dim_jugador.id_equipo` → `dim_equipo.id_equipo`
- `dim_jugador.id_posicion` → `dim_posicion.id_posicion`
- `hechos_jugador.id_jugador` → `dim_jugador.id_jugador` (relación uno a uno)

**Cobertura:** jugadores de campo con minutos en LaLiga 2025/26. Los porteros no están (ver más abajo).

---

## dim_equipo.csv · 20 filas

| Columna | Qué es | Unidad | De dónde sale |
|---|---|---|---|
| `id_equipo` | Clave propia del equipo | entero, 1 a 20, por orden alfabético | generada en el cuaderno 01 |
| `equipo` | Nombre del equipo | texto | fichero propio de posiciones; WhoScored escribe "Atletico" y "Deportivo Alaves", que se traducen con una correspondencia explícita en los cuadernos 00 y 01. Es el nombre de cruce: sin tildes y tal como lo escriben las fuentes |
| `nombre_equipo` | Nombre del equipo para enseñar en el panel: con tildes y como se conoce al club ("Alavés", "Atlético de Madrid", "Celta") | texto | escrito a mano en el cuaderno 01, uno por equipo |
| `altura_defensiva` | Posición media en el largo del campo de las entradas, intercepciones, despejes, pases bloqueados y recuperaciones del equipo | coordenada x de Opta: 0 = portería propia, 100 = portería rival. **No son metros** | `altura_defensiva_laliga_2526.csv`, calculada en el TFM (cuaderno `02_analisis_equipo`) con los eventos de Opta |
| `puntos` | Puntos reales en la liga | puntos | `clasificacion_xpts_laliga_2526.csv` (TFM, a partir de Understat) |
| `puntos_esperados` | Puntos esperados según el xG de cada partido | puntos | `clasificacion_xpts_laliga_2526.csv`, columna `xpts` (Understat) |
| `escudo` | Nombre del fichero del escudo en `images/escudos/` | texto, minúsculas, sin acentos, con guiones bajos | generado a partir de `equipo` |
| `url_escudo` | Dirección pública del escudo en este repositorio (rama `main`), para Power BI y Tableau | url https | generada a partir de `escudo` |
| `color_primario` | Color identificativo del equipo: el color de la camiseta de la primera equipación 2025/26 que no es blanco (ver "Colores de equipo") | hexadecimal, `#rrggbb` | `data/colores_equipos.csv`, calculado en el cuaderno 05 |
| `color_secundario` | El otro color de la camiseta, tal cual sale de Wikipedia, salvo en el Celta | hexadecimal, `#rrggbb` | `data/colores_equipos.csv` |
| `color_secundario_origen` | `wikipedia_equipacion`, o `revision_autor` si lo fijó el autor (solo Celta: blanco, porque el negro medido es el contorno del cuello, un 4 % de la camiseta) | texto | cuaderno 05 |
| `color_grado_1`, `color_grado_2`, `color_grado_3` | Tres grados del color del equipo para la página Comparación: el primero es `color_primario` aclarado lo justo para contrastar 3:1 con el fondo del panel (#07090E); los otros dos, cada vez más claros (o más oscuros en los colores claros: Real Madrid, Villarreal, Celta). Entre los jugadores seleccionados de un mismo club, el de más minutos se pinta con el grado 1, el siguiente con el 2 y el tercero con el 3. Distancia mínima entre dos grados de un mismo equipo (CIEDE2000): 15,7 (Celta); el resto, 16 o más | hexadecimal, `#rrggbb` | cuaderno 01 |
| `color_origen` | `wikipedia_equipacion` si el color primario es uno de los colores de camiseta medidos en Wikipedia; `revision_autor` si lo fijó el autor con otro criterio (solo Valencia) | texto | cuaderno 05 |

## dim_posicion.csv · 9 filas

| Columna | Qué es | Unidad | De dónde sale |
|---|---|---|---|
| `id_posicion` | Clave propia de la posición | entero | generada en el cuaderno 01 |
| `posicion` | Posición del jugador | texto | fichero propio de posiciones o alineaciones de WhoScored (ver `dim_jugador.posicion_origen`) |
| `grupo` | Grupo de comparación para los percentiles | texto | definido en el cuaderno 01 |

| posicion | grupo | ¿Tiene percentil? |
|---|---|---|
| central | central | sí |
| lateral | lateral | sí |
| pivote | pivote_mediocentro | sí |
| mediocentro | pivote_mediocentro | sí |
| mediapunta | mediapunta | sí, **con aviso de muestra reducida** |
| extremo | extremo | sí |
| delantero | delantero | sí |
| sin_definir | sin_definir | no |
| sin_confirmar | sin_confirmar | no. El panel deberá mostrarlo como "Posición no confirmada" |

Pivote y mediocentro van en el mismo grupo, como en el TFM, porque las fuentes no coinciden en la frontera
entre los dos puestos.

## dim_jugador.csv · 561 filas

| Columna | Qué es | Unidad | De dónde sale |
|---|---|---|---|
| `id_jugador` | Clave propia del jugador. **El nombre no sirve de clave**: hay dos David López, uno en el Mallorca y otro en el Girona | entero, 1 a 561, por equipo y nombre | generada en el cuaderno 01 |
| `jugador` | Nombre del jugador | texto | fichero propio de posiciones; para los 38 que no están en él, el nombre de Understat |
| `id_equipo` | Club actual del jugador | clave → `dim_equipo` | fichero propio de posiciones; para los 38 que no están en él, el equipo de Understat |
| `id_posicion` | Posición | clave → `dim_posicion` | ver `posicion_origen` |
| `minutos` | Minutos jugados en toda la temporada, sumando todos sus clubes | minutos | Understat (`minutes`) |
| `partidos` | Partidos jugados en toda la temporada, sumando todos sus clubes | partidos | Understat (`matches`) |
| `posicion_origen` | De dónde sale la posición: `fichero_propio` (523 jugadores) o `alineaciones_whoscored` (38) | texto | cuaderno 00 |
| `equipos_temporada` | Partidos con al menos un evento de Opta, por club. Ejemplo: "Celta Vigo 10 + Girona 17". Vacío si no tiene eventos | texto | eventos de Opta, por identificador de WhoScored |
| `id_understat` | Identificador del jugador en Understat, para auditoría | entero | Understat (`player_id`) |
| `id_whoscored` | Identificador del jugador en WhoScored, para auditoría. Vacío en los 5 jugadores sin eventos | entero | alineaciones de WhoScored |
| `fecha_nacimiento` | Fecha de nacimiento. Vacía en 4 jugadores | fecha, `aaaa-mm-dd` | Transfermarkt, plantillas 2025/26 (cuaderno 06) |
| `edad` | Edad en años cumplidos **a 31 de mayo de 2026**, último día de la temporada 2025/26. No es la edad a día de hoy. Vacía en 4 jugadores | años | calculada en el cuaderno 01 a partir de `fecha_nacimiento` |
| `altura_cm` | Altura. Vacía en 8 jugadores | centímetros | Transfermarkt |
| `pie` | Pie dominante: `Derecho`, `Izquierdo` o `Ambidiestro`. Vacío en 12 jugadores | texto | Transfermarkt |
| `nacionalidad` | Primera nacionalidad que muestra Transfermarkt. Vacía en 4 jugadores | texto, nombre del país en español | Transfermarkt |
| `nacionalidad_2` | Segunda nacionalidad, si Transfermarkt muestra dos (155 jugadores) | texto | Transfermarkt |
| `valor_mercado_tm` | **Estimación** del valor de mercado hecha por Transfermarkt, tal como aparecía en la página el día de la descarga. Es la opinión de un tercero: **no es un precio real**, ni una cifra de traspaso, ni una cláusula. Vacío en 9 jugadores | euros | Transfermarkt |
| `fecha_datos_tm` | Fecha en la que se descargaron de Transfermarkt los datos anteriores. El valor de mercado cambia con el tiempo | fecha, `aaaa-mm-dd` | cuaderno 06 |
| `url_foto` | Dirección pública del retrato del jugador en este repositorio (`images/jugadores/<id_jugador>.png`). Los 561 tienen una. PNG de 200 × 200 px en círculo, con las esquinas transparentes | url https | retrato de Transfermarkt recortado (cuaderno 08) o retrato de iniciales (cuaderno 07) |
| `url_foto_transfermarkt` | Url original en Transfermarkt del retrato que se recortó (versión grande, 300 × 390 px). Vacía en los 22 retratos de iniciales | url https | Transfermarkt (cuaderno 08) |
| `foto_origen` | `transfermarkt` (539 jugadores): retrato de Transfermarkt recortado en círculo; o `iniciales` (22): retrato generado en este proyecto, un círculo de 200 × 200 px con el color primario del equipo y las iniciales del nombre y del primer apellido | texto | cuaderno 01 |
| `color_jugador` | Color base del jugador en la página Comparación: el `color_grado_1` de su equipo. No distingue a dos jugadores del mismo club (un solo tono para 22-33 jugadores no puede); eso lo hace en Power BI la medida `Color jugador` con los tres grados de `dim_equipo` | hexadecimal, `#rrggbb` | cuaderno 01 |
| `id_transfermarkt` | Identificador del jugador en Transfermarkt, para auditoría. Vacío en los 4 jugadores no emparejados | entero | Transfermarkt (cuaderno 06) |

## hechos_jugador.csv · 561 filas

Una fila por jugador. Todas las métricas están **por 90 minutos**: total de la temporada ÷ `minutos` × 90.

| Columna | Qué es | Unidad | De dónde sale |
|---|---|---|---|
| `id_jugador` | Clave del jugador | clave → `dim_jugador` | cuaderno 01 |
| `tiene_eventos` | Verdadero si el jugador está cruzado con los eventos de Opta (ver más abajo) | verdadero/falso | cuaderno 00 |
| `goles_90` | Goles | por 90 min | Understat `goals` |
| `goles_sin_penalti_90` | Goles sin contar penaltis | por 90 min | Understat `np_goals` |
| `xg_90` | Goles esperados de sus tiros | xG por 90 min | Understat `xg` |
| `xg_sin_penalti_90` | Goles esperados sin penaltis | xG por 90 min | Understat `np_xg` |
| `asistencias_90` | Asistencias | por 90 min | Understat `assists` |
| `xa_90` | Asistencias esperadas: xG de los tiros que sale de sus pases | xA por 90 min | Understat `xa` |
| `tiros_90` | Tiros | por 90 min | Understat `shots` |
| `pases_clave_90` | Pases que terminan en tiro | por 90 min | Understat `key_passes` |
| `xg_chain_90` | xG de todas las posesiones en las que participa | xG por 90 min | Understat `xg_chain` |
| `xg_buildup_90` | xGChain sin contar sus tiros ni sus pases clave | xG por 90 min | Understat `xg_buildup` |
| `entradas_intentadas_90` | Entradas intentadas: eventos `Tackle` (llega al balón) más eventos `Challenge` (el rival le regatea) | por 90 min | Opta (WhoScored) |
| `entradas_exitosas_90` | Entradas exitosas: eventos `Tackle` con resultado `Successful` (su equipo recupera la posesión) | por 90 min | Opta |
| `intercepciones_90` | Eventos `Interception` | por 90 min | Opta |
| `despejes_90` | Eventos `Clearance` | por 90 min | Opta |
| `pases_bloqueados_90` | Eventos `BlockedPass` | por 90 min | Opta |
| `duelos_aereos_disputados_90` | Duelos aéreos disputados: todos los eventos `Aerial`, ganados y perdidos | por 90 min | Opta |
| `duelos_aereos_ganados_90` | Duelos aéreos ganados: eventos `Aerial` con resultado `Successful` | por 90 min | Opta |
| `centros_90` | Pases con el calificador `Cross` | por 90 min | Opta |
| `toques_area_90` | Toques con x ≥ 83 e y entre 21,1 y 78,9 (área rival, en coordenadas de Opta) | por 90 min | Opta |
| `pct_entradas` | Entradas exitosas ÷ entradas intentadas × 100. Vacío si no intentó ninguna (40 jugadores, todos con menos de 600 minutos) | % (no va por 90) | Opta |
| `pct_duelos_aereos` | Duelos ganados ÷ duelos disputados × 100. Vacío si no disputó ninguno (44 jugadores, todos con menos de 600 minutos) | % (no va por 90) | Opta |
| `pctl_<métrica>` | Percentil de la métrica dentro de su grupo de posición: 21 columnas, una por métrica. El nombre es el de la métrica sin `_90`. Por ejemplo, `pctl_duelos_aereos_ganados` y `pctl_pct_entradas` | 0 a 100 | cuaderno 01 (ver más abajo) |
| `percentil_fiable` | Verdadero si el jugador tiene 600 minutos o más y su grupo tiene percentil | verdadero/falso | cuaderno 01 |
| `n_grupo_referencia` | Número de jugadores contra los que se calcula su percentil (los de su grupo con 600 minutos o más). Vacío si su grupo no tiene percentil | jugadores | cuaderno 01 |
| `muestra_reducida` | Verdadero si `n_grupo_referencia` es 30 o menos. Solo afecta a mediapunta (28) | verdadero/falso | cuaderno 01 |

### Volumen frente a éxito: entradas y duelos aéreos

En los eventos de Opta cada acción lleva un resultado (`outcome_type`):

- **Duelos aéreos.** Opta registra un evento `Aerial` por cada jugador del duelo: `Successful` para el que lo
  gana y `Unsuccessful` para el que lo pierde. En la temporada hay 9.734 de cada.
- **Entradas.**
  - `Tackle` es la entrada que llega al balón: `Successful` si su equipo se queda la posesión (7.522) y
    `Unsuccessful` si no, por ejemplo porque el balón sale del campo (5.052).
  - `Challenge` es la entrada fallida: el rival le regatea. Siempre es `Unsuccessful` (5.844).

**Diferencia con el TFM.** El TFM contaba todos los `Tackle` y todos los `Aerial`, sin mirar el resultado, y los
llamaba "entradas" y "duelos aéreos". Su "entradas" no coincide con ninguna columna de este modelo: le faltan
los `Challenge` para ser intentadas y le sobran los `Unsuccessful` para ser exitosas. Sus "duelos aéreos" son
los **disputados** de este modelo. Por eso las columnas de volumen se llaman "intentadas" y "disputadas", nunca
"ganadas" ni "exitosas".

Intercepciones, despejes, pases bloqueados, centros y toques en el área mantienen las definiciones del TFM.

---

## La regla de los 600 minutos

Un percentil compara a un jugador con su grupo. Si el grupo incluye a jugadores con muy pocos minutos, sus
valores por 90 son ruido: un gol en 40 minutos da 2,25 goles por 90. Por eso:

- **El grupo de referencia solo incluye jugadores con 600 minutos o más**, el mismo umbral del TFM.
- Los jugadores con menos de 600 minutos **sí aparecen** en las tablas y **sí tienen percentil**, calculado
  contra el grupo de referencia de su posición. Pero llevan `percentil_fiable` en falso para poder filtrarlos.

## Por qué los percentiles van por grupo de posición

Las métricas significan cosas distintas según el puesto. Un central despeja muchos balones por 90 y un extremo
casi ninguno: comparado con toda la liga, cualquier central saldría arriba en despejes y cualquier extremo abajo,
y el percentil no diría nada del jugador. Dentro de su grupo, el percentil responde a la pregunta útil:
**cómo está respecto a los que juegan donde él juega**.

Los grupos `sin_definir` y `sin_confirmar` no tienen percentil. No hay un grupo de referencia con sentido
para un jugador cuya posición no se conoce.

### Tamaño de cada grupo de referencia

| Grupo | Jugadores | Con 600 min o más (`n_grupo_referencia`) |
|---|---|---|
| pivote_mediocentro | 108 | 87 |
| lateral | 94 | 73 |
| central | 95 | 71 |
| extremo | 86 | 59 |
| delantero | 83 | 50 |
| mediapunta | 39 | **28**: muestra reducida; el panel deberá avisarlo |
| sin_definir | 28 | sin percentil |
| sin_confirmar | 28 | sin percentil |

Con 28 jugadores, cada puesto del ranking de mediapunta mueve el percentil 3,6 puntos.

## Fórmula del percentil

> **percentil = (número de jugadores del grupo de referencia con un valor estrictamente menor) ÷ (número de
> jugadores del grupo de referencia) × 100**

- Es la fórmula de las cifras publicadas en el TFM y las reproduce exactamente: Valjent percentil 9 en
  intercepciones, Llorente 98 y, en el bloque bajo, 10, 19 y 38.
- **Ningún jugador del grupo de referencia llega a 100.** El mejor de un grupo de n jugadores sale en
  (n − 1) ÷ n × 100: con 71 centrales, 98,59; con 87 en pivote_mediocentro, 98,85. Es una consecuencia de la fórmula, no un error de cálculo.
- Un jugador con **menos de 600 minutos** sí puede llegar a 100 si supera al mejor del grupo de referencia.
  Ese percentil lleva `percentil_fiable` en falso.
- Los empates comparten percentil: nadie empatado está "estrictamente por debajo" de otro.
- **No coincide con `rank(pct=True)` de pandas**, que es lo que usan algunas celdas del TFM. Esa fórmula da
  Valjent 10,8 y Llorente 100 sobre los mismos 65 centrales, y no reproduce las cifras publicadas.
- **Los percentiles de este proyecto no coinciden con los del TFM, y es lo esperado.** El grupo de centrales
  pasa de 65 a 71 jugadores porque este proyecto recupera jugadores que el TFM no cruzaba, y corrige a los dos
  David López. Con el grupo de este proyecto, Valjent sale en el percentil 12,68 de intercepciones y Llorente
  en el 98,59.

## tiene_eventos: "no hizo la acción" frente a "no tengo el dato"

- `tiene_eventos` = verdadero: el jugador está cruzado con los eventos de Opta por su identificador de
  WhoScored. Un 0 en una métrica de Opta significa que **no hizo esa acción**.
- `tiene_eventos` = falso: no hay un cruce seguro con los eventos. Las nueve métricas de Opta, los dos
  porcentajes y sus percentiles están **vacíos**, nunca a cero. Las métricas de Understat sí están.

Hay **5 jugadores** con `tiene_eventos` en falso. Todos tienen menos de 600 minutos, así que ninguno tiene
percentil fiable y ninguno altera un grupo de referencia:

| Jugador | Equipo | Minutos | Motivo |
|---|---|---|---|
| Carlos Benavídez | Alavés | 311 | su posible nombre en WhoScored, "Carlos Protesoni", solo comparte el nombre de pila |
| Yago Alonso | Elche | 275 | su posible nombre en WhoScored, "Yago Santiago", solo comparte el nombre de pila |
| Adam El Mokhtari | Elche | 85 | su posible nombre en WhoScored, "Adam Boayar", solo comparte el nombre de pila |
| Sergio Lozano | Rayo Vallecano | 7 | traspaso dudoso: Understat y los eventos solo lo sitúan en el Levante |
| Rubén Iranzo | Valencia | 1 | el único candidato, "Rubo", es un indicio demasiado débil |

Detalle y minutos en `data/cruces_descartados.csv`.

## Posición deducida de las alineaciones

Hay 38 jugadores de campo con minutos en Understat que no están en el fichero propio de posiciones. Su
posición se deduce de sus titularidades en las alineaciones de WhoScored (`posicion_origen` =
`alineaciones_whoscored`):

- **Regla:** al menos 3 titularidades y más de la mitad de ellas en el mismo grupo de posición.
- **10 confirmados** a mano, con la posición propuesta por la regla.
- **28 sin confirmar**: 15 con menos de 3 titularidades, 11 que nunca fueron titulares y 2 sin identificador de
  WhoScored. Están en el grupo `sin_confirmar`, sin percentil. Ninguno pasa de 320 minutos.

El recuento de cada uno está en `data/posiciones_alineaciones.csv`.

### Equivalencia de puestos de WhoScored

| Puesto de WhoScored | Significado | Posición | Grupo |
|---|---|---|---|
| DC | defensa central | central | central |
| DL, DR | lateral izquierdo, derecho | lateral | lateral |
| DML, DMR | carrilero izquierdo, derecho | lateral | lateral |
| DMC | mediocentro defensivo | pivote | pivote_mediocentro |
| MC | mediocentro | mediocentro | pivote_mediocentro |
| AMC | mediapunta | mediapunta | mediapunta |
| AML, AMR | extremo izquierdo, derecho | extremo | extremo |
| ML, MR | interior/volante izquierdo, derecho | extremo | extremo |
| **FWL, FWR** | **delantero escorado a la izquierda, derecha** | **extremo** | **extremo** |
| FW | delantero centro | delantero | delantero |

**FWL y FWR van a extremo, y eso difiere de la equivalencia que usaba el TFM**, que los mandaba a delantero.
El cambio sigue a mi propio fichero de posiciones: entre los jugadores que están en él, los titulares en FWL
son extremos 57 veces y delanteros 10, y en FWR, extremos 46 veces y delanteros 28. La equivalencia del TFM no
seguía el criterio del propio fichero que validaba. Con el cambio, Bryan Zaragoza y Yáser Asprilla son extremos.

---

## Colores de equipo

**Qué son.** Los dos colores de la **camiseta** de la primera equipación 2025/26. El pantalón y las medias no
cuentan: el Atlético es rojo y blanco, aunque su pantalón sea azul.

**De dónde salen.** De la plantilla de equipación de la ficha de cada club en la Wikipedia en inglés: los campos
`body1`, `leftarm1` y `rightarm1` (color de fondo del cuerpo y de cada manga) y `pattern_b1`, `pattern_la1` y
`pattern_ra1` (imagen con las rayas, franjas o ribetes). El cuaderno 05 pinta la camiseta como lo hace
Wikipedia y mide qué superficie ocupa cada color. Se usa la versión de cada artículo a 31 de mayo de 2026,
último día de la temporada, porque las fichas actuales ya muestran la equipación 2026/27. Consultado el
2026-11-16.

**Color primario.** El blanco no identifica a ningún equipo salvo al Real Madrid: al Athletic nadie lo llama
blanco. Por eso, de los dos colores con más superficie, el primario es el que no es blanco. Hay tres excepciones
decididas por el autor:

- **Real Madrid:** blanco.
- **Barcelona:** el grana, su segundo color de camiseta, en lugar del azul.
- **Secundario del Celta:** blanco, fijado por el autor (`color_secundario_origen` = `revision_autor`). El segundo
  color medido era negro, pero es el contorno del cuello: un 4 % de la camiseta.
- **Valencia:** su camiseta es blanca. Se usa el naranja dominante de su escudo (`#e33e07`). Es el único color
  primario que no sale de la plantilla de Wikipedia, y por eso es el único con `color_origen` = `revision_autor`.

**Son colores aproximados, no colores de marca oficiales.** Wikipedia usa colores genéricos: el mismo `#ff0000`
para casi todos los rojos.

> **El color no identifica al equipo en este panel. Lo hace el escudo.** Con este criterio hay 7 equipos rojos
> (Athletic, Atlético, Girona, Mallorca, Osasuna, Rayo y Sevilla) y 5 azules (Alavés, Espanyol, Getafe, Oviedo
> y Real Sociedad), y varios comparten exactamente el mismo hexadecimal. El color sirve para acentuar la ficha
> del jugador seleccionado, donde solo hay un equipo en pantalla. No debe usarse para distinguir equipos en un
> gráfico. Es una decisión de diseño que viene de los datos.

| Equipo | Artículo | Revisión | Fecha de la revisión | Primario | Secundario | Origen del primario |
|---|---|---|---|---|---|---|
| Alaves | [Deportivo Alavés](https://en.wikipedia.org/wiki/Deportivo_Alavés) | 1355951832 | 2026-05-24 | `#0066e1` | `#ffffff` | wikipedia_equipacion |
| Athletic Club | [Athletic Bilbao](https://en.wikipedia.org/wiki/Athletic_Bilbao) | 1356670834 | 2026-05-29 | `#ff0b0b` | `#ffffff` | wikipedia_equipacion |
| Atletico Madrid | [Atlético Madrid](https://en.wikipedia.org/wiki/Atlético_Madrid) | 1357137026 | 2026-05-31 | `#ff0000` | `#ffffff` | wikipedia_equipacion |
| Barcelona | [FC Barcelona](https://en.wikipedia.org/wiki/FC_Barcelona) | 1356877329 | 2026-05-30 | `#ba002f` | `#14266e` | wikipedia_equipacion |
| Celta Vigo | [RC Celta de Vigo](https://en.wikipedia.org/wiki/RC_Celta_de_Vigo) | 1356706508 | 2026-05-29 | `#a3d0f4` | `#ffffff` (revisión del autor) | wikipedia_equipacion |
| Elche | [Elche CF](https://en.wikipedia.org/wiki/Elche_CF) | 1356630873 | 2026-05-28 | `#008127` | `#ffffff` | wikipedia_equipacion |
| Espanyol | [RCD Espanyol](https://en.wikipedia.org/wiki/RCD_Espanyol) | 1356534454 | 2026-05-28 | `#0000ff` | `#ffffff` | wikipedia_equipacion |
| Getafe | [Getafe CF](https://en.wikipedia.org/wiki/Getafe_CF) | 1356233553 | 2026-05-26 | `#0000ff` | `#ff0000` | wikipedia_equipacion |
| Girona | [Girona FC](https://en.wikipedia.org/wiki/Girona_FC) | 1356571866 | 2026-05-28 | `#ff0000` | `#ffffff` | wikipedia_equipacion |
| Levante | [Levante UD](https://en.wikipedia.org/wiki/Levante_UD) | 1357000448 | 2026-05-31 | `#661424` | `#222730` | wikipedia_equipacion |
| Mallorca | [RCD Mallorca](https://en.wikipedia.org/wiki/RCD_Mallorca) | 1356065821 | 2026-05-25 | `#ff0000` | `#000000` | wikipedia_equipacion |
| Osasuna | [CA Osasuna](https://en.wikipedia.org/wiki/CA_Osasuna) | 1356879811 | 2026-05-30 | `#ff0000` | `#001355` | wikipedia_equipacion |
| Rayo Vallecano | [Rayo Vallecano](https://en.wikipedia.org/wiki/Rayo_Vallecano) | 1356594400 | 2026-05-28 | `#ff0000` | `#ffffff` | wikipedia_equipacion |
| Real Betis | [Real Betis](https://en.wikipedia.org/wiki/Real_Betis) | 1356116714 | 2026-05-25 | `#349b5c` | `#ffffff` | wikipedia_equipacion |
| Real Madrid | [Real Madrid CF](https://en.wikipedia.org/wiki/Real_Madrid_CF) | 1356275441 | 2026-05-26 | `#ffffff` | `#d9d5d2` | wikipedia_equipacion |
| Real Oviedo | [Real Oviedo](https://en.wikipedia.org/wiki/Real_Oviedo) | 1356732491 | 2026-05-29 | `#0000dd` | `#e1c67a` | wikipedia_equipacion |
| Real Sociedad | [Real Sociedad](https://en.wikipedia.org/wiki/Real_Sociedad) | 1356624551 | 2026-05-28 | `#475cad` | `#ffffff` | wikipedia_equipacion |
| Sevilla | [Sevilla FC](https://en.wikipedia.org/wiki/Sevilla_FC) | 1356512655 | 2026-05-28 | `#e20000` | `#ffffff` | wikipedia_equipacion |
| Valencia | [Valencia CF](https://en.wikipedia.org/wiki/Valencia_CF) | 1356063522 | 2026-05-25 | `#e33e07` | `#ffffff` | revision_autor |
| Villarreal | [Villarreal CF](https://en.wikipedia.org/wiki/Villarreal_CF) | 1356669725 | 2026-05-29 | `#ffff00` | `#01004e` | wikipedia_equipacion |

El color dominante del escudo (cuaderno 03) no se usa en el modelo. Queda en `data/escudos.csv` y en
`data/colores_equipos.csv` (`color_escudo`) para comparar.

## Retratos de jugadores

**Fuente: Transfermarkt** (transfermarkt.es), plantillas de la temporada 2025/26. Power BI no recorta imágenes,
así que los retratos se alojan en este repositorio ya recortados en círculo, para un panel académico sin ánimo de
lucro. La url de origen de cada uno está en `data/fotos_transfermarkt.csv` y en `url_foto_transfermarkt`. Power BI
(categoría "URL de imagen") y Tableau (rol de imagen) cargan `url_foto` directamente. El panel deberá citar la
fuente de forma visible.

- Un jugador se empareja dentro de sus clubes de la temporada, por nombre exacto y con la edad comprobada contra
  WhoScored (±1 año). 8 parejas con nombre parecido las revisó y confirmó el autor una a una, y otros 2 jugadores
  que Transfermarkt escribe de otra forma (Adrián de la Fuente y Djené Dakonam) los localizó a mano.
- **539** jugadores tienen retrato de Transfermarkt y **22** no: 18 que en Transfermarkt solo tienen la
  silueta genérica, 3 sin coincidencia y 1 con cruce dudoso (Sergio Lozano, el mismo cruce de
  `cruces_descartados.csv`).
- **Recorte (cuaderno 08).** Se usa la versión grande del retrato (300 × 390 px). Se detecta la cara con OpenCV
  y se centra la cabeza en un círculo de 200 × 200 px. El círculo mide un 30 % más que el ancho de la foto, para
  que entre la cabeza entera (los retratos vienen muy cerrados); lo que queda fuera de la foto a los lados se
  rellena prolongando su borde y desenfocándolo, nunca con la cara. En vertical se usa el alto completo de la
  foto. A los PNG sin fondo se les pone gris claro detrás. El método de detección de cada uno está en
  `data/retratos_recortados.csv`.

## Datos de scouting de Transfermarkt

- Salen de las páginas de plantilla detallada 2025/26 de los 20 clubes, las mismas de los retratos, descargadas
  el 16/11/2026. Solo se usan para los 557 jugadores emparejados con seguridad.
- **Sin dato, la celda queda vacía.** Nunca hay ceros ni "desconocido".
- **No hay fecha de fin de contrato.** Esas páginas no la traen: en la vista de una temporada ya terminada,
  Transfermarkt muestra el club actual del jugador en lugar del contrato.
- Los 4 jugadores sin emparejar (Carlos Benavídez, Yago Alonso, Adam El Mokhtari y Sergio Lozano) no tienen
  edad ni ningún otro de estos datos. Ninguno tiene percentil fiable.
- Entre los 368 jugadores con percentil fiable: todos tienen edad, altura y nacionalidad; a uno le falta el pie
  y a uno el valor de mercado.

## Ficheros de trazabilidad (`data/`)

| Fichero | Filas | Contenido |
|---|---|---|
| `mapa_nombres.csv` | 561 | Un jugador del modelo por fila: nombre en cada fuente, identificadores de Understat y WhoScored, minutos, partidos en Understat, partidos con eventos y origen del cruce |
| `eventos_por_jugador.csv` | 556 | Totales de las acciones de Opta por identificador de WhoScored, partidos con eventos y reparto por club. Incluye `entradas_tfm` (todos los `Tackle`, la definición del TFM), que solo usa la auditoría. Sale del fichero de eventos en bruto del TFM (`eventos_laliga_2526.parquet`, no versionado), que tenía 577.205 eventos de todos los tipos; aquí solo quedan las acciones agregadas por jugador. La página Método del panel da la suma de las acciones defensivas de este fichero: 67.953 (entradas intentadas, intercepciones, despejes, pases bloqueados y duelos aéreos disputados; los exitosos y los ganados ya están dentro) |
| `posiciones_alineaciones.csv` | 38 | Titularidades por puesto, propuesta, si es concluyente y si está confirmada |
| `sin_minutos.csv` | 112 | Jugadores del fichero de posiciones que no jugaron en LaLiga 2025/26 |
| `cruces_descartados.csv` | 7 | Cruces dudosos que no se aplican, con su motivo y su efecto |
| `escudos.csv` | 20 | Origen de cada escudo (Wikidata o web oficial), url, licencia, autor (en los de Commons), fecha de descarga, tamaño original, escala aplicada, color primario y su peso en el escudo |
| `colores_equipos.csv` | 20 | Artículo de Wikipedia, revisión y fechas, campos de la plantilla de equipación, los dos colores medidos con su superficie, color primario, secundario, origen y color dominante del escudo (`color_escudo`, solo para comparar) |
| `wikitexto_equipaciones.json` | 20 artículos | Copia de lo leído en Wikipedia: líneas de la equipación de cada ficha con su revisión y fecha, e imágenes de los patrones y siluetas de la plantilla. Permite ejecutar el cuaderno 05 sin conexión |
| `fotos_transfermarkt.csv` | 561 | Para cada jugador, el candidato de Transfermarkt, sus datos de scouting (nacimiento, altura, pie, nacionalidad, valor de mercado estimado y fecha de descarga), su estado (`claro`, `confirmado_autor`, `dudoso` o `sin_coincidencia`), el motivo, si se aplica, y el código de respuesta y el peso de la url |
| `retratos_recortados.csv` | 539 | Para cada retrato recortado, la url original en Transfermarkt, el tamaño original, cómo se detectó la cara y el peso del PNG |
| `fotos_wikidata.csv` | 561 | Para cada jugador, la entidad de Wikidata aceptada (si la hay), la url, licencia, autor y tamaño de su foto, y el motivo cuando no se acepta ninguna |

### Valores de `origen` en `mapa_nombres.csv`

| origen | Jugadores | Qué es |
|---|---|---|
| `directo` | 466 | Cruzados por el TFM sin cambios |
| `recuperado_15` | 15 | Estaban en la tabla del TFM, pero con las métricas de Opta vacías porque el nombre no cruzó con los eventos. Recuperados por nombre en WhoScored, mismo equipo y mismos partidos |
| `recuperado_36` | 36 | En el fichero de posiciones con otro nombre que en Understat. Recuperados por nombre, mismo equipo y mismos partidos |
| `traspasado` | 6 | Understat los pone en su club anterior. Equipo = el del fichero de posiciones (club actual); minutos y partidos de toda la temporada; eventos de los dos clubes sumados |
| `recuperado_grafia` | 2 | Jugadores de Understat sin posición cuyo nombre en WhoScored es otra grafía: Yeremi/Yéremy Pino y Stanis Idumbo (Muzambo) |
| `understat_sin_posicion` | 36 | Jugadores de campo de Understat que no están en el fichero de posiciones |

Los 38 jugadores con la posición deducida de las alineaciones son los 36 `understat_sin_posicion` más los 2
`recuperado_grafia`.

Además de los 6 traspasados, hay otros 6 jugadores que tienen eventos con dos clubes y entran como directos:
Rodrigo Mendoza, Álvaro Núñez, Ilias Akhomach, Karl Etta Eyong, Adrià Pedrosa y Urko González de Zárate.
Como los eventos se cruzan por identificador, suman los dos clubes, y `equipos_temporada` muestra el reparto.

---

## Formato largo para la página Ficha

En la Ficha las métricas van en el eje vertical, una fila por métrica. Estas tres tablas dan los mismos datos que
`hechos_jugador` y `dim_jugador`, pero en formato largo. `hechos_jugador` no cambia: alimenta la página Buscador.

### dim_metrica.csv · 21 filas

| Columna | Qué es |
|---|---|
| `id_metrica` | Clave propia de la métrica |
| `metrica` | Nombre de la columna en `hechos_jugador` (p. ej. `intercepciones_90`) |
| `nombre` | Cómo se lee en el panel ("Intercepciones") |
| `nombre_corto` | Versión corta para cuando no cabe ("Intercep.") |
| `bloque` | `defensa` (9 métricas), `con_balon` (6) o `ataque` (6) |
| `orden` | Orden dentro del bloque, desde 1 |
| `unidad` | `por_90` o `porcentaje`. La unidad está aquí y no en el número |

Entradas intentadas y duelos aéreos disputados están en el bloque defensa (orden 8 y 9), aunque la Ficha no los pinte.

### hechos_metrica.csv · 11.781 filas (561 jugadores × 21 métricas)

| Columna | Qué es |
|---|---|
| `id_jugador`, `id_metrica` | Claves hacia `dim_jugador` y `dim_metrica` |
| `valor` | Valor por 90 minutos, o porcentaje de éxito si la unidad es `porcentaje`. Vacío si no hay dato (129 filas: los 5 jugadores sin eventos de Opta y los que no intentaron ninguna entrada o duelo), nunca cero |
| `percentil` | El mismo percentil de `hechos_jugador`, redondeado sin decimales. Vale para todos los jugadores; para saber si es fiable, `hechos_jugador.percentil_fiable` |

### hechos_ficha.csv · 5.049 filas (561 jugadores × 9 atributos)

| Columna | Qué es |
|---|---|
| `id_jugador` | Clave hacia `dim_jugador` |
| `orden` | Orden del atributo en la ficha, de 1 a 9 |
| `atributo` | Equipo, Puesto, Edad, Altura, Pie, Nacionalidad, Minutos, Partidos, Valor estimado |
| `valor` | Texto ya formateado: el equipo con su `nombre_equipo`, "27 años", "1,83 m", "España / Francia", "3.330", "4,5 M€". Vacío si no hay dato |

Relaciones en el modelo de Power BI, todas de uno a muchos y en una sola dirección: `dim_metrica` → `hechos_metrica`,
`dim_jugador` → `hechos_metrica` y `dim_jugador` → `hechos_ficha`.
