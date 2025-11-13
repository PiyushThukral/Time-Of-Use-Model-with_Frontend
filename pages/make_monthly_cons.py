import pandas as pd


def compute_monthly_consumption(df, consumption_cols = None):
    """
    Adds a 'total_monthly_consumption' column to the DataFrame by summing daily consumption
    across all 'Consumption_Hr_' columns, grouped by Consumer No, Year, and Month.
    Returns the modified DataFrame.
    """
    if 'total_monthly_consumption' in df.columns:
        print("✅ Column 'total_monthly_consumption' already exists.")
        return df

    try:
        # Identify hourly consumption columns
        if consumption_cols is None:
            consumption_cols = [col for col in df.columns if col.startswith('Consumption_Hr_')]



        if not consumption_cols:
            print("❌ No consumption hr columns found.")
            return df

        # Convert 'Date' column to datetime
        # if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'], format="%d-%m-%Y", errors='coerce')

        # Extract Year and Month as strings
        df['Year'] = df['Date'].dt.year.astype(str)
        df['Month'] = df['Date'].dt.month.astype(str)

        # Sum daily consumption
        df['daily_demand'] = df[consumption_cols].sum(axis=1).round(0)

        # Group by Consumer No, Month, and Year to get total monthly consumption
        monthly_df = (
            df.groupby(['Consumer No', 'Year', 'Month'])['daily_demand']
            .sum()
            .reset_index(name='total_monthly_consumption')
        )
        monthly_df['total_monthly_consumption'] = monthly_df['total_monthly_consumption'].round(0)

        # Merge back into original DataFrame
        df = df.merge(monthly_df, on=['Consumer No', 'Year', 'Month'], how='left')

        # Drop intermediate columns
        df.drop(columns=['Year', 'Month'], inplace=True)

        print("✅ Added 'total_monthly_consumption'.")
        return df

    except Exception as e:
        print(f"❌ Exception occurred during monthly consumption computation: {e}")
        return df