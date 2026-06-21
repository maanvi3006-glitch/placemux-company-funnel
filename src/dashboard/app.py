import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Locate export CSVs
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
EXPORT_CSV = os.path.join(BASE_DIR, 'data', 'exports', 'final_dashboard_data.csv')
COHORT_CSV = os.path.join(BASE_DIR, 'data', 'exports', 'cohort_analysis.csv')
ATTRIBUTION_CSV = os.path.join(BASE_DIR, 'data', 'exports', 'attribution.csv')

st.set_page_config(page_title='PlaceMux Company Funnel', layout='wide')

@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)

data = load_data(EXPORT_CSV)
cohort_data = load_data(COHORT_CSV)
attribution_data = load_data(ATTRIBUTION_CSV)

st.title('PlaceMux — Company Funnel Dashboard')

# Parse dates
if 'created_at' in data.columns:
    data['created_at'] = pd.to_datetime(data['created_at'])

# Sidebar filters
companies = ['All'] + (data['name'].astype(str).unique().tolist() if not data.empty else [])
sel_company = st.sidebar.selectbox('Select company', companies)

min_date = data['created_at'].min() if 'created_at' in data.columns and not data.empty else None
max_date = data['created_at'].max() if 'created_at' in data.columns and not data.empty else None
start, end = st.sidebar.date_input('Date range', value=(min_date, max_date)) if min_date and max_date else (None, None)

# Filter data
if sel_company == 'All':
    df = data.copy()
else:
    df = data[data['name'] == sel_company].copy()

if 'created_at' in df.columns and start and end:
    df = df[(df['created_at'] >= pd.to_datetime(start)) & (df['created_at'] <= pd.to_datetime(end))]

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(['Funnel Overview', 'Cohort Analysis', 'Attribution', 'Forecast'])

# ===== TAB 1: FUNNEL OVERVIEW =====
with tab1:
    if data.empty:
        st.warning('No data available')
    else:
        st.header('Funnel & KPIs')
        
        # Compute aggregates
        agg = {
            'searches': int(df['searches'].sum()) if 'searches' in df else 0,
            'registrations': int(df['registrations'].sum()) if 'registrations' in df else 0,
            'jobs': int(df['jobs'].sum()) if 'jobs' in df else 0,
            'impressions': int(df['impressions'].sum()) if 'impressions' in df else 0,
            'clicks': int(df['clicks'].sum()) if 'clicks' in df else 0,
            'conversions': int(df['conversions'].sum()) if 'conversions' in df else 0,
        }
        
        ctr = (agg['clicks'] / agg['impressions']) if agg['impressions'] else 0
        conversion_rate = (agg['conversions'] / agg['clicks']) if agg['clicks'] else 0
        
        # KPI metrics
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric('Searches', agg['searches'])
        with k2:
            st.metric('Registrations', agg['registrations'])
        with k3:
            st.metric('Jobs', agg['jobs'])
        with k4:
            st.metric('Impressions', agg['impressions'])
        
        k5, k6 = st.columns(2)
        with k5:
            st.metric('CTR', f"{ctr:.2%}" if agg['impressions'] else 'N/A')
        with k6:
            st.metric('Conversion Rate', f"{conversion_rate:.2%}" if agg['clicks'] else 'N/A')
        
        st.markdown('---')
        
        # Funnel chart
        st.subheader('Funnel Stages')
        stages = ['Searches', 'Registrations', 'Jobs']
        values = [agg['searches'], agg['registrations'], agg['jobs']]
        funnel_df = pd.DataFrame({'Stage': stages, 'Count': values})
        
        fig = px.bar(funnel_df, x='Stage', y='Count', text='Count', color='Stage', 
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, yaxis_title='Count')
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend chart
        st.subheader('Trends Over Time')
        if 'created_at' in df.columns:
            trend = df.groupby('created_at').sum(numeric_only=True).reset_index()
            fig2 = px.line(trend, x='created_at', y=['searches', 'clicks', 'conversions'],
                          labels={'value': 'Count', 'created_at': 'Date'})
            st.plotly_chart(fig2, use_container_width=True)
        
        # Raw data
        st.subheader('Detailed Data')
        st.dataframe(df, use_container_width=True)

# ===== TAB 2: COHORT ANALYSIS =====
with tab2:
    if cohort_data.empty:
        st.info('No cohort data available')
    else:
        st.header('Cohort Analysis')
        st.write('User cohorts by signup month')
        
        st.dataframe(cohort_data, use_container_width=True)
        
        # Cohort size chart
        if 'cohort_month' in cohort_data.columns and 'cohort_size' in cohort_data.columns:
            fig = px.bar(cohort_data, x='cohort_month', y='cohort_size', text='cohort_size',
                        color_discrete_sequence=['#1f77b4'])
            fig.update_traces(textposition='outside')
            fig.update_layout(xaxis_title='Cohort Month', yaxis_title='Cohort Size')
            st.plotly_chart(fig, use_container_width=True)

# ===== TAB 3: ATTRIBUTION =====
with tab3:
    if attribution_data.empty:
        st.info('No attribution data available')
    else:
        st.header('Attribution Analysis')
        st.write('Searches → Registrations conversion by company')
        
        # Sort by conversion rate
        attr_sorted = attribution_data.sort_values('conversion_rate', ascending=False)
        st.dataframe(attr_sorted, use_container_width=True)
        
        # Conversion chart
        fig = px.bar(attr_sorted, x='name', y='conversion_rate', text='conversion_rate',
                    color='conversion_rate', color_continuous_scale='Viridis')
        fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')
        fig.update_layout(xaxis_title='Company', yaxis_title='Conversion Rate',
                         xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ===== TAB 4: FORECAST =====
with tab4:
    st.header('Forecast')
    st.write('Simple forecast for next month based on recent trends')
    
    if not data.empty and 'created_at' in data.columns:
        # Aggregate by month
        monthly_data = data.groupby('created_at').sum(numeric_only=True).reset_index()
        
        if len(monthly_data) >= 2:
            # Simple moving average forecast
            recent = monthly_data.iloc[-3:] if len(monthly_data) >= 3 else monthly_data
            
            forecast = {
                'Metric': ['Searches', 'Registrations', 'Jobs'],
                'Forecast': [
                    int(recent['searches'].mean()),
                    int(recent['registrations'].mean()),
                    int(recent['jobs'].mean()),
                ]
            }
            
            forecast_df = pd.DataFrame(forecast)
            st.dataframe(forecast_df, use_container_width=True)
            
            # Forecast viz
            fig = px.bar(forecast_df, x='Metric', y='Forecast', text='Forecast',
                        color='Metric', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False, yaxis_title='Forecasted Count')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info('Not enough data to forecast')
    else:
        st.info('No time series data for forecast')

st.markdown('---')
st.caption(f'Data sources: Funnel | Cohort | Attribution | Enhanced analytics powered by Python')
