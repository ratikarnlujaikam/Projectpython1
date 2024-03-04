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
app = Flask(__name__)
cors = CORS(app)


def fetch_data():
    conn = create_sql_connection()
    cursor = conn.cursor()
    query_template = """
        
SELECT'[Dimension_WR]'as Process
	 ,count([Part_ID]) as [Barcode]
	 ,MAX([Date]) as LatestDate

      
  FROM [DataforAnalysis].[dbo].[Dimension_WR]
  WHERE 
    [Date] = (SELECT MAX([Date]) FROM [DataforAnalysis].[dbo].[Dimension_WR]
	where year([Date])<'2025')
union ALL 

SELECT
    '[EWMS]' as Process,COUNT(DISTINCT [Barcode]) as BarcodeCount,
    [Date]
FROM
    [DataforAnalysis].[dbo].[EWMS]
WHERE
 
    [Date] = CAST(GETDATE() - 1 AS DATE)
GROUP BY
    [Date]
union ALL
  SELECT 
    '[Hipot]' as Process ,COUNT([Barcode]) as [BarcodeCount],
    MAX([Date]) as LatestDate
FROM 
    [DataforAnalysis].[dbo].[Hipot]
WHERE 
    [Date] = (SELECT MAX([Date]) FROM [DataforAnalysis].[dbo].[Hipot]
	where year([Date]) <'2025')
	union ALL
	SELECT'[Ai_press]'as Process
	 ,count([Barcode]) as [Barcode]
	 ,MAX([Date]) as LatestDate
  FROM[DataforAnalysis].[dbo].[Ai_press]
  WHERE 
 [Date] = (SELECT MAX([Date]) FROM  [DataforAnalysis].[dbo].[Ai_press] where year([Date]) <'2025')
union ALL
SELECT'[Dynamic_Parallelism_Tester]'as Process
	 ,count([Barcode]) as [Barcode]
	 ,MAX([Date]) as LatestDate

      
  FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
  WHERE 
    [Date] = (SELECT MAX([Date]) FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
	where year([Date])<'2025')

union ALL
SELECT'[Data_matching]'as Process
	 ,count([Barcode]) as [Barcode]
	 ,MAX([Oil_Top_Time]) as LatestDate

      
  FROM  [DataforAnalysis].[dbo].[Data_matching]
  WHERE 
    [Oil_Top_Time] = (SELECT MAX([Oil_Top_Time]) FROM  [DataforAnalysis].[dbo].[Data_matching]
	where year([Oil_Top_Time])<'2025')
union ALL 
SELECT'[DataML_Test]'as Process
	 ,count([Barcode_base]) as [Barcode]
	 ,MAX([Date]) as LatestDate
  FROM [DataforAnalysis].[dbo].[DataML_Test]
  WHERE 
    [Date] = (SELECT MAX([Date]) FROM  [DataforAnalysis].[dbo].[DataML_Test]
	where year([Date])<'2025');
    """
   

    
    datasets = pd.read_sql(query_template, conn, params=())
    datasets['LatestDate'] = pd.to_datetime(datasets['LatestDate'])
    current_date = datetime.now()
    threshold_date = current_date - timedelta(days=2)
    filtered_data = datasets[datasets['LatestDate'] < threshold_date]
    return filtered_data
result = fetch_data()
result = fetch_data()
print("fetch_data",result)


from datetime import datetime

def send_line_notification(process_name, process_data):
    # Replace 'YOUR_ACCESS_TOKEN' with your LINE Notify access token
    access_token = '8gwSkB6cONlIhR3kqI2thsms392Oz3Vfj2P7DEWmyth'
    url = 'https://notify-api.line.me/api/notify'

    headers = {'Authorization': f'Bearer {access_token}'}
    
    current_time = datetime.now()
    # Customize the message to include relevant information
    message = f'Time_sent:{current_time}\n'
    
    for col, value in process_data.iloc[0].items():
        message += f'{col}:\n{value}\n'
    
    print("process_data********************************************************", process_data)

    payload = {'message': message}
    requests.post(url, headers=headers, data=payload)

# Example usage
# Assuming you have a DataFrame called 'result'
for index, row in result.iterrows():
    process_name = row['Process']
    process_data = pd.DataFrame([row])  # Create a DataFrame for the current row
    send_line_notification(process_name, process_data)






