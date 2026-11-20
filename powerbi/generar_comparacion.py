"""Genera la página Comparación del informe PBIR (powerbi/) y añade al modelo las medidas y columnas que usa.

Uso: python powerbi/generar_comparacion.py   (con Power BI Desktop cerrado; luego abrir el .pbip)

Antes de volver a ejecutarlo, comprobar con git diff qué ha guardado Power BI en los ficheros y llevarlo aquí:
Power BI reescribe los visual.json (esquema, propiedades) y los .tmdl (orden de propiedades, saltos de línea CRLF).
"""
import json, os, re, shutil, uuid

RAIZ = os.path.dirname(os.path.abspath(__file__))
REP = f"{RAIZ}/scouting-laliga-2526.Report"
SEM = f"{RAIZ}/scouting-laliga-2526.SemanticModel/definition/tables"
PAG = "comparacion"
VIS = f"{REP}/definition/pages/{PAG}/visuals"
# Esquema con el que guarda Power BI Desktop (pasó de 2.13.0 a 2.14.0 al guardar)
ESQ = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json"
BLANCO, GRIS, OSCURO, ROJO, RAYA, FONDO = "#F2F5F8", "#79879A", "#44505F", "#FF4B44", "#1A212C", "#07090E"
# Nombre interno de DIN en las formas (es lo que guarda Power BI al elegirla)
DIN_FORMA = "wf_standard-font, helvetica, arial, sans-serif"


# ------------------------------------------------------------------ ayudas
def lit(v):
    if isinstance(v, bool):
        txt = "true" if v else "false"
    elif isinstance(v, int):
        txt = f"{v}D"
    elif isinstance(v, float):
        txt = f"{v}D"
    else:
        txt = f"'{v}'"
    return {"expr": {"Literal": {"Value": txt}}}


def entero(v):
    return {"expr": {"Literal": {"Value": f"{v}L"}}}


def color(c):
    return {"solid": {"color": lit(c)}}


def col(t, c):
    return {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}


def med(t, m):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": t}}, "Property": m}}


def color_medida(t, m):
    """Color por valor de campo: el color sale de una medida que devuelve '#rrggbb'."""
    return {"solid": {"color": {"expr": med(t, m)}}}


def proy(campo, ref, nombre=None, activa=False):
    p = {"field": campo, "queryRef": ref, "nativeQueryRef": ref.split(".", 1)[1]}
    if nombre is not None:
        p["displayName"] = nombre
    if activa:
        # Power BI marca así el campo de una segmentación al guardar
        p["active"] = True
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


def texto(nombre, x, y, w, h, contenido, tam, c, familia="Segoe UI", negrita=False, alineacion="left"):
    """Texto en una forma: sin margen interior ni barra de desplazamiento. contenido = texto o medida."""
    valor = {"expr": contenido} if isinstance(contenido, dict) else lit(contenido)
    visual(nombre, x, y, w, h, {"visualType": "shape", "objects": {
        "shape": [{"properties": {"tileShape": lit("rectangle")}}],
        "fill": [{"properties": {"show": lit(False)}}],
        "outline": [{"properties": {"show": lit(False)}}],
        "text": [{"properties": {"show": lit(True)}},
                 {"selector": {"id": "default"}, "properties": {
                     "text": valor, "fontColor": color(c), "fontSize": lit(tam),
                     "fontFamily": lit(DIN_FORMA if familia == "DIN" else familia), "bold": lit(negrita),
                     "horizontalAlignment": lit(alineacion), "verticalAlignment": lit("middle"),
                     "leftMargin": lit(0), "rightMargin": lit(0), "topMargin": lit(0), "bottomMargin": lit(0)}}]},
        "visualContainerObjects": sin_marco()})


def rect(nombre, x, y, w, h, c):
    visual(nombre, x, y, w, h, {"visualType": "shape", "objects": {
        "shape": [{"properties": {"tileShape": lit("rectangle")}}],
        "fill": [{"properties": {"show": lit(True)}}, {"properties": {"fillColor": color(c), "transparency": lit(0)}, "selector": {"id": "default"}}],
        "outline": [{"properties": {"show": lit(False)}}]}, "visualContainerObjects": sin_marco()})


def fmt(ref, tinta=None, alineacion=None, fondo=None):
    p = {}
    if tinta:
        p["fontColor"] = color(tinta)
    if alineacion:
        p["alignment"] = lit(alineacion)
    if fondo:
        p["backColor"] = fondo
        # Formato por valor de campo: se evalúa fila a fila, con el comodín de datos además de la columna
        return {"properties": p, "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": ref}}
    return {"properties": p, "selector": {"metadata": ref}}


def tabla(nombre, x, y, w, h, proyecciones, anchos, formatos=(), cabecera=True, orden=None, sentido="Ascending",
          imagen=None, filtros=None, fila=1, autoajuste=True, tam=None):
    """Tabla sin fondo; cabecera=False la reduce a una línea mínima del color del fondo (no se puede ocultar).
    Sin la propiedad 'outline' y con autoSizeColumnWidth en true: así lo deja Power BI al guardar."""
    objetos = {
        "grid": [{"properties": {"gridHorizontal": lit(True), "gridHorizontalColor": color(RAYA), "gridHorizontalWeight": lit(1),
                                 "gridVertical": lit(False), "outlineStyle": lit(0), "rowPadding": lit(fila),
                                 **({"imageHeight": lit(imagen)} if imagen else {})}}],
        "columnHeaders": [{"properties": {"fontColor": color(OSCURO if cabecera else FONDO), "fontSize": lit(8 if cabecera else 1),
                                          "backColor": color(FONDO), "wordWrap": lit(False), "autoSizeColumnWidth": lit(autoajuste)}}],
        "values": [{"properties": {"backColorPrimary": color(FONDO), "backColorSecondary": color(FONDO), "wordWrap": lit(False),
                                   **({"fontSize": lit(tam)} if tam else {})}}],
        "total": [{"properties": {"totals": lit(False)}}],
        "columnWidth": [{"properties": {"value": lit(a)}, "selector": {"metadata": p["queryRef"]}} for p, a in zip(proyecciones, anchos)],
        "columnFormatting": list(formatos)}
    # Color por valor de campo: Power BI lo guarda también en "values" con el selector de la columna; sin esa entrada
    # no se pinta (configurado a mano una vez y copiado de lo que escribió Power BI)
    objetos["values"] += [f for f in formatos if "backColor" in f["properties"]]
    q = {"queryState": {"Values": {"projections": proyecciones}}}
    if orden:
        q["sortDefinition"] = {"sort": [{"field": orden, "direction": sentido}]}
    visual(nombre, x, y, w, h, {"visualType": "tableEx", "query": q, "objects": objetos, "visualContainerObjects": sin_marco()}, filtros)


def filtro_cat(nombre, tabla_, columna, valores):
    return {"name": nombre, "field": col(tabla_, columna), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "t", "Entity": tabla_, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": columna}}],
                                                       "Values": [[{"Literal": {"Value": f"'{v}'"}}] for v in valores]}}}]},
            "howCreated": "User"}


def filtro_orden_defensa(nombre):
    """Las 7 métricas de DEFENSA que se pintan: fuera entradas intentadas y duelos aéreos disputados (orden 8 y 9)."""
    return {"name": nombre, "field": col("dim_metrica", "orden"), "type": "Advanced",
            "filter": {"Version": 2, "From": [{"Name": "t", "Entity": "dim_metrica", "Type": 0}],
                       "Where": [{"Condition": {"Comparison": {"ComparisonKind": 4,
                                  "Left": {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": "orden"}},
                                  "Right": {"Literal": {"Value": "7L"}}}}}]},
            "howCreated": "User"}


def filtro_n(nombre, n, medida):
    """Filtro N superior sobre dim_metrica[nombre], ordenado por una medida de hechos_metrica."""
    sub = {"Version": 2,
           "From": [{"Name": "m", "Entity": "dim_metrica", "Type": 0}, {"Name": "h", "Entity": "hechos_metrica", "Type": 0}],
           "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "nombre"}, "Name": "field"}],
           "OrderBy": [{"Direction": 2, "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "h"}}, "Property": medida}}}],
           "Top": n}
    return {"name": nombre, "field": col("dim_metrica", "nombre"), "type": "TopN",
            "filter": {"Version": 2,
                       "From": [{"Name": "subquery", "Expression": {"Subquery": {"Query": sub}}, "Type": 2},
                                {"Name": "m", "Entity": "dim_metrica", "Type": 0}],
                       "Where": [{"Condition": {"In": {
                           "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "nombre"}}],
                           "Table": {"SourceRef": {"Source": "subquery"}}}}}]},
            "howCreated": "User"}


# Letra del eje y de las etiquetas (bajarla a 6 pt no reduce el alto mínimo de barra que pone Power BI)
TAM_EJE = 8


def barras(nombre, x, y, w, h, categoria, valor, filtros=None):
    """Barras horizontales agrupadas: eje de dos niveles (categoría > jugador), sin leyenda, color de la barra por la
    medida 'Color jugador' (Power BI no deja color por valor de campo si hay leyenda), eje de valores fijo 0-100,
    línea constante en 50 y etiquetas sin decimales."""
    cat_campo, cat_ref = categoria
    val_campo, val_ref = valor
    q = {"queryState": {
        "Category": {"projections": [proy(cat_campo, cat_ref, activa=True), proy(col("dim_jugador", "jugador"), "dim_jugador.jugador", activa=True)]},
        "Y": {"projections": [proy(val_campo, val_ref)]}},
        "sortDefinition": {"sort": [{"field": cat_campo, "direction": "Ascending"}]}}
    objetos = {
        "categoryAxis": [{"properties": {"show": lit(True), "showAxisTitle": lit(False), "labelColor": color(GRIS),
                                         "fontSize": lit(TAM_EJE), "concatenateLabels": lit(False),
                                         # Carriles finos: 40 % de hueco entre barras y 25 % en los extremos
                                         "innerPadding": entero(40), "outerPadding": entero(25)}}],
        "valueAxis": [{"properties": {"show": lit(True), "showAxisTitle": lit(False), "start": lit(0), "end": lit(100),
                                      "labelColor": color(OSCURO), "fontSize": lit(8), "gridlineShow": lit(True),
                                      "gridlineColor": color(RAYA)}}],
        "legend": [{"properties": {"show": lit(False)}}],
        # Etiquetas en gris claro: más discretas que el blanco y aún legibles dentro de una barra larga (el 99 de Llorente)
        "labels": [{"properties": {"show": lit(True), "color": color("#C3CBD5"), "fontSize": lit(TAM_EJE), "labelPrecision": entero(0),
                                   "labelDisplayUnits": lit(1)}}],
        "dataPoint": [{"properties": {"fill": color_medida("dim_jugador", "Color jugador")},
                       "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
        # En barras horizontales la línea constante del eje de valores es y1AxisReferenceLine (así la guarda Power BI)
        "y1AxisReferenceLine": [{"properties": {"show": lit(True), "displayName": lit("mediana del puesto"), "value": lit(50),
                                               "lineColor": color(OSCURO), "transparency": lit(0), "style": lit("dotted"), "width": lit(1),
                                               "position": lit("front"), "dataLabelShow": lit(False), "dataLabelColor": color(GRIS),
                                               "dataLabelText": lit("Name"), "dataLabelHorizontalPosition": lit("left"),
                                               "dataLabelVerticalPosition": lit("above")},
                                "selector": {"id": "1"}}]}
    visual(nombre, x, y, w, h, {"visualType": "clusteredBarChart", "query": q, "objects": objetos,
                                "visualContainerObjects": sin_marco(),
                                # Eje de dos niveles desplegado: se ven métrica y jugador a la vez
                                "expansionStates": [{"roles": ["Category"], "levels": [
                                    {"queryRefs": [cat_ref], "isPinned": True},
                                    {"queryRefs": ["dim_jugador.jugador"], "isPinned": True}], "root": {}}]}, filtros)


# ------------------------------------------------------------------ cabecera
# Selección al abrir la página: los tres centrales de la comparación del TFM
SELECCION_INICIAL = ["Diego Llorente", "Martin Valjent", "Antonio Raíllo"]
# 32 pt de DIN no cabe en 44 de alto: la caja de texto saca barra de desplazamiento; 54 de alto, subida 6 px
visual("titulo", 34, 16, 640, 54, {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [
    {"value": "COMPARACIÓN DE ", "textStyle": {"fontFamily": "DIN", "fontSize": "32pt", "fontWeight": "bold", "color": BLANCO}},
    {"value": "JUGADORES", "textStyle": {"fontFamily": "DIN", "fontSize": "32pt", "fontWeight": "bold", "color": ROJO}}]}]}}]},
    "visualContainerObjects": sin_marco()})
# Subtítulo gris y aviso rojo en el mismo sitio: cada medida está vacía cuando le toca a la otra
texto("subtitulo", 34, 62, 760, 18, med("dim_jugador", "Subtitulo comparacion"), 9, GRIS)
texto("avisoPuesto", 34, 62, 760, 18, med("dim_jugador", "Aviso puesto"), 9, ROJO)
def segmentacion(nombre, x, y, w, h, tabla_, columna, titulo, multiple, valores):
    """Lista desplegable con cabecera pequeña, como en el Buscador, y una selección guardada para abrir la página."""
    visual(nombre, x, y, w, h, {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {"projections": [proy(col(tabla_, columna), f"{tabla_}.{columna}", activa=True)]}}},
        "objects": {"data": [{"properties": {"mode": lit("Dropdown")}}],
                    "header": [{"properties": {"show": lit(True), "text": lit(titulo), "fontColor": color(OSCURO),
                                               "textSize": lit(8), "bold": lit(True), "background": color(FONDO)}}],
                    "selection": [{"properties": {"singleSelect": lit(not multiple), "strictSingleSelect": lit(not multiple)}}],
                    "items": [{"properties": {"fontColor": color(BLANCO), "background": color(FONDO), "textSize": lit(10)}}],
                    "general": [{"properties": {"selfFilterEnabled": lit(multiple), "filter": {"filter": {
                        "Version": 2, "From": [{"Name": "t", "Entity": tabla_, "Type": 0}],
                        "Where": [{"Condition": {"In": {
                            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": columna}}],
                            "Values": [[{"Literal": {"Value": f"'{v}'"}}] for v in valores]}}}]}}}}]},
        "visualContainerObjects": sin_marco()})


# Puesto de selección única: los percentiles solo son comparables dentro de un mismo grupo de posición, así que la
# página no deja mezclar puestos. El selector de jugadores queda filtrado por él a través de dim_posicion -> dim_jugador
segmentacion("segPuesto", 700, 24, 150, 56, "dim_posicion", "grupo", "PUESTO", False, ["central"])
# Jugadores: selección múltiple con buscador; abre con los tres centrales del TFM
segmentacion("segJugadores", 866, 24, 294, 56, "dim_jugador", "jugador", "JUGADORES", True, SELECCION_INICIAL)
visual("logoLaliga", 1182, 20, 64, 46, {"visualType": "image", "objects": {
    "general": [{"properties": {"imageUrl": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": "laliga.png"}}}}}],
    "imageScaling": [{"properties": {"imageScalingType": lit("Fit")}}]}, "visualContainerObjects": sin_marco()})
rect("lineaRoja", 34, 92, 1212, 2, ROJO)

# ------------------------------------------------------------------ tira de jugadores
# Una fila por jugador: color, foto, datos y la mediana de sus percentiles en cada bloque (DEF, BAL, ATA).
# Cabecera visible: sin ella no se sabe qué es DEF, BAL y ATA. Nombres reales en todas las columnas, aunque las
# primeras salgan en gris oscuro: con nombres en blanco el panel de formato no deja elegir la columna.
TIRA = [  # (campo, queryRef, cabecera, ancho, tinta, alineación)
    (med("dim_jugador", "Muestra color"), "dim_jugador.Muestra color", "COLOR", 8, None, None),
    (col("dim_jugador", "url_foto"), "dim_jugador.url_foto", "FOTO", 36, None, None),
    (col("dim_jugador", "jugador"), "dim_jugador.jugador", "JUGADOR", 300, BLANCO, None),
    (col("dim_equipo", "nombre_equipo"), "dim_equipo.nombre_equipo", "EQUIPO", 240, GRIS, None),
    (col("dim_jugador", "edad"), "dim_jugador.edad", "EDAD", 80, GRIS, "Right"),
    (col("dim_jugador", "minutos"), "dim_jugador.minutos", "MINUTOS", 100, GRIS, "Right"),
    (med("hechos_metrica", "Mediana defensa"), "hechos_metrica.Mediana defensa", "DEF", 130, BLANCO, "Right"),
    (med("hechos_metrica", "Mediana con balon"), "hechos_metrica.Mediana con balon", "BAL", 130, BLANCO, "Right"),
    (med("hechos_metrica", "Mediana ataque"), "hechos_metrica.Mediana ataque", "ATA", 130, BLANCO, "Right"),
]
# Columnas repartidas en los 1212 px (1184 de ancho total; con el ancho exacto sale barra horizontal).
# Fotos de 20 px y letra de 10 pt: tres filas y la cabecera caben en 80 px, de y=96 (bajo la raya roja) a y=176
tabla("tiraJugadores", 34, 96, 1212, 80,
      [proy(c, r, n) for c, r, n, *_ in TIRA], [a for *_, a, _, _ in TIRA],
      [fmt("dim_jugador.Muestra color", fondo=color_medida("dim_jugador", "Color jugador"))] +
      [fmt(r, t, al) for _, r, _, _, t, al in TIRA if t],
      cabecera=True, orden=col("dim_jugador", "minutos"), sentido="Descending", imagen=20, fila=0, tam=10)
texto("avisoSeleccion", 946, 96, 300, 16, med("dim_jugador", "Aviso seleccion"), 9, ROJO, negrita=True, alineacion="right")
# Dónde más se separan: una línea de texto
texto("separan", 34, 178, 1212, 14, med("hechos_metrica", "Texto separacion"), 8, GRIS)
rect("separador", 34, 188, 1212, 1, RAYA)

# ------------------------------------------------------------------ bloques: tres columnas a toda altura
# 482 px de alto: DEFENSA 21 barras (23 px cada una), CON BALÓN y ATAQUE 18 (26 px)
for bloque, titulo, x, w in [("defensa", "DEFENSA", 34, 382), ("con_balon", "CON BALÓN", 450, 382), ("ataque", "ATAQUE", 866, 380)]:
    texto(f"titulo_{bloque}", x, 194, w, 18, titulo, 13, BLANCO, "DIN", True)
    rect(f"raya_{bloque}", x, 212, w, 1, RAYA)
    filtros = [filtro_cat(f"filtroBloque_{bloque}", "dim_metrica", "bloque", [bloque])]
    if bloque == "defensa":
        filtros.append(filtro_orden_defensa("filtroOrden_defensa"))
    barras(f"barras_{bloque}", x, 214, w, 482,
           (col("dim_metrica", "nombre_corto"), "dim_metrica.nombre_corto"),
           (med("hechos_metrica", "Percentil metrica"), "hechos_metrica.Percentil metrica"), filtros)

# Etiqueta de la línea del 50, solo sobre DEFENSA y en la fila del título: Power BI no deja cambiar el tamaño de la
# etiqueta de la línea de referencia. Centrada en la línea del 50, medida en pantalla: x = 271 de la página
texto("etiquetaMediana", 211, 194, 120, 18, "MEDIANA DEL PUESTO", 8, OSCURO, alineacion="center")

# ------------------------------------------------------------------ pie
texto("pie", 34, 700, 1212, 16, "CADA BARRA ES EL PERCENTIL DEL JUGADOR DENTRO DE SU PUESTO · LA LÍNEA VERTICAL ES LA "
                                 "MEDIANA · VALORES POR 90 MINUTOS", 8, OSCURO)

# ------------------------------------------------------------------ escritura de la página
if os.path.isdir(f"{REP}/definition/pages/{PAG}"):
    shutil.rmtree(f"{REP}/definition/pages/{PAG}")
os.makedirs(VIS)
for v in visuales:
    os.makedirs(f"{VIS}/{v['name']}")
    json.dump(v, open(f"{VIS}/{v['name']}/visual.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
pagina = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
          "name": PAG, "displayName": "Comparación", "displayOption": "FitToPage", "height": 720, "width": 1280,
          "objects": {"background": [{"properties": {"color": color(FONDO), "transparency": lit(0)}}],
                      "outspace": [{"properties": {"color": color(FONDO), "transparency": lit(0)}}]}}
json.dump(pagina, open(f"{REP}/definition/pages/{PAG}/page.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
paginas = json.load(open(f"{REP}/definition/pages/pages.json", encoding="utf-8"))
if PAG not in paginas["pageOrder"]:
    paginas["pageOrder"].append(PAG)
json.dump(paginas, open(f"{REP}/definition/pages/pages.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)


# ------------------------------------------------------------------ modelo
def leer(ruta):
    """Lee un .tmdl con saltos de línea normalizados a \\n y devuelve también los que tenía (Power BI guarda CRLF)."""
    crudo = open(ruta, encoding="utf-8", newline="").read()
    return crudo.replace("\r\n", "\n"), ("\r\n" if "\r\n" in crudo else "\n")


def escribir(ruta, s, salto):
    open(ruta, "w", encoding="utf-8", newline="").write(s.replace("\n", salto))


def bloque_columna(nombre, extra=""):
    return (f"\tcolumn {nombre}\n\t\tdataType: string\n\t\tlineageTag: {uuid.uuid4()}\n\t\tsummarizeBy: none\n"
            f"\t\tsourceColumn: {nombre}\n{extra}\n\t\tannotation SummarizationSetBy = Automatic\n\n")


# Columnas nuevas de los CSV (cuaderno 01): color_jugador en dim_jugador y los tres grados en dim_equipo
for tabla_, cols in [("dim_jugador", ["color_jugador"]), ("dim_equipo", ["color_grado_1", "color_grado_2", "color_grado_3"])]:
    ruta = f"{SEM}/{tabla_}.tmdl"
    s, salto = leer(ruta)
    for c in cols:
        if f"\tcolumn {c}\n" in s:
            continue
        # Antes de la partición
        i = s.index("\tpartition ")
        s = s[:i] + bloque_columna(c) + s[i:]
        # dim_equipo tipa columna a columna en Power Query; dim_jugador tipa como texto todo lo no listado
        if tabla_ == "dim_equipo":
            m = re.search(r'\n([ \t]+)\{"color_secundario_origen", type text\}', s)
            s = s[:m.end()] + f',\n{m.group(1)}{{"{c}", type text}}' + s[m.end():]
    escribir(ruta, s, salto)

# Las métricas visibles: fuera de DEFENSA las de orden 8 y 9, que la página no pinta
VISIBLE = 'NOT ( dim_metrica[bloque] = "defensa" && dim_metrica[orden] > 7 )'
PLURAL = ('SWITCH ( g, "central", "CENTRALES", "lateral", "LATERALES", "pivote_mediocentro", "PIVOTES Y MEDIOCENTROS", '
          '"mediapunta", "MEDIAPUNTAS", "extremo", "EXTREMOS", "delantero", "DELANTEROS" )')
MEDIDAS = {
    "dim_jugador": [
        # Grado del color: el jugador de más minutos de su club entre los seleccionados se pinta con el grado 1, el
        # siguiente con el 2 y el tercero con el 3
        ("Color jugador",
         'VAR vEquipo = SELECTEDVALUE ( dim_jugador[id_equipo] ) VAR vMinutos = SELECTEDVALUE ( dim_jugador[minutos] ) '
         'VAR vId = SELECTEDVALUE ( dim_jugador[id_jugador] ) '
         'VAR k = COUNTROWS ( FILTER ( ALLSELECTED ( dim_jugador ), dim_jugador[id_equipo] = vEquipo && '
         '( dim_jugador[minutos] > vMinutos || ( dim_jugador[minutos] = vMinutos && dim_jugador[id_jugador] < vId ) ) ) ) + 1 '
         'RETURN IF ( HASONEVALUE ( dim_jugador[id_jugador] ), SWITCH ( TRUE (), '
         'k = 1, MAXX ( dim_jugador, RELATED ( dim_equipo[color_grado_1] ) ), '
         'k = 2, MAXX ( dim_jugador, RELATED ( dim_equipo[color_grado_2] ) ), '
         'MAXX ( dim_jugador, RELATED ( dim_equipo[color_grado_3] ) ) ) )', None),
        ("Muestra color", 'IF ( HASONEVALUE ( dim_jugador[id_jugador] ), " " )', None),
        ("Aviso seleccion",
         'VAR n = DISTINCTCOUNT ( dim_jugador[id_jugador] ) '
         'RETURN IF ( NOT ISFILTERED ( dim_jugador[jugador] ) || n < 2 || n > 3, "SELECCIONA ENTRE 2 Y 3 JUGADORES", "" )', None),
        ("Aviso puesto",
         'VAR grupos = COUNTROWS ( SUMMARIZE ( dim_jugador, dim_posicion[grupo] ) ) '
         'RETURN IF ( ISFILTERED ( dim_jugador[jugador] ) && grupos > 1, "OJO: LOS JUGADORES SELECCIONADOS NO COMPARTEN PUESTO", "" )', None),
        ("Subtitulo comparacion",
         'VAR grupos = COUNTROWS ( SUMMARIZE ( dim_jugador, dim_posicion[grupo] ) ) '
         'VAR g = MAXX ( dim_jugador, RELATED ( dim_posicion[grupo] ) ) '
         'VAR n = CALCULATE ( MAX ( hechos_jugador[n_grupo_referencia] ) ) '
         f'VAR plural = {PLURAL} '
         'RETURN IF ( NOT ISFILTERED ( dim_jugador[jugador] ) || grupos > 1, "", IF ( ISBLANK ( n ), '
         '"SIN GRUPO DE COMPARACIÓN: SU PUESTO NO ESTÁ DEFINIDO O CONFIRMADO", '
         '"PERCENTIL DENTRO DE LOS " & n & " " & plural & " DE LALIGA CON 600 MINUTOS O MÁS" ) )', None),
    ],
    "hechos_metrica": [
        # Mediana (no media) de los percentiles del jugador en las métricas visibles del apartado; sin las vacías
        ("Mediana apartado",
         f'MEDIANX ( FILTER ( dim_metrica, {VISIBLE} ), '
         'IF ( NOT ISBLANK ( CALCULATE ( SELECTEDVALUE ( hechos_metrica[valor] ) ) ), '
         'CALCULATE ( SELECTEDVALUE ( hechos_metrica[percentil] ) ) ) )', "0"),
        # Distancia entre el mejor y el peor de los seleccionados; vacía si alguno no tiene valor o percentil
        ("Separacion",
         'VAR oculta = SELECTEDVALUE ( dim_metrica[bloque] ) = "defensa" && SELECTEDVALUE ( dim_metrica[orden] ) > 7 '
         'VAR t = ADDCOLUMNS ( VALUES ( dim_jugador[id_jugador] ), '
         '"p", CALCULATE ( SELECTEDVALUE ( hechos_metrica[percentil] ) ), "v", CALCULATE ( SELECTEDVALUE ( hechos_metrica[valor] ) ) ) '
         'VAR n = COUNTROWS ( t ) '
         'RETURN IF ( HASONEVALUE ( dim_metrica[id_metrica] ) && NOT oculta && n >= 2 && n <= 3 '
         '&& COUNTROWS ( FILTER ( t, ISBLANK ( [v] ) || ISBLANK ( [p] ) ) ) = 0, MAXX ( t, [p] ) - MINX ( t, [p] ) )', "0"),
        ("Mediana defensa", 'CALCULATE ( [Mediana apartado], dim_metrica[bloque] = "defensa" )', "0"),
        ("Mediana con balon", 'CALCULATE ( [Mediana apartado], dim_metrica[bloque] = "con_balon" )', "0"),
        ("Mediana ataque", 'CALCULATE ( [Mediana apartado], dim_metrica[bloque] = "ataque" )', "0"),
        # Las tres métricas con más distancia entre el mejor y el peor de los seleccionados, en una línea
        ("Texto separacion",
         'VAR t = FILTER ( ADDCOLUMNS ( VALUES ( dim_metrica[id_metrica] ), '
         '"nom", CALCULATE ( SELECTEDVALUE ( dim_metrica[nombre] ) ), "d", CALCULATE ( [Separacion] ), '
         '"r", CALCULATE ( [Separacion ranking] ) ), NOT ISBLANK ( [d] ) ) '
         'VAR top3 = TOPN ( 3, t, [r], DESC ) VAR primero = MAXX ( top3, [r] ) '
         'RETURN IF ( ISEMPTY ( top3 ), "", "MÁS SE SEPARAN EN: " & CONCATENATEX ( top3, '
         'UPPER ( [nom] ) & " (" & [d] & IF ( [r] = primero, " PTS", "" ) & ")", " · ", [r], DESC ) )', None),
        # Para ordenar y para el filtro de las 3 primeras: desempata por el orden de la métrica
        ("Separacion ranking",
         'VAR d = [Separacion] RETURN IF ( NOT ISBLANK ( d ), d - SELECTEDVALUE ( hechos_metrica[id_metrica] ) / 1000 )', "0.000"),
    ],
}
for t, medidas in MEDIDAS.items():
    ruta = f"{SEM}/{t}.tmdl"
    s, salto = leer(ruta)
    for nombre, expr, formato in medidas:
        # Power BI guarda sin comillas los nombres sin espacios (measure Separacion = ...): se buscan las dos formas
        patron = rf"\tmeasure (?:'{re.escape(nombre)}'|{re.escape(nombre)}) = [^\n]*\n"
        if re.search(patron, s):
            # Ya existe: se actualiza su expresión (una línea) y se dejan sus propiedades
            s = re.sub(patron, lambda m: m.group(0).split(" = ", 1)[0] + f" = {expr}\n", s, count=1)
            continue
        linea = f"\tmeasure '{nombre}' = {expr}\n"
        if formato:
            linea += f"\t\tformatString: {formato}\n"
        linea += f"\t\tlineageTag: {uuid.uuid4()}\n\n"
        s = re.sub(r"(table [^\n]+\n\tlineageTag: [^\n]+\n\n)", lambda m: m.group(1) + linea, s, count=1)
    escribir(ruta, s, salto)

print("visuales:", [v["name"] for v in visuales])
