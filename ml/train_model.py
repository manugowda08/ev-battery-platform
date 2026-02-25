import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Generate synthetic training data
np.random.seed(42)
n_samples = 1000

data = {
    'capacity': np.random.normal(60, 15, n_samples),  # kWh
    'usage_years': np.random.exponential(3, n_samples),
    'grade': np.random.choice(['A', 'B', 'C'], n_samples, p=[0.3, 0.4, 0.3])
}

# Clean data
data['capacity'] = np.clip(data['capacity'], 20, 100)
data['usage_years'] = np.clip(data['usage_years'], 0, 10)

df = pd.DataFrame(data)

# Prepare features and target
X = df[['capacity', 'usage_years']]
le = LabelEncoder()
y = le.fit_transform(df['grade'])

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model and label encoder
with open('../app/ml_model.pkl', 'wb') as f:
    pickle.dump({
        'model': model,
        'label_encoder': le
    }, f)

print("Model trained and saved!")
print(f"Accuracy: {model.score(X_test, y_test):.2f}")
