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
            INSERT INTO [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester] (
    [Machine_no],
    [Date],
    [Time],
    [Operator],
    [Barcode],
    [Master_Judgment],
    [Set_Dim],
    [Set_Dim_A],
    [Set_Dim_B],
    [Set_Dim_C],
    [Ramp_to_Datum],
    [Contact_Probe_2],
    [Pivot_Height],
    [Parallelism],
    [TIR],
    [TIR_A],
    [TIR_B],
    [TIR_C],
    [FlyHeight],
    [Fly_Height_Max_Limit],
    [Fly_Height_Min_Limit],
    [Axial_Play],
    [Static_Dim],
    [Static_Dim_A],
    [Static_Dim_B],
    [Static_Dim_C],
    [RVA],
    [Speed],
    [Ramp_Pivot],
    [Projection1],
    [Flange-Ramp_pad],
    [Dimension_Max],
    [Dimension_Max_Angle],
    [Dimension_Min],
    [Dimension_Min_Angle],
    [Static_Parallelism],
    [Static_Dimension_Max],
    [Static_Dimension_Max_Angle],
    [Static_Dimension_Min],
    [Static_Dimension_Min_Angle],
    [NRRO],
    [RRO],
    [Spin_direction_Value],
    [Spin_direction_Bin_Number],
    [Spin_direction_Result],
    [Remarks],
    [Line],
    [Model],
    [2ndYield],
    [NG criteria],
    [IP],
    [MfgDate]

)
SELECT
    [Machine_no],
    [Date],
    [Time],
    [Operator],
    [Barcode],
    [Master_Judgment],
    [Set_Dim],
    [Set_Dim_A],
    [Set_Dim_B],
    [Set_Dim_C],
    [Ramp_to_Datum],
    [Contact_Probe_2],
    [Pivot_Height],
    [Parallelism],
    [TIR],
    [TIR_A],
    [TIR_B],
    [TIR_C],
    [FlyHeight],
    [Fly_Height_Max_Limit],
    [Fly_Height_Min_Limit],
    [Axial_Play],
    [Static_Dim],
    [Static_Dim_A],
    [Static_Dim_B],
    [Static_Dim_C],
    [RVA],
    [Speed],
    [Ramp_Pivot],
    [Projection1],
    [Flange-Ramp_pad],
    [Dimension_Max],
    [Dimension_Max_Angle],
    [Dimension_Min],
    [Dimension_Min_Angle],
    [Static_Parallelism],
    [Static_Dimension_Max],
    [Static_Dimension_Max_Angle],
    [Static_Dimension_Min],
    [Static_Dimension_Min_Angle],
    [NRRO],
    [RRO],
    [Spin_direction_Value],
    [Spin_direction_Bin_Number],
    [Spin_direction_Result],
    [Remarks],
    [Line],
    [Model],
    [2ndYield],
    [NG criteria],
    [IP],
    [MfgDate]

FROM [Temp_TransportData].[dbo].[Dynamic_Parallelism_Tester] AS source
WHERE Date > DATEADD(DAY, {Date_BT}, GETDATE()) and NOT EXISTS (
    SELECT 1
    FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester] AS destination
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
