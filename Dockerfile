# Imagen base
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    xfonts-75dpi xfonts-base fontconfig wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Descargar e instalar wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && apt install -y ./wkhtmltox_0.12.6-1.buster_amd64.deb \
    && rm wkhtmltox_0.12.6-1.buster_amd64.deb

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto
EXPOSE 8000

# Ejecutar la app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
