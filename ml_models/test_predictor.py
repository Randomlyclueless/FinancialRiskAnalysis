from predictor import predict_from_input

test_input = {
    'term': 36,
    'int_rate': 13.56,
    'emp_length': 10,
    'loan_amnt': 15000,
    'annual_inc': 55000,
    'purpose': 'credit_card',
    'home_ownership': 'RENT',
    'grade': 'B',
    'sub_grade': 'B2',
    'verification_status': 'Verified',
    'addr_state': 'CA',
    'open_acc': 10,
    'funded_amnt_inv': 14000,
    'zip_code': '123xx',
    'mths_since_last_delinq': 4,
    'pub_rec': 0,
    'total_pymnt_inv': 16000,
    'last_pymnt_d_month': 6,
    'last_pymnt_d_year': 2023,
    'delinq_2yrs': 0,
    'dti': 15.2,
    'revol_util': 45.0,
    'last_pymnt_amnt': 150,
    'revol_bal': 5000,
    'total_pymnt': 17000,
    'earliest_cr_line': '2001-05-01',
    'loan_age': 800,
    'installment': 456,
    'inq_last_6mths': 1,
    'total_acc': 23,
    'total_rec_prncp': 10000,
    'loan_status': 'Fully Paid',
    'funded_amnt': 15000,
    'payment_ratio': 1.13,
    'last_credit_pull_d_month': 4,
    'last_credit_pull_d_year': 2024,
    'total_rec_int': 1900
}

result = predict_from_input(test_input)
print("Prediction Result:", result)
