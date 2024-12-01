# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala Git y otras dependencias necesarias
RUN apt-get update && apt-get install -y git && apt-get clean

# Copia los archivos del repositorio al contenedor
COPY . /app

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar la aplicación
CMD ["python3", "bot.py"]

