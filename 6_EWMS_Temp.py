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
    INSERT INTO [DataforAnalysis].[dbo].[EWMS]
(
    [Machine_no], [Barcode], [Date], [Time], [Master_Judgment], [Ke_0_peak_avg], [ke_avg], [ke_min], [ke_ripple],
    [peak_variation], [run_current], [I_ripple], [start_torque], [TIR_probe_A], [NRRO_probe_A], [TIR_probe_B],
    [NRRO_probe_B], [RVA], [waviness], [NRRO_ax_FFT_1], [NRRO_rad_FFT_1], [NRRO_rad_FFT_2], [NRRO_rad_FFT_3],
    [NRRO_rad_FFT_4], [NRRO_rad_FFT_5], [NRRO_rad_FFT_6], [NRRO_rad_FFT_7], [NRRO_rad_FFT_8], [NRRO_rad_FFT_9],
    [NRRO_rad_FFT_10], [TIRax_DFT_1], [TIRax_DFT_2], [TIRax_DFT_3], [TIRax_DFT_4], [TIRax_DFT_5], [TIRax_DFT_6],
    [TIRax_DFT_7], [TIRax_DFT_8], [TIRax_DFT_9], [TIRax_DFT_10], [TIRax_DFT_11], [TIRax_DFT_12], [TIRax_DFT_13],
    [TIRax_DFT_14], [TIRax_DFT_15], [TIRax_DFT_16], [TIRax_DFT_17], [TIRax_DFT_18], [TIRax_DFT_19], [TIRax_DFT_20],
    [TIRax_DFT_21], [TIRax_DFT_22], [TIRax_DFT_23], [TIRax_DFT_24], [R1], [R2], [R3], [L1], [L12], [L13], [Flux_max_max],
    [Flux_min_min], [brg_drag], [Bemf_balance], [Temperature], [Six_Sigma_NRRO_A], [Six_Sigma_NRRO_B], [ComAngleDeviation],
    [SpinUpTime], [TIR_Mark_Ang_A], [TIR_Mark_Ang_B], [Meas_Speed], [Operator_Name], [run_current_comp], [I_ripple_comp],
    [brg_drag_comp], [pwrHfwA], [pwrHfwB], [Nrro_Avg_A], [Nrro_Avg_B], [ke_abs_max], [ke_peak_min_phase_0],
    [ke_peak_min_phase_1], [ke_peak_min_phase_2], [ke_peak_max_phase_0], [ke_peak_max_phase_1], [ke_peak_max_phase_2],
    [ke_peak_avg_phase_0], [ke_peak_avg_phase_1], [ke_peak_avg_phase_2], [ke_peak_delta_phase_0], [ke_peak_delta_phase_1],
    [ke_peak_delta_phase_2], [ke_phase_To_Phase_Avg_Delta], [Model], [Line], [RVA_2], [2ndYield], [NG criteria], [IP],
    [MfgDate]
)
SELECT  
    [Machine_no], [Barcode], [Date], [Time], [Master_Judgment], [Ke_0_peak_avg], [ke_avg], [ke_min], [ke_ripple],
    [peak_variation], [run_current], [I_ripple], [start_torque], [TIR_probe_A], [NRRO_probe_A], [TIR_probe_B],
    [NRRO_probe_B], [RVA], [waviness], [NRRO_ax_FFT_1], [NRRO_rad_FFT_1], [NRRO_rad_FFT_2], [NRRO_rad_FFT_3],
    [NRRO_rad_FFT_4], [NRRO_rad_FFT_5], [NRRO_rad_FFT_6], [NRRO_rad_FFT_7], [NRRO_rad_FFT_8], [NRRO_rad_FFT_9],
    [NRRO_rad_FFT_10], [TIRax_DFT_1], [TIRax_DFT_2], [TIRax_DFT_3], [TIRax_DFT_4], [TIRax_DFT_5], [TIRax_DFT_6],
    [TIRax_DFT_7], [TIRax_DFT_8], [TIRax_DFT_9], [TIRax_DFT_10], [TIRax_DFT_11], [TIRax_DFT_12], [TIRax_DFT_13],
    [TIRax_DFT_14], [TIRax_DFT_15], [TIRax_DFT_16], [TIRax_DFT_17], [TIRax_DFT_18], [TIRax_DFT_19], [TIRax_DFT_20],
    [TIRax_DFT_21], [TIRax_DFT_22], [TIRax_DFT_23], [TIRax_DFT_24], [R1], [R2], [R3], [L1], [L12], [L13], [Flux_max_max],
    [Flux_min_min], [brg_drag], [Bemf_balance], [Temperature], [Six_Sigma_NRRO_A], [Six_Sigma_NRRO_B], [ComAngleDeviation],
    [SpinUpTime], [TIR_Mark_Ang_A], [TIR_Mark_Ang_B], [Meas_Speed], [Operator_Name], [run_current_comp], [I_ripple_comp],
    [brg_drag_comp], [pwrHfwA], [pwrHfwB], [Nrro_Avg_A], [Nrro_Avg_B], [ke_abs_max], [ke_peak_min_phase_0],
    [ke_peak_min_phase_1], [ke_peak_min_phase_2], [ke_peak_max_phase_0], [ke_peak_max_phase_1], [ke_peak_max_phase_2],
    [ke_peak_avg_phase_0], [ke_peak_avg_phase_1], [ke_peak_avg_phase_2], [ke_peak_delta_phase_0], [ke_peak_delta_phase_1],
    [ke_peak_delta_phase_2], [ke_phase_To_Phase_Avg_Delta], [Model], [Line], [RVA_2], [2ndYield], [NG criteria], [IP],
    [MfgDate]
FROM [Temp_TransportData].[dbo].[EWMS] AS EWMS
WHERE Date > DATEADD(DAY, {Date_BT}, GETDATE()) and NOT EXISTS (
    SELECT 1
    FROM [DataforAnalysis].[dbo].[EWMS] AS destination
    WHERE
        destination.[Barcode] = EWMS.[Barcode]
        AND CONVERT(datetime, destination.[Time]) = EWMS.[Time]
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
