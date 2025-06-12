import subprocess
import os

# Ruta al archivo de audio que deseas transcribir
audio_file = "/mnt/c/Users/sonia/Downloads/Esteban_lecturas_16k.wav"

# Verifica que el archivo de audio existe
if not os.path.exists(audio_file):
    raise FileNotFoundError(f"El archivo {audio_file} no existe. Verifica la ruta.")

# Ruta al binario de whisper-cli
whisper_cli = "/mnt/c/Users/sonia/whisper.cpp/build/bin/whisper-cli"

# Verifica que el binario existe y tiene permisos de ejecución
if not os.path.exists(whisper_cli):
    raise FileNotFoundError(f"El archivo {whisper_cli} no existe. Verifica la instalación.")
if not os.access(whisper_cli, os.X_OK):
    raise PermissionError(f"El archivo {whisper_cli} no tiene permisos de ejecución. Usa 'chmod +x {whisper_cli}'.")

# Ruta al modelo preentrenado
model_file = "/mnt/c/Users/sonia/whisper.cpp/models/ggml-medium.bin"

# Verifica que el modelo existe
if not os.path.exists(model_file):
    raise FileNotFoundError(f"El modelo {model_file} no existe. Verifica que lo hayas descargado correctamente.")

# Opciones avanzadas de configuración (corregidas)
options = [
    "--print-special",       # Muestra tokens especiales (pausas, repeticiones)
    "--max-context","0",          # Desactiva el uso de contexto previo
    "-tp", "0.0",            # Reduce la creatividad del modelo
    "-l", "es"               # Idioma del audio (español)
]

# Construir el comando completo
command = [whisper_cli, "-m", model_file, "-f", audio_file] + options

# Ejecutar el comando
try:
    print(f"Ejecutando comando: {' '.join(command)}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Mostrar la salida de la transcripción
    print("Transcripción:")
    print(result.stdout)

    # Verificar si hubo errores
    if result.stderr:
        print("\nErrores:")
        print(result.stderr)

except FileNotFoundError as e:
    print(f"Error de archivo: {e}")
except PermissionError as e:
    print(f"Error de permisos: {e}")
except Exception as e:
    print(f"Error al ejecutar Whisper: {e}")
