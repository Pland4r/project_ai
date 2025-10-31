import pandas as pd
import numpy as np
from datetime import datetime

# Define date formats to try (covers all formats in sample data)
date_formats = [
    '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
    '%Y-%m-%d', '%d-%b-%Y', '%b-%d-%Y',
    '%d-%m-%y', '%y-%m-%d'
]

def clean_date(date_str):
    """Parse date from multiple formats"""
    if pd.isna(date_str) or date_str in ['', 'NaN']:
        return np.nan
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return np.nan

def clean_numeric(value):
    """Convert to numeric, handle commas and invalid values"""
    if pd.isna(value) or value in ['?', 'N/A', 'NaN', 'none', '']:
        return np.nan
    if isinstance(value, str):
        value = value.replace(',', '')
    try:
        num = float(value)
        return num if num >= 0 else np.nan  # Negative counts invalid
    except ValueError:
        return np.nan

# Load data
df = pd.read_csv('data saas.csv')

# Clean date column
df['date'] = df['date'].apply(clean_date)

# Clean numeric columns
numeric_cols = ['total_users', 'churned_users', 'new_users', 'active_users']
for col in numeric_cols:
    df[col] = df[col].apply(clean_numeric)

# Cap unreasonably large values (e.g., 99999999)
for col in numeric_cols:
    df[col] = df[col].apply(lambda x: np.nan if x > 1e6 else x)

# Drop unnecessary columns
df = df.drop(columns=['debug_info', 'extra_col', '??note'], errors='ignore')

# Save cleaned data
df.to_csv('cleaned_data.csv', index=False)
print("Data cleaning complete. Saved to cleaned_data.csv")
