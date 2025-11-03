# --- Imagen base ---
FROM python:3.11-slim-bullseye

# --- Directorio de trabajo ---
WORKDIR /app

# --- Instalar dependencias del sistema necesarias para wkhtmltopdf ---
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    xfonts-75dpi \
    xfonts-base \
    fontconfig \
    libjpeg62-turbo \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libssl1.1 \
    libxcb1 \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Descargar e instalar wkhtmltopdf oficial ---
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bullseye_amd64.deb \
    && apt install -y ./wkhtmltox_0.12.6-1.bullseye_amd64.deb \
    && rm wkhtmltox_0.12.6-1.bullseye_amd64.deb

# --- Copiar archivos del proyecto ---
COPY . .

# --- Instalar dependencias de Python ---
RUN pip install --no-cache-dir -r requirements.txt

# --- Exponer el puerto ---
EXPOSE 8000

# --- Comando para ejecutar la app ---
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
