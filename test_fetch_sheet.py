import pandas as pd
import numpy as np
import requests
import os
from openpyxl import load_workbook  # Requires openpyxl for table detection

# sheet_id = "164IpVmO9f7u8Mux4b6Yfjcee6nQJJtYZT8yGMYcZ4ow"
# url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

url = "https://docs.google.com/spreadsheets/d/1eFN39ZVBw7vNlX7N-XnhY7WtzvMfc6aCw_mu2fTufWs/edit?usp=sharing"
url = url.replace("edit?usp=sharing", "export?format=xlsx")

print(f"Attempting to fetch: {url}")
local_file = "debug_data.xlsx"


if os.path.exists(local_file):
    print(f"Loading from local cache: {local_file}")
    xl = pd.ExcelFile(local_file)
else:
    print(f"Fetching from web: {url}")
    try:
        # Download the content
        response = requests.get(url)
        response.raise_for_status() # Check for errors
        
        # Save to local disk
        with open(local_file, "wb") as f:
            f.write(response.content)
            
        # Load into pandas
        xl = pd.ExcelFile(local_file)
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        raise

try:
    # Load workbook with openpyxl to access table objects
    wb = load_workbook(local_file, data_only=True)
    
    print("Successfully fetched Excel file.")
    print(f"Sheet names found: {wb.sheetnames}\n")
    print("-" * 40)
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Check for Excel Table objects (ListObject in Excel)
        if hasattr(ws, 'tables'):
            tables = ws.tables
            print(f"### Sheet: '{sheet_name}'")
            print(f"   Found {len(tables)} Excel Table object(s):")
            
            for table_name, table_ref in tables.items():
                print(f"\n   Table Name: '{table_name}'")
                print(f"   Range: {table_ref}")
                
                # Parse the range to get dimensions
                ref_parts = table_ref.split(':')
                if len(ref_parts) == 2:
                    start_cell = ref_parts[0]
                    end_cell = ref_parts[1]
                    print(f"   From {start_cell} to {end_cell}")
                    
                    # Convert Excel references to indices
                    from openpyxl.utils import column_index_from_string, coordinate_to_tuple
                    
                    start_col_letter = ''.join(filter(str.isalpha, start_cell))
                    start_col_idx = column_index_from_string(start_col_letter)
                    start_row_idx = int(''.join(filter(str.isdigit, start_cell)))
                    
                    end_col_letter = ''.join(filter(str.isalpha, end_cell))
                    end_col_idx = column_index_from_string(end_col_letter)
                    end_row_idx = int(''.join(filter(str.isdigit, end_cell)))
                    
                    rows = end_row_idx - start_row_idx + 1
                    cols = end_col_idx - start_col_idx + 1
                    
                    print(f"   Dimensions: {rows} rows (including header) x {cols} columns")
                    print(f"   Data rows: {rows-1} rows (excluding header)")
            
            if len(tables) == 0:
                print(f"   No formal Excel Table objects found")
        
        print()

except Exception as e:
    print(f"Error: {e}")