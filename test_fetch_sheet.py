import pandas as pd
import requests
import os

# sheet_id = "164IpVmO9f7u8Mux4b6Yfjcee6nQJJtYZT8yGMYcZ4ow"
# url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

url = "https://docs.google.com/spreadsheets/d/1eFN39ZVBw7vNlX7N-XnhY7WtzvMfc6aCw_mu2fTufWs/edit?usp=sharing"
url = url.replace("edit?usp=sharing", "export?format=xlsx")

print(f"Attempting to fetch: {url}")

try:
    # Try reading as excel which supports multiple sheets
    xl = pd.ExcelFile(url)
    print("Successfully fetched Excel file.")
    print(f"Sheet names: {xl.sheet_names}")
    

except Exception as e:
    print(f"Error: {e}")
