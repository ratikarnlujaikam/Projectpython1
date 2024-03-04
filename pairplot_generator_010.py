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

app = Flask(__name__)
cors = CORS(app)


def get_parameters():
    try:
        # การเชื่อมต่อฐานข้อมูล SQL Server
        conn = create_sql_connection()

        cursor = conn.cursor()

        # ดึงข้อมูลจาก SQL
        cursor.execute(" SELECT case  when [Parameter] = 'R1 (U-V)' then  'R1_(U-V)' when [Parameter] = 'R2 (U-W)' then  'R2_(U-W)' when [Parameter] = 'R3 (V-W)' then  'R3_(V-W)' else [Parameter] end Parameters FROM [DataforAnalysis].[dbo].[parameters] where [Parameter]!='P1_Attractive_1' and  [Parameter]!='P1_Stack_1' and  [Parameter]!='P2_Attractive_2' and  [Parameter]!='P2_Stack_2' and  [Parameter]!='P3_Attractive_3' and  [Parameter]!='P3_Stack_3' and  [Parameter]!='P4_Ramp_Height' and  [Parameter]!='P5_Pivot' and  [Parameter]!='P3_Attractive_3' and  [Parameter]!='Set_Dimension_Attractive' and  [Parameter]!='Set_Dimension_Stack' and  [Parameter]!='Start Torque'  and  [Parameter]!='Parallelism_Attractive'  and  [Parameter]!='Parallelism_Stack' and  [Parameter]!='R_max-min'  and  [Parameter]!='BEMF 0-Peak' union select 'Diecast_Pivot_2' union  select 'Diecast_Ramp'")
        rows = cursor.fetchall()

        options = [{"value": row.Parameters, "text": row.Parameters}
                   for row in rows]
        # print(options)
        # ปิดการเชื่อมต่อฐานข้อมูล
        conn.close()

        # ใช้ print เพื่อแสดงข้อมูลที่คุณต้องการตรวจสอบ

        return jsonify(options)

    except Exception as e:
        # ใช้ print เพื่อแสดงข้อผิดพลาดที่เกิดขึ้น
        print(str(e))
        return str(e)


def get_model():
    try:
        # การเชื่อมต่อฐานข้อมูล SQL Server
        conn = create_sql_Component_Master()

        cursor = conn.cursor()

        # ดึงข้อมูลจาก SQL
        cursor.execute(
            "SELECT distinct [Model] as model FROM [Component_Master].[dbo].[line_for_QRcode] where [Model] !='ALL'")
        rows = cursor.fetchall()

        options = [{"value": row.model, "text": row.model} for row in rows]

        # ปิดการเชื่อมต่อฐานข้อมูล
        conn.close()

        # ใช้ print เพื่อแสดงข้อมูลที่คุณต้องการตรวจสอบ

        return jsonify(options)

    except Exception as e:
        # ใช้ print เพื่อแสดงข้อผิดพลาดที่เกิดขึ้น
        print(str(e))
        return str(e)


def get_line(model):
    try:
        # การเชื่อมต่อฐานข้อมูล SQL Server
        conn = create_sql_Component_Master()

        cursor = conn.cursor()

        # ดึงข้อมูลจาก SQL
        cursor.execute(
            "SELECT distinct [line] FROM [Component_Master].[dbo].[line_for_QRcode] WHERE [Model] != 'ALL' AND Model = '" + model + "'")
        rows = cursor.fetchall()

        options = [{"value": row.line, "text": row.line} for row in rows]

        # ปิดการเชื่อมต่อฐานข้อมูล
        conn.close()

        # ใช้ print เพื่อแสดงข้อมูลที่คุณต้องการตรวจสอบ

        return jsonify(options)

    except Exception as e:
        # ใช้ print เพื่อแสดงข้อผิดพลาดที่เกิดขึ้น
        print(str(e))
        return str(e)


def fetch_data(model, Line, start, end, selecteKPOV, selecteKPIV):
    conn = create_sql_connection()
    cursor = conn.cursor()
    # print(f"fetch_data*************************************************************",model,Line,start,end,selecteKPOV,selecteKPIV)

    query_template = """
        SELECT {selecteKPOV}, {selecteKPIV}
        FROM [Diecast].[dbo].[Pivot]
        JOIN [TransportData].[dbo].[Matching_Auto_Unit1] ON [Pivot].Diecast_S_N = [Matching_Auto_Unit1].Barcode_Base
        JOIN [DataforAnalysis].[dbo].[DataML_Test] ON [DataML_Test].Barcode_motor = [Matching_Auto_Unit1].Barcode_Motor
        WHERE [DataML_Test].[Model] = ? 
        AND [DataML_Test].[Line] = ? 
        AND [DataML_Test].[Date] BETWEEN ? AND ?
        {kpi_conditions}
    """
    # Split the comma-separated selecteKPIV into a list
    selecteKPIV_list = selecteKPIV.split(',')

    # Generate conditions for selecteKPIV columns
    kpi_conditions = ""
    for column in selecteKPIV_list:
        kpi_conditions += f"AND {column.strip()} IS NOT NULL\n"

    # Execute the query with parameters and fetch data
    query = query_template.format(selecteKPOV=selecteKPOV, selecteKPIV=','.join(selecteKPIV_list), kpi_conditions=kpi_conditions)
    datasets = pd.read_sql(query, conn, params=(model, Line, start, end))
    # print(f"output_datasets***********************fetch_data************************",datasets)
    return datasets


import matplotlib.pyplot as plt
from datetime import datetime

def make_chartML(model, line, start, end, selecteKPOV, selecteKPIV):
    datasets = fetch_data(model, line, start, end, selecteKPOV, selecteKPIV)

    if datasets is None or datasets.empty:
        # ถ้า Datasets เป็น None หรือว่าว่างให้สร้างข้อความแจ้งเตือนว่าไม่มีข้อมูล
        return "No data available"

    corrmat = datasets.corr()

    f, ax = plt.subplots(figsize=(12, 9))
    sns.heatmap(corrmat, vmax=.8, square=True, cmap='coolwarm', annot=True)

    # เพิ่ม Model, Line, และวันที่ ลงในรูปด้านบนสุด
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info_text = f"Model: {model}\nLine: {line}\nDate: {current_datetime}"
    plt.text(0.5, 1.05, info_text, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    plt.savefig('../TrainingNodeJS/chart/heatmap.png')
    plt.close()

    return send_file(f"../TrainingNodeJS/chart/heatmap.png", mimetype='image/png')

import requests


def pairplot(model, line, start, end, selecteKPOV, selecteKPIV):
    datasets = fetch_data(model, line, start, end, selecteKPOV, selecteKPIV)
    pairplot = sns.pairplot(datasets, height=4)

    pairplot.savefig('../TrainingNodeJS/chart/pairplot.png')
    plt.close()

    return send_file(f"../TrainingNodeJS/chart/pairplot.png", mimetype='image/png')


def summary_describe(model, line, start, end, selecteKPOV, selecteKPIV):
    datasets = fetch_data(model, line, start, end, selecteKPOV, selecteKPIV)
    summary = datasets.describe(include='all')
    print(f"summary_describe_fetch_data", selecteKPIV)

    # Convert the summary to a JSON format
    summary_json = summary.to_json()

    # Replace 'null' with 0 in the JSON data
    summary_json = summary_json.replace('null', 'No data')

    print(summary_json)

    # If you want to return the JSON data
    return summary_json


def BIN_KPOV(model, line, start, end, selecteKPOV, selecteKPIV, minKPOV, maxKPOV):
    # Call the summary_describe function
    data = fetch_data(model, line, start, end, selecteKPOV, selecteKPIV)
    print(type(minKPOV) )
    print(type(maxKPOV) )
    
    # Modify the selected column as needed for KPOV
    data[selecteKPOV] = pd.cut(
        data[selecteKPOV],
        bins=[-np.inf, float(minKPOV), float(maxKPOV), np.inf],
        labels=['fail_low', 'Pass', 'fail_high']
    )

    # Replace 'fail_low' and 'fail_high' with 'fail' in the KPOV column
    data[selecteKPOV].replace(['fail_low', 'fail_high'], 'fail', inplace=True)

    # Count the occurrences of different values in the original KPOV data
    count_before_smote = dict(Counter(data[selecteKPOV]))

    k = 3
    X = data.loc[:, data.columns != selecteKPOV]  # Use selecteKPOV here
    y = data[selecteKPOV]  # Use selecteKPOV here

    # Sampling strategy
    sm = SMOTE(sampling_strategy='minority', k_neighbors=k, random_state=100)
    X_res, y_res = sm.fit_resample(X, y)

    # Concatenate the resampled data
    datasets = pd.concat([pd.DataFrame(X_res), pd.DataFrame(y_res)], axis=1)

    # Replace 'fail_low' and 'fail_high' with 'fail' in the resampled KPOV data
    datasets[selecteKPOV].replace(['fail_low', 'fail_high'], 'fail', inplace=True)

    # Count the occurrences of different values in the resampled KPOV data
    count_after_smote = dict(Counter(datasets[selecteKPOV]))

    # Convert the DataFrame to a JSON object
    json_data = datasets.to_json(orient='records')

    # Create a dictionary to include the count results in the JSON response
    response_data = {
        "data": json_data,
        "count_before_smote": count_before_smote,
        "count_after_smote": count_after_smote
      
    }
    return response_data


def data_bin(model, selecteKPIV):
    conn = create_sql_connection()
    cursor = conn.cursor()
    print("data_bin", selecteKPIV)
    selecteKPIV_01 = selecteKPIV.split(',')
    
    result_datasets = []
    query = ""
    for KPIV in selecteKPIV_01:
        query_template = """
      WITH set1 AS (
        SELECT
            [id],
            [Fullname],
            [Model],
            [Parameter],
            [USL],
            [LSL],
            CL,
            [USL] - [LSL] AS "X",
            ([USL] - [LSL]) / 6 AS "Y",
            [Part],
            [Machine],
            [empNumber],
            [createdAt],
            [updatedAt]
        FROM [Component_Master].[dbo].[Master_matchings]
    )
    SELECT
        [Model],
        [Parameter],
        '-infinity' as MIN_L4,
        ROUND([LSL] - 0.0001, 4) AS "MAX_L4",

		ROUND([LSL] , 4) AS "MIN_L3",
		ROUND([LSL] + 1 * [Y]- 0.0001, 4) AS "MAX_L3",
		ROUND([LSL] + 1 * [Y], 4) AS "MIN_L2",
		ROUND([LSL] + 2 * [Y]- 0.0001, 4) AS "MAX_L2",
		ROUND([LSL] + 2 * [Y], 4) AS "MIN_L1",
		ROUND([LSL] + 3 * [Y] - 0.0001, 4) AS "MAX_L1",

		ROUND([LSL] + 3 * [Y] , 4) AS "MIN_U1",
		ROUND([LSL] + 4 * [Y] - 0.0001, 4) AS "MAX_U1",

		ROUND([LSL] + 4 * [Y] , 4) AS "MIN_U2",
		ROUND([LSL] + 5 * [Y] - 0.0001, 4) AS "MAX_U2",

		ROUND([LSL] + 5 * [Y] , 4) AS "MIN_U3",
		ROUND([LSL] + 6 * [Y] - 0.0001, 4) AS "MAX_U3",

		ROUND([LSL] + 6 * [Y] , 4) AS "MIN_U4",
		'+infinity' as [MAX_U4]

        FROM set1
WHERE [Model] = '{model}' AND [Parameter] = '{KPIV}'

        """

        query = query_template.format(model=model, KPIV=KPIV)  # Format the query string
        datasets_bin = pd.read_sql(query, conn)
        
        # Convert the DataFrame to a list of dictionaries
        datasets_bin_dict = datasets_bin.to_dict(orient='records')
        
        result_datasets.append(datasets_bin_dict)
    return result_datasets

def api_data_bin(model, kpivs):
    selecteKPIV = kpivs.split(',')
    result_datasets = data_bin(model, selecteKPIV)

    # Convert DataFrames to JSON strings
    serialized_datasets = [df.to_json(orient='records') for df in result_datasets]

    # Combine into a single JSON object with keys as KPIV names
    result_dict = {kpi: json.loads(data) for kpi, data in zip(selecteKPIV, serialized_datasets)}

    return jsonify(result_dict)

# def getdataAll (model,line,start,end,selecteKPOV,selecteKPIV):
#     datasets = fetch_data(model, line, start, end, selecteKPOV, selecteKPIV)
    
    
#     return


# ในฟังก์ชัน DATASETS_BIN
import pandas as pd
import re

def BIN_KPIV(model, line, start, end, selecteKPOV, selecteKPIV, minKPOV, maxKPOV, support, confidence):
    conn = create_sql_connection()
    cursor = conn.cursor()
    statistics_data = {}  # Store statistical data for each KPIV in a dictionary
    selecteKPIV_01 = selecteKPIV.split(',')
    datasets_bin_query = data_bin(model, selecteKPIV)
    print(f"selecteKPIV_01", selecteKPIV_01)

    if datasets_bin_query and len(datasets_bin_query) > 0:
        binned_data = pd.DataFrame()
        for KPIV in selecteKPIV_01:
            datasets = BIN_KPOV(model, line, start, end, selecteKPOV, KPIV, minKPOV, maxKPOV)  # ส่ง KPIV ไปให้ BIN_KPOV

            # Check if datasets is a dictionary
            if isinstance(datasets, dict) and 'data' in datasets:
                # Access the DataFrame inside the dictionary
                datasets_data = pd.read_json(datasets['data'])
                print(f"*****************************************************************datasets_data",datasets_data)
                

                if KPIV in datasets_data.columns:
                    print(f"*************************KPIV",KPIV)
                    # Access the appropriate dataset_query for the current KPIV
                    dataset_query = None
                    for query in datasets_bin_query:
                        if query and len(query) > 0 and query[0].get('Model') == model and query[0].get(
                                'Parameter') == KPIV:
                            dataset_query = query[0]
                            break
                    if dataset_query:
                        LCL_4 = dataset_query.get('MAX_L4', '-infinity')
                        LCL_3 = dataset_query.get('MAX_L3', '-infinity')
                        LCL_2 = dataset_query.get('MAX_L2', '-infinity')
                        LCL_1 = dataset_query.get('MAX_L1', '-infinity')
                        UCL_1 = dataset_query.get('MAX_U1', '+infinity')
                        UCL_2 = dataset_query.get('MAX_U2', '+infinity')
                        UCL_3 = dataset_query.get('MAX_U3', '+infinity')

                        print(f"**********LCL_4*********", [KPIV],LCL_4)
                        print(f"**********LCL_3*********", [KPIV],LCL_3)
                        print(f"**********LCL_2*********", [KPIV],LCL_2)
                        print(f"**********LCL_1*********", [KPIV],LCL_1)
                        print(f"**********UCL_1*********", [KPIV],UCL_1)
                        print(f"**********UCL_2*********", [KPIV],UCL_2)
                        print(f"**********UCL_3*********", [KPIV],UCL_3)

                
                
                    # Cut the KPIV column and assign it back
                    datasets_data[KPIV] = pd.cut(
                        datasets_data[KPIV],
                        bins=[-np.inf, float(LCL_4), float(LCL_3), float(LCL_2), float(LCL_1), float(UCL_1),
                              float(UCL_2), float(UCL_3), np.inf],
                        labels=['-4', '-3', '-2', '-1', '1', '2', '3', '4'],
                    )

                    binned_data = pd.concat([binned_data, datasets_data[KPIV]], axis=1)
 
    # รวมข้อมูล Projection1 เข้ากับ binned_data
        binned_data = pd.concat([binned_data, datasets_data[selecteKPOV]], axis=1)
    selectKPOV_list  = [selecteKPOV]
# เลือกคอลัมน์ที่ต้องการจาก binned_data
    selected_columns = selecteKPIV_01 + selectKPOV_list

# Print the combined list for verification
    print("******************************selected_columns", selected_columns)

# Select columns from binned_data based on the combined list
    binned_data = binned_data[selected_columns]





    from pyarc import CBA, TransactionDB
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    print(f"datasets_data****************************",binned_data)
    train, test = train_test_split(binned_data, test_size=0.1)
  
    txns_train = TransactionDB.from_DataFrame(train)
    txns_test = TransactionDB.from_DataFrame(test)

    combined_str = "0." + confidence

    support_float =  "0." + support

    cba = CBA(support=float(support_float), confidence=float(combined_str), algorithm='m1')
    cba.fit(txns_train)

    y_pred = cba.predict(txns_test)
    y_test = test[selecteKPOV]

        # Get the classification report
    classification_results = classification_report(y_test, y_pred, zero_division=1, output_dict=True)

        # Create a DataFrame from the classification results
    df_classification_results = pd.DataFrame(classification_results).transpose()
    df_classification_results.index.name = 'Class'

    # print(f"cba.clf.rules",cba.clf.rules)

        # Sample text containing rules
    text = str(cba.clf.rules)

    rules = re.findall(r'CAR {(.*?)} => {(.*?)} sup: (.*?) conf: (.*?) len: (.*?), id: (.*?)(?=, CAR|$)', text)
    data = []

    for rule in rules:
        KPIV_data, KPOV_data, sup, conf, length, rule_id = rule
        KPIV = {item.split('=')[0]: item.split('=')[1] for item in KPIV_data.split(',')}
        KPIV.update({'sup': sup, 'conf': conf, 'len': length, 'id': rule_id, selecteKPOV: KPOV_data})
        data.append(KPIV)

    df = pd.DataFrame(data)

    df['index'] = range(len(df))

# แปลงค่า 'Pass' และ 'fail' ให้เป็น 'Pass' หรือ 'fail' ตามที่คุณต้องการ
    df[selecteKPOV] = df[selecteKPOV].apply(lambda x: 'Pass' if 'Pass' in x else 'fail')

# เรียงข้อมูลด้วยคอลัมน์ 'sup' และ 'KPOV'
    df.sort_values(by=[selecteKPOV,'sup' ], inplace=True)
    # Replace this line where you define the index:
    df['index'] = range(1, len(df) + 1)

# แสดงผล DataFrame หลังจากประมวลผลเสร็จสิ้น
    print("df_rules", df)




   
# Convert the DataFrame to a list of dictionaries (JSON)
    json_data = df.where(pd.notna(df), None).to_dict(orient='records')
    classification_results_json = df_classification_results.to_json(orient='records')


    response_data = {
            "json_data": json_data,
            "classification_results_json": classification_results_json
   
        }

    print(f"*********************json_data**********************",json_data)
    print(f"*********************classification_results_json**********************",classification_results_json)
# Return the response_data dictionary

    return response_data



