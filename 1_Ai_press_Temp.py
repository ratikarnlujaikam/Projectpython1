import pyodbc

from Date_All_process import Date_between  

Date_BT = Date_between()

def create_sql_connection():
    # Replace these values with your actual database connection details
    server = '192.168.101.219'
    database = 'DataforAnalysis'
    username = 'DATALYZER'
    password = 'NMB54321'
    driver = '{SQL Server}'
    
    # Establish a connection to the database
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    connection = pyodbc.connect(conn_str)
    return connection

def fetch_data():
    try:
        # Establish a connection to the database
        conn = create_sql_connection()
        cursor = conn.cursor()

        # SQL query to insert data
        query_template = f"""
               INSERT INTO [DataforAnalysis].[dbo].[Ai_press] (
                [Machine_no], [Date], [Time], [Max_force], [Datum_probe],
                [Barcode], [Master_Judgment], [Model], [Line], [IP],
                [MfgDate], [Emp_no], [Define_row]
            )
            SELECT
                [Machine_no], [Date], [Time], [Max_force], [Datum_probe],
                [Barcode]
				, ltrim(Rtrim([Master_Judgment]))  as [Master_Judgment]
				, ltrim(Rtrim([Model])), ltrim(Rtrim([Line]))
				, [IP],
                [MfgDate]
				, [Emp_no]
				, [Define_row]
            FROM
                [Temp_TransportData].[dbo].[Ai_press] AS source
            WHERE [Date] > DATEADD(DAY, {Date_BT}, GETDATE()) and NOT EXISTS (
                SELECT 1
                FROM [DataforAnalysis].[dbo].[Ai_Press] AS destination
                WHERE
                    destination.[Barcode] = source.[Barcode]
                    AND CONVERT(datetime, destination.[Time]) = source.[Time]
            );
        """

        cursor.execute(query_template)

        # Commit the changes to the database
        conn.commit()

        # Close the database connection
        conn.close()

        print('Data fetch and insert successful.')

    except Exception as e:
        print(f'Error in fetch_data: {e}')

# Call the function
fetch_data()
