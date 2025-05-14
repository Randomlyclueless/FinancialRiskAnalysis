# eda_analysis.py

import matplotlib.pyplot as plt
import os

# Make sure the 'static' folder exists in your Django app for saving images
STATIC_DIR = os.path.join(os.getcwd(), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

def analyze_user_finances(salary, loans, credit, other, sip):
    """
    Calculate savings, stress score, and generate pie & bar charts.

    Parameters:
        salary (int): Monthly income
        loans (int): Loan EMI payments
        credit (int): Credit card bills
        other (int): Other expenses
        sip (int): Monthly SIP/investment amount

    Returns:
        dict: Contains savings, stress score, and paths to saved charts
    """

    total_expense = loans + credit + other + sip
    savings = salary - total_expense
    stress_score = int((total_expense / salary) * 100)

    # Pie Chart - Expense Distribution
    plt.figure(figsize=(6, 6))
    labels = ['Loans', 'Credit', 'Other', 'SIP', 'Savings']
    values = [loans, credit, other, sip, max(savings, 0)]  # prevent negative slice
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Monthly Financial Breakdown")
    pie_path = os.path.join(STATIC_DIR, 'pie_chart.png')
    plt.savefig(pie_path)
    plt.close()

    # Bar Chart - Savings vs Expenses
    plt.figure(figsize=(6, 4))
    plt.bar(['Savings', 'Total Expenses'], [max(savings, 0), total_expense], color=['green', 'red'])
    plt.title("Savings vs Expenses")
    plt.ylabel("Amount (₹)")
    bar_path = os.path.join(STATIC_DIR, 'bar_chart.png')
    plt.savefig(bar_path)
    plt.close()

    return {
        'savings': savings,
        'stress_score': stress_score,
        'pie_chart': f'static/pie_chart.png',
        'bar_chart': f'static/bar_chart.png'
    }
