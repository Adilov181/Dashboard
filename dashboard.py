import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
from fpdf import FPDF
import plotly.express as px

# Set page title
st.title('Enhanced Dashboard with Streamlit')

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
                st.sidebar.write(f"Selected date range: {start_date} to {end_date}")
            else:
                start_date, end_date = data['Date'].min(), data['Date'].max()

            # Filter data based on date range
            mask = (data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))
            filtered_data = data.loc[mask]

            # Debugging info: Show the filtered data
            st.write("Filtered Data:")
            st.write(filtered_data)

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
                        ["Line Chart", "Bar Chart", "Pie Chart", "Heatmap", "Scatter Plot", "Bubble Chart", "Box Plot", "Donut Chart", "Histogram", "Radar Chart"],
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
                        with chart_cols[idx % len(chart_cols)]:
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

                            elif chart_type == "Scatter Plot":
                                scatter_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
                                    x='Date:T',
                                    y=selected_column,
                                    tooltip=[selected_column, 'Date']
                                ).interactive()
                                st.altair_chart(scatter_plot, use_container_width=True)

                            elif chart_type == "Bubble Chart":
                                bubble_chart = px.scatter(filtered_data, x='Date', y=selected_column, size=selected_column, color=selected_column, hover_name='Date', size_max=60)
                                st.plotly_chart(bubble_chart)

                            elif chart_type == "Box Plot":
                                box_plot = px.box(filtered_data, x='Date', y=selected_column)
                                st.plotly_chart(box_plot)

                            elif chart_type == "Donut Chart":
                                donut_chart = px.pie(filtered_data, values=selected_column, names='Date', hole=0.3)
                                st.plotly_chart(donut_chart)

                            elif chart_type == "Histogram":
                                histogram = px.histogram(filtered_data, x=selected_column)
                                st.plotly_chart(histogram)

                            elif chart_type == "Radar Chart":
                                radar_data = filtered_data[['Date', selected_column]].set_index('Date')
                                radar_data = radar_data.T
                                radar_chart = px.line_polar(radar_data, r=radar_data.columns, theta=radar_data.index, line_close=True)
                                st.plotly_chart(radar_chart)

                    # Download filtered data
                    st.subheader('Download Data')
                    csv = filtered_data.to_csv(index=False)
                    st.download_button(label="Download CSV", data=csv, file_name='filtered_data.csv', mime='text/csv')

                    # Create a download tab for PDF or JPG
                    st.subheader('Download Dashboard')
                    download_format = st.radio("Select Download Format", ("PDF", "JPG"))

                    if st.button("Download"):
                        if download_format == "PDF":
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
                            pdf.cell(200, 10, txt="Dashboard", ln=True, align='C')

                            # Add summary metrics
                            pdf.cell(200, 10, txt="Summary Metrics", ln=True)
                            for metric, value in summary_metrics.items():
                                pdf.cell(200, 10, txt=f"{metric}: {value}", ln=True)

                            # Save the PDF
                            pdf.output("/mnt/data/dashboard.pdf")
                            with open("/mnt/data/dashboard.pdf", "rb") as file:
                                st.download_button(label="Download PDF", data=file, file_name="dashboard.pdf", mime="application/pdf")

                        elif download_format == "JPG":
                            # Generate JPG using imgkit
                            options = {'format': 'jpg', 'quality': '100'}
                            imgkit.from_file('/mnt/data/dashboard.html', '/mnt/data/dashboard.jpg', options=options)
                            with open("/mnt/data/dashboard.jpg", "rb") as file:
                                st.download_button(label="Download JPG", data=file, file_name="dashboard.jpg", mime="image/jpeg")

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info('Please upload a CSV file to proceed.')

# Run the Streamlit app
if __name__ == '__main__':
    st.write('by Abd')
