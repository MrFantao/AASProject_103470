FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY logistic_regression_model.pkl logistic_regression_model.pkl
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]