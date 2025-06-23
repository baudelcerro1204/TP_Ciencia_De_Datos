# 🏨 Proyecto de Predicción y Clustering de Reservas Hoteleras

Este proyecto permite predecir la **probabilidad de cancelación** de reservas hoteleras y clasificarlas en **clusters de comportamiento**, brindando además una **interfaz web amigable** y un **notebook Jupyter** con todo el análisis de clustering.

---

## ⚙️ Tecnologías utilizadas

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Frontend**: React + Next.js
- **Base de datos**: PostgreSQL local
- **Machine Learning**: Scikit-learn, SHAP
- **Visualización y análisis**: Jupyter Notebook

---

## 🚀 Ejecución del sistema en local

### 1. Clonar el repositorio

```bash
git clone https://github.com/baudelcerro1204/TP_Ciencia_De_Datos
git clone https://github.com/baudelcerro1204/TP_Ciencia_De_Datos_Front
```

---

### 2. Configurar la base de datos PostgreSQL

Crear una base de datos local llamada `ciencia_de_datos` con los siguientes parámetros:

| Parámetro     | Valor                | 
|---------------|----------------------|
| Host          | localhost            |
| Puerto        | 5432                 | 
| Usuario       | postgres             |
| Contraseña    | root                 |
| Base de datos | ciencia_de_datos     |

Podés hacerlo desde terminal, PgAdmin o DBeaver:

```sql
CREATE DATABASE ciencia_de_datos;
```

---

### 3. Backend (FastAPI)

#### a. Instalar dependencias

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### b. Ejecutar el backend

```bash
uvicorn main:app --reload
```

- URL: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs

---

### 4. Frontend (React + Next.js)

#### a. Instalar dependencias

```bash
npm install
```

#### b. Ejecutar el frontend

```bash
npm run dev
```

- URL: http://localhost:3000

---

### 5. Jupyter Notebook

#### a. Instalar Jupyter

```bash
pip install notebook
```

#### b. Ejecutar el notebook


Abrí los 3 notebooks para ver el análisis exploratorio, entrenar el modelo de clasificación y el de clustering con KMeans y la elección del número de clusters (`k`).

---

## 🧪 Endpoints útiles

- `POST /create-booking` → Crea una nueva reserva
- `GET /evaluate-booking/{id}` → Evalúa la probabilidad de cancelación + cluster
- `GET /all-bookings` → Lista todas las reservas

Las respuestas incluyen:
- Predicción (`Alta/Baja` probabilidad de cancelación)
- Cluster al que pertenece
- Nombre interpretativo del cluster
- Explicación SHAP del modelo

---

## ✅ Cómo validar

1. Ingresar una reserva desde el frontend o vía Swagger.
2. Evaluarla con `/evaluate-booking/{id}`.
3. Verificar que devuelva:
   - Predicción correcta
   - Cluster correspondiente
   - Probabilidad histórica
   - Explicación SHAP con las 5 variables más importantes.

---

## 📚 Créditos

Desarrollado como parte del proyecto final de Ciencia de Datos, integrando múltiples componentes en un sistema funcional y explicable.
