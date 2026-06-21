import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Locate export CSV
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
EXPORT_CSV = os.path.join(BASE_DIR, 'data', 'exports', 'final_dashboard_data.csv')

st.set_page_config(page_title='PlaceMux Company Funnel', layout='wide')

@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


data = load_data(EXPORT_CSV)

st.title('PlaceMux — Company Funnel Dashboard')

if data.empty:
    st.warning('No export data found at {}'.format(EXPORT_CSV))
    st.stop()

# Company selector
# parse date column
if 'created_at' in data.columns:
    data['created_at'] = pd.to_datetime(data['created_at'])

companies = ['All'] + data['name'].astype(str).unique().tolist()
sel = st.sidebar.selectbox('Select company', companies)

# date range filter
min_date = data['created_at'].min() if 'created_at' in data.columns else None
max_date = data['created_at'].max() if 'created_at' in data.columns else None
start, end = st.sidebar.date_input('Date range', value=(min_date, max_date))

if sel == 'All':
    df = data.copy()
else:
    df = data[data['name'] == sel].copy()

# apply date filter
if 'created_at' in df.columns and start and end:
    df = df[(df['created_at'] >= pd.to_datetime(start)) & (df['created_at'] <= pd.to_datetime(end))]

# Aggregate metrics
agg = {
    'searches': int(df['searches'].sum()) if 'searches' in df else 0,
    'registrations': int(df['registrations'].sum()) if 'registrations' in df else 0,
    'jobs': int(df['jobs'].sum()) if 'jobs' in df else 0,
    'impressions': int(df['impressions'].sum()) if 'impressions' in df else 0,
    'clicks': int(df['clicks'].sum()) if 'clicks' in df else 0,
    'conversions': int(df['conversions'].sum()) if 'conversions' in df else 0,
}

# KPIs
ctr = (agg['clicks'] / agg['impressions']) if agg['impressions'] else 0
conversion_rate = (agg['conversions'] / agg['clicks']) if agg['clicks'] else 0

# Top row KPIs
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
    st.metric('Clicks', agg['clicks'])
with k6:
    st.metric('Conversions', agg['conversions'])

kr1, kr2 = st.columns(2)
with kr1:
    st.metric('CTR', f"{ctr:.2%}" if agg['impressions'] else 'N/A')
with kr2:
    st.metric('Conversion Rate', f"{conversion_rate:.2%}" if agg['clicks'] else 'N/A')

st.markdown('---')

# Funnel chart (searches -> registrations -> jobs)
st.subheader('Funnel')
st.write('Aggregated funnel stages for selection')

stages = ['Searches', 'Registrations', 'Jobs']
values = [agg['searches'], agg['registrations'], agg['jobs']]

funnel_df = pd.DataFrame({'stage': stages, 'count': values})
fig = px.bar(funnel_df, x='stage', y='count', text='count', color='stage', color_discrete_sequence=px.colors.qualitative.Safe)
fig.update_traces(textposition='outside')
fig.update_layout(showlegend=False, yaxis_title='Count')
st.plotly_chart(fig, use_container_width=True)

st.markdown('---')

# Trend chart
st.subheader('Trends')
if 'created_at' in df.columns:
    trend = df.groupby('created_at').sum().reset_index()
    fig2 = px.line(trend, x='created_at', y=['searches','clicks','conversions'], labels={'value':'count','created_at':'Date'})
    st.plotly_chart(fig2, use_container_width=True)

# Raw table
st.subheader('Underlying Data')
st.dataframe(df)

st.markdown('---')

st.caption('Data source: {}'.format(EXPORT_CSV))
