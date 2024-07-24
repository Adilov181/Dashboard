import streamlit as st
import pandas as pd
import numpy as np

# Set page title
st.title('Simple Dashboard with Streamlit')
# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        # Check if required columns are present
        if 'Date' not in data.columns or 'Value' not in data.columns:
            st.error("The CSV file must contain 'Date' and 'Value' columns.")
        else:
            data['Date'] = pd.to_datetime(data['Date'])
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
            if filtered_data.empty:
                st.warning("No data available for the selected date range.")
            else:
                # Main panel
                st.subheader('Line Chart')
                st.line_chart(filtered_data.set_index('Date')['Value'])
                st.subheader('Bar Chart')
                st.bar_chart(filtered_data.set_index('Date')['Value'])
                st.subheader('Statistics')
                st.write(filtered_data.describe())
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info('Please upload a CSV file to proceed.')
# Run the Streamlit app
if __name__ == '__main__':
    st.write('Run this script with: `streamlit run <script_name.py>`')
