
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Exponer puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar
CMD ["streamlit", "run", "app/Home.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]