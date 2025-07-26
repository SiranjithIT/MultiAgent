from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "Chinook")

mysql_uri = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

class DatabaseConnect:
  def __init__(self, uri=mysql_uri):
    self.db = SQLDatabase.from_uri(uri)
        
  def get_db(self):
    return self.db
  
  def get_schema(self):
    return self.db.get_table_info()

  def get_table_names(self):
    return self.db.get_table_names()

  def get_columns(self, table_name: str):
    return self.db.get_columns(table_name)

  def execute_query(self, query: str):
    return self.db.execute_query(query)
      
  def run_query(self, query: str):
    return self.db.run(query)