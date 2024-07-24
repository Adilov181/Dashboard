import streamlit as st
import pandas as pd
import numpy as np
# Set page title
st.title('Simple Dashboard with Streamlit')
# Generate sample data
np.random.seed(42)
data = pd.DataFrame({
    'Date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
    'Value': np.random.randn(100).cumsum()
})
# Sidebar filters
st.sidebar.header('Filters')
date_filter = st.sidebar.date_input('Select a date range', [data['Date'].min(), data['Date'].max()])
# Ensure the date_filter is a list of datetime objects
if isinstance(date_filter, list) and len(date_filter) == 2:
    start_date, end_date = date_filter[0], date_filter[1]
else:
    start_date, end_date = data['Date'].min(), data['Date'].max()
# Filter data based on date range
filtered_data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
# Main panel
st.subheader('Line Chart')
st.line_chart(filtered_data.set_index('Date'))
st.subheader('Bar Chart')
st.bar_chart(filtered_data.set_index('Date'))
st.subheader('Statistics')
st.write(filtered_data.describe())
# Run the Streamlit app
if __name__ == '__main__':
    st.write('Run this script with: `streamlit run <script_name.py>`')
