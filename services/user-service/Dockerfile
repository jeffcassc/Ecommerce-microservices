FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Especifica explícitamente el módulo y la aplicación
ENV FLASK_APP=app.__init__
ENV FLASK_ENV=development

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]