FROM python:3.11-slim

WORKDIR /app
   
COPY . /app


COPY ./training-artifacts-py3.11/model-linear-exp1.pkl /app/training-artifacts-py3.11/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002

CMD ["uvicorn", "Script.app:app", "--host", "0.0.0.0", "--port", "8002"]
