from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

model = joblib.load("./training-artifacts-py3.11/model-linear-exp1.pkl")

app = FastAPI(
    title="Wine Quality Prediction API",
    description="FastAPI-based inference service for predicting wine quality",
    version="1.0.0"
)

class WineFeatures(BaseModel):
    # fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    # density: float
    pH: float
    sulphates: float
    alcohol: float


@app.post("/predict")
def predict_wine_quality(features: WineFeatures):
    input_data = np.array([[
        # features.fixed_acidity,
        features.volatile_acidity,
        features.citric_acid,
        features.residual_sugar,
        features.chlorides,
        features.free_sulfur_dioxide,
        features.total_sulfur_dioxide,
        # features.density,
        features.pH,
        features.sulphates,
        features.alcohol
    ]])

    prediction = model.predict(input_data)[0]

    return {
        "name": "Ashiq Firoz",
        "roll_no": "2022BCD0013",
        "wine_quality": int(prediction)
    }

@app.get("/")
def root():
    return {"message": "Wine Quality Prediction API is running"}
