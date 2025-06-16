# Usa una imagen base de Python oficial con la versión 3.11 (basada en Debian Bullseye, una versión estable).
FROM python:3.11-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo en el contenedor
COPY requirements.txt .

# Actualiza pip a la última versión para asegurar que pueda resolver las dependencias.
RUN pip install --no-cache-dir --upgrade pip

# Instala las dependencias Python desde requirements.txt
# Importante: Este requirements.txt usa sqlmodel==0.0.24 y otras versiones compatibles.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código de la aplicación al directorio de trabajo en el contenedor
COPY . .

# Expone el puerto que tu aplicación Uvicorn usará (por defecto 8000)
EXPOSE 8000

# Comando para ejecutar la aplicación cuando el contenedor se inicie
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
