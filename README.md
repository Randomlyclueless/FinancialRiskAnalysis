# 💰 Financial Risk Analysis & Banking Loan Prediction Platform

A comprehensive **financial risk analysis and loan prediction system** built using **Django** and **Flask**, designed to help users make informed financial decisions.  
This platform analyzes user financial data, predicts loan eligibility and risk, tracks savings and investments, and provides personalized financial advice.

---

## 🚀 Features

✅ **User Financial Data Analysis**
- Analyze income, expenses, savings, credit, and loans.
- Track multiple financial goals per user.

✅ **Interactive Visualizations**
- Savings and expense distribution charts.
- Track financial goal progress over time.

✅ **Loan Prediction Engine**
- Predicts loan approval and repayment risk.
- Calculates EMI and recommends ideal loan terms.

✅ **Personalized Financial Advice**
- Suggests saving and investment strategies.
- Provides tips to improve financial health.

✅ **Machine Learning Integration**
- Predicts loan eligibility using trained ML models.
- Utilizes Random Forest Classifier for accurate risk estimation.

---

## 🧠 Machine Learning Model Details

| Attribute | Description |
|------------|--------------|
| **Model Type** | Random Forest Classifier |
| **Purpose** | Predict repayment risk, eligibility, and loan term |
| **Training Data** | Processed financial dataset (`data4.csv`) |
| **Key Features** | Term, Interest Rate, Employment Length, Loan Amount, Income, Expenses, EMI, DTI, FICO Score, Revolving Utilization |
| **Metrics** | Accuracy, ROC-AUC, Confusion Matrix, Classification Report |
| **Serialization** | Model saved as a `.pkl` file for prediction reuse |

---

## 🗃 Dataset Information

The dataset represents **simulated financial records of Indian users**, containing:
- Salary, SIP investments, loan data, credit card bills.
- Financial goals (targets, deadlines, priority levels).
- Loan-related fields (interest rate, FICO score, DTI ratio, etc.).

**Database:** SQLite (`financialgoals.db`)  
**Generated Data:** Includes 2–4 goals per user with realistic financial patterns.

---

## 🛠️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Backend** | Django 5.2, Flask |
| **Database** | SQLite3 |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Machine Learning** | Scikit-learn, Pandas, NumPy |
| **Data Visualization** | Matplotlib, Seaborn |
| **Utilities** | FuzzyWuzzy, JSON, Pickle |

---

## ⚙️ Installation & Setup Guide

### 1️⃣ Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/financial-risk-analysis.git
cd financial-risk-analysis
