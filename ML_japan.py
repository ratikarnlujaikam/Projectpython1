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

from Database import create_sql_connection 

fixture_type = ['A', 'B']
line_name = ['all', '1-4', '2-6', '3-6', '3-10', '3-14', '3-17']
colors = ['blue', 'orange', 'green', 'yellow', 'magenta', 'cyan']

def make_chart(start, end):

    # -- Connect to SQL server by pymssql
    conn = create_sql_connection()
    cursor = conn.cursor()

    sql = "SELECT [Dynamic_Parallelism_Tester].[Time], " \
        + "[Dynamic_Parallelism_Tester].[Line], " \
        + "[Ai_press].[Machine_no] as Ai_Press_RTB_Fixture, " \
        + "[Dynamic_Parallelism_Tester].[Set_Dim_A], " \
        + "[Dynamic_Parallelism_Tester].[Set_Dim_B], " \
        + "[Dynamic_Parallelism_Tester].[Set_Dim_c], " \
        + "[Dynamic_Parallelism_Tester].[Projection1] AS PFH, " \
        + "CASE WHEN[Dynamic_Parallelism_Tester].[Projection1] >= 0.4648 " \
        + "AND [Dynamic_Parallelism_Tester].[Projection1] <= 0.5664 " \
        + "THEN 'OK' ELSE 'NG' END AS okng_PFH " \
        + "FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester] " \
        + "INNER JOIN[DataforAnalysis].[dbo].[Ai_press] " \
        + "ON[Dynamic_Parallelism_Tester].[Barcode] = [Ai_press].[Barcode] " \
        + "WHERE [Dynamic_Parallelism_Tester].[Model] = 'LONGSP' " \
        + "AND [Dynamic_Parallelism_Tester].[Time] >= '" + start + "' " \
        + "AND [Dynamic_Parallelism_Tester].[Time] < '" + end + "' "
    print("------  querying -------- \n" + sql)

    sql = """
WITH CTE AS (
    SELECT
        [Dynamic_Parallelism_Tester].[Barcode],
        [Dynamic_Parallelism_Tester].[Time],
        [Dynamic_Parallelism_Tester].[Line],
        [Ai_press].[Machine_no] as Ai_Press_RTB_Fixture,
        [Dynamic_Parallelism_Tester].[Set_Dim_A],
        [Dynamic_Parallelism_Tester].[Set_Dim_B],
        [Dynamic_Parallelism_Tester].[Set_Dim_c],
        [Dynamic_Parallelism_Tester].[Projection1] AS PFH,
        CASE
            WHEN [Dynamic_Parallelism_Tester].[Projection1] >= 0.4648 AND [Dynamic_Parallelism_Tester].[Projection1] <= 0.5664
            THEN 'OK'
            ELSE 'NG'
        END AS okng_PFH,
        ROW_NUMBER() OVER (PARTITION BY [Dynamic_Parallelism_Tester].[Barcode] ORDER BY [Dynamic_Parallelism_Tester].[Time] DESC) AS RowNum
    FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
    INNER JOIN [DataforAnalysis].[dbo].[Ai_press]
    ON [Dynamic_Parallelism_Tester].[Barcode] = [Ai_press].[Barcode]
    WHERE [Dynamic_Parallelism_Tester].[Model] = 'LONGSP'
    AND [Dynamic_Parallelism_Tester].[Time] >= '""" + start + """'
    AND [Dynamic_Parallelism_Tester].[Time] < '""" + end + """'
)

SELECT
    [Barcode],
    [Time] AS Time,
    [Line],
    [Ai_Press_RTB_Fixture],
    [Set_Dim_A],
    [Set_Dim_B],
    [Set_Dim_c],
    [PFH],
    [okng_PFH]
FROM CTE
WHERE RowNum = 1
"""
    print("------  querying -------- \n" + sql)

    # -- saved dataset
    dataFrame = pd.read_sql(sql, con=conn, index_col=None)
    # dataFrame.to_csv(dataDir + "dataset.csv", index=False)
    conn.close()
    print("saved dataset")

    plt.style.use("ggplot")
    df = dataFrame
    print(df.head())
    fig, axes = plt.subplots(len(fixture_type), len(
        line_name), sharex='col', figsize=(25, 10))
    # When set period
    # df = df[df["Time"] >= '2022-12-01 07:00:00']
    # df = df[df["Time"] < '2023-01-01 07:00:00']
    dateMax = str(max(df['Time']))
    dateMin = str(min(df['Time']))
    year = dateMin[0:4]
    month = dateMin[5:7]

    fig.suptitle("LongsPeak Tilt plot BY line from " +
                 str(dateMin) + " to " + str(dateMax), fontsize=20)
    k = 0
    ax = axes.ravel()
    for i in range(len(fixture_type)):
        fixture = df[df['Ai_Press_RTB_Fixture'].str.replace(
            " ", "") == fixture_type[i]]
        for j in range(len(line_name)):
            print(k)
            # ---  making tilt plot  -----------------------------------------------------------------------------
            if not line_name[j] == 'all':
                df_line = fixture[fixture['Line'] == line_name[j]]
                df_ok = df_line[df_line['okng_PFH'] == 'OK']
                df_ng = df_line[df_line['okng_PFH'] == 'NG']
                sql_ttl = "Line == \'" + str(line_name[j]) + "\'"
                print(sql_ttl)
                ttl = fixture.query(sql_ttl).count()
                sql_ng = "Line == \'" + \
                    str(line_name[j]) + "\'& okng_PFH == 'NG'"
                ng = fixture.query(sql_ng).count()
                yield_ = ng['Line'] / ttl['Line']
                label = str(line_name[j]) + " : NG " + str("{:,}".format(ng['Line'])) \
                    + "\n / Input " + str("{:,}".format(ttl['Line'])) + " >> " \
                    + str(f'{yield_ * 100:.03f}') + "%"
                print(label)
                if line_name[j] == '1-4':
                    color = 'blue'
                elif line_name[j] == '2-6':
                    color = 'orange'
                elif line_name[j] == '3-6':
                    color = 'magenta'
                elif line_name[j] == '3-10':
                    color = 'green'
                elif line_name[j] == '3-14':
                    color = 'yellow'
                elif line_name[j] == '3-17':
                    color = 'cyan'
                # print(color)

                line_name_detail = label

                X_ok = (df_ok['Set_Dim_A'] - df_ok['Set_Dim_c']
                        ) * 2 / math.sqrt(3) * 1000
                Y_ok = (df_ok['Set_Dim_A'] - 2 * df_ok['Set_Dim_B'] +
                        df_ok['Set_Dim_c']) * 2 / 3 * 1000
                ax[k].scatter(X_ok, Y_ok, s=1.5, c=color,
                              marker='.', label='OK', alpha=0.5)

                X_ng = (df_ng['Set_Dim_A'] - df_ng['Set_Dim_c']
                        ) * 2 / math.sqrt(3) * 1000
                Y_ng = (df_ng['Set_Dim_A'] - 2 * df_ng['Set_Dim_B'] +
                        df_ng['Set_Dim_c']) * 2 / 3 * 1000
                ax[k].scatter(X_ng, Y_ng, s=3, c='red',
                              marker='.', label='NG', alpha=1)

                ax[k].set_ylim(-100, 100)
                ax[k].set_xlim(-100, 100)
                ax[k].set_ylabel("Y")
                ax[k].set_xlabel("X")
                ax[k].text(-90, 80, line_name_detail)
                ax[k].vlines(0, ymin=-100, ymax=100, color='black',
                             linestyles='dashed', linewidth=0.5)
                ax[k].hlines(0, xmin=-100, xmax=100, color='black',
                             linestyles='dashed', linewidth=0.5)
                ax[k].set_title("line" + line_name[j] +
                                " Fixture " + fixture_type[i])
                ax[k].legend(loc="lower left", markerscale=10, fontsize=10)

            # ---  Making histogram  ---------------------------------------------------------------------------------
            else:
                bins = 500
                hist_range = (0.4, 0.6)
                ymax = 1500
                column_name = 'PFH'

                for m in range(len(line_name)):
                    if not m == 0:
                        line = fixture[fixture['Line'] == line_name[m]]

                        if line_name[m] == '3-10':
                            H_color = 'green'
                        elif line_name[m] == '1-4':
                            H_color = 'blue'
                        elif line_name[m] == '2-6':
                            H_color = 'orange'
                        elif line_name[m] == '3-14':
                            H_color = 'yellow'
                        elif line_name[m] == '3-6':
                            H_color = 'magenta'
                        elif line_name[m] == '3-17':
                            H_color = 'cyan'
                        # print(color)
                        ax[k].hist(line[column_name], bins=bins, alpha=0.3,
                                   color=H_color, label=line_name[m], range=hist_range)

                ax[k].vlines(0.4648, ymin=0, ymax=ymax, color='black',
                             linestyles='dashed', linewidth=0.5)
                ax[k].vlines(0.5664, ymin=0, ymax=ymax, color='black',
                             linestyles='dashed', linewidth=0.5)
                ax[k].set_ylabel("Frequency")
                ax[k].set_title(
                    "PFH Histogram by line & fixture_" + fixture_type[i], fontsize=15)
                ax[k].legend(loc="upper left", markerscale=10, fontsize=10)
                ax[k].set_ylim(0, ymax)

            k = k+1
    plt.savefig("../TrainingNodeJS/chart/tilt_plot_"+".png")
    plt.close()
    plt.show()
    return send_file(f"../TrainingNodeJS/chart/tilt_plot_"+".png", mimetype='image/png')