#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from pathlib import Path

######################
# Import internal libraries
import functions as fn

# Current script's directory
current_dir = Path(__file__).parent.parent

# Relative path to a subfolder named "data"
data_folder = current_dir / "personal-sheet-data"

filelist = []
# Loop through all files in that folder
for file in data_folder.iterdir():
    if file.is_file():
        filelist.append(file.name)
        
#########################
# Load raw data
for file in filelist:
    raw_df = pd.read_csv(f"personal-sheet-data/{file}")
    #raw_df["year"] = file.split("-")[1].split(".")[0]

#########################
# Setup page and CSS
fn.setup_page()
fn.load_css()

#########################
# Data setup

df_grouped = fn.data_cleanup(raw_df)

# Define the correct month order
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

#########################
# Setup tabs

tab1, tab2 = st.tabs(["Annual", "Monthly"])

#########################
# Sidebar
with st.sidebar:
    st.title('💰 Finance tracker')
    
    year_list = list(df_grouped.year.unique())[::-1]
    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_grouped[df_grouped.year == selected_year]
    
with tab1:
    st.markdown("# Annual Spending")
    
    #######################
    ## Bar Chart  #########
    #######################
    
    # Define a selection for hover
    hover = alt.selection_single(fields=['Category'], on='mouseover', empty='none')
    
    # Selection bound to legend
    #legend_selection = alt.selection_multi(fields=['Category'], bind='legend', empty='none')
    
    # Build the stacked bar chart
    bar_chart = alt.Chart(df_selected_year).mark_bar().encode(
        x=alt.X('Month:N', title='Month', axis=alt.Axis(labelAngle=0),sort=month_order),  # :N for nominal (categorical)
        y=alt.Y('sum(Amount):Q', title='TotalAmount'),
        color=alt.Color('Category:N', title='Category'),
        order=alt.Order('Amount:Q', sort='descending'),
        tooltip=['Month', 'Category', alt.Tooltip('Amount:Q', format='$,.2f')],
        opacity=alt.condition(hover, alt.value(1), alt.value(0.55))
    ).properties(
        title='Monthly Spending Stacked by Category'
    ).add_params(hover)
    
    st.altair_chart(bar_chart)

with tab2:
    col = st.columns((3,1), gap='medium')

    with col[1]:
        # Filter months present in the data, and preserve the order
        available_months = [m for m in month_order if m in df_selected_year['Month'].unique()]
        
        # Streamlit slider to select month
        selected_month = st.select_slider('Select Month', options=available_months)
        
        st.markdown( selected_month + " monthly total compared to previous month")
        total_amount = df_selected_year[df_selected_year['Month'] == selected_month]['Amount'].sum()
        previous_month = month_order[month_order.index(selected_month) - 1]
        previous_total = df_selected_year[df_selected_year['Month'] == previous_month]['Amount'].sum()
        total_difference = round(total_amount - previous_total, 2)
        
        st.metric(label=selected_month, value=f"${total_amount:,.2f}", delta=total_difference, delta_color="inverse")
        
        st.markdown("Highest spent category in " + selected_month + " compared to previous month")
        
        df_amount_difference_sorted = fn.calculate_amount_difference(df_selected_year, selected_month)
        
        first_category_name = df_amount_difference_sorted.Category.iloc[0]
        first_category_amount = round(df_amount_difference_sorted.Amount.iloc[0], 2)
        if selected_month == df_selected_year['Month'].unique()[0]:
            first_category_delta = "No data"
        else:
            first_category_delta = f"${df_amount_difference_sorted.Amount_difference.iloc[0]:,.2f}"
        
        st.metric(label=first_category_name, value=first_category_amount, delta=first_category_delta, delta_color="inverse")
        
        with st.expander('About', expanded=True):
            st.write('''
                - Data: Self-collected.
                - :orange[**Monthly spending**]: spending in a month divided by category.
                - :orange[**Categories**]: self-defined categories for spending.
                
                :orange-badge[⚠️ Last updated 2025 May 1]
                ''')
    
        with col[0]:
            st.markdown("# Monthly Spending")
            
            #st.markdown('#### Monthly Expenses')
            
            #######################
            ## Pie Chart  #########
            #######################
            
            # Filter dataframe based on selected month
            filtered_pie_chart_df = df_selected_year[df_selected_year['Month'] == selected_month]
            
            # Define a selection for hover
            hover = alt.selection_single(fields=['Category'], on='mouseover', empty='none')
            
            # Calculate percentage for eachCategory
            filtered_pie_chart_df['percentage'] = ((filtered_pie_chart_df['Amount'] / filtered_pie_chart_df['Amount'].sum()) * 100) .round(2).astype(str)
            
            filtered_pie_chart_df['percentage_text'] = filtered_pie_chart_df['percentage'].round(2).astype(str) + '%'
            
            df_grouped_pie_sorted = filtered_pie_chart_df.sort_values('Amount')
            
            # Sorting the categories legends
            sorted_categories = df_grouped_pie_sorted['Category'].tolist()[::-1]

            # Create pie chart
            pie_chart = alt.Chart(df_grouped_pie_sorted).mark_arc().encode(
                theta='Amount:Q',
                color=alt.Color('Category:N',
                sort=sorted_categories,  # Sort legend by value
                legend=alt.Legend(title="Category")
            ), 
                order=' Amount:Q',
                tooltip=['Category', 'Amount'],
                opacity=alt.condition(hover, alt.value(1), alt.value(0.3))
            ).properties(
                width=400,
                height=400,
                title=f"Category Breakdown for {selected_month}"
            ).add_params(hover)
            
            # Format the percentage with `%` symbol in the tooltip
            pie_chart = pie_chart.configure_view(
                strokeOpacity=0  # Removes the border around the chart for better visual effect
            ).transform_calculate(
                percentage_text="datum.percentage + '%'"  # Append '%' to percentage value
            ).encode(
                tooltip=[
                    'Category:N',
                    alt.Tooltip('Amount:Q', format='$,.2f', title='Amount'),
                    alt.Tooltip('percentage_text:N', title='Percentage')  # Show percentage with %
                ]
            )

            st.altair_chart(pie_chart, use_container_width=True)
            
            #######################
            ## Category explanation
            #######################
            
            with st.expander("See explanation"):
                st.markdown('''
                    #### Category explanation
                    
                    **Work**: In progress
                ''')
            
            #######################
            ## Table Chart  #######
            #######################
            
            # Filter dataframe based on selected month
            filtered_table_df = df_selected_year[df_selected_year['Month'] == selected_month]

            # Group the data by month andCategory
            df_grouped_table = filtered_table_df.groupby(['Category'], as_index=False)['Amount'].sum()
            
            df_grouped_table_sorted = df_grouped_table.sort_values("Amount", ascending=False)
            
            st.caption("Category table for " + selected_month)
            
            st.dataframe(df_grouped_table_sorted,
                        column_order=("Category", "Amount"),
                        hide_index=True,
                        width=None,
                        column_config={
                        "Category": st.column_config.TextColumn(
                            "Category",
                        ),
                        "Amount": st.column_config.ProgressColumn(
                            "Total Annual Amount",
                            format="dollar",
                            min_value=0,
                            max_value=max(df_grouped_table_sorted.Amount)
                        ),
                        }
                    )