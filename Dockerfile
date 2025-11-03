# Imagen base
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar wkhtmltopdf y dependencias del sistema
RUN apt-get update && \
    apt-get install -y wkhtmltopdf && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
