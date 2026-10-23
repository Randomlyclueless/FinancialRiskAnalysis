
# 💰 Financial Risk Analysis & Banking Loan Prediction Platform

A Django-based financial dashboard for loan repayment-risk prediction, EMI calculation, and investment tracking. The application uses a saved scikit-learn model for prediction and SQLite by default, with database URL configuration available for deployment environments.

## 🚀 Features

- **User Authentication:** Sign up and log in using Django authentication.
- **Loan Risk Prediction:** Submit loan and financial details to receive a model prediction about repayment risk.
- **Rule-Based Eligibility Estimate:** Calculate the debt-to-income (DTI) ratio and compare it with the application's 50% threshold.
- **Loan-Term Handling:** Return the loan term supplied by the user.
- **EMI Calculator:** Calculate estimated monthly instalments and total interest.
- **Savings and Investment Tracker:** Add investments, view user-specific investment records, and calculate totals and percentages against the profile salary.
- **Prediction API:** Accept POST requests using JSON or form data and return a JSON prediction response.

> **Note:** This is an educational project, not a lender's underwriting system. A model prediction is not an actual loan approval or a guarantee of repayment.

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Backend / Web Framework | Python, Django 5.2 |
| Database | SQLite by default; database URL configuration is supported |
| Authentication | Django authentication and session middleware |
| Data Handling | Pandas |
| Machine Learning | scikit-learn |
| Frontend | Django templates, HTML, CSS, JavaScript |
| Static File Serving | WhiteNoise |
| Deployment Server | Gunicorn |

## 📁 Project Structure

```text
FinancialRiskAnalysis/
├── authapp/
│   ├── forms.py             # Loan and investment forms
│   ├── models.py            # LoanApplication, Investment, Profile
│   ├── urls.py              # Application routes
│   └── views.py             # Authentication, loan, EMI, savings views
├── bankrisk/
│   ├── settings.py          # Django settings and database configuration
│   └── urls.py              # Root URL configuration
├── ml_models/
│   └── predictor.py         # Loads and calls the saved prediction model
├── manage.py
├── requirements.txt
└── README.md
```

The prediction code expects the saved model at `ml_models/model_application.pkl`. Ensure that this artifact is available before starting the application.

## 🧠 How the Application Works

### 1. Loan Risk Prediction

1. The user submits loan amount, income, expenses, EMI, interest rate, loan term, and employment length.
2. Django validates the form and prepares the input values.
3. `ml_models/predictor.py` maps the submitted fields to the feature names expected by the model.
4. The saved model returns a class prediction and estimated failure probability.
5. The Django view saves the loan application against the logged-in user.

The prediction describes estimated repayment risk. It does **not** mean that a lender has approved or rejected the loan.

### 2. Savings and Investment Tracking

1. The application gets or creates a profile for the logged-in user.
2. A submitted investment is saved with the current user.
3. Investment records are filtered by the logged-in user.
4. The view calculates the total investment, remaining amount relative to profile salary, percentage, and chart data.

### 3. EMI Calculation

The EMI calculator uses the loan amount, annual interest rate, and tenure in months to calculate a monthly instalment and estimated total interest.

### 4. Prediction API

The prediction endpoint accepts POST requests with JSON or form data. It validates the required inputs, converts them to numeric values, invokes the prediction wrapper, and returns a JSON response.

## 💻 Getting Started

### Prerequisites

- Python 3.9 or later, compatible with the pinned dependencies
- pip
- The saved model file: `ml_models/model_application.pkl`

### 1. Clone the Repository

```bash
git clone https://github.com/Randomlyclueless/FinancialRiskAnalysis.git
cd FinancialRiskAnalysis
```

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

For local development, the application defaults to SQLite at `db.sqlite3`. The settings file also supports a `DATABASE_URL` environment variable.

For deployment:

- Set `SECRET_KEY` through an environment variable.
- Set `DEBUG=False`.
- Configure `ALLOWED_HOSTS` for the deployment domain.
- Configure trusted CSRF origins appropriately.

Do not use a development secret key in production.

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

Open the application at:

```text
http://127.0.0.1:8000/
```

To prepare static files for deployment, run:

```bash
python manage.py collectstatic
```

## 🤖 Machine Learning Model

The prediction wrapper loads `ml_models/model_application.pkl` when the predictor module is imported. A module-level `LoanPredictor` instance is then reused for prediction requests instead of explicitly loading the pickle file inside each prediction call.

The prediction wrapper expects these features:

- `loan_amnt`
- `annual_inc`
- `int_rate`
- `term`
- `emp_length`
- `installment`

The training script included in the supplied project output configures a scikit-learn pipeline with median imputation and a `RandomForestClassifier` using:

- `n_estimators=200`
- `max_depth=12`
- `min_samples_leaf=2`
- `class_weight="balanced"`
- `random_state=42`
- `n_jobs=-1`

The training script reports classification metrics, including accuracy, ROC-AUC, a confusion matrix, and a classification report.

Validate that the training script and deployed model artifact use the same feature schema before retraining or replacing the model.

## ⚡ Performance Notes

The current predictor wrapper reuses a module-level model instance rather than explicitly loading the model inside every prediction call.

The savings-tracker view currently calculates the investment total in Python after retrieving the user's investment records. One possible optimization is to use Django's database aggregation with `Sum()` for the total.

For example:

```python
from django.db.models import Sum

investments = Investment.objects.filter(user=request.user)

total_investment = (
    investments.aggregate(total=Sum("amount"))["total"]
    or Decimal("0.00")
)
```

This allows the database to calculate the total instead of retrieving every matching record solely for the summation. However, the view also needs investment records to prepare chart data, so the overall effect should be benchmarked.

**No reproducible benchmark was included in the reviewed source files to verify a 25–30% latency reduction.** Only claim that percentage if measurements establish the baseline, optimized result, workload, and measurement method.

## 🔐 Security and Deployment Notes

- Keep `SECRET_KEY` out of source control.
- Set `DEBUG=False` in production.
- Review `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for the actual deployment domain.
- Only load pickle files from trusted sources because unpickling an untrusted artifact can execute arbitrary code.
- Treat this project as a demonstration rather than a source of professional financial advice or credit decisions.

## 📌 Current Limitations and Items to Verify

- Add benchmark results if claiming a measured performance improvement.
- Confirm that the saved model artifact is available during deployment.
- Confirm that the model's class labels match the repayment-risk interpretation shown to users.
- Add automated tests for authentication, loan prediction, EMI calculations, and investment totals.
