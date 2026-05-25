# Placeholder for DDoS detection model
# Replace this with your trained model file
# Model should be saved as a joblib pickle file (.pkl)

# Expected features for prediction:
# [pktrate, tot_kbps, pktcount, bytecount, tcp_flag, udp_flag, icmp_flag]

# Model should output probabilities for binary classification:
# [normal_probability, attack_probability]

# Example training code (for reference):
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load your dataset
df = pd.read_csv('dataset_sdn.csv')

# Prepare features
features = ['pktrate', 'tot_kbps', 'pktcount', 'bytecount']
X = df[features]

# Add protocol encoding
X = pd.get_dummies(X, columns=['protocol'], prefix='proto')

# Target
y = df['label']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'ddos_model.pkl')
"""
