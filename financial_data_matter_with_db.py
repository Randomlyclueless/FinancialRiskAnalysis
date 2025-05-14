import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
import json
from datetime import datetime, timedelta
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

def load_dataset(file_path):
    """Load dataset and handle basic cleaning."""
    try:
        df = pd.read_csv(file_path)
        df = df.dropna(how='all')
        df = df.fillna(0)
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def simulate_users(df, num_users=10):
    """Simulate multiple users with Indian names and 2-4 goals per user."""
    # List of Indian names
    indian_names = ['Aisha', 'Rohan', 'Meena', 'Arjun', 'Sneha', 'Vikram', 'Isha', 'Dev', 'Priya', 'Aman']
    
    # Ensure we have enough names by cycling through the list
    user_names = indian_names * (num_users // len(indian_names) + 1)
    user_names = user_names[:num_users]
    
    # Group by purpose to ensure diversity of goals
    purpose_groups = df.groupby('purpose')
    purposes = list(purpose_groups.groups.keys())
    
    # Create a new DataFrame for users
    user_dfs = []
    for user in user_names:
        # Sample 2-4 purposes per user
        user_purposes = np.random.choice(purposes, size=np.random.randint(2, 5), replace=False)
        for purpose in user_purposes:
            purpose_df = purpose_groups.get_group(purpose).sample(1)
            purpose_df['name'] = user
            user_dfs.append(purpose_df)
    
    # Combine into a single DataFrame
    new_df = pd.concat(user_dfs, ignore_index=True)
    return new_df

def fuzzy_match_column(col_name, target, threshold=90):
    """Fuzzy match column names with stricter threshold."""
    score = fuzz.partial_ratio(col_name.lower(), target.lower())
    return score >= threshold

def map_columns(df, schema_fields):
    """Map dataset columns to schema fields with improved fuzzy matching."""
    column_mapping = {}
    available_columns = df.columns.tolist()
    
    for field in schema_fields:
        best_match = None
        best_score = 0
        for col in available_columns:
            score = fuzz.partial_ratio(col.lower(), field.lower())
            if score > best_score and score >= 90:
                best_score = score
                best_match = col
        column_mapping[field] = best_match
    
    column_mapping['goal_name'] = 'purpose'
    column_mapping['monthly_contribution'] = 'installment'
    column_mapping['target_amount'] = None
    column_mapping['saved_so_far'] = None
    
    return column_mapping

def preprocess_data(df, column_mapping):
    """Preprocess data and derive missing fields."""
    numeric_fields = ['target_amount', 'saved_so_far', 'monthly_contribution']
    for field, col in column_mapping.items():
        if col and field in numeric_fields:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if column_mapping['target_amount'] is None and 'installment' in df.columns:
        df['target_amount'] = df['installment'] * 36
        column_mapping['target_amount'] = 'target_amount'
    
    if column_mapping['saved_so_far'] is None and 'installment' in df.columns:
        np.random.seed(42)
        df['payments_made'] = np.random.randint(1, 37, size=len(df))
        df['saved_so_far'] = df['installment'] * df['payments_made']
        column_mapping['saved_so_far'] = 'saved_so_far'
    
    if column_mapping['deadline'] is None:
        df['deadline'] = (datetime(2025, 5, 12) + timedelta(days=3*365)).strftime('%Y-%m-%d')
        column_mapping['deadline'] = 'deadline'
    
    if column_mapping['priority_level'] is None and 'int.rate' in df.columns:
        df['priority_level'] = pd.cut(df['int.rate'], bins=5, labels=[1, 2, 3, 4, 5])
        df['priority_level'] = df['priority_level'].astype(int)
        column_mapping['priority_level'] = 'priority_level'
    
    if column_mapping['is_locked'] is None and 'not.fully.paid' in df.columns:
        df['is_locked'] = df['not.fully.paid'].astype(bool)
        column_mapping['is_locked'] = 'is_locked'
    
    if column_mapping['auto_allocate'] is None and 'credit.policy' in df.columns:
        df['auto_allocate'] = df['credit.policy'].astype(bool)
        column_mapping['auto_allocate'] = 'auto_allocate'
    
    return df, column_mapping

def validate_and_flag(df, column_mapping, schema_fields):
    """Validate mappings and flag remaining issues."""
    flags = []
    for field in schema_fields:
        if column_mapping[field] is None:
            flags.append({
                "field": field,
                "status": "missing",
                "suggestion": f"Add a '{field}' column."
            })
    return df, flags

def calculate_accuracy(column_mapping, schema_fields, df_columns):
    """Calculate direct and overall mapping accuracy."""
    total_fields = len(schema_fields)
    direct_mappings = 0
    direct_possible = 0
    for field, mapped_col in column_mapping.items():
        if mapped_col in df_columns:
            direct_mappings += 1
            direct_possible += 1
        elif mapped_col and mapped_col not in df_columns:
            direct_possible += 1
    direct_accuracy = (direct_mappings / direct_possible * 100) if direct_possible > 0 else 0
    overall_mappings = sum(1 for field, col in column_mapping.items() if col is not None)
    overall_accuracy = (overall_mappings / total_fields) * 100
    return direct_accuracy, overall_accuracy

def generate_financial_advice(record):
    """Generate personalized financial advice for a user."""
    progress = (record['saved_so_far'] / record['target_amount']) * 100
    remaining = record['target_amount'] - record['saved_so_far']
    deadline_date = datetime.strptime(record['deadline'], '%Y-%m-%d')
    current_date = datetime(2025, 5, 12)
    months_left = (deadline_date.year - current_date.year) * 12 + (deadline_date.month - current_date.month)
    months_needed = remaining / record['monthly_contribution'] if record['monthly_contribution'] > 0 else float('inf')
    
    advice = f"Progress: {progress:.1f}% (Saved {record['saved_so_far']:.1f} of {record['target_amount']:.1f}). "
    advice += f"Remaining: {remaining:.1f}. Months left: {months_left}. "
    
    if record['is_locked']:
        advice += "This goal is locked (non-payment risk). "
        increase = 0.1 if record['priority_level'] <= 3 else 0.2
        new_contribution = record['monthly_contribution'] * (1 + increase)
        advice += f"Increase contribution by {increase*100:.0f}% to {new_contribution:.1f}/month to finish faster. "
    else:
        if months_needed > months_left:
            increase = (months_needed - months_left) * record['monthly_contribution'] / months_left
            advice += f"You're behind! Increase contribution by {increase:.1f}/month to finish on time. "
        else:
            advice += "You're on track. "
            increase = 0.05 if record['priority_level'] <= 3 else 0.1
            new_contribution = record['monthly_contribution'] * (1 + increase)
            advice += f"Consider adding {increase*100:.0f}% ({new_contribution:.1f}/month) to finish earlier. "
    
    if not record['auto_allocate']:
        advice += "Enable auto-allocation to ensure consistent payments."
    
    return advice, progress

def store_in_db(df):
    """Store the processed data in SQLite database."""
    conn = sqlite3.connect('financial_goals.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            name TEXT,
            goal_name TEXT,
            target_amount FLOAT,
            saved_so_far FLOAT,
            monthly_contribution FLOAT,
            deadline TEXT,
            priority_level INTEGER,
            is_locked BOOLEAN,
            auto_allocate BOOLEAN,
            progress FLOAT,
            advice TEXT,
            int_rate FLOAT,
            fico INTEGER,
            dti FLOAT,
            revol_util FLOAT
        )
    ''')
    
    for _, record in df.iterrows():
        advice, progress = generate_financial_advice(record)
        cursor.execute('''
            INSERT INTO goals (name, goal_name, target_amount, saved_so_far, monthly_contribution, deadline,
                              priority_level, is_locked, auto_allocate, progress, advice, int_rate, fico, dti, revol_util)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record['name'], record['goal_name'], record['target_amount'], record['saved_so_far'],
            record['monthly_contribution'], record['deadline'], record['priority_level'],
            record['is_locked'], record['auto_allocate'], progress, advice,
            record['int.rate'], record['fico'], record['dti'], record['revol.util']
        ))
    
    conn.commit()
    conn.close()

def create_visualizations(df):
    """Create visualizations for saved_so_far vs target_amount and monthly_contribution by priority_level."""
    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    index = range(min(len(df), 20))  # Limit to 20 for visualization
    plt.bar(index, df['target_amount'][:20], bar_width, label='Target Amount', color='lightblue')
    plt.bar([i + bar_width for i in index], df['saved_so_far'][:20], bar_width, label='Saved So Far', color='teal')
    plt.xlabel('Goals')
    plt.ylabel('Amount ($)')
    plt.title('Saved So Far vs Target Amount by Goal')
    plt.xticks([i + bar_width/2 for i in index], (df['name'] + ': ' + df['goal_name'])[:20], rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('saved_vs_target.png')
    plt.close()
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x='priority_level', y='monthly_contribution', hue='name', data=df[:20])
    plt.xlabel('Priority Level')
    plt.ylabel('Monthly Contribution ($)')
    plt.title('Monthly Contribution by Priority Level and User')
    plt.tight_layout()
    plt.savefig('monthly_contribution_by_priority.png')
    plt.close()

def convert_to_json(df, column_mapping, schema_fields):
    """Convert DataFrame to structured JSON."""
    records = []
    for _, row in df.iterrows():
        record = {}
        for field in schema_fields:
            col = column_mapping[field]
            if col:
                record[field] = row[col]
        record['name'] = row['name']
        record['progress'], record['advice'] = generate_financial_advice(row)
        record['int_rate'] = row['int.rate']
        record['fico'] = row['fico']
        record['dti'] = row['dti']
        record['revol_util'] = row['revol.util']
        records.append(record)
    return records

def process_financial_dataset(file_path, schema_fields):
    """Main function to process financial dataset with analysis."""
    df = load_dataset(file_path)
    if df is None:
        return None, [], 0, 0
    
    # Simulate multiple users (10 users, 2-4 goals each = 20-40 records)
    df = simulate_users(df, num_users=10)
    
    column_mapping = map_columns(df, schema_fields)
    df, column_mapping = preprocess_data(df, column_mapping)
    df, flags = validate_and_flag(df, column_mapping, schema_fields)
    
    df['progress'] = (df['saved_so_far'] / df['target_amount']) * 100
    df['advice'] = df.apply(lambda row: generate_financial_advice(row)[0], axis=1)
    
    json_output = convert_to_json(df, column_mapping, schema_fields)
    
    direct_accuracy, overall_accuracy = calculate_accuracy(column_mapping, schema_fields, df.columns)
    
    store_in_db(df)
    create_visualizations(df)
    
    return json_output, flags, direct_accuracy, overall_accuracy, df

if __name__ == "__main__":
    schema_fields = [
        "goal_name", "target_amount", "saved_so_far", "monthly_contribution",
        "deadline", "priority_level", "is_locked", "auto_allocate"
    ]
    file_path = "loan_data.csv"
    json_output, flags, direct_accuracy, overall_accuracy, analysis_df = process_financial_dataset(file_path, schema_fields)
    
    print("JSON Output (First 5 Records):")
    print(json.dumps(json_output[:5], indent=2))
    
    print("\nFlags:")
    for flag in flags:
        print(f"Field: {flag['field']}, Status: {flag['status']}, Suggestion: {flag['suggestion']}")
    
    print("\nAccuracy:")
    print(f"Direct Mapping Accuracy: {direct_accuracy:.2f}%")
    print(f"Overall Accuracy (including derived fields): {overall_accuracy:.2f}%")
    
    print("\nAvailable Goals:")
    for _, row in analysis_df.head(20).iterrows():
        print(f"{row['name']}: {row['goal_name']}")
    
    selected_goal = input("Enter the goal_name to view details (or press Enter for first user): ").strip()
    if not selected_goal:
        selected_goal = analysis_df['goal_name'].iloc[0]
    
    user_data = analysis_df[analysis_df['goal_name'] == selected_goal]
    if not user_data.empty:
        user_record = user_data.iloc[0]
        print(f"\nSelected User Data ({user_record['name']}: {selected_goal}):")
        print(json.dumps(user_record.to_dict(), indent=2))
        print(f"Financial Advice: {user_record['advice']}")
    else:
        print(f"Goal '{selected_goal}' not found in the first 20 records.")
    
    print("\nVisualizations saved as 'saved_vs_target.png' and 'monthly_contribution_by_priority.png'.")
    print("Data stored in SQLite database 'financial_goals.db'.")