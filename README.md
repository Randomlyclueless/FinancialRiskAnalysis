Financial Risk Analysis & Banking Loan Prediction Platform
A Django-based financial dashboard for loan repayment-risk prediction, EMI calculation, and investment tracking. The application uses a saved scikit-learn model for prediction and SQLite by default, with database URL configuration available for deployment environments.
Features
- User accounts: Sign up and log in using Django authentication.
- Loan risk prediction: Submit loan and financial details to receive a model prediction about repayment risk.
- Rule-based eligibility estimate: Calculate a debt-to-income (DTI) ratio and compare it with the application's 50% threshold.
- Loan-term handling: Return the loan term supplied by the user.
- EMI calculator: Calculate estimated monthly instalments and total interest.
- Savings and investment tracker: Add investments, view user-specific investment records, and calculate totals and percentages against the profile salary.
- Prediction endpoint: Accept POST requests using JSON or form data and return a JSON prediction response.
This is an educational project, not a lender's underwriting system. A model prediction is not an actual loan approval or a guarantee of repayment.

Technology Stack
Layer	Technology evidenced in the project
Backend / web framework	Python, Django 5.2
Database	SQLite by default; DATABASE_URL can configure another supported database
Authentication	Django authentication and session middleware
Data handling	Pandas
Machine learning	scikit-learn saved model
Frontend	Django templates, HTML, CSS, and JavaScript
Static-file serving	WhiteNoise
Deployment server dependency	Gunicorn


Application Structure
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
The prediction code expects the saved model at ml_models/model_application.pkl. Ensure that this artifact is present before starting the Django application.
How the Main Flows Work
Loan risk prediction
1. The user submits loan amount, income, expenses, EMI, interest rate, loan term, and employment length.
2. Django validates the form and prepares the values for prediction.
3. ml_models/predictor.py maps the submitted fields to the feature names expected by the model.
4. The saved model returns a class prediction and estimated failure probability.
5. The Django view saves the loan application against the logged-in user.
The model's status describes predicted repayment risk. It does not mean a lender has approved or rejected a loan.
Savings and investment tracking
1. The view gets or creates a profile for the logged-in user.
2. A submitted investment is saved with the current user.
3. Investment records are filtered by the logged-in user.
4. The view calculates the total investment, remaining amount relative to profile salary, percentage, and chart data.
EMI calculation
The EMI calculator uses the loan amount, annual interest rate, and tenure in months to calculate a monthly instalment and estimated total interest.
Getting Started
Prerequisites
- Python 3.9 or later (use a Python version compatible with the pinned dependencies)
- pip
- The saved model file: ml_models/model_application.pkl
1. Clone the repository
Replace the URL below with the repository URL you use:
git clone https://github.com/Randomlyclueless/FinancialRiskAnalysis.git
cd FinancialRiskAnalysis
2. Create and activate a virtual environment
Windows PowerShell:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
macOS / Linux:
python -m venv .venv
source .venv/bin/activate
3. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
4. Configure environment variables
For local development, Django defaults to SQLite at db.sqlite3. The settings file also supports a DATABASE_URL environment variable.

Set a secret key through the SECRET_KEY environment variable for deployment. Do not use a development secret key in production. Configure DEBUG=False and ALLOWED_HOSTS appropriately before deploying.
5. Apply migrations and start the server
python manage.py migrate
python manage.py runserver
Open http://127.0.0.1:8000/ in your browser.

If static assets need to be prepared for deployment, run:
python manage.py collectstatic
Machine Learning Model
The prediction wrapper loads ml_models/model_application.pkl once when the predictor module is imported, then reuses the loaded model through a module-level LoanPredictor instance.

The wrapper expects these input features:
- loan_amnt
- annual_inc
- int_rate
- term
- emp_length
- installment
The training script included in the supplied project output configures a scikit-learn pipeline with median imputation and a RandomForestClassifier (n_estimators=200, max_depth=12, min_samples_leaf=2, class_weight="balanced", and n_jobs=-1). Validate that the training script and the deployed model artifact use the same feature schema before retraining or replacing the model.
Performance Notes
The current predictor wrapper reuses a module-level model instance rather than explicitly loading the pickle file inside each prediction call.

The savings-tracker view currently calculates the investment total in Python after retrieving the user's investment records. A possible optimization is to use Django's database aggregation (Sum) for the total. Because the view also needs records for chart data, the end-to-end effect should be benchmarked before describing it as a measured improvement.

No reproducible benchmark was included in the reviewed source files to verify a 25–30% latency reduction. Only claim that percentage on a resume if you have measurements showing the baseline, optimized result, workload, and measurement method.
Security and Deployment Notes
- Keep SECRET_KEY out of source control and set it through the environment.
- Set DEBUG=False in production.
- Review ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS for the actual deployment domain.
- Only load pickle files from trusted sources; unpickling an untrusted artifact can execute arbitrary code.
- The project should be treated as a demonstration, not a source of professional financial advice or credit decisions.
Current Limitations / Items to Verify
- Add benchmark results if you want to substantiate a performance-improvement claim.
- Confirm the saved model artifact is included or otherwise supplied during deployment.
- Confirm that the model's class labels match the interpretation of repayment risk in the UI.
- Add automated tests for authentication, loan prediction, EMI calculations, and investment totals.
