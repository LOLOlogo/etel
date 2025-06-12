import tkinter as tk
from tkinter import filedialog, messagebox
import json

def seleccionar_archivos_json():
    """
    Abre una ventana para seleccionar dos archivos JSON:
      - Uno con el análisis general.
      - Otro con el análisis sintáctico/morfosintáctico.
    Muestra un mensaje de error si no se seleccionan exactamente dos.
    :return: Lista con las rutas de los dos archivos seleccionados o None si la selección es inválida.
    """
    messagebox.showinfo(
        "Selección de archivos",
        ("Seleccione los dos archivos JSON generados previamente:\n"
         "- Uno con el análisis general del texto.\n"
         "- Otro con el análisis sintáctico/morfosintáctico.")
    )
    archivos = filedialog.askopenfilenames(
        title="Seleccionar archivos JSON",
        filetypes=[("Archivos JSON", "*.json")],
        multiple=True
    )
    if len(archivos) != 2:
        messagebox.showerror("Error", "Debe seleccionar exactamente dos archivos JSON.")
        return None
    return list(archivos)

def simplificar_detalles(morfologia, pos):
    """
    Simplifica y traduce los atributos morfosintácticos a un lenguaje sencillo,
    organizando la información en el orden requerido para que cualquier persona (incluso un niño)
    pueda entenderla.
    
    Para verbos (pos en ["VERB", "AUX"]):
      Orden deseado: 
         [VerbForm] [Mood]; [Tense] (si existe); [Person] [Number]
      Ejemplo: si se tiene {"VerbForm": "Fin", "Mood": "Imp", "Tense": "Pres", "Person": "3", "Number": "Sing"}
         se mostrará: "conjugado imperativo; presente; 3ª persona singular"
    
    Para determinantes (pos == "DET"):
      Orden deseado:
         [PronType] [Definite]; [Gender]; [Number]
      Ejemplo: si se tiene {"PronType": "Art", "Definite": "Ind", "Gender": "Masc", "Number": "Sing"}
         se mostrará: "artículo indefinido; masculino; singular"
    
    Para otros tipos se muestra en un orden genérico.
    
    :param morfologia: Diccionario con atributos morfosintácticos.
    :param pos: Etiqueta gramatical del token (por ejemplo, "VERB", "DET").
    :return: Cadena con los valores simplificados y organizados.
    """
    # Diccionario de traducciones para los valores:
    traducciones = {
        "Mood": {"Ind": "indicativo", "Subj": "subjuntivo", "Imp": "imperativo"},
        "Number": {"Sing": "singular", "Plur": "plural"},
        "Tense": {"Past": "pasado", "Pres": "presente", "Fut": "futuro"},
        "VerbForm": {"Fin": "conjugado", "Inf": "infinitivo", "Part": "participio"},
        "Definite": {"Def": "definido", "Ind": "indefinido"},
        "PronType": {"Art": "artículo", "Prs": "pronombre"},
        "Gender": {"Masc": "masculino", "Fem": "femenino"},
        "Person": {"1": "1ª persona", "2": "2ª persona", "3": "3ª persona"},
        "Reflex": {"Yes": "sí", "No": "no"}
    }
    
    if pos in ["VERB", "AUX"]:
        verbform = traducciones["VerbForm"].get(morfologia.get("VerbForm", ""), morfologia.get("VerbForm", ""))
        mood = traducciones["Mood"].get(morfologia.get("Mood", ""), morfologia.get("Mood", ""))
        tense = traducciones["Tense"].get(morfologia.get("Tense", ""), morfologia.get("Tense", ""))
        person = traducciones["Person"].get(morfologia.get("Person", ""), morfologia.get("Person", ""))
        number = traducciones["Number"].get(morfologia.get("Number", ""), morfologia.get("Number", ""))
        result = verbform
        if mood:
            result += " " + mood
        if tense:
            result += "; " + tense
        if person and number:
            result += "; " + person + " " + number
        elif person:
            result += "; " + person
        elif number:
            result += "; " + number
        return result

    elif pos == "DET":
        pronType = traducciones["PronType"].get(morfologia.get("PronType", ""), morfologia.get("PronType", ""))
        definite = traducciones["Definite"].get(morfologia.get("Definite", ""), morfologia.get("Definite", ""))
        gender = traducciones["Gender"].get(morfologia.get("Gender", ""), morfologia.get("Gender", ""))
        number = traducciones["Number"].get(morfologia.get("Number", ""), morfologia.get("Number", ""))
        result = ""
        if pronType and definite:
            result += pronType + " " + definite
        elif pronType:
            result += pronType
        elif definite:
            result += definite
        if gender:
            result += "; " + gender
        if number:
            result += "; " + number
        return result

    else:
        order = ["VerbForm", "Mood", "Tense", "Number", "Gender", "Definite", "PronType", "Person", "Reflex"]
        parts = []
        for key in order:
            if key in morfologia:
                parts.append(traducciones.get(key, {}).get(morfologia[key], morfologia[key]))
        return "; ".join(parts)

# Mapeo de etiquetas gramaticales: se agrupan los nombres propios (PROPN) con los sustantivos (NOUN).
etiquetas_traducidas = {
    "DET": "determinante",
    "NOUN": "sustantivo",
    "PROPN": "sustantivo",
    "VERB": "verbo",
    "AUX": "verbo auxiliar",
    "ADJ": "adjetivo",
    "ADV": "adverbio",
    "PRON": "pronombre",
    "ADP": "preposición",
    "CCONJ": "conjunción",
    "SCONJ": "conjunción",
    "PART": "partícula",
    "NUM": "número",
    "PUNCT": "signo de puntuación",
    "SYM": "símbolo",
    "X": "otro"
}

def procesar_oracion(oracion, contador_oracion):
    """
    Procesa una oración del análisis sintáctico y genera HTML para:
      - Una tabla de tokens con las columnas: Palabra, Categoría y Detalles.
    :param oracion: Diccionario con la información de la oración.
    :param contador_oracion: Número de la oración.
    :return: Cadena HTML con el informe de la oración.
    """
    html_out = f"<h3>Oración {contador_oracion}</h3>\n"
    oracion_texto = oracion.get("oracion", "Texto no disponible")
    html_out += f"<p><em>\"{oracion_texto}\"</em></p>\n"
    html_out += """<table class="token-table">
        <tr>
            <th>Palabra</th>
            <th>Categoría</th>
            <th>Detalles</th>
        </tr>
    """
    tokens = oracion.get("tokens", oracion.get("sintaxis", []))
    for token in tokens:
        palabra = token.get("texto", "")
        pos = token.get("pos", token.get("tipo", ""))
        categoria = etiquetas_traducidas.get(pos, pos)
        morfologia = token.get("morph", {})
        if isinstance(morfologia, dict) and morfologia:
            detalles = simplificar_detalles(morfologia, pos)
        else:
            detalles = "-"
        html_out += f"""<tr>
            <td>{palabra}</td>
            <td>{categoria}</td>
            <td>{detalles}</td>
        </tr>
        """
    html_out += "</table>\n"
    return html_out

def crear_html(contenido):
    """
    Recibe el contenido HTML para el cuerpo y lo encapsula dentro de una estructura HTML completa,
    con cabecera y estilos definidos.
    :param contenido: Cadena HTML que representa el contenido del body.
    :return: Cadena HTML completa.
    """
    header = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Informe de Evaluación del Lenguaje</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f9f9f9; color: #333; margin: 20px; }
    h1 { color: #2E8B57; text-align: center; }
    h2 { color: #4682B4; border-bottom: 2px solid #4682B4; padding-bottom: 5px; }
    h3 { color: #555; }
    h4 { color: #666; margin-top: 20px; }
    h5 { color: #777; margin-top: 10px; }
    .section { margin-bottom: 40px; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background-color: #eee; }
    .token-table th { background-color: #d0e6f7; }
    .categoria-table th { background-color: #f0e68c; }
    .resumen p { font-size: 16px; }
  </style>
</head>
<body>
  <h1>Informe de Evaluación del Lenguaje</h1>
"""
    footer = """
  <div style="text-align: center; margin-top: 50px;">
    <p>Manuel G. Hevia</p>
    <p><a href="https://www.linkedin.com/in/M-G-hevia-logopeda" target="_blank">www.linkedin.com/in/M-G-hevia-logopeda</a></p>
  </div>
</body>
</html>"""
    return header + contenido + footer

def generar_informe_visual(json_general, json_sintactico, nombre_archivo="informe_visual.html"):
    """
    Genera un informe HTML visual y amigable a partir de los datos de los archivos JSON.
    Se organizan secciones para:
      - Resumen general
      - Categorías lingüísticas
      - Texto transcrito
      - Análisis sintáctico/morfosintáctico (por oración)
    """
    contenido = ""
    # Sección: Resumen General
    resumen = json_general.get("resumen", {})
    total_palabras = resumen.get("total_palabras", "No disponible")
    palabras_unicas = resumen.get("palabras_unicas", "No disponible")
    ratio = resumen.get("ratio_tipo_token", "No disponible")
    prom_oracion = resumen.get("promedio_palabras_oracion", "No disponible")
    long_media = resumen.get("longitud_media_palabra", "No disponible")
    texto_transcrito = json_general.get("texto_transcrito", "No se encontró el texto transcrito.")
    
    contenido += f"""  <div class="section resumen">
    <h2>Resumen General</h2>
    <p><strong>Total de palabras:</strong> {total_palabras}</p>
    <p><strong>Palabras únicas:</strong> {palabras_unicas}</p>
    <p><strong>Ratio Tipo-Token:</strong> {float(ratio) if isinstance(ratio, (float,int)) else ratio:.3f}</p>
    <p><strong>Promedio de palabras por oración:</strong> {prom_oracion}</p>
    <p><strong>Longitud media de palabra:</strong> {long_media}</p>
  </div>
"""
    # Sección: Categorías Lingüísticas
    categorias = json_general.get("categorias", {})
    sustantivos = categorias.get("sustantivos", {})
    nombres_propios = categorias.get("nombres_propios", {})
    sust_comb = {}
    if isinstance(sustantivos, dict):
        for k, v in sustantivos.items():
            sust_comb[k] = sust_comb.get(k, 0) + v
    if isinstance(nombres_propios, dict):
        for k, v in nombres_propios.items():
            sust_comb[k] = sust_comb.get(k, 0) + v

    def tabla_categoria(titulo, datos):
        table = f"""<h3>{titulo}</h3>
        <table class="categoria-table">
          <tr><th>Palabra</th><th>Frecuencia</th></tr>
        """
        if isinstance(datos, dict) and datos:
            for palabra, freq in datos.items():
                table += f"<tr><td>{palabra}</td><td>{freq}</td></tr>\n"
        else:
            table += f"<tr><td colspan='2'>No se han identificado {titulo.lower()}.</td></tr>\n"
        table += "</table>\n"
        return table

    contenido += """  <div class="section categorias">
    <h2>Categorías Lingüísticas</h2>
"""
    contenido += tabla_categoria("Sustantivos (incluyendo nombres propios)", sust_comb)
    contenido += tabla_categoria("Verbos", categorias.get("verbos", {}))
    contenido += tabla_categoria("Adjetivos", categorias.get("adjetivos", {}))
    contenido += tabla_categoria("Adverbios", categorias.get("adverbios", {}))
    contenido += tabla_categoria("Pronombres", categorias.get("pronombres", {}))
    contenido += tabla_categoria("Determinantes", categorias.get("determinantes", {}))
    contenido += tabla_categoria("Adposiciones", categorias.get("adposiciones", {}))
    contenido += tabla_categoria("Conjunciones", categorias.get("conjunciones", {}))
    contenido += "  </div>\n"

    # Sección: Texto Transcrito
    contenido += """  <div class="section texto-transcrito">
    <h2>Texto Transcrito</h2>
    <p style="font-size:16px;">{0}</p>
  </div>
""".format(texto_transcrito)

    # Sección: Análisis Sintáctico y Morfosintáctico
    contenido += """  <div class="section sintactico">
    <h2>Análisis Sintáctico y Morfosintáctico</h2>
    <p>Se presenta a continuación el análisis de cada oración en un lenguaje sencillo.</p>
"""
    contador_oracion = 1
    if isinstance(json_sintactico, list) and len(json_sintactico) > 0 and "oraciones" in json_sintactico[0]:
        for fragmento in json_sintactico:
            fragmento_texto = fragmento.get("fragmento", "")
            if fragmento_texto:
                contenido += f"<h3>Fragmento: {fragmento_texto}</h3>\n"
            for oracion in fragmento.get("oraciones", []):
                contenido += procesar_oracion(oracion, contador_oracion)
                contador_oracion += 1
    elif isinstance(json_sintactico, list):
        for oracion in json_sintactico:
            contenido += procesar_oracion(oracion, contador_oracion)
            contador_oracion += 1
    else:
        contenido += "<p>No se encontró un análisis sintáctico válido.</p>\n"
    contenido += "  </div>\n"  # Fin sección sintáctica

    html = crear_html(contenido)

    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html)
        messagebox.showinfo("Éxito", f"El informe visual se ha generado correctamente en:\n{nombre_archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al generar el informe visual:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    archivos = seleccionar_archivos_json()
    if archivos:
        try:
            with open(archivos[0], "r", encoding="utf-8") as f:
                json_general = json.load(f)
            with open(archivos[1], "r", encoding="utf-8") as f:
                json_sintactico = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron leer los archivos JSON:\n{e}")
            exit(1)
        generar_informe_visual(json_general, json_sintactico, nombre_archivo="informe_visual.html")
