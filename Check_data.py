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

app = Flask(__name__)
cors = CORS(app)



def send_notification(process_name):
    # Replace these values with your email configuration
    sender_email = 'ratikran@gmail.com'
    receiver_email = 'recipient_email@gmail.com'
    password = 'your_email_password'

    subject = f'No results found for {process_name}'
    body = f'The query for process {process_name} did not return any results.'

    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def fetch_data():
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = """
        
SELECT'[DataforAnalysis].[dbo].[Dimension_WR]'as Process
	 ,count([Part_ID]) as [Barcode]
	 ,MAX([Date]) as LatestDate

      
  FROM [DataforAnalysis].[dbo].[Dimension_WR]
  WHERE 
    [Date] = (SELECT MAX([Date]) FROM [DataforAnalysis].[dbo].[Dimension_WR]
	where year([Date])<'2025')
union ALL 

SELECT
    '[DataforAnalysis].[dbo].[EWMS]' as Process,COUNT(DISTINCT [Barcode]) as BarcodeCount,
    [Date]
FROM
    [DataforAnalysis].[dbo].[EWMS]
WHERE
    [Date] = CAST(GETDATE() AS DATE) OR
    [Date] = CAST(GETDATE() - 1 AS DATE)
GROUP BY
    [Date]
union ALL
  SELECT 
    '[DataforAnalysis].[dbo].[Hipot]' as Process ,COUNT([Barcode]) as [BarcodeCount],
    MAX([Date]) as LatestDate
FROM 
    [DataforAnalysis].[dbo].[Hipot]
WHERE 
    [Date] = (SELECT MAX([Date]) FROM [DataforAnalysis].[dbo].[Hipot]
	where year([Date]) <'2025')
	union ALL
	SELECT'[DataforAnalysis].[dbo].[Ai_press]'as Process
	 ,count([Barcode]) as [Barcode]
	 ,MAX([Date]) as LatestDate
  FROM[DataforAnalysis].[dbo].[Ai_press]
  WHERE 
 [Date] = (SELECT MAX([Date]) FROM  [DataforAnalysis].[dbo].[Ai_press] where year([Date]) <'2025')
union ALL
SELECT'[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]'as Process
	 ,count([Barcode]) as [Barcode]
	 ,MAX([Date]) as LatestDate

      
  FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
  WHERE 
    [Date] = (SELECT MAX([Date]) FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
	where year([Date])<'2025')

union ALL
SELECT'[DataforAnalysis].[dbo].[Data_matching]'as Process
	 ,count([Barcode]) as [Barcode]
	 ,MAX([Oil_Top_Time]) as LatestDate

      
  FROM  [DataforAnalysis].[dbo].[Data_matching]
  WHERE 
    [Oil_Top_Time] = (SELECT MAX([Oil_Top_Time]) FROM  [DataforAnalysis].[dbo].[Data_matching]
	where year([Oil_Top_Time])<'2025')
union ALL 
SELECT'[DataforAnalysis].[dbo].[DataML_Test]'as Process
	 ,count([Barcode_base]) as [Barcode]
	 ,MAX([Date]) as LatestDate
  FROM [DataforAnalysis].[dbo].[DataML_Test]
  WHERE 
    [Date] = (SELECT MAX([Date]) FROM  [DataforAnalysis].[dbo].[DataML_Test]
	where year([Date])<'2025');
    """
   

    
    datasets = pd.read_sql(query_template, conn, params=())

    return datasets
result = fetch_data()
print("fetch_data",result)



def send_line_notification(process_name, process_data):
    # Replace 'YOUR_ACCESS_TOKEN' with your LINE Notify access token
    access_token = '8gwSkB6cONlIhR3kqI2thsms392Oz3Vfj2P7DEWmyth'
    url = 'https://notify-api.line.me/api/notify'

    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Customize the message to include relevant information
    message = f'No results found for {process_name}\n\n{process_data.to_string(index=False)}'

    payload = {'message': message}
    requests.post(url, headers=headers, data=payload)

# ... (your existing code)

def check_sql_server_connection():
    try:
        conn = create_sql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # Execute a simple query to check the connection
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")
        return False

# Check SQL Server connection
if not check_sql_server_connection():
    # SQL Server connection failed, send LINE notification
    send_line_notification("SQL Server Connection", pd.DataFrame(columns=["Status"], data=[["Failed"]]))
    print("LINE notification sent for SQL Server Connection")
else:
    # SQL Server connection successful, proceed with fetching data
    result = fetch_data()
    print("fetch_data", result)

    # Check if the result is empty and send LINE notification for each process
    for process_name in result['Process']:
        process_data = result[result['Process'] == process_name]
        if process_data.empty:
            send_line_notification(process_name, process_data)
            print(f"LINE notification sent for {process_name}")

    # This line is outside the loop and will only use the last process_name and process_data
    result_line = send_line_notification(process_name, process_data)
    print(result_line)


