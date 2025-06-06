import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error


target_name = 'HAT-P-20'

df = pd.read_csv("all_transits_averaged.csv")

df['obs_date_time'] = pd.to_datetime(df['obs_date_time'])

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
xgb_model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
xgb_model.fit(X_train_scaled, y_train)

# Predict
y_pred = xgb_model.predict(X_test_scaled)

# Evaluate
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"RMSE: {mean_squared_error(y_test, y_pred):.5f}")

# Plot actual vs predicted
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, color='blue', label='Predicted vs Actual')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', label='Ideal Fit')
plt.xlabel('Actual rel_flux')
plt.ylabel('Predicted rel_flux')
plt.title(target_name + ': Actual vs Predicted rel_flux (XGBRegressor)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
