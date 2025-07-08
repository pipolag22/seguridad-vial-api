# Usa una imagen base de Python oficial con la versión 3.11-slim-bullseye
FROM python:3.11-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo en el contenedor
COPY requirements.txt .

# Actualiza pip a la última versión
RUN pip install --no-cache-dir --upgrade pip

# Instala git y otras herramientas de compilación necesarias para dependencias (útil para algunas dependencias transitivas)
# Limpia el cache de apt para reducir el tamaño final de la imagen.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Instala las dependencias Python desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código
COPY . .

# Expone el puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
