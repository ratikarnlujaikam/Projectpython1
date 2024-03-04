import pyodbc

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
        query_template = """
-- WITH clause and CTE definition (unchanged)
WITH cte AS (
    SELECT
        [Dynamic_Parallelism_Tester].[Date],
        [Dynamic_Parallelism_Tester].[Time],
        [Barcode_base],
        [Dynamic_Parallelism_Tester].[Barcode],
        [Barcode_rotor],
        [Datum_probe],
        [Max_force],
        [FlyHeight],
        [Parallelism],
        [Pivot_Height],
        [Projection1],
        [Ramp_Pivot],
        [Ramp_to_Datum],
        [Flange-Ramp_pad],
        [Set_Dim],
        [Set_Dim_A],
        [Set_Dim_B],
        [Set_Dim_C],
        [Ke_0_peak_avg],
        [Bemf_balance],
        [brg_drag],
        [ke_avg],
        [ke_ripple],
        [NRRO_ax_FFT_1],
        [NRRO_probe_A],
        [NRRO_probe_B],
        [NRRO_rad_FFT_1],
        [run_current],
        ewms.[RVA],
        [start_torque],
        [TIR_probe_A],
        [TIR_probe_B],
        [R_max_min],
        [R1_UV],
        [R2_UW],
        [R3_VW],
        [Axial_play_data],
        [Oil_top_data],
        [Oil_bottom_data],
        [Dynamic_Parallelism_Tester].[Model],
        [Line_no] AS Line,
        ROW_NUMBER() OVER (PARTITION BY [Dynamic_Parallelism_Tester].[Barcode] ORDER BY [Dynamic_Parallelism_Tester].[Time] desc) AS RowNum
    FROM
        [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
    LEFT JOIN [DataforAnalysis].[dbo].[EWMS] ON [Dynamic_Parallelism_Tester].Barcode = EWMS.Barcode
    LEFT JOIN [DataforAnalysis].[dbo].[Ai_press] ON [Dynamic_Parallelism_Tester].Barcode = [Ai_press].Barcode
    LEFT JOIN [DataforAnalysis].[dbo].[Hipot] ON [Dynamic_Parallelism_Tester].Barcode = [Hipot].Barcode
    LEFT JOIN [TransportData].[dbo].[Matching] ON [Dynamic_Parallelism_Tester].Barcode = [Matching].Barcode_Motor
    LEFT JOIN [T1749].[dbo].[IP_Connect] ON [Dynamic_Parallelism_Tester].IP = [IP_Connect].IP_Address
    WHERE
        [Dynamic_Parallelism_Tester].[Date] > DATEADD(DAY, -10, GETDATE()) AND
        [Dynamic_Parallelism_Tester].[Barcode] NOT LIKE '%OK%' AND
        [Dynamic_Parallelism_Tester].[Barcode] NOT LIKE '%NG%' AND
        [Dynamic_Parallelism_Tester].[Barcode] NOT LIKE '%MASTER%' AND
        [Dynamic_Parallelism_Tester].[Barcode] NOT LIKE '%DUMMY%'
)

-- INSERT INTO statement
INSERT INTO [DataforAnalysis].[dbo].DataML_Test
SELECT
    [Date],
    [Time],
    [Barcode_base],
    [Barcode],
    [Barcode_rotor],
    [Datum_probe],
    [Max_force],
    [FlyHeight],
    [Parallelism],
    [Pivot_Height],
    [Projection1],
    [Ramp_Pivot],
    [Ramp_to_Datum],
    [Flange-Ramp_pad],
    [Set_Dim],
    [Set_Dim_A],
    [Set_Dim_B],
    [Set_Dim_C],
    [Ke_0_peak_avg],
    [Bemf_balance],
    [brg_drag],
    [ke_avg],
    [ke_ripple],
    [NRRO_ax_FFT_1],
    [NRRO_probe_A],
    [NRRO_probe_B],
    [NRRO_rad_FFT_1],
    [run_current],
    [RVA],
    [start_torque],
    [TIR_probe_A],
    [TIR_probe_B],
    [R_max_min],
    [R1_UV],
    [R2_UW],
    [R3_VW],
    [Axial_play_data],
    [Oil_top_data],
    [Oil_bottom_data],
    [Model],
    [Line]
FROM cte
WHERE RowNum = 1 AND NOT EXISTS (
    SELECT 1
    FROM [DataforAnalysis].[dbo].DataML_Test AS Target
    WHERE Target.[Barcode_motor] = cte.[Barcode]  -- Adjust this column name based on your actual schema
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
