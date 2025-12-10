import pyodbc
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class Database:
    def __init__(self):
        self.server = os.getenv('DB_SERVER', 'localhost')
        self.database = os.getenv('DB_NAME', 'HospitalDB')
    
    def get_connection(self):
        """Conexiune cu Windows Authentication"""
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'Trusted_Connection=yes;'  # Pentru Windows Authentication
        )
        return pyodbc.connect(conn_str)
    
    def execute_query(self, query, params=None):
        """Pentru INSERT, UPDATE, DELETE"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        conn.close()
        
    def fetch_data(self, query, params=None):
        """Pentru SELECT - returnează coloane și date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        conn.close()
        return columns, data
    
    def fetch_dataframe(self, query, params=None):
        """Pentru SELECT - returnează pandas DataFrame (mai ușor de folosit!)"""
        conn = self.get_connection()
        df = pd.read_sql(query, conn, params=params if params else None)
        conn.close()
        return df

# Creăm o instanță globală
db = Database()