import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
# Set page title
st.title('Enhanced Dashboard')
# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)        
        # Check if the 'Date' column is present
        if 'Date' not in data.columns:
            st.error("The CSV file must contain a 'Date' column.")
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
                # Select numerical columns for plotting
                numerical_columns = filtered_data.select_dtypes(include=['number']).columns
                if not numerical_columns.any():
                    st.error("The CSV file must contain numerical columns for visualization.")
                else:
                    selected_column = st.sidebar.selectbox("Select a column to visualize", numerical_columns)
                    chart_types = st.sidebar.multiselect(
                        "Select Chart Types",
                        ["Line Chart", "Bar Chart", "Pie Chart", "Heatmap"],
                        default=["Line Chart", "Bar Chart"]
                    )                    
                    # Summary Metrics in Tabular Form
                    st.subheader('Summary Metrics')
                    summary_metrics = {
                        'Metric': ['Average', 'Sum', 'Max', 'Min'],
                        'Value': [
                            filtered_data[selected_column].mean(),
                            filtered_data[selected_column].sum(),
                            filtered_data[selected_column].max(),
                            filtered_data[selected_column].min()
                        ]
                    }
                    st.table(pd.DataFrame(summary_metrics))
                    st.subheader('Statistics')
                    st.write(filtered_data.describe())                    
                    # Display selected charts
                    chart_cols = st.columns(len(chart_types))                    
                    for idx, chart_type in enumerate(chart_types):
                        with chart_cols[idx]:
                            st.subheader(chart_type)                            
                            if chart_type == "Line Chart":
                                line_chart = alt.Chart(filtered_data).mark_line().encode(
                                    x='Date:T',
                                    y=selected_column
                                )
                                st.altair_chart(line_chart, use_container_width=True)
                            elif chart_type == "Bar Chart":
                                bar_chart = alt.Chart(filtered_data).mark_bar().encode(
                                    x='Date:T',
                                    y=selected_column
                                )
                                st.altair_chart(bar_chart, use_container_width=True)
                            elif chart_type == "Pie Chart":
                                pie_data = filtered_data.groupby('Date').sum().reset_index()
                                plt.figure(figsize=(6, 4))
                                plt.pie(pie_data[selected_column], labels=pie_data['Date'], autopct='%1.1f%%')
                                st.pyplot(plt)
                            elif chart_type == "Heatmap":
                                heatmap_data = filtered_data.pivot_table(index='Date', values=selected_column, aggfunc='sum')
                                plt.figure(figsize=(6, 4))
                                sns.heatmap(heatmap_data, annot=True, fmt="g", cmap='viridis')
                                st.pyplot(plt)
                    # Download filtered data
                    st.subheader('Download Data')
                    csv = filtered_data.to_csv(index=False)
                    st.download_button(label="Download CSV", data=csv, file_name='filtered_data.csv', mime='text/csv')
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info('Please upload a CSV file to proceed.')

# Run the Streamlit app
if __name__ == '__main__':
    st.write('By ABD')
