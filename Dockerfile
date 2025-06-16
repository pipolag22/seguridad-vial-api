# Usa una imagen base de Python oficial con la versión 3.11 (basada en Debian Bullseye, una versión estable).
FROM python:3.11-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo en el contenedor
COPY requirements.txt .

# Actualiza pip a la última versión para asegurar que pueda resolver las dependencias.
RUN pip install --no-cache-dir --upgrade pip

# Instala git y otras herramientas de compilación necesarias para dependencias.
# Limpia el cache de apt para reducir el tamaño final de la imagen.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Instala las dependencias Python desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código de la aplicación al directorio de trabajo en el contenedor
COPY . .

# Expone el puerto que tu aplicación Uvicorn usará (por defecto 8000)
EXPOSE 8000

# Comando para ejecutar la aplicación cuando el contenedor se inicie
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]