import pandas as pd

# Define the correct month order
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Calculation month-over-month population migrations
def calculate_amount_difference(input_df, input_month):
    selected_month_data = input_df[input_df['Month'] == input_month].reset_index()
    previous_month = month_order[month_order.index(input_month) - 1]
    previous_month_data = input_df[input_df['Month'] == previous_month].reset_index()
    selected_month_data['Amount_difference'] = selected_month_data.Amount.sub(previous_month_data.Amount, fill_value=0)
    return pd.concat([selected_month_data.Category, selected_month_data.Amount, selected_month_data.Amount_difference], axis=1).sort_values(by="Amount", ascending=False)
