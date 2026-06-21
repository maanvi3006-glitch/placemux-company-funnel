"""Cleaning functions for raw data"""

def clean_company_names(df):
    df['clean_name'] = df['name'].str.lower().str.strip()
    return df
