import unittest
from pairplot_generator_002 import BIN_KPIV 
from flask import Flask, jsonify
import json
from Database import create_sql_connection
from Database import create_sql_Component_Master
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
from pairplot_generator_002 import BIN_KPOV 
class TestBINFunctions(unittest.TestCase):
    def test_BIN_KPOV(self):
        # เตรียมข้อมูลที่จำเป็น
        model = ...
        line = ...
        start = ...
        end = ...
        selecteKPOV = ...
        selecteKPIV = ...
        minKPOV = ...
        maxKPOV = ...
        data_df, response_data_json = BIN_KPIV(model, line, start, end, selecteKPOV, selecteKPIV, minKPOV, maxKPOV)
        self.assertIsInstance(data_df, pd.DataFrame)
        self.assertIsInstance(response_data_json, str)
        result = BIN_KPOV(model, line, start, end, selecteKPOV, selecteKPIV, minKPOV, maxKPOV)

        # ตรวจสอบผลลัพธ์ที่คาดหวัง
        self.assertIsInstance(result, dict)
        self.assertIn("data", result)
        self.assertIn("count_before_smote", result)
        self.assertIn("count_after_smote", result)

    def test_BIN_KPIV(self):
        # เตรียมข้อมูลที่จำเป็น
        model = ...
        line = ...
        start = ...
        end = ...
        selecteKPOV = ...
        selecteKPIV = ...
        minKPOV = ...
        maxKPOV = ...

        # เรียกใช้ BIN_KPIV
        data_df, response_data_json = BIN_KPIV(model, line, start, end, selecteKPOV, selecteKPIV, minKPOV, maxKPOV)

        # ตรวจสอบผลลัพธ์ที่คาดหวัง
        self.assertIsInstance(data_df, pd.DataFrame)
        self.assertIsInstance(response_data_json, str)
        # เพิ่มตรวจสอบค่าอื่น ๆ ตามความเหมาะสม

if __name__ == '__main__':
    unittest.main()