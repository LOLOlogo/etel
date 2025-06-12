import sys
import spacy
import whisper
import json
import warnings
from collections import Counter
import tkinter as tk
from tkinter import filedialog, Text, Toplevel, messagebox, Menu, Scrollbar, Frame, RIGHT, Y, BOTH
from tkinter.ttk import Button, Label, Style

# Suprime advertencias de algunos módulos (por ejemplo, de whisper)
warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")

# ---------------------------
# Configuración Global
# ---------------------------

# Flag para elegir el pipeline: False = modelo estándar, True = modelo Transformer
use_transformer = False

# Flag para la fragmentación del discurso:
#   - True: Fragmentación automática (se intenta separar por párrafos y, de no haber, se usa segmentación oracional)
#   - False: Fragmentación manual usando el delimitador "//"
fragmentacion_automatica = False

# Variable global para almacenar datos de análisis (útil para exportar a JSON)
datos = {}

# Función para cargar el pipeline según la selección actual
def cargar_pipeline():
    global nlp
    if use_transformer:
        try:
            # Modelo basado en transformers para español (requiere más recursos)
            nlp = spacy.load("es_dep_news_trf")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el modelo Transformer:\n{e}")
            # Si falla, se carga el modelo estándar
            nlp = spacy.load("es_core_news_lg")
    else:
        nlp = spacy.load("es_core_news_lg")

# Cargar el pipeline inicial (modelo estándar por defecto)
cargar_pipeline()

# ---------------------------
# Funciones de Audio y Transcripción
# ---------------------------

def seleccionar_audio():
    global label_archivo  # Para actualizar la etiqueta con el archivo seleccionado
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo de audio",
        filetypes=[("Archivos de audio", "*.wav *.mp3 *.m4a *.flac")]
    )
    if archivo:
        label_archivo.config(text=f"Archivo seleccionado: {archivo}")
        transcribir_audio(archivo)

def transcribir_audio(ruta_audio):
    # Carga el modelo Whisper y transcribe el audio
    model = whisper.load_model("medium")
    result = model.transcribe(
        ruta_audio,
        language="es",  # Idioma español
        task="transcribe",
        temperature=0.0,
        no_speech_threshold=0.1,
        logprob_threshold=-1.0,
        condition_on_previous_text=False,
        fp16=False
    )
    # Muestra la transcripción en el cuadro de texto
    texto_transcripcion.delete(1.0, tk.END)
    texto_transcripcion.insert(tk.END, result["text"])

# ---------------------------
# Análisis Léxico y Estadísticas Básicas
# ---------------------------
def analizar_texto():
    """
    Realiza un análisis léxico y morfosintáctico básico (sin el desglose sintáctico detallado por fragmento)
    y muestra estadísticas globales del texto.
    """
    global datos
    texto = texto_transcripcion.get(1.0, tk.END).strip()
    if not texto:
        messagebox.showerror("Error", "No hay texto transcrito para analizar.")
        return

    doc = nlp(texto)

    # Clasificación por categorías: sustantivos, verbos, adjetivos, adverbios, pronombres, determinantes, adposiciones, conjunciones
    categorias = {
        "sustantivos": [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]],
        "verbos": [token.text.lower() for token in doc if token.pos_ in ["VERB", "AUX"]],
        "adjetivos": [token.text.lower() for token in doc if token.pos_ == "ADJ"],
        "adverbios": [token.text.lower() for token in doc if token.pos_ == "ADV"],
        "pronombres": [token.text.lower() for token in doc if token.pos_ == "PRON"],
        "determinantes": [token.text.lower() for token in doc if token.pos_ == "DET"],
        "adposiciones": [token.text.lower() for token in doc if token.pos_ == "ADP"],
        "conjunciones": [token.text.lower() for token in doc if token.pos_ in ["CCONJ", "SCONJ"]]
    }
    estadisticas = {cat: Counter(lista) for cat, lista in categorias.items()}

    # Cálculo de métricas globales
    palabras = [token.text for token in doc if token.is_alpha]
    total_palabras = len(palabras)
    palabras_unicas = len(set(palabras))
    type_token_ratio = palabras_unicas / total_palabras if total_palabras > 0 else 0

    oraciones = list(doc.sents)
    tamanos_oracion = [len([token for token in sent if token.is_alpha]) for sent in oraciones]
    promedio_oracion = sum(tamanos_oracion) / len(tamanos_oracion) if oraciones else 0
    longitudes_palabras = [len(token) for token in palabras]
    promedio_palabra = sum(longitudes_palabras) / len(longitudes_palabras) if palabras else 0

    # Mostrar resultados en una ventana
    ventana_analisis = Toplevel(ventana)
    ventana_analisis.title("Análisis Avanzado del Texto")
    ventana_analisis.geometry("900x700")
    ventana_analisis.configure(bg="#f5f5f5")

    texto_resultados = Text(ventana_analisis, wrap="word", font=("Arial", 11),
                            bg="#ffffff", fg="#333333", padx=10, pady=10)
    texto_resultados.pack(fill="both", expand=True, padx=20, pady=20)

    texto_resultados.insert(tk.END, "Resumen Global:\n")
    texto_resultados.insert(tk.END, f"  - Total de palabras: {total_palabras}\n")
    texto_resultados.insert(tk.END, f"  - Palabras únicas: {palabras_unicas}\n")
    texto_resultados.insert(tk.END, f"  - Ratio Tipo-Token: {type_token_ratio:.3f}\n")
    texto_resultados.insert(tk.END, f"  - Promedio de palabras por oración: {promedio_oracion:.2f}\n")
    texto_resultados.insert(tk.END, f"  - Longitud media de palabra: {promedio_palabra:.2f}\n\n")

    texto_resultados.insert(tk.END, "Estadísticas por Categoría Gramatical:\n")
    for categoria, conteo in estadisticas.items():
        total_cat = sum(conteo.values())
        texto_resultados.insert(tk.END, f"  - {categoria.capitalize()} (total: {total_cat}):\n")
        for palabra, count in conteo.items():
            texto_resultados.insert(tk.END, f"      {palabra}: {count}  ")
        texto_resultados.insert(tk.END, "\n")
    texto_resultados.insert(tk.END, "\n")

    # Almacenamos los datos para exportar
    datos = {
        "resumen": {
            "total_palabras": total_palabras,
            "palabras_unicas": palabras_unicas,
            "ratio_tipo_token": type_token_ratio,
            "promedio_palabras_oracion": promedio_oracion,
            "longitud_media_palabra": promedio_palabra
        },
        "categorias": {cat: dict(conteo) for cat, conteo in estadisticas.items()}
    }

    Button(ventana_analisis, text="Guardar Análisis como JSON",
           command=lambda: guardar_datos_json(datos)).pack(pady=10)
    texto_resultados.configure(state="disabled")

# ---------------------------
# Análisis Sintáctico/Morfosintáctico con Fragmentación
# ---------------------------
def analizar_fragmentacion_sintactica():
    """
    Segmenta el texto en fragmentos y, para cada fragmento, realiza un análisis sintáctico/morfosintáctico.
    La segmentación se realiza de forma:
       - Automática: si 'fragmentacion_automatica' es True, se intenta separar por párrafos (doble salto de línea)
         y, en su defecto, se utiliza la segmentación oracional de spaCy.
       - Manual: si es False, se asume que el usuario utiliza el delimitador "//".
    En cada fragmento se obtiene el análisis detallado (para cada oración, se listan las palabras con sus categorías,
    función sintáctica, lema, etiqueta, palabra cabeza y morfología).
    """
    texto = texto_transcripcion.get(1.0, tk.END).strip()
    if not texto:
        messagebox.showerror("Error", "No hay texto para analizar.")
        return

    # Determinar fragmentos según el modo seleccionado
    if fragmentacion_automatica:
        # Si existen varios párrafos (separados por doble salto de línea), usarlos; de lo contrario, usar segmentación oracional.
        paragraphs = [p.strip() for p in texto.split("\n\n") if p.strip()]
        if len(paragraphs) > 1:
            fragments = paragraphs
        else:
            doc = nlp(texto)
            fragments = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    else:
        if "//" in texto:
            fragments = [frag.strip() for frag in texto.split("//") if frag.strip()]
        else:
            fragments = [texto.strip()]

    analysis_result = []
    # Para cada fragmento se realiza la segmentación en oraciones y se analiza cada token.
    for frag in fragments:
        frag_doc = nlp(frag)
        fragment_analysis = {
            "fragmento": frag,
            "oraciones": []
        }
        for sent in frag_doc.sents:
            sent_analysis = {
                "oracion": sent.text,
                "tokens": []
            }
            for token in sent:
                token_info = {
                    "texto": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "tag": token.tag_,
                    "dep": token.dep_,
                    "head": token.head.text,
                    "morph": token.morph.to_dict()
                }
                sent_analysis["tokens"].append(token_info)
            fragment_analysis["oraciones"].append(sent_analysis)
        analysis_result.append(fragment_analysis)

    # Mostrar el análisis en una nueva ventana
    ventana_sintaxis = Toplevel(ventana)
    ventana_sintaxis.title("Análisis Sintáctico y Morfosintáctico Fragmentado")
    ventana_sintaxis.geometry("900x700")
    ventana_sintaxis.configure(bg="#f5f5f5")

    texto_resultados = Text(ventana_sintaxis, wrap="word", font=("Arial", 11),
                              bg="#ffffff", fg="#333333", padx=10, pady=10)
    texto_resultados.pack(fill="both", expand=True, padx=20, pady=20)

    # Escribir el análisis en el widget de texto
    for frag_analysis in analysis_result:
        texto_resultados.insert(tk.END, "Fragmento:\n")
        texto_resultados.insert(tk.END, frag_analysis["fragmento"] + "\n")
        for sent_analysis in frag_analysis["oraciones"]:
            texto_resultados.insert(tk.END, "  Oración: " + sent_analysis["oracion"] + "\n")
            for token_info in sent_analysis["tokens"]:
                line = "    - {} (Lemma: {}, POS: {}, Tag: {}, Dep: {}, Head: {}, Morph: {})\n".format(
                    token_info["texto"],
                    token_info["lemma"],
                    token_info["pos"],
                    token_info["tag"],
                    token_info["dep"],
                    token_info["head"],
                    token_info["morph"]
                )
                texto_resultados.insert(tk.END, line)
            texto_resultados.insert(tk.END, "\n")
        texto_resultados.insert(tk.END, "\n")

    Button(ventana_sintaxis, text="Guardar Análisis Sintáctico como JSON",
           command=lambda: guardar_datos_json(analysis_result)).pack(pady=10)
    texto_resultados.configure(state="disabled")

# ---------------------------
# Función para Guardar Datos en JSON
# ---------------------------
def guardar_datos_json(datos):
    if not datos:
        messagebox.showerror("Error", "No hay datos para guardar.")
        return

    archivo = filedialog.asksaveasfilename(
        title="Guardar como",
        defaultextension=".json",
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )
    if archivo:
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", f"Datos guardados exitosamente en:\n{archivo}")
        except IOError as io_error:
            messagebox.showerror("Error de Escritura", f"No se pudo guardar el archivo:\n{io_error}")
        except Exception as e:
            messagebox.showerror("Error Desconocido", f"Ocurrió un error inesperado:\n{e}")

# ---------------------------
# Funciones para Alternar Opciones
# ---------------------------
def cambiar_pipeline():
    global use_transformer
    use_transformer = not use_transformer
    cargar_pipeline()
    modelo = "Transformer (es_dep_news_trf)" if use_transformer else "Estándar (es_core_news_lg)"
    messagebox.showinfo("Pipeline", f"Se ha cambiado al pipeline: {modelo}")

def toggle_fragmentacion():
    global fragmentacion_automatica
    fragmentacion_automatica = not fragmentacion_automatica
    estado = "Automática" if fragmentacion_automatica else "Manual (//)"
    messagebox.showinfo("Fragmentación del Discurso", f"La segmentación se ha configurado a: {estado}")

# ---------------------------
# Configuración de la Interfaz Gráfica (Tkinter)
# ---------------------------
ventana = tk.Tk()
ventana.title("Transcriptor y Analizador de Audio")
ventana.geometry("100x100")
ventana.minsize(600, 60)
ventana.configure(bg="#f5f5f5")

style = Style()
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 10), background="#f5f5f5", foreground="#333333")
label_archivo = Label(ventana, text="No se ha seleccionado ningún archivo", background="#f5f5f5", font=("Arial", 12))
label_archivo.pack(pady=10)

# Barra de menú
menubar = Menu(ventana)
ventana.option_add("*Font", "Arial 10")

# Menú Archivo
menu_archivo = Menu(menubar, tearoff=0)
menu_archivo.add_command(label="Seleccionar Audio", command=seleccionar_audio)
menu_archivo.add_command(label="Transcribir Audio", command=lambda: transcribir_audio(filedialog.askopenfilename()))
menu_archivo.add_separator()
menu_archivo.add_command(label="Salir", command=ventana.quit)
menubar.add_cascade(label="Archivo", menu=menu_archivo)

# Menú Análisis
menu_analisis = Menu(menubar, tearoff=0)
menu_analisis.add_command(label="Analizar Texto Avanzado", command=analizar_texto)
menu_analisis.add_command(label="Analizar Fragmentación Sintáctica", command=analizar_fragmentacion_sintactica)
menu_analisis.add_command(label="Guardar Data .json", command=lambda: guardar_datos_json(datos) if datos else messagebox.showerror("Error", "No hay datos para guardar."))
menubar.add_cascade(label="Análisis", menu=menu_analisis)

# Menú Opciones
menu_opciones = Menu(menubar, tearoff=0)
menu_opciones.add_command(label="Cambiar Pipeline (Transformer/Estándar)", command=cambiar_pipeline)
menu_opciones.add_command(label="Alternar Fragmentación (Automática/Manual)", command=toggle_fragmentacion)
menubar.add_cascade(label="Opciones", menu=menu_opciones)

ventana.config(menu=menubar)

# Frame para el cuadro de texto de transcripción
frame_transcripcion = Frame(ventana, bg="#ffffff", bd=2, relief="ridge")
frame_transcripcion.pack(pady=10, padx=20, fill="x")

scrollbar_transcripcion = Scrollbar(frame_transcripcion)
scrollbar_transcripcion.pack(side=RIGHT, fill=Y)

texto_transcripcion = Text(
    frame_transcripcion,
    wrap="word",
    font=("Arial", 12),
    bg="#ffffff",
    fg="#333333",
    height=6,
    width=60,
    padx=10,
    pady=10,
    bd=0,
    highlightthickness=0,
    yscrollcommand=scrollbar_transcripcion.set
)
texto_transcripcion.pack(side="left", fill="x")
scrollbar_transcripcion.config(command=texto_transcripcion.yview)

datos = {}

ventana.mainloop()
