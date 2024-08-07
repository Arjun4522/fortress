

# Step 2: Import libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
import joblib
#from google.colab import files

# Step 3: Upload the dataset
data_path = 'dataset_sdn.csv'

# Step 4: Load and preprocess the dataset
data = pd.read_csv(data_path)
data = data.dropna()

# Print size and features of dataset
print("Shape of dataset:", data.shape)
print("Columns: ", data.columns)

# Select features and target
X = data[['pktcount', 'bytecount', 'dur', 'dur_nsec', 'tot_dur', 'flows', 'packetins',
          'pktperflow', 'byteperflow', 'pktrate', 'Pairflow', 'Protocol', 'port_no',
          'tx_bytes', 'rx_bytes', 'tx_kbps', 'rx_kbps', 'tot_kbps']]
y = data['label']
X_encoded = pd.get_dummies(X, columns=['Protocol'])

# Split data for testing and training
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Perform ANOVA feature selection
k_best = SelectKBest(score_func=f_classif, k=4)
X_train_best = k_best.fit_transform(X_train, y_train)
X_test_best = k_best.transform(X_test)

# Get the selected feature names
selected_feature_names = X_encoded.columns[k_best.get_support()]

print(k_best)
print(X_train_best)
print(X_test_best)
print(selected_feature_names)

# Train Random Forest Classifier with selected features
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train_best, y_train)

# Save the model and the selected features
joblib.dump(clf, 'model.joblib')
joblib.dump(selected_feature_names, 'selected_features.joblib')

print("Model and feature names saved successfully.")
