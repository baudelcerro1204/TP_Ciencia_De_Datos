import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt

# 1. Carga y prepara datos
dataset = pd.read_csv("data/processed/spotify_full_dataset.csv")
cols = ['danceability','energy','valence','tempo']
df = dataset.dropna(subset=cols + ['popularity'])
X = df[cols]
y = df['popularity']

# 2. Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. Carga modelo y scaler
scaler = joblib.load("models/zscore_scaler.pkl")
model  = joblib.load("models/random_forest_popularity.pkl")

# 4. Escala y predice
X_test_scaled = scaler.transform(X_test)
y_pred = model.predict(X_test_scaled)

# 5. Calcula métricas
print("MAE: ", mean_absolute_error(y_test, y_pred))
print("MSE: ", mean_squared_error(y_test, y_pred))
print("R²:  ", r2_score(y_test, y_pred))

# 7. Gráfica actual vs predicho
plt.scatter(y_test, y_pred)
plt.plot([0,100],[0,100], "--")
plt.xlabel("Popularidad real")
plt.ylabel("Popularidad predicha")
plt.title("Actual vs Predicho")
plt.show()
