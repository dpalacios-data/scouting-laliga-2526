"""Genera la página Buscador del informe PBIR (powerbi/) y ajusta el modelo semántico.

Uso: python powerbi/generar_buscador.py   (con Power BI Desktop cerrado; luego abrir el .pbip)
"""
import json, os, re, shutil

# Carpeta powerbi/ del repositorio: la del propio script
RAIZ = os.path.dirname(os.path.abspath(__file__))
REP = f"{RAIZ}/scouting-laliga-2526.Report"
SEM = f"{RAIZ}/scouting-laliga-2526.SemanticModel/definition/tables"
PAG = "a141c468cdbe0d976a0a"
VIS = f"{REP}/definition/pages/{PAG}/visuals"
ESQ = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json"


def lit(v):
    """Literal de PBIR: texto entre comillas simples, número con sufijo D, booleano tal cual."""
    if isinstance(v, bool):
        txt = "true" if v else "false"
    elif isinstance(v, (int, float)):
        txt = f"{v}D"
    else:
        txt = "'" + v + "'"
    return {"expr": {"Literal": {"Value": txt}}}


def color(c):
    return {"solid": {"color": lit(c)}}


def columna(tabla, col):
    return {"Column": {"Expression": {"SourceRef": {"Entity": tabla}}, "Property": col}}


def proyeccion(tabla, col, nombre=None):
    p = {"field": columna(tabla, col), "queryRef": f"{tabla}.{col}", "nativeQueryRef": col}
    if nombre:
        p["displayName"] = nombre
    return p


def sin_marco():
    """Sin fondo, sin borde, sin título ni cabecera del contenedor."""
    return {"background": [{"properties": {"show": lit(False)}}],
            "border": [{"properties": {"show": lit(False)}}],
            "title": [{"properties": {"show": lit(False)}}],
            "visualHeader": [{"properties": {"show": lit(False)}}],
            "dropShadow": [{"properties": {"show": lit(False)}}],
            "padding": [{"properties": {k: lit(0) for k in ("top", "bottom", "left", "right")}}]}


visuales = []


def visual(nombre, x, y, w, h, cuerpo):
    visuales.append({"$schema": ESQ, "name": nombre,
                     "position": {"x": x, "y": y, "z": len(visuales) * 1000, "height": h, "width": w,
                                  "tabOrder": len(visuales) * 1000},
                     "visual": cuerpo})


def texto(nombre, x, y, w, h, tramos):
    visual(nombre, x, y, w, h, {"visualType": "textbox",
                                "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": tramos}]}}]},
                                "visualContainerObjects": sin_marco()})


def rectangulo(nombre, x, y, w, h, c):
    cont = sin_marco()
    visual(nombre, x, y, w, h, {"visualType": "shape", "objects": {
        "shape": [{"properties": {"tileShape": lit("rectangle")}}],
        "fill": [{"properties": {"show": lit(True)}},
                 {"properties": {"fillColor": color(c), "transparency": lit(0)}, "selector": {"id": "default"}}],
        "outline": [{"properties": {"show": lit(False)}}]},
        "visualContainerObjects": cont})


def texto_forma(nombre, x, y, w, h, contenido, tam, c, familia="Segoe UI"):
    cont = sin_marco()
    visual(nombre, x, y, w, h, {"visualType": "shape", "objects": {
        "shape": [{"properties": {"tileShape": lit("rectangle")}}],
        "fill": [{"properties": {"show": lit(False)}}],
        "outline": [{"properties": {"show": lit(False)}}],
        "text": [{"properties": {"show": lit(True)}},
                 {"selector": {"id": "default"}, "properties": {"text": lit(contenido), "fontColor": color(c),
                                 "fontSize": lit(tam), "fontFamily": lit(familia),
                                 "horizontalAlignment": lit("left"), "verticalAlignment": lit("middle"),
                                 "leftMargin": lit(0), "rightMargin": lit(0), "topMargin": lit(0), "bottomMargin": lit(0)}}]},
        "visualContainerObjects": cont})


def filtro(tabla, col, condicion):
    """Selección guardada de una segmentación: lo que se ve marcado al abrir el informe."""
    ref = {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": col}}
    return {"filter": {"Version": 2, "From": [{"Name": "t", "Entity": tabla, "Type": 0}],
                       "Where": [{"Condition": condicion(ref)}]}}


def segmentacion(nombre, x, tabla, col, titulo, modo, defecto=None):
    objetos = {
        "data": [{"properties": {"mode": lit(modo)}}],
        "header": [{"properties": {"show": lit(True), "text": lit(titulo), "fontColor": color("#44505F"),
                                   "textSize": lit(8), "bold": lit(True), "background": color("#07090E")}}],
        "items": [{"properties": {"fontColor": color("#F2F5F8"), "background": color("#07090E"), "textSize": lit(10)}}],
        "general": [{"properties": {"outlineColor": color("#07090E"), "outlineWeight": lit(0)}}]}
    if modo == "Between":
        # Barra deslizante con los dos extremos; las casillas de valor, sin caja
        objetos["slider"] = [{"properties": {"show": lit(True), "color": color("#FF4B44")}}]
        objetos["numericInputStyle"] = [{"properties": {"fontColor": color("#F2F5F8"), "background": color("#07090E"),
                                                       "textSize": lit(9)}}]
    if defecto:
        objetos["general"][0]["properties"]["filter"] = defecto
        # En un rango, Power BI guarda además el extremo inferior en data.numericStart
        if modo == "Between":
            objetos["data"][0]["properties"]["numericStart"] = {"expr": {"Literal": {"Value": "600D"}}}
    visual(nombre, x, 104, 236, 80, {
        "visualType": "slicer",
        # Power BI marca el campo de la segmentación como activo al guardar
        "query": {"queryState": {"Values": {"projections": [proyeccion(tabla, col) | {"active": True}]}}},
        "objects": objetos,
        "visualContainerObjects": sin_marco()})


# ---------------------------------------------------------------- objetos de la página
GRIS, BLANCO, ROJO = "#79879A", "#F2F5F8", "#FF4B44"
texto("titulo", 34, 16, 760, 62, [
    {"value": "BUSCADOR DE ", "textStyle": {"fontFamily": "DIN", "fontSize": "36pt", "fontWeight": "bold", "color": BLANCO}},
    {"value": "JUGADORES", "textStyle": {"fontFamily": "DIN", "fontSize": "36pt", "fontWeight": "bold", "color": ROJO}}])
texto_forma("subtitulo", 34, 64, 760, 20, "LALIGA 2025/26 · 561 JUGADORES · PERCENTILES DENTRO DE SU PUESTO", 9, GRIS)
visual("logoLaliga", 1182, 22, 64, 50, {"visualType": "image", "objects": {
    "general": [{"properties": {"imageUrl": {"expr": {"ResourcePackageItem": {
        "PackageName": "RegisteredResources", "PackageType": 1, "ItemName": "laliga.png"}}}}}],
    "imageScaling": [{"properties": {"imageScalingType": lit("Fit")}}]},
    "visualContainerObjects": sin_marco()})
rectangulo("lineaRoja", 34, 96, 1212, 2, ROJO)
# Al abrir: MINUTOS desde 600 y MUESTRA = solo percentiles fiables
# Formato que escribe el propio Power BI al fijar el mínimo: comparación >= con literal decimal (D)
desde_600 = filtro("dim_jugador", "minutos", lambda ref: {"Comparison": {
    "ComparisonKind": 2, "Left": ref, "Right": {"Literal": {"Value": "600D"}}}})
solo_fiables = filtro("hechos_jugador", "muestra", lambda ref: {"In": {
    "Expressions": [ref], "Values": [[{"Literal": {"Value": "'Solo fiables'"}}]]}})
for nombre, x, tabla, col, tit, modo, defecto in [
        ("segPuesto", 34, "dim_posicion", "grupo", "PUESTO", "Dropdown", None),
        ("segEquipo", 278, "dim_equipo", "nombre_equipo", "EQUIPO", "Dropdown", None),
        ("segEdad", 522, "dim_jugador", "edad", "EDAD", "Between", None),
        ("segMinutos", 766, "dim_jugador", "minutos", "MINUTOS", "Between", None),
        ("segMuestra", 1010, "hechos_jugador", "muestra", "MUESTRA", "Dropdown", solo_fiables)]:
    segmentacion(nombre, x, tabla, col, tit, modo, defecto)
rectangulo("lineaSeparadora", 34, 186, 1212, 1, "#1A212C")

# Tabla
# (tabla, columna, cabecera, ancho). Foto y escudo sin texto de cabecera (espacios)
COLS = [("dim_jugador", "url_foto", " ", 54), ("dim_equipo", "url_escudo", "  ", 44),
        ("dim_jugador", "jugador", "JUGADOR", 290), ("dim_posicion", "posicion", "POSICIÓN", 140),
        ("dim_jugador", "edad", "EDAD", 60), ("dim_jugador", "minutos", "MINUTOS", 70),
        ("hechos_jugador", "pctl_intercepciones_fiable", "INTERCEP.", 107),
        ("hechos_jugador", "pctl_entradas_exitosas_fiable", "ENTRADAS", 107),
        ("hechos_jugador", "pctl_duelos_aereos_ganados_fiable", "AÉREOS", 106),
        ("hechos_jugador", "pctl_xg_fiable", "xG", 106), ("hechos_jugador", "pctl_xa_fiable", "xA", 106)]
PCTL = [f"{t}.{c}" for t, c, _, _ in COLS if c.startswith("pctl_")]
# Rojo #FF4B44 al 15 % de opacidad sobre el fondo #07090E: se lee sin competir con el número
BARRA = "#2C1316"
formato_cols = []
for ref in PCTL:
    formato_cols.append({"properties": {
        "dataBars": {"minValue": lit(0), "maxValue": lit(100), "positiveColor": color(BARRA),
                     "negativeColor": color(BARRA), "axisColor": color("#07090E"),
                     "reverseDirection": lit(False), "hideText": lit(False),
                     "totalMatchingOption": {"expr": {"Literal": {"Value": "1L"}}}},
        "labelPrecision": {"expr": {"Literal": {"Value": "0L"}}},
        # El número en blanco
        "fontColor": color("#F2F5F8")},
        "selector": {"metadata": ref}})
for t, c, tinta in [("dim_jugador", "jugador", "#F2F5F8"), ("dim_posicion", "posicion", "#79879A"),
                   ("dim_jugador", "edad", "#79879A"), ("dim_jugador", "minutos", "#79879A")]:
    formato_cols.append({"properties": {"fontColor": color(tinta)}, "selector": {"metadata": f"{t}.{c}"}})
anchos = [{"properties": {"value": lit(w)}, "selector": {"metadata": f"{t}.{c}"}} for t, c, _, w in COLS]
visual("tablaJugadores", 34, 198, 1212, 500, {
    "visualType": "tableEx",
    "query": {"queryState": {"Values": {"projections": [proyeccion(t, c, n) for t, c, n, _ in COLS]}},
              # Ordenada por minutos, de mayor a menor
              "sortDefinition": {"sort": [{"field": columna("dim_jugador", "minutos"), "direction": "Descending"}]}},
    "objects": {
        "grid": [{"properties": {"gridHorizontal": lit(True), "gridHorizontalColor": color("#1A212C"),
                                 "gridHorizontalWeight": lit(1), "gridVertical": lit(False),
                                 "outlineStyle": lit(0), "imageHeight": lit(34), "rowPadding": lit(1)}}],
        "columnHeaders": [{"properties": {"fontColor": color("#44505F"), "fontSize": lit(8),
                                          "backColor": color("#07090E"), "wordWrap": lit(False),
                                          "autoSizeColumnWidth": lit(True)}}],
        "values": [{"properties": {"backColorPrimary": color("#07090E"), "backColorSecondary": color("#07090E"),
                                   "wordWrap": lit(False)}}],
        "total": [{"properties": {"totals": lit(False)}}],
        "columnWidth": anchos,
        "columnFormatting": formato_cols},
    "visualContainerObjects": sin_marco()})
texto_forma("notaPie", 34, 702, 1212, 16, "PERCENTIL DENTRO DEL PUESTO · ENTRADAS Y AÉREOS SON LOS GANADOS, NO LOS DISPUTADOS · SOLO JUGADORES CON 600 MINUTOS O MÁS", 8, "#44505F")

# Botón a la Ficha: el camino visible de una página a otra (la Ficha se elige con su selector de jugador)
visual("verFicha", 1030, 34, 130, 30, {"visualType": "actionButton", "objects": {
    "icon": [{"properties": {"show": lit(False)}}],
    "text": [{"properties": {"show": lit(True)}},
             {"selector": {"id": "default"}, "properties": {
                 "text": lit("VER FICHA →"), "fontColor": color("#F2F5F8"), "fontSize": lit(9), "fontFamily": lit("Segoe UI"),
                 "bold": lit(True), "horizontalAlignment": lit("center"), "verticalAlignment": lit("middle")}}],
    "fill": [{"properties": {"show": lit(False)}}],
    "outline": [{"properties": {"show": lit(True)}},
                {"selector": {"id": "default"}, "properties": {"lineColor": color("#FF4B44"), "weight": lit(1)}}]},
    "visualContainerObjects": sin_marco() | {"visualLink": [{"properties": {
        "show": lit(True), "type": lit("PageNavigation"), "navigationSection": lit("ficha")}}]}})

# ---------------------------------------------------------------- escritura de los visuales
if os.path.isdir(VIS):
    shutil.rmtree(VIS)
for v in visuales:
    os.makedirs(f"{VIS}/{v['name']}")
    json.dump(v, open(f"{VIS}/{v['name']}/visual.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------- página: 1280 x 720, fondo #07090E
pagina = json.load(open(f"{REP}/definition/pages/{PAG}/page.json", encoding="utf-8"))
pagina.update({"displayName": "Buscador", "width": 1280, "height": 720, "displayOption": "FitToPage"})
pagina["objects"] = {"background": [{"properties": {"color": color("#07090E"), "transparency": lit(0)}}],
                     "outspace": [{"properties": {"color": color("#07090E"), "transparency": lit(0)}}]}
json.dump(pagina, open(f"{REP}/definition/pages/{PAG}/page.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------- imagen del logo como recurso registrado
shutil.copyfile(f"{RAIZ}/laliga.png", f"{REP}/StaticResources/RegisteredResources/laliga.png")
informe = json.load(open(f"{REP}/definition/report.json", encoding="utf-8"))
reg = next(p for p in informe["resourcePackages"] if p["name"] == "RegisteredResources")
if not any(i["name"] == "laliga.png" for i in reg["items"]):
    reg["items"].append({"name": "laliga.png", "path": "laliga.png", "type": "Image"})
json.dump(informe, open(f"{REP}/definition/report.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------- modelo: atributos que no se suman
NO_SUMAR = {"dim_jugador": ["edad", "minutos", "partidos", "altura_cm", "valor_mercado_tm"],
            "hechos_jugador": None}   # None = todas las pctl_*
for tabla, cols in NO_SUMAR.items():
    ruta = f"{SEM}/{tabla}.tmdl"
    s = open(ruta, encoding="utf-8").read()
    bloques = re.split(r"(?=\n\tcolumn )", s)
    for i, b in enumerate(bloques):
        m = re.match(r"\n\tcolumn (\S+)", b)
        if not m or (cols is not None and m.group(1) not in cols) or (cols is None and not m.group(1).startswith("pctl_")):
            continue
        b = b.replace("summarizeBy: sum", "summarizeBy: none")
        b = b.replace("annotation SummarizationSetBy = Automatic", "annotation SummarizationSetBy = User")
        if cols is None and "formatString:" not in b:   # percentiles sin decimales
            b = b.replace("\t\tdataType: double\n", "\t\tdataType: double\n\t\tformatString: 0\n", 1)
        bloques[i] = b
    open(ruta, "w", encoding="utf-8", newline="").write("".join(bloques))

# ---------------------------------------------------------------- percentil solo si es fiable (si no, en blanco)
import uuid
ruta = f"{SEM}/hechos_jugador.tmdl"
s = open(ruta, encoding="utf-8").read()
nuevas = ""
for t, c, _, _ in COLS:
    if c.endswith("_fiable") and f"column {c} " not in s:
        base = c.removesuffix("_fiable")
        nuevas += (f"\n\tcolumn {c} = IF ( hechos_jugador[percentil_fiable], hechos_jugador[{base}] )\n"
                   f"\t\tdataType: double\n\t\tformatString: 0\n\t\tlineageTag: {uuid.uuid4()}\n"
                   f"\t\tsummarizeBy: none\n\t\tisDataTypeInferred\n\n\t\tannotation SummarizationSetBy = User\n")
if "column muestra " not in s:
    nuevas += (f'\n\tcolumn muestra = IF ( hechos_jugador[percentil_fiable], "Solo fiables", "No fiables" )\n'
               f"\t\tdataType: string\n\t\tlineageTag: {uuid.uuid4()}\n"
               f"\t\tsummarizeBy: none\n\t\tisDataTypeInferred\n\n\t\tannotation SummarizationSetBy = Automatic\n")
if nuevas:
    # Se insertan justo antes de la partición
    i = s.index("\n\tpartition ")
    s = s[:i] + nuevas + s[i:]
    open(ruta, "w", encoding="utf-8", newline="").write(s)
print("visuales:", [v["name"] for v in visuales])
