FROM python:3.9-slim

WORKDIR /app

COPY product-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY product-service/app ./app
COPY shared ./shared

ENV FLASK_APP=app
ENV FLASK_ENV=development

EXPOSE 5001

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]