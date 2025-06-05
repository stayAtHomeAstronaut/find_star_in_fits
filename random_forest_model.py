import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error


target_name = 'HAT-P-20'

target_name = 'HAT-P-3'

target_name = 'WASP-12'

target_name = 'KELT-3'
target_name = 'WASP-107'
target_name = 'HAT-P-61'
# Load your data (replace with your actual path if needed)
df = pd.read_csv("all_transits_averaged.csv")

# Convert datetime column
df['obs_date_time'] = pd.to_datetime(df['obs_date_time'])

# Filter for KELT-3 and sort by time
target_data = df[df['target_name'] == target_name ].sort_values('obs_date_time').reset_index(drop=True)

# Feature engineering
target_data['hour'] = target_data['obs_date_time'].dt.hour + target_data['obs_date_time'].dt.minute / 60.0
target_data['blue_over_red_lag1'] = target_data['blue_over_red'].shift(1)
target_data = target_data.dropna()

# Define features and target
X = target_data[['blue_over_red', 'blue_over_red_lag1', 'hour']]
y = target_data['rel_flux']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train_scaled, y_train)

# Predict
y_pred = rf.predict(X_test_scaled)

# Evaluate
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"RMSE: {mean_squared_error(y_test, y_pred):.5f}")
#print(f"RMSE: {mean_squared_error(y_test, y_pred, squared=False):.5f}")

# Plot actual vs predicted
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, color='blue', label='Predicted vs Actual')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', label='Ideal Fit')
plt.xlabel('Actual rel_flux')
plt.ylabel('Predicted rel_flux')
plt.title(target_name + ': Actual vs Predicted rel_flux')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

