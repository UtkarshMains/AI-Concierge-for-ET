import pandas as pd
import sqlite3

# Read CSV file
df = pd.read_csv("user_data.csv")   # <-- your CSV file path

# Connect to SQLite DB
conn = sqlite3.connect("et_data.db")

# Write dataframe to table
df.to_sql("user_data", conn, if_exists="replace", index=False)

# Verify data
print(pd.read_sql("SELECT * FROM user_data", conn))

# Close connection
conn.close()
#tables created- user_data, site_data