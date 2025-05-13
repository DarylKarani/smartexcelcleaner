import pandas as pd
import json
from datetime import datetime

def load_config(config_path="config.json"):
    """Load config or set defaults"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "remove_duplicates": True,
            "format_dates": "YYYY-MM-DD",
            "calculate_missing_totals": True,
            "sort_by_date": True
        }

def read_excel(file_path):
    return pd.read_excel(file_path)

def preprocess(df):
    """Strip whitespace and drop empty columns/rows"""
    df.columns = df.columns.str.strip()
    df = df.dropna(how='all')  # drop completely empty rows
    df = df.dropna(axis=1, how='all')  # drop completely empty columns
    return df

def standardize_headers(df):
    """Rename to standard headers like: date, product, quantity, unit_price, total"""
    header_map = {
        'amount paid': 'total',
        'qty': 'quantity',
        'price': 'unit_price',
        'items': 'product'
        # you can add more mappings here
    }
    df.columns = [header_map.get(col.lower(), col.lower()) for col in df.columns]
    return df

def format_data(df, config):
    """Convert dates and numbers"""
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    for col in ['quantity', 'unit_price', 'total']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def clean_and_validate(df, config):
    """Clean data based on config settings"""
    if config["remove_duplicates"]:
        df = df.drop_duplicates()
    
    if config["calculate_missing_totals"] and all(col in df.columns for col in ['quantity', 'unit_price']):
        # Only calculate where total is missing or zero
        mask = df['total'].isna() | (df['total'] == 0)
        df.loc[mask, 'total'] = df.loc[mask, 'quantity'] * df.loc[mask, 'unit_price']
    
    if config["sort_by_date"] and 'date' in df.columns:
        df = df.sort_values('date')
        
    df['cleaned_on'] = datetime.today().strftime('%Y-%m-%d')
    return df

def export_cleaned_file(df, output_path="sales_cleaned.xlsx"):
    df.to_excel(output_path, index=False)
    return output_path

def main():
    config = load_config()
    input_file = "sales.xlsx"
    output_file = "sales_cleaned.xlsx"
    
    try:
        df = read_excel(input_file)
        df = preprocess(df)
        df = standardize_headers(df)
        df = format_data(df, config)
        print("Columns after formatting:", df.columns.tolist())
        df = clean_and_validate(df, config)
        output_path = export_cleaned_file(df, output_file)
        print(f"Cleaned data has been saved to {output_path}")
    except Exception as e:
        print(f"Error processing the file: {e}")

if __name__ == "__main__":
    main()
