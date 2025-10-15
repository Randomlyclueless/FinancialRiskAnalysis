from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from authapp.models import LoanApplication, Profile, Investment
from .forms import LoanApplicationForm, InvestmentForm
from ml_models.predictor import (
    predict_from_input,
    predict_loan_approval,
    predict_loan_term,
    predict_loan_eligibility
)
import json

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('authapp:home')

        messages.error(request, 'Invalid username or password')
    return render(request, 'authapp/login.html')

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create the profile if it doesn't already exist
            Profile.objects.get_or_create(user=user, defaults={'salary': 50000.00})
            messages.success(request, 'Account created! Please log in.')
            return redirect('authapp:login')  # Update this to use the namespace
        messages.error(request, 'Signup failed; please check the form.')
    else:
        form = UserCreationForm()
    return render(request, 'authapp/signup.html', {'form': form})

@login_required(login_url='login')
# Home view with ML Predictions and Loan Form
@login_required(login_url='login')
def home(request):
    loan_approval = None
    loan_term = None
    loan_eligibility = None

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            try:
                # Prepare instance without saving
                instance = form.save(commit=False)

                # Map form fields to expected model fields
                input_data = {
                    'term': int(form.cleaned_data['loan_term']),
                    'int_rate': float(form.cleaned_data['interest_rate']),
                    'emp_length': float(form.cleaned_data.get('emp_length', 0)),
                    'loan_amount': float(form.cleaned_data.get('loan_amount', 0)),
                    'income': float(form.cleaned_data.get('income', 0)),
                    'expenses': float(form.cleaned_data.get('expenses', 0)),
                    'emi': float(form.cleaned_data.get('emi', 0))
                }

                print("Input data prepared for prediction:", input_data)

                # Ensure no negative values for important fields
                if input_data['term'] <= 0:
                    raise ValueError("Loan term must be positive")
                if input_data['int_rate'] < 0:
                    raise ValueError("Interest rate cannot be negative")
                if input_data['loan_amount'] <= 0:
                    raise ValueError("Loan amount must be positive")
                if input_data['income'] <= 0:
                    raise ValueError("Income must be positive")

                # Run predictions with try/except for each to prevent cascading failures
                try:
                    loan_approval = predict_loan_approval(input_data)
                except Exception as e:
                    loan_approval = {"status": "Unknown", "error": str(e)}
                    print(f"Approval prediction error: {str(e)}")
                
                try:
                    loan_term = predict_loan_term(input_data)
                except Exception as e:
                    loan_term = {"loan_term": input_data['term'], "error": str(e)}
                    print(f"Term prediction error: {str(e)}")
                
                try:
                    loan_eligibility = predict_loan_eligibility(input_data)
                except Exception as e:
                    loan_eligibility = {"eligible": "Unknown", "error": str(e)}
                    print(f"Eligibility prediction error: {str(e)}")

                # Assign predictions to instance
                instance.user = request.user
                instance.predicted_loan_approval = bool(loan_approval.get('prediction', 0)) if isinstance(loan_approval, dict) else False
                instance.predicted_loan_term = loan_term.get('loan_term', 12) if isinstance(loan_term, dict) else 12

                # Save instance
                instance.save()

                messages.success(request, 'Application submitted successfully!')
                
                # No redirect to keep showing results
                
            except KeyError as e:
                messages.error(request, f"Missing required field: {str(e)}")
            except ValueError as e:
                messages.error(request, f"Invalid input: {str(e)}")
            except Exception as e:
                messages.error(request, f"Processing error: {str(e)}")
                import traceback
                print(traceback.format_exc())  # Detailed error in console
        else:
            # Display specific form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = LoanApplicationForm()

    return render(request, 'authapp/home.html', {
        'form': form,
        'loan_approval': loan_approval,
        'loan_term': loan_term,
        'loan_eligibility': loan_eligibility
    })


# Savings Tracker view with chart
@login_required(login_url='login')
def savings_tracker(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'salary': Decimal('00.0')}
    )

    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            inv = form.save(commit=False)
            inv.user = request.user
            inv.save()
            messages.success(request, 'Investment added!')
            return redirect('savings_tracker')

    form = InvestmentForm()
    investments = Investment.objects.filter(user=request.user)

    total_investment = sum(inv.amount for inv in investments)
    salary = profile.salary or Decimal('0')
    remaining = salary - total_investment
    percentage = (total_investment / salary * 100) if salary else 0

    dates = [inv.investment_date.strftime("%Y-%m-%d") for inv in investments]
    amounts = [float(inv.amount) for inv in investments]

    if not investments.exists():
        messages.info(request, "No investments yet. Add one to see the chart.")

    return render(request, 'authapp/savings_tracker.html', {
        'form': form,
        'investments': investments,
        'total_investment': total_investment,
        'remaining': remaining,
        'percentage': round(float(percentage), 2),
        'salary': salary,
        'dates': json.dumps(dates),
        'amounts': json.dumps(amounts),
    })
    
# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

# AJAX risk prediction endpoint
def predict_risk(request):
    if request.method == 'POST':
        term = request.POST.get('term')
        int_rate = request.POST.get('int_rate')
        emp_length = request.POST.get('emp_length')

        # Validate input data
        if not term or not int_rate or not emp_length:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        input_data = {
            'term': int(term),
            'int_rate': float(int_rate),
            'emp_length': float(emp_length),
            # Add any other required fields here
        }

        try:
            result = predict_from_input(input_data)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': f"Prediction failed: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=400)


from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def loan_info(request):
    return render(request, 'authapp/loan_info.html')



from django.shortcuts import render, redirect
from django.http import HttpResponse


def emi_calculator(request):
    emi = None
    loan_amount = None
    interest_rate = None
    tenure_months = None
    total_interest = None

    if request.method == 'POST':
        try:
            loan_amount = float(request.POST.get('loan_amount'))
            interest_rate = float(request.POST.get('interest_rate'))
            tenure_months = int(request.POST.get('tenure_months'))

            # Validate inputs
            if loan_amount <= 0:
                raise ValueError("Loan amount must be greater than zero")
            if interest_rate <= 0:
                raise ValueError("Interest rate must be greater than zero")
            if tenure_months <= 0:
                raise ValueError("Loan tenure must be greater than zero")

            # EMI calculation
            monthly_rate = interest_rate / (12 * 100)
            emi = (loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure_months)) / (((1 + monthly_rate) ** tenure_months) - 1)
            
            # Calculate total interest
            total_payment = emi * tenure_months
            total_interest = total_payment - loan_amount
            
            # Format for display
            emi = "{:.2f}".format(emi)
            total_interest = "{:.2f}".format(total_interest)

        except ValueError as e:
            return render(request, 'authapp/emi_form.html', {'error': str(e)})
        except Exception as e:
            return render(request, 'authapp/emi_form.html', {'error': f"Calculation error: {e}"})
    
    # Render the form or result
    context = {
        'emi': emi,
        'loan_amount': loan_amount,
        'interest_rate': interest_rate,
        'tenure_months': tenure_months,
        'total_interest': total_interest
    }
    
    return render(request, 'authapp/emi_form.html', context)

# Helper function can be removed as the calculation is now inline in the view
# Or you can keep it and modify it to return more values:
def calculate_emi(loan_amount, interest_rate, tenure_months):
    monthly_rate = interest_rate / (12 * 100)
    emi = (loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure_months)) / (((1 + monthly_rate) ** tenure_months) - 1)
    total_payment = emi * tenure_months
    total_interest = total_payment - loan_amount
    
    return {
        'emi': round(emi, 2),
        'total_interest': round(total_interest, 2),
        'total_payment': round(total_payment, 2)
    }