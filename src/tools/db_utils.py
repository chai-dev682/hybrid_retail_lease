import csv
import pymysql
import json
from datetime import datetime
import os
from dotenv import load_dotenv
# Database Configuration (move to a separate config file later)
load_dotenv()
timeout = 10

DB_CONFIG = {
    "charset":"utf8mb4",
    "connect_timeout":timeout,
    "cursorclass":pymysql.cursors.DictCursor,
    "db":os.environ.get("db"),
    "host":os.environ.get("host"),
    "password":os.environ.get("password"),
    "read_timeout":timeout,
    "port":int(os.environ.get("port")),
    "user":os.environ.get("user"),
    "write_timeout":timeout,
}

TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS retail_leases (
  id INT PRIMARY KEY,
  StartDate DATE,
  ExpiryDate DATE,
  CurrentRentPa DECIMAL(10,2), -- Annual rent in thousands
  CurrentRentSqm DECIMAL(10,2), -- Rent per square meter
  CentreName VARCHAR(255),
  TenantCategory VARCHAR(255),
  TenantSubCategory VARCHAR(255),
  Lessor VARCHAR(255),
  Lessee VARCHAR(255),
  Area DECIMAL(10,2) -- Leased area in square meters
);
"""

def format_date(value):
    try:
        # Try parsing ISO format (2012-09-07T00:00:00)
        date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        try:
            # Try parsing MM/DD/YYYY format
            date_obj = datetime.strptime(value, '%m/%d/%Y')
        except ValueError:
            # If both fail, try YYYY-MM-DD format
            date_obj = datetime.strptime(value, '%Y-%m-%d')
    
    # Format the datetime object as a string in MySQL's DATE format
    return date_obj.strftime('%Y-%m-%d')

def create_database_connection(config):
    return pymysql.connect(**config)

def create_table(connection, schema):
    cursor = connection.cursor()
    cursor.execute(schema)
    connection.commit()

def insert_data(connection, data):
    cursor = connection.cursor()
    sql = """
    INSERT INTO retail_leases (id, StartDate, ExpiryDate, CurrentRentPa, CurrentRentSqm, CentreName, TenantCategory, TenantSubCategory, Lessor, Lessee, Area) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, data)
    connection.commit()

# Main function
def import_csv_to_mysql(csv_file_path):
    connection = create_database_connection(DB_CONFIG)
    create_table(connection, TABLE_SCHEMA)

    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header

        for row in reader:
            cleaned_data = (
                int(row[2]),
                format_date(row[6]),
                format_date(row[7]),
                int(row[25]),
                int(row[26]),
                row[12],
                row[32],
                row[33],
                row[20],
                row[21],
                int(row[17])
            )
            insert_data(connection, cleaned_data)

    connection.close()
    print("CSV data imported successfully into MySQL database.")

def format_rag_contexts(matches: list):
    contexts = []
    for x in matches:
        text = ""
        for i in list(x.keys()):
            if i == "id":
                continue
            if i in x:
                text += f"{i}: {x[i]}\n"
        if text:
            contexts.append(text)
    context_str = "\n---\n".join(contexts)
    return context_str

def query_sql(query: str):
    # Query sql database based on query and return list of matching elements
    connection = create_database_connection(DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute(query)
    print(query)
    return format_rag_contexts(cursor.fetchall())

# Entry point
# if __name__ == "__main__":
    # import_csv_to_mysql(f"{config.FIXTURES}/MattFarmerAI-TikTok-Profile-Scripts-analytics.csv")
    # query_sql("SELECT * \nFROM tiktok_data \nORDER BY views DESC;")