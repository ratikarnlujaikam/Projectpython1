import pyodbc

def create_sql_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=192.168.101.219;'
            'DATABASE=DataforAnalysis_NEW;'
            'UID=DATALYZER;'
            'PWD=NMB54321'
        )
        
        return conn
    except pyodbc.Error as e:
        print("Error connecting to SQL Server:", e)
        return None
    
def create_sql_Component_Master():
    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=192.168.101.219;'
            'DATABASE=Component_Master;'
            'UID=DATALYZER;'
            'PWD=NMB54321'
        )
        
        return conn
    except pyodbc.Error as e:
        print("Error connecting to SQL Server:", e)
        return None
