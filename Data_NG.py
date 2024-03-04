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
from itertools import product
app = Flask(__name__)
cors = CORS(app)



# ไม่มี NEST

def fetch_data(processes,line_columns,date_only):
    
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = f"""
   SELECT '{processes}',[Line_no] as [Line],[{processes}].[Machine_no],'',[Barcode],DATEPART(hour, [Time]) as [Hour]
  FROM [Oneday_ReadtimeData].[dbo].[{processes}] join [T1749].[dbo].[IP_Connect]  on  [IP] = [IP_Address]
  where 
    [Time] between '{date_only}' + ' 07:00:00' and DATEADD(day,1,'{date_only}') + ' 06:59:59' and
   [Barcode] not like 'OK%' and 
   [Barcode] not like 'NG%'
  group by [Line_no],[{processes}].[Machine_no],DATEPART(hour, [Time]),[Barcode]
    """
    cursor.execute(query_template)
    #print({processes},query_template)
    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Process', 'Line', 'Machine_no', '{processes}', 'Barcode', 'Hour'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    data_1 = pd.DataFrame(rows)
    
    return data_1

def count_occurrences(processes, line_columns):
    # Create an empty DataFrame to store the results
    result_df = pd.DataFrame()

    # Generate all combinations of processes and line columns
    process_line_combinations = product(processes, line_columns)

    # Iterate through each combination
    for process, line_column in process_line_combinations:
        current_datetime = datetime.now()
        date_only = current_datetime.date()
        data = fetch_data(process, line_column, date_only)

        # Convert 'Hour' to datetime
        data['Hour'] = pd.to_datetime(data['Hour'], format='%H')

        # Count occurrences based on specified columns
        count_result = data.groupby(['Process', 'Line', 'Machine_no', data['Hour'].dt.hour]).size().reset_index(name='input')

        # Append the results to the overall result DataFrame
        result_df = pd.concat([result_df, count_result], ignore_index=True)

    return result_df


# มี MC columns NEST
def fetch_AT_Unit(processes,line_columns,date_only):
    
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = f"""
     SELECT 'ATUnit',[{line_columns}] as Line,[Machine_no],'' as Nest,[Barcode],DATEPART(hour, [Time]) as [Hour]
  FROM [Oneday_ReadtimeData].[dbo].[AT_Unit]
  where 
    [Time] between '{date_only}' + ' 07:00:00' and DATEADD(day,1,'{date_only}') + ' 06:59:59' and
   [Barcode] not like 'OK%' and 
   [Barcode] not like 'NG%'
    """
    cursor.execute(query_template)
    #print({processes},query_template)
    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Process', 'Line', 'Machine_no', '{processes}', 'Barcode', 'Hour'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    data_1 = pd.DataFrame(rows)
    
    return data_1

def count_AT_Unit(processes, line_columns):
    # Create an empty DataFrame to store the results
    result_df = pd.DataFrame()

    # Generate all combinations of processes and line columns
    process_line_combinations = product(processes, line_columns)

    # Iterate through each combination
    for process, line_column in process_line_combinations:
        current_datetime = datetime.now()
        date_only = current_datetime.date()
        data = fetch_AT_Unit(process, line_column, date_only)

        # Convert 'Hour' to datetime
        data['Hour'] = pd.to_datetime(data['Hour'], format='%H')

        # Count occurrences based on specified columns
        count_result = data.groupby(['Process', 'Line', 'Machine_no', data['Hour'].dt.hour]).size().reset_index(name='input')

        # Append the results to the overall result DataFrame
        result_df = pd.concat([result_df, count_result], ignore_index=True)

    return result_df

def fetch_data_Air_leak(processes, line_columns,date_only):
    conn = create_sql_connection()
    cursor = conn.cursor()
  

    query_template = f"""
     SELECT 'Airleak' as Process,[Line_IP] as [Line],[Machine_no],[Barcode],DATEPART(hour, [Time]) as [Hour] ,[Nest]
  FROM [Oneday_ReadtimeData].[dbo].[Air_leak]
  where 
    [Time] between '{date_only}' + ' 07:00:00' and DATEADD(day,1,'{date_only}') + ' 06:59:59' and
   [Barcode] not like 'OK%' and 
   [Barcode] not like 'NG%'
  group by [Line_IP],[Machine_no],DATEPART(hour, [Time]),[Nest],[Barcode]

    """
    cursor.execute(query_template)
    #print(query_template)

    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Process', 'Line', 'Machine_no','Barcode', 'Hour', 'Nest'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    data_1 = pd.DataFrame(rows)

    return data_1

def count_Air_leak(processes, line_columns):
    # Create an empty DataFrame to store the results
    result_df = pd.DataFrame()

    # Iterate through each process and line column
    for process in processes:
        for line_column in line_columns:

            current_datetime = datetime.now()
            date_only = current_datetime.date()
            data = fetch_data_Air_leak(process, line_column,date_only)


            # Convert 'Hour' to datetime
            data['Hour'] = pd.to_datetime(data['Hour'], format='%H')

            # Count occurrences based on specified columns
            count_result = data.groupby(['Process', 'Line', 'Machine_no', 'Nest', data['Hour'].dt.hour]).size().reset_index(name='input')

            # Append the results to the overall result DataFrame
            result_df = result_df.append(count_result, ignore_index=True)

    return result_df


def fetch_data_He_Leakk(processes, line_columns, date_only):
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = f"""
      SELECT 'Helium',[Line_no] as [Line],[He_Leakk].[Machine_no],[Head_Name] as Nest,[Barcode],DATEPART(hour, [Time]) as [Hour]
  FROM [Oneday_ReadtimeData].[dbo].[He_Leakk] join [T1749].[dbo].[IP_Connect] on  [He_Leakk].[Machine_no] = [Remark]
  where 
    [Time] between '{date_only}' + ' 07:00:00' and DATEADD(day,1,'{date_only}') + ' 06:59:59' and
   [Barcode] not like 'OK%' and 
   [Barcode] not like 'NG%'
  group by [Line_no],[He_Leakk].[Machine_no],[Head_Name],DATEPART(hour, [Time]),Barcode
    """
    cursor.execute(query_template)
    #print(query_template)
    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Process', 'Line', 'Machine_no', 'Nest', 'Barcode', 'Hour'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    data_1 = pd.DataFrame(rows)

    return data_1

def count_He_Leakk(processes, line_columns):
    # Create an empty DataFrame to store the results
    result_df = pd.DataFrame()

    # Iterate through each process and line column
    for process in processes:
        for line_column in line_columns:
            current_datetime = datetime.now()
            date_only = current_datetime.date()
            data = fetch_data_He_Leakk(process, line_column,date_only)


            # Convert 'Hour' to datetime
            data['Hour'] = pd.to_datetime(data['Hour'], format='%H')

            # Count occurrences based on specified columns
            count_result = data.groupby(['Process', 'Line', 'Machine_no', 'Nest', data['Hour'].dt.hour]).size().reset_index(name='input')

            # Append the results to the overall result DataFrame
            result_df = result_df.append(count_result, ignore_index=True)

    return result_df



def fetch_NO_MC_AND_NEST(processes,line_columns,date_only):
    
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = f"""
    SELECT '{processes}' as Process, [{line_columns}] as Line, '' as Machine_no, '' as Nest, [Barcode], DATEPART(hour, [Time]) as Hour
    FROM [Oneday_ReadtimeData].[dbo].[{processes}]
    WHERE [Time] BETWEEN '{date_only}' + ' 07:00:00' AND DATEADD(day, 1, '{date_only}') + ' 06:59:59'
    AND [Barcode] NOT LIKE 'OK%' AND [Barcode] NOT LIKE 'NG%'
    GROUP BY [{line_columns}], DATEPART(hour, [Time]), [Barcode];
    """
    cursor.execute(query_template)
    print(query_template)
    #print({processes},query_template)
    # Fetch rows one by one and append as dictionaries to the list
    rows = []
    for row in cursor:
        rows.append(dict(zip(['Process', 'Line','Machine_no','Nest','Barcode', 'Hour'], row)))

    conn.close()

    # Convert the list of dictionaries to a DataFrame
    data_1 = pd.DataFrame(rows)
    
    return data_1

def count_NO_MC_AND_NEST(processes, line_columns):
    # Create an empty DataFrame to store the results
    result_df = pd.DataFrame()

    # Generate all combinations of processes and line columns
    process_line_combinations = product(processes, line_columns)

    # Iterate through each combination
    for process, line_column in process_line_combinations:
        current_datetime = datetime.now()
        date_only = current_datetime.date()
        data = fetch_NO_MC_AND_NEST(process, line_column, date_only)

        # Convert 'Hour' to datetime
        data['Hour'] = pd.to_datetime(data['Hour'], format='%H')

        # Count occurrences based on specified columns
        count_result = data.groupby(['Process', 'Line', data['Hour'].dt.hour]).size().reset_index(name='input')

        # Append the results to the overall result DataFrame
        result_df = pd.concat([result_df, count_result], ignore_index=True)

    return result_df



def merge_data():
    processes_ewms = ['EWMS']
    line_columns_ewms = ['Line_no']
    data_ewms = count_occurrences(processes_ewms, line_columns_ewms)

    processes_at_unit = ['AT_Unit']
    line_columns_at_unit = ['Line_IP']
    data_at_unit = count_AT_Unit(processes_at_unit, line_columns_at_unit)

    processes_at_PCB_Height = ['PCB_Height']
    line_columns_PCB_Height = ['Line_no']
    PCB_Height = count_occurrences(processes_at_PCB_Height, line_columns_PCB_Height)

    processes_at_Air_leak = ['Air_leak']
    line_columns_Air_leak = ['Line_IP']
    Air_leak = count_Air_leak(processes_at_Air_leak, line_columns_Air_leak)

    processes_at_He_Leakk = ['He_Leakk']
    line_columns_He_Leakk = ['Line_IP']
    He_Leakk = count_He_Leakk(processes_at_He_Leakk, line_columns_He_Leakk)

    processes_at_DynamicPara = ['Dynamic_Parallelism_Tester']
    line_columns_DynamicPara = ['Line_no']
    DynamicPara = count_occurrences(processes_at_DynamicPara, line_columns_DynamicPara)

    processes_at_Hipot = ['Hipot']
    line_columns_Hipot = ['Line_no']
    Hipot = count_occurrences(processes_at_Hipot, line_columns_Hipot)

    processes_at_Imbalance = ['Imbalance_Static']
    line_columns_Imbalance = ['Line_no']
    Imbalance = count_occurrences(processes_at_Imbalance, line_columns_Imbalance)

    processes_at_G_meter = ['G_meter']
    line_columns_G_meter = ['Line_no']
    G_meter = count_occurrences(processes_at_G_meter, line_columns_G_meter)

    processes_at_Camera_Motor = ['VMI_Motor']
    line_columns_Camera_Motor = ['Line_IP']
    Camera_Motor = count_NO_MC_AND_NEST(processes_at_Camera_Motor, line_columns_Camera_Motor)

    processes_at_Camera_Ramp = ['VMI_Ramp']
    line_columns_Camera_Ramp = ['Line_IP']
    Camera_Ramp = count_NO_MC_AND_NEST(processes_at_Camera_Ramp, line_columns_Camera_Ramp)

    processes_at_Camera_Diverter = ['VMI_Ramp']
    line_columns_Camera_Diverter = ['Line_IP']
    Camera_Diverter = count_NO_MC_AND_NEST(processes_at_Camera_Diverter, line_columns_Camera_Diverter)

    merged_data = pd.concat([data_ewms, data_at_unit, PCB_Height, Air_leak, He_Leakk, DynamicPara, Hipot, Imbalance, G_meter,
                            Camera_Motor, Camera_Ramp, Camera_Diverter], ignore_index=True)

    return merged_data

# Call the function
result = merge_data()
print(result)





