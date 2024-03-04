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
        -- Insert data from [DataforAnalysis].[dbo].[Dimension_WR] into [Temp_TransportData].[dbo].[Dimension_WR]
INSERT INTO [DataforAnalysis].[dbo].[Dimension_WR] (
    [Machine_no],
    [Part_ID],
    [Date],
    [Time],
    [Result],
    [Master_Judgment],
    [Operator],
    [Set_Dimension_Stack],
    [Result_0],
    [Parallelism_Stack],
    [Result_1],
    [P1_Stack_1],
    [Result_2],
    [P2_Stack_2],
    [Result_3],
    [P3_Stack_3],
    [Result_4],
    [P4_Ramp_Height],
    [Result_5],
    [P5_Pivot],
    [Result_6],
    [Set_Dimension_Attractive],
    [Result_7],
    [Parallelism_Attractive],
    [Result_8],
    [P4_Attractive_1],
    [Result_9],
    [P5_Attractive_2],
    [Result_10],
    [P6_Attractive_3],
    [Result_11],
    [Remark],
    [P6_Reference],
    [Result_12],
    [Reference_Solder_Height],
    [Result_13],
    [Model],
    [Line],
    [IP],
    [MfgDate]
)
SELECT
    [Machine_no],
    [Part_ID],
    [Date],
    [Time],
    [Result],
    [Master_Judgment],
    [Operator],
    [Set_Dimension_Stack],
    [Result_0],
    [Parallelism_Stack],
    [Result_1],
    [P1_Stack_1],
    [Result_2],
    [P2_Stack_2],
    [Result_3],
    [P3_Stack_3],
    [Result_4],
    [P4_Ramp_Height],
    [Result_5],
    [P5_Pivot],
    [Result_6],
    [Set_Dimension_Attractive],
    [Result_7],
    [Parallelism_Attractive],
    [Result_8],
    [P4_Attractive_1],
    [Result_9],
    [P5_Attractive_2],
    [Result_10],
    [P6_Attractive_3],
    [Result_11],
    [Remark],
    [P6_Reference],
    [Result_12],
    [Reference_Solder_Height],
    [Result_13],
    [Model],
    [Line],
    [IP],
    [MfgDate]
FROM [DataforAnalysis].[dbo].[Dimension_WR] AS source
WHERE Date > DATEADD(DAY, {Date_BT}, GETDATE()) and NOT EXISTS (
    SELECT 1
    FROM [DataforAnalysis].[dbo].[Dimension_WR] AS destination
    WHERE
        destination.[Part_ID] = source.[Part_ID]
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
