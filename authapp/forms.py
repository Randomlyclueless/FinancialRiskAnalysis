from django import forms
from .models import LoanApplication

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['loan_amount', 'income', 'expenses', 'emi', 'interest_rate', 'loan_term', 'emp_length']  # Added emp_length
        widgets = {
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'income': forms.NumberInput(attrs={'class': 'form-control'}),
            'expenses': forms.NumberInput(attrs={'class': 'form-control'}),
            'emi': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'loan_term': forms.NumberInput(attrs={'class': 'form-control'}),
            'emp_length': forms.NumberInput(attrs={'class': 'form-control'}),  # Add the input widget for emp_length
        }

from django.shortcuts import render, redirect

from .models import Investment


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['investment_type', 'amount', 'investment_date']
        widgets = {
            'investment_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'investment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }