import sys
import spacy

#para ejecutar este codigo es necesario usar anaconda 
# colocr esto en anaconda pront > conda activate base 
# asegurar las rutas
# usar comando "python y ruta completa"

# Verifica el entorno actual
print("Ruta de Python:", sys.executable)
print("Versiones de módulos instalados:")
print("SpaCy:", spacy.__version__)


import whisper
import spacy
from tkinter import Tk, filedialog, Text, Button, Label, Scrollbar, END, Frame, RIGHT, Y
from collections import Counter
from tkinter import Tk, Text, Frame, Scrollbar, Y, RIGHT, BOTH, Toplevel, Menu
from tkinter.ttk import Button, Label, Style
import json
from tkinter import filedialog

# Carga el modelo de SpaCy para español
nlp = spacy.load("es_core_news_lg")

# Función para seleccionar archivo de audio
def seleccionar_audio():
    global label_archivo  # Asegúrate de que label_archivo sea global
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo de audio",
        filetypes=[("Archivos de audio", "*.wav *.mp3 *.m4a *.flac")]
    )
    if archivo:
        label_archivo.config(text=f"Archivo seleccionado: {archivo}")
        transcribir_audio(archivo)

# Luego, en el bloque principal de la GUI:

# Función para transcribir el audio seleccionado
def transcribir_audio(ruta_audio):
    # Carga el modelo Whisper
    model = whisper.load_model("large-v3")
    
    # Transcripción del archivo con configuraciones personalizadas
    result = model.transcribe(
        ruta_audio,
        language="es",  # Idioma español
        task="transcribe",  # Solo transcribir, no traducir
        temperature=0.0,  # Reduce la "creatividad" del modelo
        no_speech_threshold=0.1,  # Detecta silencios como parte del texto
        logprob_threshold=-1.0,  # Mantén palabras con baja probabilidad
        condition_on_previous_text=False,  # No condicionar la predicción en texto previo
        fp16=False  # Usa precisión de 32 bits para mayor estabilidad
    )

    # Muestra el texto transcrito en el cuadro de texto
    texto_transcripcion.delete(1.0, END)  # Limpia el cuadro de texto
    texto_transcripcion.insert(END, result["text"])  # Inserta el texto transcrito

datos = {}
# Función para analizar sintácticamente el texto transcrito
def analizar_texto():
    global datos  # Usar la variable global para compartir datos con otras funciones

    # Obtén el texto del cuadro de transcripción
    texto = texto_transcripcion.get(1.0, END).strip()

    if not texto:
        # Muestra un mensaje si no hay texto para analizar
        from tkinter import messagebox
        messagebox.showerror("Error", "No hay texto transcrito para analizar.")
        return

    # Procesa el texto con SpaCy
    doc = nlp(texto)

    # Análisis directo con contadores
    verbos_auxiliares = Counter(token.text.lower() for token in doc if token.pos_ == "AUX")
    sustantivos_comunes = Counter(token.text.lower() for token in doc if token.pos_ == "NOUN")
    sustantivos_propios = Counter(token.text for token in doc if token.pos_ == "PROPN")
    verbos = Counter(token.text.lower() for token in doc if token.pos_ == "VERB")
    adjetivos = Counter(token.text.lower() for token in doc if token.pos_ == "ADJ")
    palabras = [token.text.lower() for token in doc if token.is_alpha]

    # Cálculos globales de palabras
    total_palabras = len(palabras)
    palabras_unicas = len(set(palabras))

    # Crear una nueva ventana para mostrar el análisis
    ventana_analisis = Toplevel(ventana)
    ventana_analisis.title("Resultados del Análisis")
    ventana_analisis.geometry("800x600")
    ventana_analisis.configure(bg="#f5f5f5")

    # Añadir un cuadro de texto para los resultados
    texto_resultados = Text(ventana_analisis, wrap="word", font=("Arial", 12), bg="#ffffff", fg="#333333", padx=10, pady=10)
    texto_resultados.pack(fill="both", expand=True, padx=20, pady=20)

    # Mostrar resultados en la nueva ventana
    texto_resultados.insert(END, "Resumen del texto:\n")
    texto_resultados.insert(END, f"  Número total de palabras: {total_palabras}\n")
    texto_resultados.insert(END, f"  Número total de palabras diferentes: {palabras_unicas}\n\n")

    texto_resultados.insert(END, "Análisis detallado:\n\n")

    # Mostrar los datos analizados
    texto_resultados.insert(END, f"Total de verbos auxiliares: {sum(verbos_auxiliares.values())}\n")
    for aux, count in verbos_auxiliares.items():
        texto_resultados.insert(END, f"  {aux}: {count} veces\n")
    texto_resultados.insert(END, "\n")

    texto_resultados.insert(END, f"Total de sustantivos comunes: {sum(sustantivos_comunes.values())}\n")
    for noun, count in sustantivos_comunes.items():
        texto_resultados.insert(END, f"  {noun}: {count} veces\n")
    texto_resultados.insert(END, "\n")

    texto_resultados.insert(END, f"Total de sustantivos propios: {sum(sustantivos_propios.values())}\n")
    for propn, count in sustantivos_propios.items():
        texto_resultados.insert(END, f"  {propn}: {count} veces\n")
    texto_resultados.insert(END, "\n")

    texto_resultados.insert(END, f"Total de verbos: {sum(verbos.values())}\n")
    for verb, count in verbos.items():
        texto_resultados.insert(END, f"  {verb}: {count} veces\n")
    texto_resultados.insert(END, "\n")

    texto_resultados.insert(END, f"Total de adjetivos: {sum(adjetivos.values())}\n")
    for adj, count in adjetivos.items():
        texto_resultados.insert(END, f"  {adj}: {count} veces\n")
    texto_resultados.insert(END, "\n")

    # Actualiza los datos globales
    datos = {
        "total_palabras": total_palabras,
        "palabras_unicas": palabras_unicas,
        "verbos_auxiliares": dict(verbos_auxiliares),
        "sustantivos_comunes": dict(sustantivos_comunes),
        "sustantivos_propios": dict(sustantivos_propios),
        "verbos": dict(verbos),
        "adjetivos": dict(adjetivos),
        "texto_transcrito": texto
    }

    # Añadir botón para guardar los datos desde la ventana de análisis
    Button(ventana_analisis, text="Guardar como JSON", command=lambda: guardar_datos_json(datos)).pack(pady=10)

    # Hacer el cuadro de texto solo de lectura
    texto_resultados.configure(state="disabled")

def guardar_datos_json(datos):
    """
    Guarda los datos proporcionados en un archivo JSON.
    
    :param datos: Diccionario con los datos analizados, incluyendo el texto transcrito.
    """
    if not datos:
        # Si el diccionario está vacío, muestra un mensaje de error
        from tkinter import messagebox
        messagebox.showerror("Error", "No hay datos para guardar.")
        return

    # Abre un cuadro de diálogo para seleccionar la ubicación y el nombre del archivo
    archivo = filedialog.asksaveasfilename(
        title="Guardar como",
        defaultextension=".json",
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )

    if archivo:  # Si el usuario seleccionó un archivo
        try:
            # Guarda el diccionario completo en un archivo JSON
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)  # Guarda en formato JSON
            
            # Muestra un mensaje de éxito
            from tkinter import messagebox
            messagebox.showinfo("Éxito", f"Datos guardados exitosamente en:\n{archivo}")
        except IOError as io_error:
            # Error relacionado con el archivo
            messagebox.showerror("Error de Escritura", f"No se pudo guardar el archivo:\n{io_error}")
        except Exception as e:
            # Otros errores
            messagebox.showerror("Error Desconocido", f"Ocurrió un error inesperado:\n{e}")


from tkinter import Tk, Text, Frame, Scrollbar, Y, RIGHT, BOTH
from tkinter.ttk import Button, Label, Style
# Configuración de la ventana principal
ventana = Tk()
ventana.title("Transcriptor y Analizador de Audio")
ventana.geometry("100x100")  # Tamaño inicial adecuado
ventana.minsize(600, 60)  # Tamaño mínimo permitido
ventana.configure(bg="#f5f5f5")  # Fondo gris claro

# Configuración de estilo
style = Style()
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 10), background="#f5f5f5", foreground="#333333")  # Reducir la fuente

# Crear la barra de menú
menubar = Menu(ventana)
# Cambiar la fuente del menú desplegable
ventana.option_add("*Font", "Arial 10")  # Cambia la fuente de todos los elementos

# Menú Archivo
menu_archivo = Menu(menubar, tearoff=0)
menu_archivo.add_command(label="Seleccionar Audio", command=seleccionar_audio)
menu_archivo.add_command(label="Transcribir Audio", command=transcribir_audio)
menu_archivo.add_separator()
menu_archivo.add_command(label="Salir", command=ventana.quit)
menubar.add_cascade(label="Archivo", menu=menu_archivo)

# Menú Análisis
menu_analisis = Menu(menubar, tearoff=0)
menu_analisis.add_command(label="Analizar Texto", command=analizar_texto)
menu_analisis.add_command(label="Guardar Data .json", command=lambda: guardar_datos_json(datos))  # Botón de guardar
menubar.add_cascade(label="Análisis", menu=menu_analisis)

# Configurar la barra de menú en la ventana principal
ventana.config(menu=menubar)

# Frame para el cuadro de texto de transcripción
frame_transcripcion = Frame(ventana, bg="#ffffff", bd=2, relief="ridge")
frame_transcripcion.pack(pady=10, padx=20, fill="x")  # Ajuste del espaciado

# Scrollbar para el cuadro de transcripción
scrollbar_transcripcion = Scrollbar(frame_transcripcion)
scrollbar_transcripcion.pack(side=RIGHT, fill=Y)

# Cuadro de texto para mostrar la transcripción (ajustado)
texto_transcripcion = Text(
    frame_transcripcion,
    wrap="word",  # Ajusta las palabras automáticamente en el texto
    font=("Arial", 12),
    bg="#ffffff",
    fg="#333333",
    height=6,  # Ajusta la altura a 6 líneas
    width=60,   # Ajusta el ancho a 60 caracteres
    padx=10,
    pady=10,
    bd=0,
    highlightthickness=0,
    yscrollcommand=scrollbar_transcripcion.set
)
texto_transcripcion.pack(side="left", fill="x")  # El cuadro se ajusta horizontalmente
scrollbar_transcripcion.config(command=texto_transcripcion.yview)

# Inicializa el diccionario global para los datos
datos = {}

# Inicia la ventana
ventana.mainloop()
