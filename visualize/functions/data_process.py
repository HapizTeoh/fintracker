import pandas as pd

def data_cleanup(input_df):
    # Remove rows with all NaN values
    clean_df = input_df.dropna(how='all')

    # Remove unused rows
    to_remove = ["SAVE","STATIC EXPENSES","DYNAMIC EXPENSES", "EXTRA CASH", "NOTABLE PURCHASE", "EXCESS"]
    clean_df = clean_df[~clean_df["Category"].isin(to_remove)]

    # Saving vs Spending vs Earning
    saving_category = ['ESPP', 'ENDOWUS FLAGSHIP','ENDOWUS CASH SMART SECURE','SAVINGS ACC ']
    earning_category = ['on-calls, MBO']

    # Category that saves money
    saving_df = clean_df[clean_df["Category"].isin(saving_category)]

    # Category that earns money
    earning_df = clean_df[clean_df["Category"].isin(earning_category)]

    # Remaining categories are spending
    spending_df = clean_df[~clean_df["Category"].isin(saving_category)]

    # Remove columns
    spending_df = spending_df.drop('Annual Total', axis=1)
    spending_df = spending_df.drop('Description', axis=1)

    # Remove earning categories
    spending_df = spending_df[spending_df["Category"] != "on-calls, MBO"]

    # Remove last row
    spending_df = spending_df[:-1]

    # Change wide to long df
    long_df = pd.melt(spending_df, id_vars=["Category"], var_name="Month", value_name="Amount")

    # Remove limit
    long_df = long_df[long_df["Month"] != "Limit"]

    # Remove parentheses and convert the value to negative
    long_df['Amount'] = long_df['Amount'].replace(r'\(\$(\d+\.\d+|\d+)\)', r'-\1', regex=True)

    # Remove the dollar sign ($) from the 'Amount' column
    long_df['Amount'] = long_df['Amount'].str.replace('$', '', regex=False)

    # Remove the commas, then convert to float
    long_df['Amount'] = long_df['Amount'].replace({',': ''}, regex=True).astype(float)

    # Group the data by month and Category
    df_grouped = long_df.groupby(['Month', 'Category'], as_index=False)['Amount'].sum()
    df_grouped['year'] = "2024"
    
    return df_grouped