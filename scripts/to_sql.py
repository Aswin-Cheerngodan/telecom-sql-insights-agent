# import pandas as pd
# import sqlite3

# # Read the Excel file
# excel_file = "data/Assignment_Mock_data_AIEngineer.xlsx"  # Replace with your file path

# # two sheets: mapping_data and main_data
# main_df = pd.read_excel(excel_file, sheet_name=0)  # first sheet

# # Connect to SQLite database (creates if not exists)
# conn = sqlite3.connect("project_database.db")
# cursor = conn.cursor()

# # Save DataFrame into SQL tables
# main_df.to_sql("main_data", conn, if_exists="replace", index=False)

# # Commit and close
# conn.commit()
# conn.close()

# print("Excel data successfully converted into SQL database!")



### Option 2

import pandas as pd
from sqlalchemy import create_engine
import sqlite3

# Read the Excel file
excel_file = 'data/Assignment_Mock_data_AIEngineer.xlsx'

# Read sheets
main_data_df = pd.read_excel(excel_file, sheet_name='Main Data')

# Data Cleaning
# Remove any extra blank rows or NaN-only rows
main_data_df.dropna(how='all', inplace=True)


# Create SQLite Database 
engine = create_engine('sqlite:///telecom_data.db', echo=False)

# Write DataFrame to SQL tables
main_data_df.to_sql('usage_logs', engine, if_exists='replace', index=False)

print("✅ Data successfully written to SQL database!")

# Test a query
query = """
SELECT 
    imsi,
    imsitac,
    vmcc,
    vmnc,
    hmcc,
    hmnc,
    data_inbound_downloaded_bytes,
    data_outbound_uploaded_bytes,
    device_type,
    extract_date,
    (data_inbound_downloaded_bytes + data_inbound_uploaded_bytes + 
     data_outbound_downloaded_bytes + data_outbound_uploaded_bytes) AS total_data_usage
FROM usage_logs
WHERE device_type = 'NON-IOT'
  AND extract_date >= '2025-01-01'
ORDER BY total_data_usage DESC
LIMIT 10;
"""

# Execute query and show result
result = pd.read_sql_query(query, engine)
print("\nTop 10 NON-IoT Records by Total Data Usage :")
print(result)