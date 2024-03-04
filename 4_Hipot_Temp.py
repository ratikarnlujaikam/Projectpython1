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
            INSERT INTO [DataforAnalysis].[dbo].[Hipot] (
    [Machine_no]
      ,[Barcode]
      ,[Date]
      ,[Time]
      ,[Master_Judgment]
      ,[Operator]
      ,[Spin_direction_Sensor]
      ,[Speed_check]
      ,[Check_contact]
      ,[R1_UV]
      ,[R2_UW]
      ,[R3_VW]
      ,[R1_UV_raw]
      ,[R2_UV_raw]
      ,[R3_VW_raw]
      ,[R_max_min]
      ,[R_delta_rel]
      ,[R_Max_per_Min]
      ,[R_imb_R2_R1]
      ,[R_imb_R3_R1]
      ,[R_WCT]
      ,[T_coil]
      ,[Bearing_drag]
      ,[Check_contact_HiPot]
      ,[HighPot_test]
      ,[Check_contact_hammer]
      ,[Cycle_time]
      ,[act_Comment]
      ,[Model]
      ,[Line]
      ,[R_Test_Counterplate]
      ,[2ndYield]
      ,[NG_criteria]
      ,[IP]
      ,[MfgDate]
  

)
SELECT
   [Machine_no]
      ,[Barcode]
      ,[Date]
      ,[Time]
      ,[Master_Judgment]
      ,[Operator]
      ,[Spin_direction_Sensor]
      ,[Speed_check]
      ,[Check_contact]
      ,[R1_UV]
      ,[R2_UW]
      ,[R3_VW]
      ,[R1_UV_raw]
      ,[R2_UV_raw]
      ,[R3_VW_raw]
      ,[R_max_min]
      ,[R_delta_rel]
      ,[R_Max_per_Min]
      ,[R_imb_R2_R1]
      ,[R_imb_R3_R1]
      ,[R_WCT]
      ,[T_coil]
      ,[Bearing_drag]
      ,[Check_contact_HiPot]
      ,[HighPot_test]
      ,[Check_contact_hammer]
      ,[Cycle_time]
      ,[act_Comment]
      ,[Model]
      ,[Line]
      ,[R_Test_Counterplate]
      ,[2ndYield]
      ,[NG_criteria]
      ,[IP]
      ,[MfgDate]
FROM [Temp_TransportData].[dbo].[Hipot] AS source
where Date > DATEADD(DAY, {Date_BT}, GETDATE()) and NOT EXISTS (
    SELECT 1
    FROM [DataforAnalysis].[dbo].[Hipot] AS destination
    WHERE
        destination.[Barcode] = source.[Barcode]
        AND destination.[Time] = source.[Time]
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
