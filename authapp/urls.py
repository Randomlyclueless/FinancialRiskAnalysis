from django.urls import path
from authapp import views


urlpatterns = [
    path('', views.login_view, name='login'),  # Default route to login page
    path('home/', views.home, name='home'),  # Home page
    path('signup/', views.signup_view, name='signup'),
    path('loan-info/', views.loan_info, name='loan_info'),  # Loan info page
    path('emi_form/', views.emi_calculator, name='emi_form'),  # EMI form page
    path('savings_tracker/', views.savings_tracker, name='savings_tracker'),  # Savings tracker
]
