Este repositorio ofrece una aproximación al código presentado en el Congreso de AELFA celebrado en Salamanca (2025).
Por razones académicas y de propiedad intelectual, no se incluye el programa completo, ya que forma parte de un proyecto de mayor envergadura.

No obstante, se proporciona un ejemplo funcional que permite comprender el enfoque general y replicar, de forma modular, algunos de los procesos y resultados obtenidos.

📌 El póster presentado durante el congreso será incorporado próximamente a este repositorio.

Para cualquier consulta, duda o propuesta de colaboración, puedes contactarme a través del siguiente enlace:
🔗 https://linktr.ee/Logololo

Estructura del repositorio

▪ Archivos HTML
Corresponden a los formularios utilizados para el registro y almacenamiento de datos, con excepción del informe visual..

▪ Archivos de transcripción
Incluyen tanto la lógica de transcripción de audios mediante el modelo Whisper como el análisis lingüístico posterior con spaCy.
Dado que algunos scripts pueden no ejecutarse correctamente en todos los entornos, se recomienda revisar y adaptar el código según sea necesario. Como apoyo, se ha incluido también el código base utilizado con Whisper.

▪ Generación de informes
A partir de los datos generados en formato .json por los scripts de transcripción, se sugiere utilizar el archivo crear_informe.py. Este script genera una salida estructurada que emula el informe visual.html original.
