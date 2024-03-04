import pyodbc
from Date_All_process import Date_between
import pandas as pd
import numpy as np

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

def fetch_data(model, Line, start, process ,MC_NAME):
    conn = create_sql_connection()
    cursor = conn.cursor()
    if MC_NAME == 'Dimension_WR':
            query_template = f"""
         SELECT [Time]
              ,cast(DATEPART(hour,[DataforAnalysis].[dbo].[Dimension_WR].[Time]) as varchar) as [hr]
              ,case when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dimension_WR].[Time]) over (order by [DataforAnalysis].[dbo].[Dimension_WR].[Time] desc) - [DataforAnalysis].[dbo].[Dimension_WR].[Time]) as time)) < 120 
              then datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dimension_WR].[Time]) over (order by [DataforAnalysis].[dbo].[Dimension_WR].[Time] desc) - [DataforAnalysis].[dbo].[Dimension_WR].[Time]) as time)) 
              when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dimension_WR].[Time]) over (order by [DataforAnalysis].[dbo].[Dimension_WR].[Time] desc) - [DataforAnalysis].[dbo].[Dimension_WR].[Time]) as time)) >= 120 then 0 end as [C/T in sec]
              ,case when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dimension_WR].[Time]) over (order by [DataforAnalysis].[dbo].[Dimension_WR].[Time] desc) - [DataforAnalysis].[dbo].[Dimension_WR].[Time]) as time)) >= 120 
              then datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dimension_WR].[Time]) over (order by [DataforAnalysis].[dbo].[Dimension_WR].[Time] desc) - [DataforAnalysis].[dbo].[Dimension_WR].[Time]) as time)) 
              when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dimension_WR].[Time]) over (order by [DataforAnalysis].[dbo].[Dimension_WR].[Time] desc) - [DataforAnalysis].[dbo].[Dimension_WR].[Time]) as time)) < 120 then 0 end as [D/T]
              ,[DataforAnalysis].[dbo].[Dimension_WR].{process} as [Parameter]
              ,[DataforAnalysis].[dbo].[Dimension_WR].[Model] as [model]
              ,[Component_Master].[dbo].[Master_matchings].LSL as [LSL]
              ,[Component_Master].[dbo].[Master_matchings].CL as [CL]
              ,[Component_Master].[dbo].[Master_matchings].USL as [USL]
              ,Machine_no as [AVG]
              ,[DataforAnalysis].[dbo].[Dimension_WR].Part_ID as Barcode
              FROM [DataforAnalysis].[dbo].[Dimension_WR]
              INNER JOIN [Component_Master].[dbo].[Master_matchings]
              ON [DataforAnalysis].[dbo].[Dimension_WR].Model = [Component_Master].[dbo].[Master_matchings].Model
              WHERE 
                  CONVERT(DATE,[DataforAnalysis].[dbo].[Dimension_WR].[Time]) = ?
                  AND [DataforAnalysis].[dbo].[Dimension_WR].[Model] = ?
                  AND [DataforAnalysis].[dbo].[Dimension_WR].[Line] = ?
                  AND [Component_Master].[dbo].[Master_matchings].[Parameter] = ?
                  AND [Component_Master].[dbo].[Master_matchings].[createdAt] = (
                      SELECT MAX([Component_Master].[dbo].[Master_matchings].[createdAt]) 
                      FROM [Component_Master].[dbo].[Master_matchings]
                      
                  )"""
    elif  MC_NAME == 'Dynamic_Parallelism_Tester':
        query_template = f"""
        SELECT [Time]
              ,cast(DATEPART(hour,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as varchar) as [hr]
              ,case when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) < 120 
              then datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) 
              when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) >= 120 then 0 end as [C/T in sec]
              ,case when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) >= 120 
              then datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) 
              when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) < 120 then 0 end as [D/T]
              ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].{process} as [Parameter]
              ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model] as [model]
              ,[Component_Master].[dbo].[Master_matchings].LSL as [LSL]
              ,[Component_Master].[dbo].[Master_matchings].CL as [CL]
              ,[Component_Master].[dbo].[Master_matchings].USL as [USL]
              ,Machine_no as [AVG]
              ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].Barcode
              FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
              INNER JOIN [Component_Master].[dbo].[Master_matchings]
              ON [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].Model = [Component_Master].[dbo].[Master_matchings].Model
              WHERE 
                  CONVERT(DATE,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) = ?
                  AND [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model] = ?
                  AND [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Line] = ?
                  AND [Component_Master].[dbo].[Master_matchings].[Parameter] = ?
                  AND [Component_Master].[dbo].[Master_matchings].[createdAt] = (
                      SELECT MAX([Component_Master].[dbo].[Master_matchings].[createdAt]) 
                      FROM [Component_Master].[dbo].[Master_matchings])
    """
    elif  MC_NAME == 'EWMS':
        query_template = f"""
        SELECT [Time]
              ,cast(DATEPART(hour,[DataforAnalysis].[dbo].[EWMS].[Time]) as varchar) as [hr]
              ,case when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[EWMS].[Time]) over (order by [DataforAnalysis].[dbo].[EWMS].[Time] desc) - [DataforAnalysis].[dbo].[EWMS].[Time]) as time)) < 120 
              then datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[EWMS].[Time]) over (order by [DataforAnalysis].[dbo].[EWMS].[Time] desc) - [DataforAnalysis].[dbo].[EWMS].[Time]) as time)) 
              when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[EWMS].[Time]) over (order by [DataforAnalysis].[dbo].[EWMS].[Time] desc) - [DataforAnalysis].[dbo].[EWMS].[Time]) as time)) >= 120 then 0 end as [C/T in sec]
              ,case when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[EWMS].[Time]) over (order by [DataforAnalysis].[dbo].[EWMS].[Time] desc) - [DataforAnalysis].[dbo].[EWMS].[Time]) as time)) >= 120 
              then datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[EWMS].[Time]) over (order by [DataforAnalysis].[dbo].[EWMS].[Time] desc) - [DataforAnalysis].[dbo].[EWMS].[Time]) as time)) 
              when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[EWMS].[Time]) over (order by [DataforAnalysis].[dbo].[EWMS].[Time] desc) - [DataforAnalysis].[dbo].[EWMS].[Time]) as time)) < 120 then 0 end as [D/T]
              ,[DataforAnalysis].[dbo].[EWMS].{process} as [Parameter]
              ,[DataforAnalysis].[dbo].[EWMS].[Model] as [model]
              ,[Component_Master].[dbo].[Master_matchings].LSL as [LSL]
              ,[Component_Master].[dbo].[Master_matchings].CL as [CL]
              ,[Component_Master].[dbo].[Master_matchings].USL as [USL]
              ,Machine_no as [AVG]
              ,[DataforAnalysis].[dbo].[EWMS].Barcode
              FROM [DataforAnalysis].[dbo].[EWMS]
              INNER JOIN [Component_Master].[dbo].[Master_matchings]
              ON [DataforAnalysis].[dbo].[EWMS].Model = [Component_Master].[dbo].[Master_matchings].Model
              WHERE 
                  CONVERT(DATE,[DataforAnalysis].[dbo].[EWMS].[Time]) = ?
                  AND [DataforAnalysis].[dbo].[EWMS].[Model] = ?
                  AND [DataforAnalysis].[dbo].[EWMS].[Line] = ?
                  AND [Component_Master].[dbo].[Master_matchings].[Parameter] = ?
                  AND [Component_Master].[dbo].[Master_matchings].[createdAt] = (
                      SELECT MAX([Component_Master].[dbo].[Master_matchings].[createdAt]) 
                      FROM [Component_Master].[dbo].[Master_matchings])
    """
    else:
        raise ValueError(f"Unsupported MC_NAME: {MC_NAME}")
             
    
    datasets = pd.read_sql(query_template, conn, params=(start, model, Line, process))

    control_specs = f"""
    SELECT [LCL], [UCL], [CL], [CL_STD], [LCL_STD], [UCL_STD], [createdAt]
    FROM [TransportData].[dbo].[ControlSpecs]
    WHERE [Model] = '{model}' AND [Parameter] = '{process}' AND [Line] = '{Line}'
    AND [createdAt] = (
        SELECT MAX([createdAt])
        FROM [TransportData].[dbo].[ControlSpecs]
        WHERE [Model] = '{model}' AND [Parameter] = '{process}' AND [Line] = '{Line}'
    )
    GROUP BY [LCL], [UCL], [CL], [CL_STD], [LCL_STD], [UCL_STD], [createdAt]
"""
    control_specs_1 = pd.read_sql(control_specs, conn)
    datafarm = pd.DataFrame(control_specs_1)


    
    hr = datasets['hr']     #x1
    DT_INSEC = datasets['C/T in sec']   #X2
    DT = datasets['D/T']    #x3
    Parameter = datasets['Parameter']   #x4
    model = datasets['model']   #x5
    LSL = datasets['LSL']   #x6
    CL = datasets['CL']   #x7
    USL = datasets['USL']   #x8
    Machine = datasets['AVG']   #x9
    Barcode = datasets['Barcode']   #x10
    UCL = datafarm['UCL']   #x10
    LCL = datafarm['LCL']   #x10
    
    
    Time = pd.DataFrame({'Time': pd.date_range('00:00', '23:00', freq='H').strftime('%H:%M')})
    
    new_df = pd.DataFrame({
    'Time': pd.to_datetime(datasets['Time']),  # แปลงเป็นรูปแบบ datetime
    'hr': hr, #x1
    'C/T in sec': DT_INSEC,  #x2
    'D/T': DT,  #x3
    'Parameter': Parameter,  #x4
    'model': model,  #x5
    'LSL': LSL,  #x6
    'LCL': LCL,  #x6
    'CL': CL,   #x7
    'UCL': UCL, #x8
    'USL': USL, #x8
    'Machine': Machine, #x9
    'Barcode': Barcode #x10
    })
    # print("Columns in new_df:", new_df.columns)
    # print("Unique values in 'LSL' column:", new_df['LSL'].unique())
    # print("Data type of 'LSL' column:", new_df['LSL'].dtype)
    # print(new_df['C/T in sec'])

# x1,x5,x6,x7,x8,x9
    result_grouped = new_df.rename(columns={'LSL': 'LSL_Original', 'CL': 'CL_Original', 'USL': 'USL_Original'}).groupby(['hr', 'LSL_Original', 'CL_Original', 'USL_Original'])

    result = result_grouped.agg(
    Cycle_time_sec=('C/T in sec', lambda x: np.sum(x) / np.count_nonzero(x)),
    Down_time_min=('D/T', lambda x: np.sum(x) / 60),
    AVG=('Parameter', lambda x: np.average(x)),
    mean=('Parameter', lambda x: np.mean(x)),
    STD=('Parameter', lambda x: np.std(x)),

    Parameter=('Parameter', 'first'),
    LSL=('LSL_Original', 'first'),
    CL=('CL_Original', 'first'),
    USL=('USL_Original', 'first'),
    model=('model', 'first'),
    Machine=('Machine', 'first'),
    
 
).reset_index()
    




# Assuming 'Parameter', 'LSL', 'USL', and 'hr' are columns in your DataFrame
    new_df['yield_1'] = np.where((new_df['Parameter'] >= new_df['LSL']) & (new_df['Parameter'] <= new_df['USL']), 1, np.nan)
    new_df['yield_2'] = np.where(((new_df['Parameter'] >= new_df['LSL']) & (new_df['Parameter'] <= new_df['USL'])), 1, np.nan)
    new_df['yield_3'] = np.where((new_df['Parameter'] < new_df['LSL']) | (new_df['Parameter'] > new_df['USL']), 1, np.nan)

# Group by 'hr' and calculate yield metrics for each hour
    grouped_df = new_df.groupby('hr').agg(
    data=('yield_1', 'count'),
    data2=('yield_2', 'count'),
    data3=('yield_3', 'count')

)
# Calculate yield percentage for each hour, handling division by zero
    grouped_df['yield_percentage'] = np.where((grouped_df['data2'] + grouped_df['data3']) != 0,
                                           grouped_df['data'] / (grouped_df['data2'] + grouped_df['data3']) * 100,
                                           np.nan)

    # Assuming 'hr' is a common column between 'result' and 'grouped_df'
    merged_df = pd.merge(result, grouped_df, on='hr', how='inner')

# Display the merged DataFrame
    selected_columns = ['hr', 'Cycle_time_sec', 'Down_time_min', 'AVG', 'mean', 'STD', 'Parameter', 'LSL', 'USL','yield_percentage','model','CL','Machine']

# Select only the desired columns from the merged DataFrame

    selected_df = merged_df[selected_columns].round(2)
    
    result['CPK'] = np.select(
    [
        (result['Parameter'] > result['USL'] - 3 * result['STD']) ,
        (result['Parameter'] < result['LSL'] - 3 * result['STD']) | ((result['Parameter'] > result['USL'] - 3 * result['STD']) & (result['LSL'] == 0)),
        (result['Parameter'] >= result['LSL'] - 3 * result['STD']) & (result['Parameter'] <= result['USL'] - 3 * result['STD'])
    ],
    [
        (result['USL'] - result['AVG']) / (3 * result['STD']),
        (result['AVG'] - result['LSL']) / (3 * result['STD']),
        (result['USL'] - result['AVG']) / (3 * result['STD'])
    ],
    default=np.nan
)
    CPK = result.groupby('hr')['CPK'].mean()

    selected_df['CPK'] = selected_df['hr'].map(CPK)
    selected_df = selected_df.round(2)
    data ={
        'Time': selected_df['hr']+ ':00',
        '%yield':selected_df['yield_percentage'],
        'Cycle_time (sec)':selected_df['Cycle_time_sec'],
        'Cycle_time(sec)':selected_df['Down_time_min'],
        'AVG':selected_df['AVG'],
        'STD':selected_df['STD'],
        'CPK':selected_df['CPK'],
        'model':selected_df['model'],
        'LSL':selected_df['LSL'],
        'CL':selected_df['CL'],
        'USL':selected_df['USL'],
        'Machine':selected_df['Machine'],
    }
    selected_df = pd.DataFrame(data)
    selected_df['Time'] = pd.to_datetime(selected_df['Time'].astype(str) + ':00').dt.strftime('%H:%M')
    
    
    


    print(selected_df)
    import seaborn as sns
    import matplotlib.pyplot as plt

    selected_df = selected_df.sort_values(by='Time')
    plt.figure(figsize=(12, 6))
    lsl_color = 'red'
    cl_color = 'grey'
    usl_color = 'red'
    ucl_color = 'Orange'
    lcl_color = 'Orange'

    datafarm['Time'] = selected_df['Time'] 
    print(datafarm)

    selected_df = pd.merge(selected_df, datafarm[['Time', 'LCL', 'UCL','UCL_STD','LCL_STD']], on='Time', how='left')

    selected_df[['LCL', 'UCL','UCL_STD','LCL_STD']] = selected_df[['LCL', 'UCL','UCL_STD','LCL_STD']].ffill()
    print(selected_df)
# เพิ่มเส้นกราฟ
    sns.lineplot(x='Time', y='USL', data=selected_df, label='USL', color=usl_color ,linestyle='dashed')
    sns.lineplot(x='Time', y='UCL', data=selected_df, label='UCL', color=ucl_color, linestyle='dashed')
    sns.lineplot(x='Time', y='CL', data=selected_df, label='CL', color=cl_color,linestyle='dashed')
    sns.lineplot(x='Time', y='LCL', data=selected_df, label='LCL', color=lcl_color, linestyle='dashed')
    sns.lineplot(x='Time', y='LSL', data=selected_df, label='LSL', color=lsl_color ,linestyle='dashed')
    
    sns.lineplot(x='Time', y='AVG', data=selected_df, hue='Machine', marker='o')

    
    plt.grid(True, linestyle='--', alpha=0.10)
# เพิ่มรายละเอียดแกน X, Y และตั้งชื่อกราฟ
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.title(MC_NAME)
    plt.legend()

# Save the plot as an image (adjust the filename and format as needed)
    plt.savefig('Xbar_SPC.png', bbox_inches='tight')
    return datasets



def input (model,Line,process,start,MC_NAME):
    
    data = fetch_data(model, Line, start, process,MC_NAME)
   
    return data

model = 'LONGSP'
Line = 'B17'
process = 'P1_Stack_1'
start = '2024-01-06'
MC_NAME = 'Dimension_WR'
input(model,Line,process,start,MC_NAME)



# model = 'LONGSP'
# Line = '3-6'
# process = 'Projection1'
# start = '2024-01-06'
# MC_NAME = 'Dynamic_Parallelism_Tester'
# input(model,Line,process,start,MC_NAME)


# model = 'LONGSP'
# Line = '3-6'
# process = 'TIR_probe_A'
# start = '2024-01-06'
# MC_NAME = 'EWMS'
# input(model,Line,process,start,MC_NAME)





