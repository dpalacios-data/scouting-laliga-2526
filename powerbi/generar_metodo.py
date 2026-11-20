"""Genera la página Método del informe PBIR (powerbi/), su imagen de 71 puntos y las medidas que usa.

Uso: python powerbi/generar_metodo.py   (con Power BI Desktop cerrado; luego abrir el .pbip)

Casi todo es texto fijo. Salen del modelo: el número de jugadores del panel (561) y el gráfico de jugadores con
percentil fiable por grupo. Antes de volver a ejecutarlo, comprobar con git diff qué ha guardado Power BI y llevarlo
aquí (esquema, propiedades, saltos de línea de los .tmdl).
"""
import json, os, re, shutil, uuid

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
REP = f"{RAIZ}/scouting-laliga-2526.Report"
SEM = f"{RAIZ}/scouting-laliga-2526.SemanticModel/definition/tables"
PAG = "metodo"
VIS = f"{REP}/definition/pages/{PAG}/visuals"
ESQ = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json"
BLANCO, GRIS, OSCURO, ROJO, RAYA, FONDO = "#F2F5F8", "#79879A", "#44505F", "#FF4B44", "#1A212C", "#07090E"
DIN_FORMA = "wf_standard-font, helvetica, arial, sans-serif"   # nombre interno de DIN en las formas
BARRA_GRUPO, PUNTO_GRIS = "#3F5468", "#2F3E50"


# ------------------------------------------------------------------ ayudas
def lit(v):
    txt = ("true" if v else "false") if isinstance(v, bool) else (f"{v}D" if isinstance(v, (int, float)) else f"'{v}'")
    return {"expr": {"Literal": {"Value": txt}}}


def entero(v):
    return {"expr": {"Literal": {"Value": f"{v}L"}}}


def color(c):
    return {"solid": {"color": lit(c)}}


def col(t, c):
    return {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": c}}


def med(t, m):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": t}}, "Property": m}}


def sin_marco():
    return {k: [{"properties": {"show": lit(False)}}] for k in ("background", "border", "title", "visualHeader", "dropShadow")} | \
        {"padding": [{"properties": {k: lit(0) for k in ("top", "bottom", "left", "right")}}]}


visuales = []


def visual(nombre, x, y, w, h, cuerpo):
    visuales.append({"$schema": ESQ, "name": nombre,
                     "position": {"x": x, "y": y, "z": len(visuales) * 1000, "height": h, "width": w, "tabOrder": len(visuales) * 1000},
                     "visual": cuerpo})


def texto(nombre, x, y, w, h, contenido, tam, c, familia="Segoe UI", negrita=False, alineacion="left", vertical="top"):
    """Texto en una forma: sin margen ni barra de desplazamiento; parte en líneas si no cabe. contenido = texto o medida."""
    valor = {"expr": contenido} if isinstance(contenido, dict) else lit(contenido)
    visual(nombre, x, y, w, h, {"visualType": "shape", "objects": {
        "shape": [{"properties": {"tileShape": lit("rectangle")}}],
        "fill": [{"properties": {"show": lit(False)}}],
        "outline": [{"properties": {"show": lit(False)}}],
        "text": [{"properties": {"show": lit(True)}},
                 {"selector": {"id": "default"}, "properties": {
                     "text": valor, "fontColor": color(c), "fontSize": lit(tam),
                     "fontFamily": lit(DIN_FORMA if familia == "DIN" else familia), "bold": lit(negrita),
                     "horizontalAlignment": lit(alineacion), "verticalAlignment": lit(vertical),
                     "leftMargin": lit(0), "rightMargin": lit(0), "topMargin": lit(0), "bottomMargin": lit(0)}}]},
        "visualContainerObjects": sin_marco()})


def rect(nombre, x, y, w, h, c):
    visual(nombre, x, y, w, h, {"visualType": "shape", "objects": {
        "shape": [{"properties": {"tileShape": lit("rectangle")}}],
        "fill": [{"properties": {"show": lit(True)}}, {"properties": {"fillColor": color(c), "transparency": lit(0)}, "selector": {"id": "default"}}],
        "outline": [{"properties": {"show": lit(False)}}]}, "visualContainerObjects": sin_marco()})


def imagen(nombre, x, y, w, h, fichero):
    visual(nombre, x, y, w, h, {"visualType": "image", "objects": {
        "general": [{"properties": {"imageUrl": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": fichero}}}}}],
        "imageScaling": [{"properties": {"imageScalingType": lit("Fit")}}]}, "visualContainerObjects": sin_marco()})


def titulo_bloque(nombre, x, y, w, rotulo):
    texto(f"titulo_{nombre}", x, y, w, 16, rotulo, 13, BLANCO, "DIN", True, vertical="middle")
    rect(f"raya_{nombre}", x, y + 18, w, 1, RAYA)


def puntos(nombre, x, y, w, alto, lineas, alto_titulo=14):
    """Lista de puntos: título en blanco y explicación en gris debajo. alto = alto de cada punto, o lista de altos."""
    altos = alto if isinstance(alto, list) else [alto] * len(lineas)
    yy = y
    for k, ((tit, expl), a) in enumerate(zip(lineas, altos)):
        texto(f"{nombre}_{k}_t", x, yy, w, alto_titulo, tit, 9, BLANCO, negrita=True)
        texto(f"{nombre}_{k}_e", x, yy + alto_titulo, w, a - alto_titulo - 2, expl, 9, GRIS)
        yy += a


# ------------------------------------------------------------------ imagen: 71 puntos, el último en rojo
def puntos_percentil(ruta, n=71, ancho=382, alto=44, escala=2):
    """71 puntos en fila (el grupo de centrales): 70 en gris y el último en rojo, con fondo transparente.
    Se dibuja al doble de tamaño para que se vea nítido en pantallas con escala."""
    w, h = ancho * escala, alto * escala
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    paso = w / n
    r = paso * 0.32
    for i in range(n):
        cx, cy = paso * (i + 0.5), h / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ROJO if i == n - 1 else PUNTO_GRIS)
    im.save(ruta)


PNG = "percentil_71.png"
puntos_percentil(f"{RAIZ}/{PNG}")
# Registrado en el informe como recurso, igual que el logo
shutil.copyfile(f"{RAIZ}/{PNG}", f"{REP}/StaticResources/RegisteredResources/{PNG}")
informe = json.load(open(f"{REP}/definition/report.json", encoding="utf-8"))
reg = next(p for p in informe["resourcePackages"] if p["name"] == "RegisteredResources")
if not any(i["name"] == PNG for i in reg["items"]):
    reg["items"].append({"name": PNG, "path": PNG, "type": "Image"})
json.dump(informe, open(f"{REP}/definition/report.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ------------------------------------------------------------------ cabecera
visual("titulo", 34, 16, 700, 54, {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [
    {"value": "QUÉ ES ESTO ", "textStyle": {"fontFamily": "DIN", "fontSize": "32pt", "fontWeight": "bold", "color": BLANCO}},
    {"value": "Y QUÉ NO", "textStyle": {"fontFamily": "DIN", "fontSize": "32pt", "fontWeight": "bold", "color": ROJO}}]}]}}]},
    "visualContainerObjects": sin_marco()})
texto("subtitulo", 34, 68, 760, 18, "FUENTES, MÉTODO Y LÍMITES · LALIGA 2025/26", 9, GRIS, vertical="middle")
imagen("logoLaliga", 1182, 22, 64, 46, "laliga.png")
rect("lineaRoja", 34, 96, 1212, 2, ROJO)

# ------------------------------------------------------------------ columna 1: datos y comprobación
titulo_bloque("datos", 34, 112, 382, "DE DÓNDE SALEN LOS DATOS")
texto("datos_texto", 34, 134, 382, 76,
      "Ninguna fuente pública distingue central de lateral ni pivote de extremo, y sin eso no se puede comparar a un "
      "jugador con los de su puesto. La asignación de posición es propia y se validó contra las alineaciones de WhoScored.",
      9, GRIS)
# Fuentes: nombre en blanco, qué aporta en gris y la cifra a la derecha. La de Understat sale del modelo.
FUENTES = [
    ("Understat", "Minutos, partidos, goles, xG, xA y xG chain", med("dim_jugador", "Jugadores del panel")),
    # Suma de data/eventos_por_jugador.csv: entradas intentadas, intercepciones, despejes, pases bloqueados y
    # duelos aéreos disputados (los exitosos y los ganados ya están dentro de los intentados y disputados)
    ("WhoScored", "Acciones defensivas con cualificador Opta y alineaciones", "67.953"),
    ("Transfermarkt", "Edad, altura, pie, nacionalidad, valor y retrato", "557"),
    ("Elaboración propia", "Posición real de cada jugador", "637"),
    ("Wikipedia", "Colores de la equipación local", "20"),
]
for k, (nombre, aporta, cifra) in enumerate(FUENTES):
    y = 218 + k * 36
    texto(f"fuente_{k}_n", 34, y, 300, 14, nombre, 9, BLANCO, negrita=True)
    texto(f"fuente_{k}_a", 34, y + 15, 340, 17, aporta, 9, GRIS)
    texto(f"fuente_{k}_c", 336, y, 80, 14, cifra, 9, BLANCO, negrita=True, alineacion="right")
    rect(f"fuente_{k}_raya", 34, y + 33, 382, 1, RAYA)
titulo_bloque("comprobar", 34, 416, 382, "CÓMO COMPROBARLO")
puntos("comprobar", 34, 438, 382, 62, [
    ("Repositorio público", "Nueve cuadernos numerados, del 00 al 08, que se ejecutan en orden"),
    ("Ficheros de origen con su hash", "SHA-256 verificables desde un clon limpio"),
    ("Cuaderno de auditoría", "Reproduce las cifras publicadas antes de comparar"),
    ("Cruces escritos como listas", "Cada emparejamiento de nombre está a la vista"),
])

# ------------------------------------------------------------------ columna 2: el percentil
titulo_bloque("percentil", 450, 112, 382, "CÓMO SE LEE UN PERCENTIL")
texto("percentil_texto", 450, 134, 382, 50,
      "Es el porcentaje de jugadores de su puesto que quedan estrictamente por debajo. Nada de medias: cuenta cuántos superas.",
      9, GRIS)
imagen("percentil_puntos", 450, 192, 382, 44, PNG)
texto("percentil_ejemplo", 450, 244, 382, 70,
      "Un central que supera a 70 de los otros 70 sale en el percentil 98,6, no en 100. Y como el grupo tiene 71, cada "
      "puesto vale 1,4 puntos: por eso el panel da el percentil sin decimales.", 9, GRIS)
titulo_bloque("referencia", 450, 326, 382, "CONTRA CUÁNTOS SE COMPARA")
texto("referencia_texto", 450, 348, 382, 36,
      "Solo entran los jugadores con 600 minutos o más. Con menos, una buena tarde distorsiona la temporada.", 9, GRIS)
# Jugadores con percentil fiable por grupo: sale del modelo. Mediapunta en rojo por muestra reducida.
visual("grupos", 450, 390, 382, 150, {
    "visualType": "clusteredBarChart",
    "query": {"queryState": {
        "Category": {"projections": [{"field": col("dim_posicion", "grupo_nombre"), "queryRef": "dim_posicion.grupo_nombre",
                                      "nativeQueryRef": "grupo_nombre", "active": True}]},
        "Y": {"projections": [{"field": med("hechos_jugador", "Jugadores fiables"), "queryRef": "hechos_jugador.Jugadores fiables",
                               "nativeQueryRef": "Jugadores fiables"}]}},
        "sortDefinition": {"sort": [{"field": med("hechos_jugador", "Jugadores fiables"), "direction": "Descending"}]}},
    "objects": {
        "categoryAxis": [{"properties": {"show": lit(True), "showAxisTitle": lit(False), "labelColor": color(GRIS), "fontSize": lit(8),
                                         "innerPadding": entero(40), "outerPadding": entero(10)}}],
        "valueAxis": [{"properties": {"show": lit(False), "showAxisTitle": lit(False), "gridlineShow": lit(False)}}],
        "legend": [{"properties": {"show": lit(False)}}],
        "labels": [{"properties": {"show": lit(True), "color": color("#C3CBD5"), "fontSize": lit(8), "labelPrecision": entero(0)}}],
        "dataPoint": [{"properties": {"fill": {"solid": {"color": {"expr": med("hechos_jugador", "Color grupo")}}}},
                       "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}]},
    "visualContainerObjects": sin_marco()})
titulo_bloque("decisiones", 450, 554, 382, "TRES DECISIONES QUE LO RECORREN TODO")
# La última explicación ocupa dos líneas: su punto es más alto
puntos("decisiones", 450, 576, 382, [36, 36, 48], [
    ("Siempre la mediana, nunca la media", "Un jugador con cifras infladas no mueve la mediana del grupo"),
    ("Un hueco se queda vacío, nunca a cero", "Cero significa que no lo hizo, vacío significa que no se sabe"),
    ("Volumen y éxito, separados", "Duelos disputados y duelos ganados no son lo mismo, y se llaman distinto"),
])

# ------------------------------------------------------------------ columna 3: límites y cuadre
titulo_bloque("limites", 866, 112, 380, "QUÉ NO CUBRE")
puntos("limites", 866, 134, 380, 55, [
    ("Porteros", "39 fuera. Necesitan paradas, salidas y goles esperados a puerta, que estas fuentes no dan completos"),
    ("Fin de contrato", "La única fuente disponible es de la temporada siguiente, y mezclarla falsearía la lectura"),
    ("Segunda División", "WhoScored no publica sus eventos, así que no hay acciones defensivas para comparar"),
    ("Posición sin confirmar", "28 jugadores: 26 con menos de 3 titularidades y 2 sin identificador de WhoScored. "
                               "Ninguno pasa de 330 minutos"),
    ("Sin métricas de eventos", "5 jugadores cuyo cruce de nombre no quedó demostrado. Vacío, nunca cero"),
    ("Mediapunta", "Solo 28 jugadores de referencia. El percentil ahí es menos fiable y el panel lo avisa"),
])
titulo_bloque("cuadre", 866, 478, 380, "DE 637 A 561")
CUADRE = [("Jugadores de campo en el fichero de posiciones", "637"),
          ("No disputaron ningún minuto", "−112"),
          ("Cruce de nombre no demostrado", "−2"),
          ("Recuperados de Understat sin posición", "+38")]
for k, (etq, n) in enumerate(CUADRE):
    y = 500 + k * 30
    texto(f"cuadre_{k}_e", 866, y, 300, 16, etq, 9, GRIS, vertical="middle")
    texto(f"cuadre_{k}_n", 1166, y, 80, 16, n, 9, GRIS, alineacion="right", vertical="middle")
rect("cuadre_raya", 866, 624, 380, 2, ROJO)
texto("cuadre_total_e", 866, 634, 300, 28, "Jugadores del panel", 13, ROJO, "DIN", True, vertical="middle")
texto("cuadre_total_n", 1146, 634, 100, 28, med("dim_jugador", "Jugadores del panel"), 18, ROJO, "DIN", True,
      alineacion="right", vertical="middle")

# ------------------------------------------------------------------ pie
texto("pie", 34, 700, 1212, 16, "TEMPORADA 2025/26 COMPLETA · 38 JORNADAS · github.com/dpalacios-data/scouting-laliga-2526",
      8, OSCURO, vertical="middle")

# ------------------------------------------------------------------ escritura de la página
if os.path.isdir(f"{REP}/definition/pages/{PAG}"):
    shutil.rmtree(f"{REP}/definition/pages/{PAG}")
os.makedirs(VIS)
for v in visuales:
    os.makedirs(f"{VIS}/{v['name']}")
    json.dump(v, open(f"{VIS}/{v['name']}/visual.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
pagina = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
          "name": PAG, "displayName": "Método", "displayOption": "FitToPage", "height": 720, "width": 1280,
          "objects": {"background": [{"properties": {"color": color(FONDO), "transparency": lit(0)}}],
                      "outspace": [{"properties": {"color": color(FONDO), "transparency": lit(0)}}]}}
json.dump(pagina, open(f"{REP}/definition/pages/{PAG}/page.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
paginas = json.load(open(f"{REP}/definition/pages/pages.json", encoding="utf-8"))
if PAG not in paginas["pageOrder"]:
    paginas["pageOrder"].append(PAG)
json.dump(paginas, open(f"{REP}/definition/pages/pages.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)


# ------------------------------------------------------------------ modelo (los .tmdl se guardan con CRLF, como Power BI)
def leer(ruta):
    crudo = open(ruta, encoding="utf-8", newline="").read()
    return crudo.replace("\r\n", "\n"), ("\r\n" if "\r\n" in crudo else "\n")


def escribir(ruta, s, salto):
    open(ruta, "w", encoding="utf-8", newline="").write(s.replace("\n", salto))


def poner_medida(s, nombre, expr, formato=None):
    patron = rf"\tmeasure (?:'{re.escape(nombre)}'|{re.escape(nombre)}) = [^\n]*\n"
    if re.search(patron, s):
        return re.sub(patron, lambda m: m.group(0).split(" = ", 1)[0] + f" = {expr}\n", s, count=1)
    linea = f"\tmeasure '{nombre}' = {expr}\n" + (f"\t\tformatString: {formato}\n" if formato else "") + f"\t\tlineageTag: {uuid.uuid4()}\n\n"
    return re.sub(r"(table [^\n]+\n\tlineageTag: [^\n]+\n\n)", lambda m: m.group(1) + linea, s, count=1)


ruta = f"{SEM}/dim_jugador.tmdl"
s, salto = leer(ruta)
s = poner_medida(s, "Jugadores del panel", "FORMAT ( COUNTROWS ( ALL ( dim_jugador ) ), \"0\" )")
escribir(ruta, s, salto)

ruta = f"{SEM}/hechos_jugador.tmdl"
s, salto = leer(ruta)
s = poner_medida(s, "Jugadores fiables", "CALCULATE ( COUNTROWS ( hechos_jugador ), hechos_jugador[percentil_fiable] = TRUE () )", "0")
s = poner_medida(s, "Color grupo", f'IF ( SELECTEDVALUE ( dim_posicion[grupo] ) = "mediapunta", "{ROJO}", "{BARRA_GRUPO}" )')
escribir(ruta, s, salto)

# Nombre del grupo para el eje del gráfico (columna calculada)
ruta = f"{SEM}/dim_posicion.tmdl"
s, salto = leer(ruta)
if "\tcolumn grupo_nombre = " not in s:
    nueva = ('\tcolumn grupo_nombre = SWITCH ( dim_posicion[grupo], "central", "Central", "lateral", "Lateral", '
             '"pivote_mediocentro", "Pivote y mediocentro", "mediapunta", "Mediapunta", "extremo", "Extremo", '
             '"delantero", "Delantero", "sin_definir", "Sin definir", "sin_confirmar", "Sin confirmar" )\n'
             f"\t\tdataType: string\n\t\tlineageTag: {uuid.uuid4()}\n\t\tsummarizeBy: none\n\t\tisDataTypeInferred\n\n"
             "\t\tannotation SummarizationSetBy = Automatic\n\n")
    i = s.index("\tpartition ")
    s = s[:i] + nueva + s[i:]
escribir(ruta, s, salto)
print("visuales:", len(visuales))
