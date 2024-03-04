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

def fetch_data(model, Line, start, process,arrayMC):
    conn = create_sql_connection()
    cursor = conn.cursor()

    query_template = f"""
                       select cast(DATEPART(hour,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as varchar) as [hr]
              ,case when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) < 120 
              then datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) 
              when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) >= 120 then 0 end as [C/T in sec]
              ,case when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) >= 120 
              then datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) 
              when datediff(SECOND,0,cast((lag([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) over (order by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time] desc) - [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) as time)) < 120 then 0 end as [D/T]
              ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].{process} as [Parameter]
              ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model] as [model]
              ,[TransportData].[dbo].[Master_matchings].LSL as [LSL]
              ,[TransportData].[dbo].[Master_matchings].CL as [CL]
              ,[TransportData].[dbo].[Master_matchings].USL as [USL]
              ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Machine_no] as [MC]
              ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Barcode]
              FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
              INNER JOIN [TransportData].[dbo].[Master_matchings]
              ON [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].Model = [TransportData].[dbo].[Master_matchings].Model
              where CONVERT(DATE,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Time]) = ?
              and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model] = ?
              and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Line] = ?
              and [TransportData].[dbo].[Master_matchings].[Parameter] = ?
              and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Machine_no] = ?
              and [TransportData].[dbo].[Master_matchings].[createdAt] = (select max([TransportData].[dbo].[Master_matchings].[createdAt]) from [TransportData].[dbo].[Master_matchings])
             
    """
    datasets = pd.read_sql(query_template, conn, params=(start, model, Line, process,arrayMC))
    
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
    print(control_specs_1)

    
    

    
    hr = datasets['hr']     #x1
    DT_INSEC = datasets['C/T in sec']   #X2
    DT = datasets['D/T']    #x3
    Parameter = datasets['Parameter']   #x4
    model = datasets['model']   #x5
    LSL = datasets['LSL']   #x6
    CL = datasets['CL']   #x7
    USL = datasets['USL']   #x8
    Machine = datasets['MC']   #x9
    Barcode = datasets['Barcode']   #x10
    LCL = control_specs_1['LCL']   #x10
    UCL = control_specs_1['UCL']   #x10
    
    LCL_VALUE = control_specs_1['LCL']   #x10
    UCL_VALUE = control_specs_1['UCL']   #x10
  
# Multiply by 10
    LCL = float(LCL_VALUE)
    UCL = float(UCL_VALUE)
    
    new_df = pd.DataFrame({
    'hr': hr, #x1
    'C/T in sec': DT_INSEC,  #x2
    'D/T': DT,  #x3
    'Parameter': Parameter,  #x4
    'model': model,  #x5
    'LSL': LSL,  #x6
    'CL': CL,   #x7
    'USL': USL, #x8
    'Machine': Machine, #x9
    'Barcode': Barcode, #x10
    'LCL': LCL, #x10
    'UCL': UCL, #x10

    })
    # Set 'LCL' and 'UCL' values for all rows in new_df
    new_df['LCL'] = LCL
    new_df['UCL'] = UCL


   
    print("Columns in new_df:", new_df.columns)


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
    LCL=('LCL', 'first'),
    UCL=('UCL', 'first'),
    
 
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
    selected_columns = ['hr', 'Cycle_time_sec', 'Down_time_min', 'AVG', 'mean', 'STD', 'Parameter', 'LSL', 'USL','yield_percentage','model','CL','Machine','LCL','UCL']

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
    selected_df = selected_df.round(5)
    





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
        'LCL':selected_df['LCL'],
        'UCL':selected_df['UCL'],
    }
    selected_df = pd.DataFrame(data)
    selected_df['Time'] = pd.to_datetime(selected_df['Time'].astype(str) + ':00').dt.strftime('%H:%M')
    selected_df = selected_df.sort_values(by='Time')

    # print(selected_df)
    import seaborn as sns
    import matplotlib.pyplot as plt

# Create a figure and axis
    plt.figure(figsize=(10, 4))
    
# Plot the lines with different styles, markers, and colors
    sns.lineplot(x='Time', y='USL', data=selected_df, label='USL', linestyle='--', marker='o', color='red')
    sns.lineplot(x='Time', y='UCL', data=selected_df, label='UCL', linestyle=':', marker='v', color='orange')
    sns.lineplot(x='Time', y='CL', data=selected_df, label='CL', linestyle='-.', marker='^', color='green')
    sns.lineplot(x='Time', y='LCL', data=selected_df, label='LCL', linestyle=':', marker='v', color='orange')
    sns.lineplot(x='Time', y='LSL', data=selected_df, label='LSL', linestyle='--', marker='o', color='red')
    sns.lineplot(x='Time', y='AVG', data=selected_df, label=data['Machine'][0], linestyle='-', marker='o', color='blue')

# Set labels and title
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.title(f'SPC {model[0]}')

# Show legend
    plt.legend()
# Show the plot
    plt.show()
  

    return datasets

def create_chart_data(selected_df):
    # Extract relevant columns from the DataFrame
    time = selected_df['Time']
    lcl = selected_df['LCL']
    ucl = selected_df['UCL']
    lcl_std = selected_df['LCL_STD']
    ucl_std = selected_df['UCL_STD']
    cl = selected_df['CL']
    cl_std = selected_df['CL_STD']

    # Create a dictionary for each series
    series_lcl = {'name': 'LCL', 'data': lcl.to_list()}
    series_ucl = {'name': 'UCL', 'data': ucl.to_list()}
    series_lcl_std = {'name': 'LCL_STD', 'data': lcl_std.to_list()}
    series_ucl_std = {'name': 'UCL_STD', 'data': ucl_std.to_list()}
    series_cl = {'name': 'CL', 'data': cl.to_list()}
    series_cl_std = {'name': 'CL_STD', 'data': cl_std.to_list()}

    # Create a dictionary to represent the entire chart data
    chart_data = {
        'categories': time.to_list(),
        'series': [series_lcl, series_ucl, series_lcl_std, series_ucl_std, series_cl, series_cl_std]
    }

    return chart_data





def input(model, Line, process, start, arrayMC):
    # Create an empty list to store data for each machine code
    data_list = []

    # Iterate over each machine code in the arrayMC
    for machine_code in arrayMC:
        data = fetch_data(model, Line, start, process, machine_code)
        
        # Append the data for each machine code to the list
        data_list.append(data)
        
        print(f"Data for Machine Code {machine_code}:")
   

    # Concatenate the data for all machine codes into a single DataFrame
    result_df = pd.concat(data_list, ignore_index=True)

    print("Concatenated Data for All Machine Codes:")
    print(result_df)
        
# Example usage
model = 'LONGSP'
Line = '3-6'
process = 'Projection1'
start = '2024-01-08'
arrayMC = ['FB-028-053', 'FB-028-045']

input(model, Line, process, start, arrayMC)
