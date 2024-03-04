from flask import Flask, jsonify
import json
import seaborn as sns
import numpy as np
import base64
import datetime
from flask import send_file, Flask, jsonify, request
from flask_cors import CORS
import pyodbc
import math
import matplotlib.pyplot as plt
import pandas as pd
import pymssql
import matplotlib
matplotlib.use('Agg')
from imblearn.over_sampling import SMOTE
from collections import Counter

from Database import create_sql_connection
from Database import create_sql_Component_Master

import pandas as pd  # Import pandas at the beginning of your script
from email.mime.text import MIMEText
import smtplib
import requests
from datetime import datetime, timedelta

# pip install openpyxl
from openpyxl import Workbook

app = Flask(__name__)
cors = CORS(app)


def fetch_data():
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = """
    SELECT [Line_IP] + ' : ' + [This_Tactime].Model as Line,
           CAST((60 * COUNT(DISTINCT DATEPART(MINUTE, [Time]))) / [Tactime] AS INT) as Target,
           DATEPART(HOUR, [Time]) as Hr,
           'Target' as Process,
           [Design]
    FROM [Setlot].[dbo].[Master_Setlot]
         JOIN [Setlot].[dbo].[This_Tactime] ON [Line_IP] = [This_Tactime].Line
    WHERE [Time] BETWEEN 
          CASE WHEN DATEPART(hour, getdate()) >= 7 THEN FORMAT(getdate(), 'yyyy-MM-dd') + ' 07:00:00' 
          ELSE DATEADD(day, -1, FORMAT(getdate(), 'yyyy-MM-dd')) + ' 06:59:59' END
          AND 
          CASE WHEN DATEPART(hour, getdate()) >= 7 THEN DATEADD(day, 1, FORMAT(getdate(), 'yyyy-MM-dd')) + ' 07:00:00'
          ELSE FORMAT(getdate(), 'yyyy-MM-dd') + ' 06:59:59' END
    GROUP BY [Line_IP] + ' : ' + [This_Tactime].Model, DATEPART(HOUR, [Time]), [Tactime], [Design];
    """
    
    cursor.execute(query_template)
    
    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Line', 'Target', 'Hr', 'Process', 'Design'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    data_1 = pd.DataFrame(rows)

    return data_1


def Accum_Target():
    df = fetch_data()
    df.sort_values(['Line', 'Design', 'Hr'], inplace=True)

# print the DataFrame after sorting
    print("\nAfter Sorting:")
    print(df)

# Use groupby and cumsum to calculate cumulative sum within each partition
    df['Accum_Target'] = df.groupby(['Line', 'Design'])['Target'].cumsum()

# print the DataFrame after calculating cumulative sum
    print("\nAfter Cumulative Sum:")
    print(df)

# Add 'Process' column
    df['Process'] = 'Accum_Target'

# Map the hours for sorting
    hr_mapping = {
    '07': 1, '08': 2, '09': 3, '10': 4, '11': 5, '12': 6,
    '13': 7, '14': 8, '15': 9, '16': 10, '17': 11, '18': 12,
    '19': 13, '20': 14, '21': 15, '22': 16, '23': 17, '24': 18,
    '00': 19, '01': 20, '02': 21, '03': 22, '04': 23, '05': 24, '06': 25
}

# Map the hours for sorting
    df['Hr_Map'] = df['Hr'].map(hr_mapping)

# print the DataFrame before sorting
    print("Before Sorting:")
    print(df)

# Sort the DataFrame by 'Line', 'Design', and 'Hr_Map'
    df.sort_values(['Line', 'Design', 'Hr_Map'], inplace=True)

# print the DataFrame after sorting
    print("\nAfter Sorting:")
    print(df)

# Drop the temporary 'Hr_Map' column
    df.drop('Hr_Map', axis=1, inplace=True)

# print the DataFrame after dropping 'Hr_Map'
    print("\nAfter Dropping 'Hr_Map':")
    print(df)

# Reorder the columns
    df = df[['Line', 'Accum_Target', 'Hr', 'Process', 'Design']]

# print the final DataFrame
    print("\nFinal DataFrame:")
    print(df)

    return df


def fetch_data_Output():
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = """
    	 select [Line_IP] + ' : ' + [This_Tactime].Model as Line
  , count(Barcode) as [Output]
  ,DATEPART(HOUR,  [Time]) as [Hour]
  ,'.Output' as [Process],[Design]
  FROM [Setlot].[dbo].[Master_Setlot] join [Setlot].[dbo].[This_Tactime] on [Line_IP] = [This_Tactime].Line
  where [Time] between case when DATEPART(hour, getdate()) >= 7 then format(getdate(),'yyyy-MM-dd')  + ' 07:00:00' 
  else DATEADD(day,-1,format(getdate(),'yyyy-MM-dd') ) + ' 06:59:59' end
  and case when DATEPART(hour, getdate()) >= 7 then DATEADD(day,1,format(getdate(),'yyyy-MM-dd') ) + ' 07:00:00'
  else format(getdate(),'yyyy-MM-dd')  + ' 06:59:59' end
  group by [Line_IP] , [This_Tactime].Model,DATEPART(HOUR,  [Time]) ,[Design];
    """
    
    cursor.execute(query_template)
    
    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Line', '.Output', 'Hr', 'Process', 'Design'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    Output = pd.DataFrame(rows)

    return Output


def Output():
    df = fetch_data_Output()
    df.sort_values(['Line', 'Design', 'Hr'], inplace=True)

# print the DataFrame after sorting
    print("\nAfter Sorting:")
    print(df)

# Use groupby and cumsum to calculate cumulative sum within each partition
    df['Accum_Output'] = df.groupby(['Line', 'Design'])['.Output'].cumsum()

# print the DataFrame after calculating cumulative sum
    print("\nAfter Cumulative Sum:")
    print(df)

# Add 'Process' column
    df['Process'] = 'Output'

# Map the hours for sorting
    hr_mapping = {
    '07': 1, '08': 2, '09': 3, '10': 4, '11': 5, '12': 6,
    '13': 7, '14': 8, '15': 9, '16': 10, '17': 11, '18': 12,
    '19': 13, '20': 14, '21': 15, '22': 16, '23': 17, '24': 18,
    '00': 19, '01': 20, '02': 21, '03': 22, '04': 23, '05': 24, '06': 25
}

# Map the hours for sorting
    df['Hr_Map'] = df['Hr'].map(hr_mapping)

# print the DataFrame before sorting
    print("Before Sorting:")
    print(df)

# Sort the DataFrame by 'Line', 'Design', and 'Hr_Map'
    df.sort_values(['Line', 'Design', 'Hr_Map'], inplace=True)

# print the DataFrame after sorting
    print("\nAfter Sorting:")
    print(df)

# Drop the temporary 'Hr_Map' column
    df.drop('Hr_Map', axis=1, inplace=True)

# print the DataFrame after dropping 'Hr_Map'
    print("\nAfter Dropping 'Hr_Map':")
    print(df)

# Reorder the columns
    df = df[['Line', 'Accum_Output', 'Hr', 'Process', 'Design']]

# print the final DataFrame
    print("\nFinal DataFrame:")
    print(df)

    return df



def fetch_data_sumNG():
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = """
    select [Compare_NG_Process].Line + ' : ' + [This_Tactime].Model as Line,sum([First_NG]) as [Qty],[Hour],[Design]
  FROM [Oneday_ReadtimeData].[dbo].[Compare_NG_Process] join [Setlot].[dbo].[This_Tactime] on [Compare_NG_Process].Line = [This_Tactime].Line
   where MfgDate = case when DATEPART(hour, getdate()) >= 0 and DATEPART(hour, getdate()) <= 6 then format(getdate()-1,'yyyy-MM-dd')
  else format(getdate(),'yyyy-MM-dd') end  and [Compare_NG_Process].Line != ''
   and [Compare_NG_Process].Line in (select distinct [Line_IP]  from [Setlot].[dbo].[Master_Setlot]
   where [Time] between case when DATEPART(hour, getdate()) >= 7 then format(getdate(),'yyyy-MM-dd')  + ' 07:00:00' 
  else DATEADD(day,-1,format(getdate(),'yyyy-MM-dd') ) + ' 06:59:59' end
  and case when DATEPART(hour, getdate()) >= 7 then DATEADD(day,1,format(getdate(),'yyyy-MM-dd') ) + ' 07:00:00'
  else format(getdate(),'yyyy-MM-dd')  + ' 06:59:59' end)
   and Process != 'Camera Diverter'  
   --and [Compare_NG_Process].Line like '1-6%'
   group by [Compare_NG_Process].Line,Hour,[This_Tactime].Model,[Design]  ;
    """
    
    cursor.execute(query_template)
    
    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Line', 'Qty', 'Hr','Design'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    sumNG = pd.DataFrame(rows)

    return sumNG


def fetch_data_DownTime():
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = """
   SELECT Line_downtime.[Line] + ' : ' + Model as Line
,convert(int,SUBSTRING([Start_time], 1, 2)) as Hr
,sum([Lost_Qty]) as [DT],Design
FROM [Machine DownTime].[dbo].[Line_downtime] join [Setlot].[dbo].[This_Tactime]
on Line_downtime.Line = This_Tactime.Line
where [Timestamp] between case when DATEPART(hour, getdate()) >= 7 then format(getdate(),'yyyy-MM-dd')  + ' 07:00:00' 
  else DATEADD(day,-1,format(getdate(),'yyyy-MM-dd') ) + ' 06:59:59' end
  and case when DATEPART(hour, getdate()) >= 7 then DATEADD(day,1,format(getdate(),'yyyy-MM-dd') ) + ' 07:00:00'
  else format(getdate(),'yyyy-MM-dd')  + ' 06:59:59' end
group by Line_downtime.Line,SUBSTRING([Start_time], 1, 2),Model,Design ;
    """
    cursor.execute(query_template)
    
    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Line', 'Hr', 'DT','Design'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    DownTime = pd.DataFrame(rows)
    DownTime['DT'] = DownTime['DT'].fillna(0).astype(int)
    return DownTime







data_1 = fetch_data()
data_Accum_Target = Accum_Target()
# data.to_excel('Accum_Target.xlsx', index=False)
print("Data:")
print(data_Accum_Target)

data = fetch_data_Output()
print("data",data)

data_Output = Output()
print("data_Output",data_Output)
# data.to_excel('output_data.xlsx', index=False)

data_sumNG = fetch_data_sumNG()
print("fetch_data_sumNG",data_sumNG)

DownTime = fetch_data_DownTime()
print("fetch_data_DownTime",DownTime)


# Join data and data_1 on common columns Line, Hr, and Design
merged_data = pd.merge(data, data_1, on=['Line', 'Hr', 'Design'], how='outer')

# Join with data_Accum_Target on common columns Line, Hr, and Design
merged_data = pd.merge(merged_data, data_Accum_Target, on=['Line', 'Hr', 'Design'], how='outer')

# Join with data_Output on common columns Line, Hr, and Design
merged_data = pd.merge(merged_data, data_Output, on=['Line', 'Hr', 'Design'], how='outer')

# Join with data_sumNG on common columns Line, Hr, and Design
merged_data = pd.merge(merged_data, data_sumNG, on=['Line', 'Hr', 'Design'], how='outer')

# Join with DownTime on common columns Line, Hr, and Design
merged_data = pd.merge(merged_data, DownTime, on=['Line', 'Hr', 'Design'], how='outer')

merged_data['diff'] = merged_data['Target'] - merged_data['.Output']
# Fill NaN values with 0
merged_data = merged_data.fillna(0)
print(merged_data)

# Print the final merged data
print(merged_data[['Line', '.Output', 'Target', 'diff','Accum_Output', 'Accum_Target', 'Hr', 'Design', 'Qty', 'DT']])

# Rename columns in the merged data
merged_data = merged_data.rename(columns={
    'Line': 'Line',
    '.Output': 'Actual',
    'Target': 'Plan',
    'diff':'diff',
    'Accum_Output': 'Accum.Actual',
    'Accum_Target': 'Accum_Plan',
    'Hr': 'Hour',
    'Qty': 'NG',
    'DT': 'DT'
})

# Selecting the desired columns
selected_columns = ['Line', 'Actual', 'Plan', 'diff', 'Accum.Actual', 'Accum_Plan', 'Hour', 'NG', 'DT', 'Design']

# Filtering rows where Actual + NG + DT > 0
filtered_data = merged_data[merged_data['Actual'] + merged_data['NG'] + merged_data['DT'] > 0]

# Mapping the Hour column values
hour_mapping = {
    '0': '00', '1': '01', '2': '02', '3': '03', '4': '04', '5': '05',
    '6': '06', '7': '*07', '8': '*08', '9': '*09', '10': '*10',
    '11': '*11', '12': '*12', '13': '*13', '14': '*14', '15': '*15',
    '16': '*16', '17': '*17', '18': '*18', '19': '*19', '20': '*20',
    '21': '*21', '22': '*22', '23': '*23'
}


filtered_data['Hour'] = filtered_data['Hour'].astype(str).map(hour_mapping).fillna(filtered_data['Hour'])

# Final selection of columns
result_data = filtered_data[selected_columns]
print(result_data)
result_data.to_excel('result_data.xlsx', index=False)







# def fetch_data_and_insert():
#     conn = create_sql_connection()
#     cursor = conn.cursor()

#     # Query template to fetch data
#     query_template = """
#         -- Your SQL SELECT query here
#         SELECT Line, Actual, Plan, diff, Accum_Actual, Accum_Plan, Hour, NG, DT, Design
#         FROM [YourSourceTable]
#     """

#     cursor.execute(query_template)

#     # Fetch rows one by one and append as dictionaries to the list
#     rows = []
#     for row in cursor:
#         rows.append(dict(zip(['Line', 'Actual', 'Plan', 'diff', 'Accum_Actual', 'Accum_Plan', 'Hour', 'NG', 'DT', 'Design'], row)))

#     # Convert the list of dictionaries to a DataFrame
#     data_1 = pd.DataFrame(rows)

#     # Insert Dataframe into SQL Server
#     for index, row in data_1.iterrows():
#         insert_query = f"""
#             INSERT INTO [DataforAnalysis].[dbo].[YourTableName] 
#             (Line, Actual, Plan, diff, Accum_Actual, Accum_Plan, Hour, NG, DT, Design)
#             VALUES
#             ({row['Line']}, {row['Actual']}, {row['Plan']}, {row['diff']}, {row['Accum_Actual']}, {row['Accum_Plan']}, {row['Hour']}, {row['NG']}, {row['DT']}, {row['Design']})
#         """
#         cursor.execute(insert_query)

#     conn.commit()
#     conn.close()

# # Example usage:
# fetch_data_and_insert()

















# from datetime import datetime

# def send_line_notification(process_name, process_data):
#     # Replace 'YOUR_ACCESS_TOKEN' with your LINE Notify access token
#     access_token = '8gwSkB6cONlIhR3kqI2thsms392Oz3Vfj2P7DEWmyth'
#     url = 'https://notify-api.line.me/api/notify'

#     headers = {'Authorization': f'Bearer {access_token}'}
    
#     current_time = datetime.now()
#     # Customize the message to include relevant information
#     message = f'Time_sent:{current_time}\n'
    
#     for col, value in process_data.iloc[0].items():
#         message += f'{col}:\n{value}\n'
    
#     print("process_data********************************************************", process_data)

#     payload = {'message': message}
#     requests.post(url, headers=headers, data=payload)

# # Example usage
# # Assuming you have a DataFrame called 'result'
# for index, row in result.iterrows():
#     process_name = row['Process']
#     process_data = pd.DataFrame([row])  # Create a DataFrame for the current row
#     send_line_notification(process_name, process_data)






