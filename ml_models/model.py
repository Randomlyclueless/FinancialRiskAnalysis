import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score

# Load data
try:
    df = pd.read_csv('dataset/data4.csv', encoding='latin1')
except FileNotFoundError:
    print("Error: 'data4.csv' not found in D:\\Python projects\\RiskAnalysis")
    exit(1)

# Data Cleaning
df = df.drop(['Unnamed: 0', 'id', 'member_id', 'next_pymnt_d'], axis=1, errors='ignore')
df['term'] = df['term'].str.extract('(\d+)').astype(float)
df['emp_length'] = df['emp_length'].str.extract('(\d+)').astype(float)
df['emp_length'] = df['emp_length'].fillna(10)

if df['int_rate'].dtype == 'object':
    df['int_rate'] = df['int_rate'].str.replace('%', '').astype(float)
else:
    if df['int_rate'].max() < 1:
        df['int_rate'] = df['int_rate'] * 100

date_cols = ['last_pymnt_d', 'last_credit_pull_d']
for col in date_cols:
    if col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], format='%b-%y', errors='coerce')
            df[f'{col}_year'] = df[col].dt.year
            df[f'{col}_month'] = df[col].dt.month
        except:
            df = df.drop(col, axis=1)

df = df.dropna(subset=['repay_fail'])

# Feature Engineering
if all(col in df.columns for col in ['total_pymnt', 'funded_amnt']):
    df['payment_ratio'] = df['total_pymnt'] / df['funded_amnt']
    df['payment_ratio'] = df['payment_ratio'].replace([np.inf, -np.inf], np.nan)

if 'issue_d' in df.columns:
    try:
        df['issue_d'] = pd.to_datetime(df['issue_d'], format='%b-%y')
        df['loan_age'] = (pd.to_datetime('today') - df['issue_d']).dt.days
    except:
        pass

# Model Preparation
X = df.drop('repay_fail', axis=1)
y = df['repay_fail']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

numeric_features = X.select_dtypes(include=['float64', 'int64']).columns.tolist()
categorical_features = X.select_dtypes(include=['object']).columns.tolist()

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Model Training
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    ))
])

model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("ROC AUC:", roc_auc_score(y_test, y_proba))

# Save model
model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f, protocol=4)
print(f"\nModel saved successfully at: {model_path}")