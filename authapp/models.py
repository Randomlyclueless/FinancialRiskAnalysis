from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()
class LoanApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null = True, related_name='loan_applications')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    income = models.DecimalField(max_digits=12, decimal_places=2)
    expenses = models.DecimalField(max_digits=12, decimal_places=2)
    emi = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    loan_term = models.IntegerField()
    predicted_loan_approval = models.BooleanField(null=True, blank=True)
    predicted_loan_term = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    emp_length = models.CharField(max_length=20, null=True, blank=True)  # Add emp_length field if needed

    def __str__(self):
        return f"Loan of ₹{self.loan_amount} for {self.loan_term} months by {self.user.username}"

    class Meta:
        verbose_name = "Loan Application"
        verbose_name_plural = "Loan Applications"
        ordering = ['-created_at']

class Investment(models.Model):
    INVESTMENT_TYPE_CHOICES = [
        ('SIP', 'SIP'),
        ('Mutual Funds', 'Mutual Funds'),
        ('Stocks', 'Stocks'),
        ('Fixed Deposit', 'Fixed Deposit'),
        ('Gold', 'Gold'),
        ('Crypto', 'Crypto'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, db_index=True)  # Link to User model (optional)
    investment_type = models.CharField(max_length=50, choices=INVESTMENT_TYPE_CHOICES, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    investment_date = models.DateField(db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.investment_type} - ₹{self.amount} on {self.investment_date}"

    class Meta:
        verbose_name = "Investment"
        verbose_name_plural = "Investments"
        ordering = ['-investment_date']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )  # Salary field with a validator to prevent negative or zero salary
    address = models.CharField(max_length=255, null=True, blank=True)  # Optional address field
    contact_number = models.CharField(max_length=15, null=True, blank=True)  # Optional contact number field
    
    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
