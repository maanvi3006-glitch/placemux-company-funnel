"""Basic data validation utilities"""

def validate_not_null(df, cols):
    return df[cols].notnull().all().all()
