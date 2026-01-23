from ucimlrepo import fetch_ucirepo
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import linear_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import json
import os
import joblib

# fetch dataset
print("Loading dataset")
wine_quality = fetch_ucirepo(id=186)

# data (as pandas dataframes)
X = wine_quality.data.features
y = wine_quality.data.targets

# # metadata
# print(wine_quality.metadata)

print("Preprocessing Dataset")
# variable information
print(wine_quality.variables)


# X_t = X.copy()
# X_t['quantity'] = y
# corr_matrix = X_t.corr()
# corr_with_target = corr_matrix['quantity'].sort_values(ascending=False)

# X_t = X_t.drop(columns=['density','chlorides','fixed_acidity'])
# y_t = X_t['quantity']
# X_t = X_t.drop(columns=['quantity'])

X = X.drop(columns=['density','fixed_acidity'])

print("Splitting train test data")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# 02 X_train, X_test, y_train, y_test = train_test_split(X_t, y_t, test_size=0.2, random_state=42)

# scaler = StandardScaler()
# scaler.fit(X_train)

# X_train_scaled = scaler.transform(X_train)
# X_test_scaled = scaler.transform(X_test)

# print("Training Linear Regression Model")

# model = LinearRegression()
# model.fit(X_train, y_train)

print("Training Linear Regression Model Lasso alpha 0.1")
model = RandomForestRegressor(n_estimators=100,max_depth=15, random_state=0)
model.fit(X_train,y_train)

model_filename = 'output/model-linear-exp1.pkl'
os.makedirs(os.path.dirname(model_filename), exist_ok=True)
joblib.dump(model, model_filename)
print(f"Model saved to {model_filename}")

r2_score_value = model.score(X_test, y_test)
print(f"R^2 Score: {r2_score_value:.2f}")


y_pred = model.predict(X_test)

mse_value = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error (MSE): {mse_value:.2f}")

print("Saving as a JSON output")

data = {
    "Experiment ID": "Exp-02",
    "Model Type": "Linear Regression - Lasso",
    "Hyperparameters": "Regularization",
    "Preprocessing-Steps": "Standardization",
    "Feature-Selection-Method": "correlation-based",
    "Train/Test-Split" : "80-20" ,
    "MSE" : mse_value,
    "accuracy" : r2_score_value
}

filename = 'output/metrics.json'

if os.path.exists(filename):
    with open(filename, 'r') as json_file:
        existing_data = json.load(json_file)
    
    if isinstance(existing_data, list):
        existing_data.append(data)
    else:
        existing_data = [existing_data, data]
    
    with open(filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)
else:
    with open(filename, 'w') as json_file:
        json.dump([data], json_file, indent=4)

print(f"Data successfully saved to {filename}")
