from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LoanApplication, Investment, Profile

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('loan_amount', 'income', 'expenses', 'emi',
                    'interest_rate', 'loan_term',
                    'predicted_loan_approval', 'predicted_loan_term', 'created_at')
    list_filter  = ('predicted_loan_approval',)
    search_fields = ('loan_amount',)

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'investment_type', 'amount', 'investment_date')
    list_filter  = ('investment_type',)
    search_fields = ('user__username',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'salary')
    search_fields = ('user__username',)
