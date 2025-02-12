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
    "port":21086,
    "user":os.environ.get("user"),
    "write_timeout":timeout,
}

# Table schema (define in a separate module if needed)
TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS tiktok_data (  
  id INT AUTO_INCREMENT PRIMARY KEY,  
  views INT,  
  comments INT,  
  shares INT,  
  likes INT,  
  bookmark INT,  
  duration INT,  
  link_to_tiktok TEXT,  
  caption TEXT,  
  transcripts TEXT,  
  hashtags JSON, -- Changed to JSON type to store lists of hashtags  
  cover_image TEXT,  
  audio TEXT,  
  date_posted DATE  
);
"""

# Data cleaning and formatting functions (can be expanded)
def clean_number(value):
    return int(value.replace(',', ''))

def format_date(value):
    date_obj = datetime.strptime(value, '%m/%d/%Y')  
    # Format the datetime object as a string in MySQL's DATE format  
    formatted_date = date_obj.strftime('%Y-%m-%d') 
    return formatted_date  # Assuming date is already in correct format

# Database interaction functions
def create_database_connection(config):
    return pymysql.connect(**config)

def create_table(connection, schema):
    cursor = connection.cursor()
    cursor.execute(schema)
    connection.commit()

def insert_data(connection, data):
    cursor = connection.cursor()
    sql = """
    INSERT INTO tiktok_data (views, comments, shares, likes, bookmark, duration, link_to_tiktok, caption, transcripts, hashtags, cover_image, audio, date_posted) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            hashtags_json = json.dumps([tag.strip() for tag in row[9].split(',')])
            cleaned_data = (
                clean_number(row[0]),
                clean_number(row[1]),
                clean_number(row[2]),
                clean_number(row[3]),
                clean_number(row[4]),
                int(row[5]),
                row[6],
                row[7],
                row[8],
                hashtags_json,
                row[10],
                row[11],
                format_date(row[12])
            )
            insert_data(connection, cleaned_data)

    connection.close()
    print("CSV data imported successfully into MySQL database.")

def format_rag_contexts(matches: list):
    contexts = []
    for x in matches:
        text = ""
        if "caption" in x:
            text += f"caption: {x['caption']}\n"
        if "transcripts" in x:
            text += f"transcript: {x['transcripts']}\n"
        if "views" in x:
            text += f"views: {x['views']}\n"
        if "comments" in x:
            text += f"comments: {x['comments']}\n"
        if "shares" in x:
            text += f"shares: {x['shares']}\n"
        if "likes" in x:
            text += f"likes: {x['likes']}\n"
        if "bookmark" in x:
            text += f"bookmark: {x['bookmark']}\n"
        if "duration" in x:
            text += f"duration: {x['duration']}\n"
        if "date_posted" in x:
            text += f"date: {x['date_posted']}\n"
        for i in list(x.keys()):
            if "necessary_info__" in i:
                text += f"{i.split('__')[1]}: {x[i]}\n"
        if text:  # Only append non-empty text
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