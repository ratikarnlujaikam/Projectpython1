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
from KPIVRankingNGfractionFunctions import KPIVRankingNGfraction
from DataSciencePreprocessingFunctions import RemoveConstantColumnTable
from DataSciencePreprocessingFunctions import CleanDataForKPIVRanking
from pairplot_generator import fetch_data
from pairplot_generator import BinKPOV_Auto

app = Flask(__name__)
cors = CORS(app)




import pandas as pd
import KPIVRankingNGfractionFunctions as KPIVrank

def perform_ranking(model, Line, start, end, selecteKPOV, selecteKPIV, specValue, specLimits):
    # Fetching data
    data = fetch_data(model, Line, start, end, selecteKPOV, selecteKPIV)
    
    # Extracting selected KPIVs
    selecteKPIV_list = selecteKPIV.split(',')
    DataKPIV = data[selecteKPIV_list].copy()
    
    # Extracting selected KPOV
    DataKPOV = data[selecteKPOV].to_numpy()
    
    # Performing KPIV ranking
    RankingContinuous,RankingResultsCategorical = KPIVrank.KPIVRankingNGfraction(
        DataKPIV,
        DataKPOV,
        specValue,
        specLimits
    )
    print("RankingContinuous",RankingContinuous,)
    print("RankingResultsCategorical",RankingResultsCategorical)

# RankingContinuous
    # Creating a dictionary to hold the formatted data
    formatted_data = {
        'significant_KPIVs': {
            'KPIVRanking': RankingContinuous['KPIVRanking'],
            'RankingError': RankingContinuous['RankingError'],
            'nSignificant': RankingContinuous['nSignificant'],
            'rankingErrorAverage': RankingContinuous['rankingErrorAverage'],
            'reliability': RankingContinuous['reliability'],
        },
    }

    # Extracting data from the formatted_data dictionary
    KPIVRanking = formatted_data['significant_KPIVs']['KPIVRanking']
    RankingError = formatted_data['significant_KPIVs']['RankingError']
    nSignificant = formatted_data['significant_KPIVs']['nSignificant']
    rankingErrorAverage = formatted_data['significant_KPIVs']['rankingErrorAverage']
    reliability = formatted_data['significant_KPIVs']['reliability']

    # Creating a DataFrame from the extracted data
    data_frame = pd.DataFrame({
        'KPIVRanking': KPIVRanking,
        'RankingError': RankingError,
        'nSignificant': nSignificant,
        'rankingErrorAverage': rankingErrorAverage,
        'reliability': reliability
    })

    data_frame.reset_index(drop=True, inplace=True)
    data_frame.index += 1


    formatted_cate = {
        'significant_KPIVs': {
            'KPIVRanking': RankingResultsCategorical['KPIVRanking'],
            'RankingError': RankingResultsCategorical['RankingError'],
            'nSignificant': RankingResultsCategorical['nSignificant'],
            'rankingErrorAverage': RankingResultsCategorical['rankingErrorAverage'],
            'reliability': RankingResultsCategorical['reliability'],
        },
    }

    # Extracting data from the formatted_data dictionary
    KPIVRanking_2 = formatted_cate['significant_KPIVs']['KPIVRanking']
    RankingError_2 = formatted_cate['significant_KPIVs']['RankingError']
    nSignificant_2 = formatted_cate['significant_KPIVs']['nSignificant']
    rankingErrorAverage_2 = formatted_cate['significant_KPIVs']['rankingErrorAverage']
    reliability_2 = formatted_cate['significant_KPIVs']['reliability']

    # Creating a DataFrame from the extracted data
    data_frame_2 = pd.DataFrame({
        'KPIVRanking': KPIVRanking_2,
        'RankingError': RankingError_2,
    })

    data_frame_2.reset_index(drop=True, inplace=True)
    data_frame_2.index += 1
    return data_frame,nSignificant,rankingErrorAverage,reliability,data_frame_2,nSignificant_2,rankingErrorAverage_2,reliability_2


def Bin_Auto(model, selecteKPOV):
    conn = create_sql_connection()
    cursor = conn.cursor()
    
    query = """
     SELECT
      [Parameter] as KPOV
      ,[LSL] as MinKPOV
      ,[CL] as specValue
      ,[USL] as MaxKPOV
    FROM [Component_Master].[dbo].[Master_matchings]
    where [Model]=? and [Parameter]=?
    """
    
    Output_BinKPOV = pd.read_sql(query, conn, params=(model, selecteKPOV))
    # Convert the DataFrame to a dictionary
    result = Output_BinKPOV.to_dict(orient='records')[0]  # Assuming there's only one record
    # Return the result as a regular dictionary
    return result



# Rest of your code
def get_ranking(model, line, start, end, selecteKPOV, selecteKPIV):
    result = Bin_Auto(model, selecteKPOV)
    specValue=(result['specValue'])
    MinKPOV=(result['MinKPOV'])
    MaxKPOV=(result['MaxKPOV'])
    specLimits=([MinKPOV,MaxKPOV])
    
    result_tuple = perform_ranking(model, line, start, end, selecteKPOV, selecteKPIV, specValue, specLimits)
   
    data_frame, nSignificant, rankingErrorAverage, reliability, data_frame_2, nSignificant_2, rankingErrorAverage_2, reliability_2 = result_tuple
    
    result_dict = data_frame.to_dict(orient='records')
    
    # Check if result_dataframe_2 has data
    if not data_frame_2.empty:
        result_dict_2 = data_frame_2.to_dict(orient='records')
    else:
        result_dict_2 = []  # or any other default value
        
    print("result_dict", result_dict)
    print("nSignificant", nSignificant)
    print("rankingErrorAverage", rankingErrorAverage)
    print("reliability", reliability)

    
    return jsonify({
                    # Continuous KPIVs
                    'result_dict_1': result_dict, 
                    "nSignificant": nSignificant,"rankingErrorAverage": rankingErrorAverage,"reliability":reliability,
                    # Categorical KPIVs
                    'result_dict_2': result_dict_2,
                    'nSignificant_2':nSignificant_2,'rankingErrorAverage_2':rankingErrorAverage_2,'reliability_2':reliability_2
                    
                    })



# # Example usage
# model = "LONGSP"
# Line = "3-6"
# start = "2023-10-26"
# end = "2023-10-27"
# selecteKPOV = "Projection1"
# selecteKPIV = "Set_Dim_A,Set_Dim_B,Set_Dim_C"

# result = get_ranking(model, Line, start, end, selecteKPOV, selecteKPIV)
# print(result)




