"""Attribution analysis - track searches and registrations to compute conversion paths"""
import pandas as pd


def compute_attribution(searches, registrations):
    """
    Compute attribution: for each company, count searches and successful conversions.
    Returns attribution table showing search -> registration funnel per company.
    """
    if searches.empty or registrations.empty:
        return pd.DataFrame()
    
    searches['created_at'] = pd.to_datetime(searches['created_at'])
    registrations['created_at'] = pd.to_datetime(registrations['created_at'])
    
    search_counts = searches.groupby('company_id').size().rename('total_searches')
    reg_counts = registrations.groupby('company_id').size().rename('total_registrations')
    
    attribution = pd.DataFrame({'company_id': search_counts.index})
    attribution = attribution.merge(search_counts.reset_index(), on='company_id', how='left')
    attribution = attribution.merge(reg_counts.reset_index(), on='company_id', how='left')
    
    attribution[['total_searches', 'total_registrations']] = attribution[['total_searches', 'total_registrations']].fillna(0).astype(int)
    
    # Compute conversion rate: registrations / searches
    attribution['conversion_rate'] = (attribution['total_registrations'] / attribution['total_searches'].replace(0, 1)).round(4)
    
    return attribution
