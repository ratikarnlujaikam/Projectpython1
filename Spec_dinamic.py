import pyodbc
from datetime import datetime, timedelta
import moment 

server = '192.168.101.219'
database = 'DataforAnalysis'
username = 'DATALYZER'
password = 'NMB54321'

conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
connection = pyodbc.connect(conn_str)

# สร้าง cursor เพื่อทำงานกับฐานข้อมูล
cursor = connection.cursor()

# สร้างคำสั่ง SQL สำหรับ model และ line
sql_query = "SELECT DISTINCT model, line FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester] where model !=''"

# ทำการ execute คำสั่ง SQL
cursor.execute(sql_query)

# ดึงผลลัพธ์
result = cursor.fetchall()

# สร้างคำสั่ง SQL สำหรับ parameter
query_parameter = "SELECT DISTINCT [Parameter] FROM [Component_Master].[dbo].[Master_matchings] WHERE [Part]='Motor_Dim' and [Parameter]!= 'Diecast_Pivot_2' and [Parameter] != 'Diecast_Ramp' and [Parameter] !='Ramp_to_Datum' and [Parameter]!='Ramp_to_Flange'"
# query_parameter = "SELECT DISTINCT [Parameter] FROM [Component_Master].[dbo].[Master_matchings] WHERE [Part]='Motor_Dim' and [Parameter]= 'Projection1'"
# ทำการ execute คำสั่ง SQL
cursor.execute(query_parameter)

# ดึงผลลัพธ์
result_parameter = cursor.fetchall()



start_date = (datetime.now() - timedelta(days=91)).strftime('%Y-%m-%d')
finish_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# ใช้ข้อมูลใน for loop สำหรับ parameter
for row_parameter in result_parameter:
    parameter = row_parameter[0]
    print(parameter)

    # สร้าง connection เพื่อทำการ execute คำสั่ง SQL ใน for loop ถัดไป
    with pyodbc.connect(conn_str) as connection:
        cursor = connection.cursor()

        # ใช้ข้อมูลใน for loop สำหรับ model และ line
        for row in result:
            model, line = row
            currentModel = model
            productionline = line

            # ทำสิ่งที่ต้องการในแต่ละรอบของ for loop
            query_data = f"""with Xbar (x1,x2,x3,x4) as
                (select case when [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[{parameter}] < [Component_Master].[dbo].[Master_matchings].[USL] 
                and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[{parameter}] > [Component_Master].[dbo].[Master_matchings].[LSL]
                then [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[{parameter}] end as [X]
                ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model]
                ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Line]
                ,[Component_Master].[dbo].[Master_matchings].[Parameter]
                FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
                inner join [Component_Master].[dbo].[Master_matchings]
                on [Component_Master].[dbo].[Master_matchings].[Model] = [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model]
                where [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Date] between '{start_date}' and '{finish_date}'
                and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model] = '{currentModel}'
                and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Line] = '{productionline}'
                and [Component_Master].[dbo].[Master_matchings].[Parameter] = '{parameter}'
                and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Barcode] not in (select [Barcode_Motor] from [TransportData].[dbo].[Register])
                and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[{parameter}] > [LSL]
                AND [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[{parameter}] < [USL]
                ),
                
                Sbar (s1,s2) as
                (select cast(stdev([DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[{parameter}]) as decimal(10,5))
                ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model]
                FROM [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester]
                where [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Date] between '{start_date}' and '{finish_date}'
                and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model] = '{currentModel}'
                and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Line] = '{productionline}'
                and [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Barcode] not in (select [Barcode_Motor] from [TransportData].[dbo].[Register])
                group by [DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Model]
                ,[DataforAnalysis].[dbo].[Dynamic_Parallelism_Tester].[Date]
                )
                
                select
                x2 as [Model]
                ,x4 as [Parameter]
                ,x3 as [Line]
                ,cast(AVG(x1) as decimal(10,3)) as [CL]
                ,cast(AVG(x1) as decimal(10,3))-(3*cast(stdev(x1) as decimal(10,3))) as [LCL]
                ,cast(AVG(x1) as decimal(10,3))+(3*cast(stdev(x1) as decimal(10,3))) as [UCL]
                  ,cast(AVG(s1) as decimal(10,3)) as [CL_STD]
                ,cast(AVG(s1) as decimal(10,3))-(3*cast(stdev(s1) as decimal(10,3))) as [LCL_STD]
                ,cast(AVG(s1) as decimal(10,3))+(3*cast(stdev(s1) as decimal(10,3))) as [UCL_STD]
              
                from Xbar inner join Sbar on Xbar.x2 = Sbar.s2
                group by x2,x3,x4"""

            # ทำการ execute คำสั่ง SQL
            cursor.execute(query_data)

            # ดึงผลลัพธ์
            result_data = cursor.fetchall()

            # ทำสิ่งที่ต้องการกับผลลัพธ์
            for row in result_data:
                Model, Parameter, Line, CL, LCL, UCL, CL_STD, LCL_STD, UCL_STD = row
                createdAt = moment.now().format('YYYY-MM-DD HH:mm:ss')  # Assuming moment.now() returns a moment object
                updatedAt = moment.now().format('YYYY-MM-DD HH:mm:ss')  # Assuming moment.now() returns a moment object

    # Construct the SQL query
                sql_query = f"""
        INSERT INTO [TransportData].[dbo].[ControlSpecs]
        VALUES('{Model}', '{Line}', '{Parameter}', {CL}, {LCL}, {UCL}, {CL_STD}, {LCL_STD}, {UCL_STD}, '{createdAt}', '{updatedAt}');
    """
            cursor.execute(sql_query)
            print(sql_query)


connection.close()        
