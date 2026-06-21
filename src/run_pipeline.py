"""Simple ETL pipeline to produce dashboard export"""
import os
import sys
import pandas as pd

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analytics.cohort_analysis import compute_cohort_analysis
from analytics.attribution import compute_attribution
from analytics.forecasting import forecast_funnel_metrics

# Use local relative paths to avoid import errors when running as a script
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_PATH = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_PATH = os.path.join(BASE_DIR, 'data', 'processed')
EXPORT_PATH = os.path.join(BASE_DIR, 'data', 'exports', 'final_dashboard_data.csv')
COHORT_PATH = os.path.join(BASE_DIR, 'data', 'exports', 'cohort_analysis.csv')
ATTRIBUTION_PATH = os.path.join(BASE_DIR, 'data', 'exports', 'attribution.csv')


def load_raw():
    companies = pd.read_csv(os.path.join(RAW_PATH, 'companies.csv'))
    searches = pd.read_csv(os.path.join(RAW_PATH, 'searches.csv'))
    registrations = pd.read_csv(os.path.join(RAW_PATH, 'registrations.csv'))
    jobs = pd.read_csv(os.path.join(RAW_PATH, 'jobs.csv'))
    return companies, searches, registrations, jobs


def clean_companies(companies):
    companies['clean_name'] = companies['name'].astype(str).str.lower().str.strip()
    return companies


def aggregate_funnel(companies, searches, registrations, jobs):
    # parse dates and aggregate by company_id and date (month)
    searches['created_at'] = pd.to_datetime(searches['created_at'])
    registrations['created_at'] = pd.to_datetime(registrations['created_at'])
    jobs['posted_at'] = pd.to_datetime(jobs['posted_at'])

    searches['date'] = searches['created_at'].dt.to_period('M').dt.to_timestamp()
    registrations['date'] = registrations['created_at'].dt.to_period('M').dt.to_timestamp()
    jobs['date'] = jobs['posted_at'].dt.to_period('M').dt.to_timestamp()

    s = searches.groupby(['company_id', 'date']).size().rename('searches')
    r = registrations.groupby(['company_id', 'date']).size().rename('registrations')
    j = jobs.groupby(['company_id', 'date']).size().rename('jobs')

    df = companies.set_index('company_id')
    # create full index of company x dates present
    idx = pd.MultiIndex.from_product([df.index, pd.Index(sorted(set(s.index.get_level_values(1).tolist() + r.index.get_level_values(1).tolist() + j.index.get_level_values(1).tolist())))], names=['company_id','date'])
    out = pd.DataFrame(index=idx).join(s, how='left').join(r, how='left').join(j, how='left')
    out = out.fillna(0).reset_index()
    out = out.merge(companies[['company_id','name']], on='company_id', how='left')

    # derive simple metrics
    out['impressions'] = (out['searches'] * 100).astype(int)
    out['clicks'] = (out['searches'] * 10).astype(int)
    out['conversions'] = out['registrations'].astype(int)

    # add clean name
    out['clean_name'] = out['name'].astype(str).str.lower().str.strip()

    # reorder columns
    out = out[['company_id','name','date','clean_name','searches','registrations','jobs','impressions','clicks','conversions']]
    out = out.rename(columns={'date':'created_at'})
    return out


def main():
    os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)
    companies, searches, registrations, jobs = load_raw()
    companies = clean_companies(companies)
    funnel = aggregate_funnel(companies, searches, registrations, jobs)

    # write the funnel export directly
    funnel.to_csv(EXPORT_PATH, index=False)
    print('Wrote export to', EXPORT_PATH)
    
    # Compute cohort analysis
    cohort = compute_cohort_analysis(registrations)
    if not cohort.empty:
        cohort.to_csv(COHORT_PATH, index=False)
        print('Wrote cohort analysis to', COHORT_PATH)
    
    # Compute attribution
    attribution = compute_attribution(searches, registrations)
    if not attribution.empty:
        # merge with company names
        attribution = attribution.merge(companies[['company_id', 'name']], on='company_id', how='left')
        attribution.to_csv(ATTRIBUTION_PATH, index=False)
        print('Wrote attribution to', ATTRIBUTION_PATH)
    
    # Compute forecast for next month
    monthly_funnel = funnel.groupby('created_at')[['searches', 'registrations', 'jobs']].sum()
    forecast = forecast_funnel_metrics(monthly_funnel)
    print('Next month forecast:', forecast)


if __name__ == '__main__':
    main()
