# Campos calculados del panel de Tableau

Generado por `notebooks/09_tabla_tableau.ipynb` a partir de los nombres de columna de `datos_tableau.csv`: si se
cambia una métrica, se vuelve a ejecutar el cuaderno y este fichero cambia con ella.

Cada bloque se pega en **Análisis → Crear campo calculado**, con el nombre que lleva encima.

> **Sin probar en Tableau.** Estos campos están escritos a partir del CSV, pero no se han pegado ni ejecutado en
> Tableau. Si alguno da error al pegarlo, hay que corregirlo aquí, en el cuaderno 09, y volver a generarlo.

## Parámetros

Crear dos parámetros (**clic derecho en el panel de datos → Crear parámetro**):

| Nombre | Tipo de datos | Valores permitidos | Valor actual |
|---|---|---|---|
| `Eje X` | Cadena | Lista | `Intercepciones` |
| `Eje Y` | Cadena | Lista | `Duelos aéreos ganados` |

Lista de valores, igual para los dos (se puede pegar entera con **Agregar desde el portapapeles**):

```
Intercepciones
Entradas exitosas
% de entradas exitosas
Despejes
Pases bloqueados
Duelos aéreos ganados
% de duelos aéreos ganados
Entradas intentadas
Duelos aéreos disputados
Pases clave
xG chain
xG buildup
Centros
Toques en el área
Tiros
Goles
Goles sin penalti
xG
xG sin penalti
Asistencias
xA
```

Después, **clic derecho en cada parámetro → Mostrar parámetro**.

## Valor del eje X

```
CASE [Eje X]
WHEN "Intercepciones" THEN [Intercepciones]
WHEN "Entradas exitosas" THEN [Entradas exitosas]
WHEN "% de entradas exitosas" THEN [% de entradas exitosas]
WHEN "Despejes" THEN [Despejes]
WHEN "Pases bloqueados" THEN [Pases bloqueados]
WHEN "Duelos aéreos ganados" THEN [Duelos aéreos ganados]
WHEN "% de duelos aéreos ganados" THEN [% de duelos aéreos ganados]
WHEN "Entradas intentadas" THEN [Entradas intentadas]
WHEN "Duelos aéreos disputados" THEN [Duelos aéreos disputados]
WHEN "Pases clave" THEN [Pases clave]
WHEN "xG chain" THEN [xG chain]
WHEN "xG buildup" THEN [xG buildup]
WHEN "Centros" THEN [Centros]
WHEN "Toques en el área" THEN [Toques en el área]
WHEN "Tiros" THEN [Tiros]
WHEN "Goles" THEN [Goles]
WHEN "Goles sin penalti" THEN [Goles sin penalti]
WHEN "xG" THEN [xG]
WHEN "xG sin penalti" THEN [xG sin penalti]
WHEN "Asistencias" THEN [Asistencias]
WHEN "xA" THEN [xA]
END
```

## Valor del eje Y

```
CASE [Eje Y]
WHEN "Intercepciones" THEN [Intercepciones]
WHEN "Entradas exitosas" THEN [Entradas exitosas]
WHEN "% de entradas exitosas" THEN [% de entradas exitosas]
WHEN "Despejes" THEN [Despejes]
WHEN "Pases bloqueados" THEN [Pases bloqueados]
WHEN "Duelos aéreos ganados" THEN [Duelos aéreos ganados]
WHEN "% de duelos aéreos ganados" THEN [% de duelos aéreos ganados]
WHEN "Entradas intentadas" THEN [Entradas intentadas]
WHEN "Duelos aéreos disputados" THEN [Duelos aéreos disputados]
WHEN "Pases clave" THEN [Pases clave]
WHEN "xG chain" THEN [xG chain]
WHEN "xG buildup" THEN [xG buildup]
WHEN "Centros" THEN [Centros]
WHEN "Toques en el área" THEN [Toques en el área]
WHEN "Tiros" THEN [Tiros]
WHEN "Goles" THEN [Goles]
WHEN "Goles sin penalti" THEN [Goles sin penalti]
WHEN "xG" THEN [xG]
WHEN "xG sin penalti" THEN [xG sin penalti]
WHEN "Asistencias" THEN [Asistencias]
WHEN "xA" THEN [xA]
END
```

## Percentil del eje X

```
CASE [Eje X]
WHEN "Intercepciones" THEN [Intercepciones (percentil)]
WHEN "Entradas exitosas" THEN [Entradas exitosas (percentil)]
WHEN "% de entradas exitosas" THEN [% de entradas exitosas (percentil)]
WHEN "Despejes" THEN [Despejes (percentil)]
WHEN "Pases bloqueados" THEN [Pases bloqueados (percentil)]
WHEN "Duelos aéreos ganados" THEN [Duelos aéreos ganados (percentil)]
WHEN "% de duelos aéreos ganados" THEN [% de duelos aéreos ganados (percentil)]
WHEN "Entradas intentadas" THEN [Entradas intentadas (percentil)]
WHEN "Duelos aéreos disputados" THEN [Duelos aéreos disputados (percentil)]
WHEN "Pases clave" THEN [Pases clave (percentil)]
WHEN "xG chain" THEN [xG chain (percentil)]
WHEN "xG buildup" THEN [xG buildup (percentil)]
WHEN "Centros" THEN [Centros (percentil)]
WHEN "Toques en el área" THEN [Toques en el área (percentil)]
WHEN "Tiros" THEN [Tiros (percentil)]
WHEN "Goles" THEN [Goles (percentil)]
WHEN "Goles sin penalti" THEN [Goles sin penalti (percentil)]
WHEN "xG" THEN [xG (percentil)]
WHEN "xG sin penalti" THEN [xG sin penalti (percentil)]
WHEN "Asistencias" THEN [Asistencias (percentil)]
WHEN "xA" THEN [xA (percentil)]
END
```

## Percentil del eje Y

```
CASE [Eje Y]
WHEN "Intercepciones" THEN [Intercepciones (percentil)]
WHEN "Entradas exitosas" THEN [Entradas exitosas (percentil)]
WHEN "% de entradas exitosas" THEN [% de entradas exitosas (percentil)]
WHEN "Despejes" THEN [Despejes (percentil)]
WHEN "Pases bloqueados" THEN [Pases bloqueados (percentil)]
WHEN "Duelos aéreos ganados" THEN [Duelos aéreos ganados (percentil)]
WHEN "% de duelos aéreos ganados" THEN [% de duelos aéreos ganados (percentil)]
WHEN "Entradas intentadas" THEN [Entradas intentadas (percentil)]
WHEN "Duelos aéreos disputados" THEN [Duelos aéreos disputados (percentil)]
WHEN "Pases clave" THEN [Pases clave (percentil)]
WHEN "xG chain" THEN [xG chain (percentil)]
WHEN "xG buildup" THEN [xG buildup (percentil)]
WHEN "Centros" THEN [Centros (percentil)]
WHEN "Toques en el área" THEN [Toques en el área (percentil)]
WHEN "Tiros" THEN [Tiros (percentil)]
WHEN "Goles" THEN [Goles (percentil)]
WHEN "Goles sin penalti" THEN [Goles sin penalti (percentil)]
WHEN "xG" THEN [xG (percentil)]
WHEN "xG sin penalti" THEN [xG sin penalti (percentil)]
WHEN "Asistencias" THEN [Asistencias (percentil)]
WHEN "xA" THEN [xA (percentil)]
END
```

## Mediana del eje X

```
{ FIXED [Puesto] : MEDIAN(IIF([Percentil fiable], [Valor del eje X], NULL)) }
```

## Mediana del eje Y

```
{ FIXED [Puesto] : MEDIAN(IIF([Percentil fiable], [Valor del eje Y], NULL)) }
```

**Por qué FIXED y no WINDOW_MEDIAN.** La línea de referencia tiene que marcar lo mismo contra lo que se calculó el
percentil: el grupo de referencia, que son los jugadores de ese puesto con percentil fiable (600 minutos o más).
Con WINDOW_MEDIAN la mediana sería la de los jugadores que se ven, y se movería al filtrar por edad, equipo o
minutos: un jugador en el percentil 50 dejaría de caer sobre la línea y el panel se contradiría. Con FIXED sobre
`Puesto`, cada jugador lleva la mediana de su grupo de referencia, que cambia al cambiar de puesto y no cambia con
los demás filtros.

Para que eso se cumpla:

- Los filtros de edad, equipo y minutos tienen que ser **filtros normales de dimensión**. Si alguno se añade al
  contexto (**Agregar al contexto**) o se pone como filtro de la fuente de datos o del extracto, se aplica antes
  del FIXED y la mediana vuelve a moverse.
- En la vista tiene que haber **un solo puesto** (filtro o parámetro de selección única): cada puesto tiene su
  mediana, y con varios a la vez no hay una única línea.
- La línea de referencia se hace con **Analítica → Línea de referencia → Valor: Mediana del eje X, agregado
  Promedio**. Dentro de un puesto el valor es el mismo para todos sus jugadores, así que promedio, mínimo o máximo
  dan lo mismo.
- Un jugador sin dato en la métrica no cuenta para la mediana. La mediana del grupo y el percentil 50 no coinciden
  al milímetro: el percentil cuenta quién queda estrictamente por debajo, así que el jugador mediano sale en torno
  al 49-50.

## Cuadrante

```
IF ISNULL([Valor del eje X]) OR ISNULL([Valor del eje Y]) THEN "Sin dato"
ELSEIF [Valor del eje X] >= [Mediana del eje X] AND [Valor del eje Y] >= [Mediana del eje Y]
    THEN "Por encima en " + [Eje X] + " y en " + [Eje Y]
ELSEIF [Valor del eje X] >= [Mediana del eje X]
    THEN "Por encima en " + [Eje X] + ", por debajo en " + [Eje Y]
ELSEIF [Valor del eje Y] >= [Mediana del eje Y]
    THEN "Por debajo en " + [Eje X] + ", por encima en " + [Eje Y]
ELSE "Por debajo en " + [Eje X] + " y en " + [Eje Y]
END
```

Es un cálculo de fila, no de tabla: compara cada jugador con la mediana de su grupo de referencia, la misma de las
líneas, así que tampoco cambia con los filtros de edad, equipo o minutos. Quien está justo en la mediana cuenta
como «por encima».
