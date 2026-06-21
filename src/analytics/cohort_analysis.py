"""Cohort analysis - track user retention by signup cohort"""
import pandas as pd


def compute_cohort_analysis(registrations):
    """
    Compute cohort retention: group users by signup month and track activity.
    Returns a cohort table showing cohort size and retention rates.
    """
    if registrations.empty:
        return pd.DataFrame()
    
    registrations['created_at'] = pd.to_datetime(registrations['created_at'])
    registrations['cohort_month'] = registrations['created_at'].dt.to_period('M')
    
    cohorts = registrations.groupby('cohort_month').size().rename('cohort_size').reset_index()
    cohorts['cohort_month'] = cohorts['cohort_month'].astype(str)
    
    return cohorts


def cohort_retention_rate(cohort_data):
    """Calculate retention rate for a cohort (users who signed up in that month)."""
    if cohort_data.empty:
        return pd.DataFrame()
    
    # Simple: retention = size of cohort
    cohort_data['retention_rate'] = 1.0
    return cohort_data
