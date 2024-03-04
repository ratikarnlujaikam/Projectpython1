import pyodbc

from Date_All_process import Date_between  
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

def fetch_data():
    try:
        # Establish a connection to the database
        conn = create_sql_connection()
        cursor = conn.cursor()

        # SQL query to insert data
        query_template = f"""
    with cte1 as (
SELECT  [AxialPlay_Fac2].[Barcode]
      ,[AxialPlay_Fac2].Axial_Play
      ,[Oilfill_Fac2].[Oilfill]
      ,[AxialPlay_Fac2].[Line]
      ,[AxialPlay_Fac2].[Model]
      ,'Rotor' AS Part
      ,TRY_PARSE([AxialPlay_Fac2].[Time] AS datetime)AS datetime
      ,[AxialPlay_Fac2].[Machine]
      ,[Oilfill_Fac2].[Time]
      ,[Oilfill_Fac2].Filling_Station
	  FROM [SPD_Fac2].[dbo].[AxialPlay_Fac2]
	  join [SPD_Fac2].[dbo].[Oilfill_Fac2] on [AxialPlay_Fac2].Barcode = [Oilfill_Fac2].Barcode 
	  WHERE  [Oilfill_Fac2].Machine = 'Auto1'and [AxialPlay_Fac2].Date > DATEADD(day,{Date_BT},GETDATE()))

, cte2 as (
	  SELECT
	  [Oilfill_Fac2].[Barcode]
      ,[Oilfill_Fac2].Oilfill as oilbuttom
      ,CONVERT(DATETIME,  Convert(nvarchar(50),[Oilfill_Fac2].[Date],120) +' '+ Convert(nvarchar(50),[Oilfill_Fac2].[Time],120 )) as  _DateTime 
      ,[Oilfill_Fac2].Filling_Station
	  FROM [SPD_Fac2].[dbo].[AxialPlay_Fac2]
	  join [SPD_Fac2].[dbo].[Oilfill_Fac2] on [AxialPlay_Fac2].Barcode = [Oilfill_Fac2].Barcode
	  WHERE  [Oilfill_Fac2].Machine = 'Auto2'and [Oilfill_Fac2].Date > DATEADD(day,{Date_BT},GETDATE()))

,Final as (
SELECT
	ROW_NUMBER() OVER (PARTITION BY cte1.[Barcode] ORDER BY cte1.datetime desc) AS RowNum,
    cte1.[Barcode],
    cte1.Axial_Play,
    cte1.[Oilfill],
    cte2.oilbuttom,
    cte1.[Line],
    cte1.[Model],
    cte1.Part,
    cte1.datetime,
    cte1.[Machine],
    cte1.[Time],
    cte1.Filling_Station as Filling_Station_1,
    cte2._DateTime,
    cte2.Filling_Station as Filling_Station_2
FROM
    cte1
JOIN
    cte2 ON cte1.Barcode = cte2.Barcode
	)


INSERT INTO [DataforAnalysis].[dbo].[Data_matching] (
   
    [Barcode],
    [Axial_Play],
    [Oil_Top],
    [Oil_Bottom],
    [Line],
    [Model],
    [Part],
    [Timestamp],
    [MC_Axial_Play],
    [Oil_Top_Time],
    [MC_Oil_Top],
    [Oil_Bottom_Time],
    [MC_Oil_Bottom]
)
SELECT
    [Barcode],
    Axial_Play,
    [Oilfill],
    oilbuttom,
    [Line],
    [Model],
    Part,
    datetime,
    [Machine],
    [Time],
    Filling_Station_1,
    DateTime,
    Filling_Station_2
FROM Final
WHERE
    RowNum='1'  and NOT EXISTS (
        SELECT 1
        FROM [DataforAnalysis].[dbo].[Data_matching] dm
        WHERE dm.Barcode = Final.Barcode
        AND dm.Timestamp = Final.datetime
    );

    BEGIN

with Final as (
SELECT [Barcode]
,[Axial_Play]
,[Oil_Up_Amount]
,[Oil_Low_Amount]
 ,[Line]
 ,[Model]
 ,'Rotor' as process
,CONVERT(DATETIME,  Convert(nvarchar(50),[Date],120) +' '+ Convert(nvarchar(50),[Time],120)) as Date_Axial_Play
,[Axial_Play_Press_Number]
,CONVERT(DATETIME,  Convert(nvarchar(50),[Date],120) +' '+ Convert(nvarchar(50),[Time],120)) as Date_Oil_Up
,[Oil_Up_number]
,CONVERT(DATETIME,  Convert(nvarchar(50),[Date],120) +' '+ Convert(nvarchar(50),[Time],120)) as Date_Oil_Low
,[Oil_Low_number]
FROM [SPD_Fac2].[dbo].[AxialPlay_Auto_Fac2]
WHERE [AxialPlay_Auto_Fac2].[Date] > DATEADD(DAY,{Date_BT},GETDATE()) )

INSERT INTO [DataforAnalysis].[dbo].[Data_matching]([Barcode],[Axial_Play],[Oil_Top],[Oil_Bottom],[Line],[Model],[Part],[Timestamp]
,[MC_Axial_Play],[Oil_Top_Time],[MC_Oil_Top],[Oil_Bottom_Time],[MC_Oil_Bottom])

SELECT * from Final
where NOT EXISTS (
        SELECT 1
        FROM [DataforAnalysis].[dbo].[Data_matching] dm
        WHERE dm.Barcode = Final.Barcode
       
    );
END

        """

        cursor.execute(query_template)

        # Commit the changes to the database
        conn.commit()

        # Close the database connection
        conn.close()

        print('Data fetch and insert successful.')

    except Exception as e:
        print(f'Error in fetch_data: {e}')

# Call the function
fetch_data()
