# Usa Python 3.11 (estable y compatible)
FROM python:3.11-slim

# Crea un directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu proyecto
COPY . /app

# Instala dependencias del sistema necesarias para psycopg2 y reportlab
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto donde correrá Flask
EXPOSE 5000

# Comando para iniciar la app Flask con Gunicorn
CMD ["gunicorn", "app:app"]
