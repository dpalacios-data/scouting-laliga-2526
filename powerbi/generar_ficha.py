"""Genera la página Ficha del informe PBIR (powerbi/) y añade al modelo las medidas que usa.

Uso: python powerbi/generar_ficha.py   (con Power BI Desktop cerrado; luego abrir el .pbip)

Lleva ya lo que Power BI cambia al guardar (esquema 2.14, sin 'outline', autoSizeColumnWidth en true).
Antes de volver a ejecutarlo, comprobar con git diff si Power BI ha cambiado algo más y llevarlo aquí.
"""
import json, os, re, shutil, uuid

# Saltos de línea con que Power BI guarda los .tmdl
CRLF = "\r\n"
RAIZ = os.path.dirname(os.path.abspath(__file__))
REP = f"{RAIZ}/scouting-laliga-2526.Report"
SEM = f"{RAIZ}/scouting-laliga-2526.SemanticModel/definition/tables"
PAG = "ficha"
VIS = f"{REP}/definition/pages/{PAG}/visuals"
ESQ = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json"
BLANCO, GRIS, OSCURO, ROJO, RAYA, FONDO = "#F2F5F8", "#79879A", "#44505F", "#FF4B44", "#1A212C", "#07090E"
BARRA = "#2C1316"   # rojo #FF4B44 al 15 % sobre el fondo
# Nombre interno de las fuentes en el formato de los objetos visuales (DIN se guarda así al elegirla en Power BI)
FUENTES = {"DIN": "wf_standard-font, helvetica, arial, sans-serif"}


def lit(v):
    txt = ("true" if v else "false") if isinstance(v, bool) else (f"{v}D" if isinstance(v, (int, float)) else f"'{v}'")
    return {"expr": {"Literal": {"Value": txt}}}


def color(c):
    return {"solid": {"color": lit(c)}}


def col(t, c):
    return {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}


def med(t, m):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": t}}, "Property": m}}


def proy(campo, ref, nombre=None):
    p = {"field": campo, "queryRef": ref, "nativeQueryRef": ref.split(".", 1)[1]}
    if nombre is not None:
        p["displayName"] = nombre
    return p


def sin_marco():
    return {k: [{"properties": {"show": lit(False)}}] for k in ("background", "border", "title", "visualHeader", "dropShadow")} | \
        {"padding": [{"properties": {k: lit(0) for k in ("top", "bottom", "left", "right")}}]}


visuales = []


def visual(nombre, x, y, w, h, cuerpo, filtros=None):
    v = {"$schema": ESQ, "name": nombre,
         "position": {"x": x, "y": y, "z": len(visuales) * 1000, "height": h, "width": w, "tabOrder": len(visuales) * 1000},
         "visual": cuerpo}
    if filtros:
        v["filterConfig"] = {"filters": filtros}
    visuales.append(v)


def texto(nombre, x, y, w, h, contenido, tam, c, familia="Segoe UI", negrita=False):
    """Texto en una forma: sin margen interior ni barra de desplazamiento. contenido = texto o medida."""
    # Una medida va envuelta en "expr" para que la forma muestre su valor
    valor = {"expr": contenido} if isinstance(contenido, dict) else lit(contenido)
    visual(nombre, x, y, w, h, {"visualType": "shape", "objects": {
        "shape": [{"properties": {"tileShape": lit("rectangle")}}],
        "fill": [{"properties": {"show": lit(False)}}],
        "outline": [{"properties": {"show": lit(False)}}],
        "text": [{"properties": {"show": lit(True)}},
                 {"selector": {"id": "default"}, "properties": {
                     "text": valor, "fontColor": color(c), "fontSize": lit(tam), "fontFamily": lit(FUENTES.get(familia, familia)), "bold": lit(negrita),
                     "horizontalAlignment": lit("left"), "verticalAlignment": lit("middle"),
                     "leftMargin": lit(0), "rightMargin": lit(0), "topMargin": lit(0), "bottomMargin": lit(0)}}]},
        "visualContainerObjects": sin_marco()})


def rect(nombre, x, y, w, h, c):
    visual(nombre, x, y, w, h, {"visualType": "shape", "objects": {
        "shape": [{"properties": {"tileShape": lit("rectangle")}}],
        "fill": [{"properties": {"show": lit(True)}}, {"properties": {"fillColor": color(c), "transparency": lit(0)}, "selector": {"id": "default"}}],
        "outline": [{"properties": {"show": lit(False)}}]}, "visualContainerObjects": sin_marco()})


def tabla(nombre, x, y, w, h, proyecciones, anchos, formatos=(), cabecera=True, orden=None, imagen=None, filtros=None, fila=1,
          sentido="Ascending"):
    """Tabla sin fondo; cabecera=False la reduce a una línea mínima del color del fondo (no se puede ocultar)."""
    objetos = {
        "grid": [{"properties": {"gridHorizontal": lit(True), "gridHorizontalColor": color(RAYA), "gridHorizontalWeight": lit(1),
                                 "gridVertical": lit(False), "outlineStyle": lit(0), "rowPadding": lit(fila),
                                 **({"imageHeight": lit(imagen)} if imagen else {})}}],
        "columnHeaders": [{"properties": {"fontColor": color(OSCURO if cabecera else FONDO), "fontSize": lit(8 if cabecera else 1),
                                          "backColor": color(FONDO), "wordWrap": lit(False), "autoSizeColumnWidth": lit(True)}}],
        "values": [{"properties": {"backColorPrimary": color(FONDO), "backColorSecondary": color(FONDO), "wordWrap": lit(False)}}],
        "total": [{"properties": {"totals": lit(False)}}],
        "columnWidth": [{"properties": {"value": lit(a)}, "selector": {"metadata": p["queryRef"]}} for p, a in zip(proyecciones, anchos)],
        "columnFormatting": list(formatos)}
    q = {"queryState": {"Values": {"projections": proyecciones}}}
    if orden:
        q["sortDefinition"] = {"sort": [{"field": orden, "direction": sentido}]}
    visual(nombre, x, y, w, h, {"visualType": "tableEx", "query": q, "objects": objetos, "visualContainerObjects": sin_marco()}, filtros)


def fmt(ref, tinta=None, alineacion=None, barras=False):
    p = {}
    if tinta:
        p["fontColor"] = color(tinta)
    if alineacion:
        p["alignment"] = lit(alineacion)
    if barras:
        p["dataBars"] = {"minValue": lit(0), "maxValue": lit(100), "positiveColor": color(BARRA), "negativeColor": color(BARRA),
                         "axisColor": color(FONDO), "reverseDirection": lit(False), "hideText": lit(False),
                         "totalMatchingOption": {"expr": {"Literal": {"Value": "1L"}}}}
    return {"properties": p, "selector": {"metadata": ref}}


def filtro_cat(nombre, tabla_, columna, valores):
    return {"name": nombre, "field": col(tabla_, columna), "type": "Categorical", "howCreated": "User",
            "filter": {"Version": 2, "From": [{"Name": "t", "Entity": tabla_, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": columna}}],
                                                       "Values": [[{"Literal": {"Value": f"'{v}'"}}] for v in valores]}}}]}}


def filtro_un_jugador(nombre):
    """Filtro de objeto visual: el objeto solo muestra algo cuando hay un único jugador elegido."""
    return [{"name": nombre, "field": med("dim_jugador", "Jugador elegido"), "type": "Advanced", "howCreated": "User",
             "filter": {"Version": 2, "From": [{"Name": "d", "Entity": "dim_jugador", "Type": 0}],
                        "Where": [{"Condition": {"Comparison": {"ComparisonKind": 0,
                                   "Left": {"Measure": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "Jugador elegido"}},
                                   "Right": {"Literal": {"Value": "1L"}}}}}]}}]


def filtro_n(nombre, n, descendente):
    """Filtro N superior (descendente) o N inferior sobre dim_metrica[nombre_corto], ordenado por 'Percentil ranking'.
    Esa medida está vacía cuando la métrica no tiene valor, así que esas métricas no entran nunca."""
    sub = {"Version": 2,
           "From": [{"Name": "m", "Entity": "dim_metrica", "Type": 0}, {"Name": "h", "Entity": "hechos_metrica", "Type": 0}],
           "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "nombre_corto"}, "Name": "field"}],
           "OrderBy": [{"Direction": 2 if descendente else 1,
                        "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "h"}}, "Property": "Percentil ranking"}}}],
           "Top": n}
    return [{"name": nombre, "field": col("dim_metrica", "nombre_corto"), "type": "TopN", "howCreated": "User",
             "filter": {"Version": 2,
                        "From": [{"Name": "subquery", "Expression": {"Subquery": {"Query": sub}}, "Type": 2},
                                 {"Name": "m", "Entity": "dim_metrica", "Type": 0}],
                        "Where": [{"Condition": {"In": {
                            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "nombre_corto"}}],
                            "Table": {"SourceRef": {"Source": "subquery"}}}}}]}}]


def boton_ir(nombre, x, y, w, h, rotulo, tam, c, pagina):
    """Botón con el aspecto de un texto (sin icono, relleno ni borde) que navega a otra página del informe."""
    estilo = {"text": lit(rotulo), "fontColor": color(c), "fontSize": lit(tam), "fontFamily": lit("Segoe UI"),
              "horizontalAlignment": lit("left"), "verticalAlignment": lit("middle"),
              "leftMargin": lit(0), "rightMargin": lit(0), "topMargin": lit(0), "bottomMargin": lit(0)}
    visual(nombre, x, y, w, h, {"visualType": "actionButton", "objects": {
        "icon": [{"properties": {"show": lit(False)}}],
        "text": [{"properties": {"show": lit(True)}}, {"selector": {"id": "default"}, "properties": estilo}],
        "fill": [{"properties": {"show": lit(False)}}],
        "outline": [{"properties": {"show": lit(False)}}]},
        "visualContainerObjects": sin_marco() | {"visualLink": [{"properties": {"show": lit(True), "type": lit("PageNavigation"),
                                                       "navigationSection": lit(pagina)}}]}})


# ------------------------------------------------------------------ cabecera
boton_ir("volver", 34, 14, 200, 14, "← BUSCADOR", 8, OSCURO, "a141c468cdbe0d976a0a")
texto("nombreJugador", 34, 30, 700, 46, med("dim_jugador", "Nombre jugador"), 36, BLANCO, "DIN", True)
texto("subtituloFicha", 34, 80, 760, 18, med("dim_jugador", "Subtitulo ficha"), 9, GRIS)
visual("segJugador", 800, 36, 360, 40, {
    "visualType": "slicer",
    "query": {"queryState": {"Values": {"projections": [proy(col("dim_jugador", "jugador"), "dim_jugador.jugador") | {"active": True}]}}},
    "objects": {"data": [{"properties": {"mode": lit("Dropdown")}}],
                "header": [{"properties": {"show": lit(False)}}],
                "selection": [{"properties": {"singleSelect": lit(True), "strictSingleSelect": lit(True)}}],
                "items": [{"properties": {"fontColor": color(BLANCO), "background": color(FONDO), "textSize": lit(10)}}],
                # La página se elige con este selector (no hay drillthrough: su filtro recortaba la lista a un jugador).
                # Abre con Diego Llorente, el fichaje que propone el TFM; con buscador para los 561
                "general": [{"properties": {"selfFilterEnabled": lit(True), "filter": {"filter": {
                    "Version": 2, "From": [{"Name": "d", "Entity": "dim_jugador", "Type": 0}],
                    "Where": [{"Condition": {"In": {
                        "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "jugador"}}],
                        "Values": [[{"Literal": {"Value": "'Diego Llorente'"}}]]}}}]}}}}]},
    "visualContainerObjects": sin_marco()})
visual("logoLaliga", 1182, 22, 64, 46, {"visualType": "image", "objects": {
    "general": [{"properties": {"imageUrl": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": "laliga.png"}}}}}],
    "imageScaling": [{"properties": {"imageScalingType": lit("Fit")}}]}, "visualContainerObjects": sin_marco()})
rect("lineaRoja", 34, 106, 1212, 2, ROJO)

# ------------------------------------------------------------------ columna izquierda
# Retrato con medida, como el escudo: una sola fila y vacía si no hay un jugador elegido
tabla("retrato", 34, 124, 134, 134, [proy(med("dim_jugador", "Foto jugador"), "dim_jugador.Foto jugador", " ")], [130],
      cabecera=False, imagen=124, fila=0)
# Escudo como objeto visual de imagen con la URL de una medida: sin fondo propio, así solo se ve el PNG transparente.
# Una tabla pintaría sus celdas del color del fondo (no admite transparencia) y taparía el retrato.
visual("escudo", 128, 218, 52, 52, {"visualType": "image", "objects": {
    "image": [{"properties": {"sourceType": lit("imageUrl"), "sourceUrl": {"expr": med("dim_jugador", "Escudo jugador")}}}],
    "imageScaling": [{"properties": {"imageScalingType": lit("Fit")}}]}, "visualContainerObjects": sin_marco()})
tabla("datosJugador", 34, 274, 272, 250,
      [proy(col("hechos_ficha", "atributo"), "hechos_ficha.atributo", " "), proy(col("hechos_ficha", "valor"), "hechos_ficha.valor", "  ")],
      [110, 158], [fmt("hechos_ficha.atributo", GRIS), fmt("hechos_ficha.valor", BLANCO, "Right")],
      cabecera=False, fila=3, filtros=filtro_un_jugador("filtroDatosJugador"))
texto("tituloEquipo", 34, 536, 272, 14, "SU EQUIPO EN LA TEMPORADA", 8, OSCURO)
tabla("bloqueEquipo", 34, 554, 272, 56,
      [proy(med("dim_jugador", "Puntos equipo"), "dim_jugador.Puntos equipo", "PTS"),
       proy(med("dim_jugador", "Puntos esperados equipo"), "dim_jugador.Puntos esperados equipo", "xPTS"),
       proy(med("dim_jugador", "Altura defensiva equipo"), "dim_jugador.Altura defensiva equipo", "ALTURA")],
      [90, 90, 90], [fmt(r, BLANCO, "Left") for r in ("dim_jugador.Puntos equipo", "dim_jugador.Puntos esperados equipo", "dim_jugador.Altura defensiva equipo")])

# ------------------------------------------------------------------ bloques de métricas
# Alto de una fila y de la cabecera según el relleno de fila (medidos en Power BI: con relleno 3, fila de 20)
def alto_tabla(filas, relleno):
    return (18 + 2 * relleno) + filas * (14 + 2 * relleno) + 4


RELLENO_METRICAS = 10   # filas más altas: DEFENSA acaba sobre y = 420
for i, (bloque, titulo, filas) in enumerate([("defensa", "DEFENSA", 7), ("con_balon", "CON BALÓN", 6), ("ataque", "ATAQUE", 6)]):
    x = 332 + i * 314
    texto(f"titulo_{bloque}", x, 124, 286, 18, titulo, 13, BLANCO, "DIN", True)
    rect(f"raya_{bloque}", x, 142, 286, 1, RAYA)
    filtros = [filtro_cat(f"filtroBloque_{bloque}", "dim_metrica", "bloque", [bloque])]
    if bloque == "defensa":
        # Las 7 primeras: fuera entradas intentadas y duelos aéreos disputados
        filtros.append({"name": "filtroOrden_defensa", "field": col("dim_metrica", "orden"), "type": "Advanced", "howCreated": "User",
                        "filter": {"Version": 2, "From": [{"Name": "t", "Entity": "dim_metrica", "Type": 0}],
                                   "Where": [{"Condition": {"Comparison": {"ComparisonKind": 4,
                                              "Left": {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": "orden"}},
                                              "Right": {"Literal": {"Value": "7L"}}}}}]}})
    tabla(f"metricas_{bloque}", x, 148, 286, alto_tabla(filas, RELLENO_METRICAS),
          [proy(col("dim_metrica", "nombre_corto"), "dim_metrica.nombre_corto", " "),
           proy(med("hechos_metrica", "Valor metrica"), "hechos_metrica.Valor metrica", "VALOR"),
           proy(med("hechos_metrica", "Percentil metrica"), "hechos_metrica.Percentil metrica", "PERCENTIL")],
          [128, 66, 86],   # 280 de 286: con el ancho exacto aparece barra horizontal
          [fmt("dim_metrica.nombre_corto", GRIS), fmt("hechos_metrica.Valor metrica", BLANCO, "Right"),
           fmt("hechos_metrica.Percentil metrica", BLANCO, "Right", barras=True)],
          filtros=filtros, fila=RELLENO_METRICAS)

# ------------------------------------------------------------------ dónde destaca y dónde se queda corto
RELLENO_RANKING = 7   # tres filas con cabecera en 120 de alto
for nombre, x, titulo, descendente in [("destaca", 332, "DÓNDE DESTACA", True), ("flojo", 806, "DÓNDE SE QUEDA CORTO", False)]:
    texto(f"titulo_{nombre}", x, 450, 440, 14, titulo, 8, OSCURO)
    tabla(f"ranking_{nombre}", x, 470, 440, 120,
          [proy(col("dim_metrica", "nombre_corto"), "dim_metrica.nombre_corto", " "),
           proy(med("hechos_metrica", "Valor metrica"), "hechos_metrica.Valor metrica", "VALOR"),
           proy(med("hechos_metrica", "Percentil metrica"), "hechos_metrica.Percentil metrica", "PERCENTIL")],
          [200, 100, 130],   # 430 de 440, por la misma razón que arriba
          [fmt("dim_metrica.nombre_corto", GRIS), fmt("hechos_metrica.Valor metrica", BLANCO, "Right"),
           fmt("hechos_metrica.Percentil metrica", BLANCO, "Right", barras=True)],
          orden=med("hechos_metrica", "Percentil metrica"), sentido="Descending" if descendente else "Ascending",
          filtros=filtro_n(f"filtroN_{nombre}", 3, descendente), fila=RELLENO_RANKING)

# ------------------------------------------------------------------ aviso y pie
texto("aviso", 332, 646, 914, 16, med("dim_jugador", "Aviso fiabilidad"), 8, ROJO)
texto("pie", 34, 700, 1212, 16, "PERCENTIL DENTRO DE SU PUESTO · VALORES POR 90 MINUTOS SALVO LOS PORCENTAJES · "
                                 "FUENTES: UNDERSTAT, WHOSCORED Y TRANSFERMARKT", 8, OSCURO)

# ------------------------------------------------------------------ página: detalles con dim_jugador[jugador]
if os.path.isdir(f"{REP}/definition/pages/{PAG}"):
    shutil.rmtree(f"{REP}/definition/pages/{PAG}")
os.makedirs(VIS)
for v in visuales:
    os.makedirs(f"{VIS}/{v['name']}")
    json.dump(v, open(f"{VIS}/{v['name']}/visual.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
pagina = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
          "name": PAG, "displayName": "Ficha", "displayOption": "FitToPage", "height": 720, "width": 1280,
          "objects": {"background": [{"properties": {"color": color(FONDO), "transparency": lit(0)}}],
                      "outspace": [{"properties": {"color": color(FONDO), "transparency": lit(0)}}]}}
json.dump(pagina, open(f"{REP}/definition/pages/{PAG}/page.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
paginas = json.load(open(f"{REP}/definition/pages/pages.json", encoding="utf-8"))
if PAG not in paginas["pageOrder"]:
    paginas["pageOrder"].append(PAG)
json.dump(paginas, open(f"{REP}/definition/pages/pages.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ------------------------------------------------------------------ modelo: medidas y orden de las métricas
MEDIDAS = {
    "dim_jugador": [
        ("Nombre jugador", 'COALESCE ( SELECTEDVALUE ( dim_jugador[jugador] ), "Selecciona un jugador" )', None),
        ("Subtitulo ficha",
         'VAR n = SELECTEDVALUE ( hechos_jugador[n_grupo_referencia] ) '
         'VAR g = IF ( HASONEVALUE ( dim_jugador[id_jugador] ), MAXX ( dim_jugador, RELATED ( dim_posicion[grupo] ) ) ) '
         'VAR plural = SWITCH ( g, "central", "CENTRALES", "lateral", "LATERALES", "pivote_mediocentro", "PIVOTES Y MEDIOCENTROS", '
         '"mediapunta", "MEDIAPUNTAS", "extremo", "EXTREMOS", "delantero", "DELANTEROS" ) '
         'RETURN IF ( NOT HASONEVALUE ( dim_jugador[id_jugador] ), "", IF ( ISBLANK ( n ), '
         '"SIN GRUPO DE COMPARACIÓN: SU PUESTO NO ESTÁ DEFINIDO O CONFIRMADO", '
         '"COMPARADO CON " & n & " " & plural & " DE LALIGA CON 600 MINUTOS O MÁS" ) )', None),
        ("Aviso fiabilidad",
         'IF ( HASONEVALUE ( dim_jugador[id_jugador] ) && NOT SELECTEDVALUE ( hechos_jugador[percentil_fiable] ), '
         'IF ( SELECTEDVALUE ( dim_jugador[minutos] ) < 600, '
         '"ESTE JUGADOR TIENE MENOS DE 600 MINUTOS: SUS PERCENTILES NO SON COMPARABLES", '
         '"ESTE JUGADOR NO TIENE PUESTO CONFIRMADO: NO TIENE PERCENTILES" ), "" )', None),
        ("Jugador elegido", 'IF ( HASONEVALUE ( dim_jugador[id_jugador] ), 1 )', "0"),
        ("Foto jugador", 'IF ( HASONEVALUE ( dim_jugador[id_jugador] ), SELECTEDVALUE ( dim_jugador[url_foto] ) )', "ImageUrl"),
        # Sin un jugador elegido devuelve un SVG vacío: el objeto de imagen no pinta su recuadro gris de marcador
        ("Escudo jugador", 'IF ( HASONEVALUE ( dim_jugador[id_jugador] ), MAXX ( dim_jugador, RELATED ( dim_equipo[url_escudo] ) ), '
         '"data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'1\' height=\'1\'/>" )', "ImageUrl"),
        ("Puntos equipo", 'IF ( HASONEVALUE ( dim_jugador[id_jugador] ), MAXX ( dim_jugador, RELATED ( dim_equipo[puntos] ) ) )', "0"),
        ("Puntos esperados equipo", 'IF ( HASONEVALUE ( dim_jugador[id_jugador] ), MAXX ( dim_jugador, RELATED ( dim_equipo[puntos_esperados] ) ) )', "0.0"),
        ("Altura defensiva equipo", 'IF ( HASONEVALUE ( dim_jugador[id_jugador] ), MAXX ( dim_jugador, RELATED ( dim_equipo[altura_defensiva] ) ) )', "0.0"),
    ],
    "hechos_metrica": [
        ("Valor metrica",
         'VAR v = SELECTEDVALUE ( hechos_metrica[valor] ) VAR u = SELECTEDVALUE ( dim_metrica[unidad] ) '
         'RETURN IF ( ISBLANK ( v ), BLANK (), IF ( u = "porcentaje", FORMAT ( v, "0" ) & " %", FORMAT ( v, "0.00" ) ) )', None),
        ("Percentil metrica", 'SELECTEDVALUE ( hechos_metrica[percentil] )', "0"),
        ("Percentil ranking",
         'VAR p = SELECTEDVALUE ( hechos_metrica[percentil] ) VAR v = SELECTEDVALUE ( hechos_metrica[valor] ) '
         'VAR oculta = SELECTEDVALUE ( dim_metrica[bloque] ) = "defensa" && SELECTEDVALUE ( dim_metrica[orden] ) > 7 '
         'RETURN IF ( NOT ISBLANK ( p ) && NOT ISBLANK ( v ) && NOT oculta, p - SELECTEDVALUE ( hechos_metrica[id_metrica] ) / 1000 )',
         "0.000"),
    ],
}
for t, medidas in MEDIDAS.items():
    ruta = f"{SEM}/{t}.tmdl"
    s = open(ruta, encoding="utf-8").read()
    for nombre, expr, extra in medidas:
        # Power BI guarda sin comillas los nombres sin espacios (measure Separacion = ...): se buscan las dos formas
        patron = rf"\tmeasure (?:'{re.escape(nombre)}'|{re.escape(nombre)}) = [^\n]*\n"
        if re.search(patron, s):
            # Ya existe: se actualiza su expresión (una sola línea) y se dejan sus propiedades
            s = re.sub(patron, lambda m: m.group(0).split(" = ", 1)[0] + f" = {expr}\n", s, count=1)
            continue
        linea = f"\tmeasure '{nombre}' = {expr}\n"
        if extra == "ImageUrl":
            linea += "\t\tdataCategory: ImageUrl\n"
        elif extra:
            linea += f"\t\tformatString: {extra}\n"
        linea += f"\t\tlineageTag: {uuid.uuid4()}\n\n"
        s = re.sub(r"(table [^\n]+\n\tlineageTag: [^\n]+\n\n)", lambda m: m.group(1) + linea, s, count=1)
    # Power BI guarda los .tmdl con CRLF: se escriben igual
    open(ruta, "w", encoding="utf-8", newline=CRLF).write(s)
# Las métricas y los atributos se ordenan por su campo "orden" al ordenar por el texto
for tabla_, columna in [("dim_metrica", "nombre"), ("dim_metrica", "nombre_corto"), ("hechos_ficha", "atributo")]:
    ruta = f"{SEM}/{tabla_}.tmdl"
    s = open(ruta, encoding="utf-8").read()
    # Bloque de la columna hasta la siguiente línea "column"/"measure"/"partition" (Power BI reordena sus propiedades)
    bloque = re.search(rf"\tcolumn {columna}\n(.*?)(?=\n\t(column|measure|partition) )", s, re.S).group(1)
    if "sortByColumn:" not in bloque:
        s = s.replace(f"\tcolumn {columna}\n\t\tdataType: string\n",
                      f"\tcolumn {columna}\n\t\tdataType: string\n\t\tsortByColumn: orden\n", 1)
    # Power BI guarda los .tmdl con CRLF: se escriben igual
    open(ruta, "w", encoding="utf-8", newline=CRLF).write(s)
print("visuales:", [v["name"] for v in visuales])
