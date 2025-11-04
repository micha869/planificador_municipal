# Imagen base oficial de Python
FROM python:3.11-slim

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias mínimas necesarias
RUN apt-get update && apt-get install -y \
    wget \
    fontconfig \
    libjpeg62-turbo \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar los archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la app Flask con Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
