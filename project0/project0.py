from urllib.request import urlretrieve
import tabula
import json
import pandas
import sqlite3
from sqlite3 import Error

#downloads and saves pdf
def fetchIncidents(url, file_name):
    myTempFile = urlretrieve(url, file_name)
    return myTempFile

def extractIncidents(file_name):
    #get dictionary of top, left, width, height, text
    myJson = tabula.read_pdf(file_name, pages = 1, area = (98.64, 51.12, 576, 734.4), columns = (111.6, 161.28, 239.04, 341.28, 427.28, 464.4, 523.44, 568.08, 599.04, 631.44, 683.28), stream = True, guess = False, output_format = 'json')

    #create list of data dictionary
    myJsonList = myJson[0]['data']

    #create dataframe with dictionary information
    myIndex1 = range(len(myJsonList))
    myIndex2 = range(len(myJsonList[0]))
    myX = range(len(myIndex1)*len(myIndex2))
    myColumns = ['top', 'left', 'width', 'height', 'text']
    myDf = pandas.DataFrame(index = myX, columns = myColumns)
    for i in myIndex1:
        for j in myIndex2:
            for k in myColumns:
                myDf[k].loc[i*len(myIndex2)+j] = myJsonList[i][j][k]
    myDf = myDf[myDf.top != 0]
    myDf = myDf[myDf.height > 2]
    myDf = myDf.sort_values(by = ['left', 'top'])
    myDf = myDf.reset_index(drop = True)

    #create transformed dataframe with only the leftmost column as rows to then add the relative vertical distances from each of the other extractions to the left most column extractions 
    myMin = min(myDf['left'])
    minCount = sum(myDf.left == myMin)
    myX2 = range(minCount)
    myY2 = range(myDf.shape[0])
    myDfDist = pandas.DataFrame(index = myX2, columns = myY2)
    myLeft = [None] * len(myY2)
    myTop = [None] * len(myY2)
    myMinPos = [None] * len(myY2)
    myText = [None] * len(myY2)
    for i in myX2:
        for j in myY2:
            myDfDist.iloc[i, j] = abs(myDf['top'].loc[i] - myDf['top'].loc[j])
            myLeft[j] = myDf['left'].loc[j]
            myTop[j] = myDf['top'].loc[j]
            myText[j] = myDf['text'].loc[j]
    for i in myX2:
        for j in myY2:
            if min(myDfDist.iloc[:, j]) == myDfDist.iloc[i, j]:
                myMinPos[j] = i

    #add Row number based on relative distance to each of the extractions
    myDf2 = pandas.DataFrame()
    myDf2['Left'] = myLeft
    myDf2['Top'] = myTop
    myDf2['Row'] = myMinPos
    myDf2['Text'] = myText
    myDf2 = myDf2.sort_values(by = ['Left', 'Row', 'Top'])
    myDf2 = myDf2.reset_index(drop = True)
    myX3 = range(myDf2.shape[0])

    #create final dataframe adding elements based on left location and Row from relative vertical distance calculation
    myColumns3 = ['Arrest Date / Time', 'Case Number', 'Arrest Location', 'Offense', 'Arrestee', 'Arrestee Birthday', 'Arrestee Address', 'City', 'State', 'Zip Code', 'Status', 'Officer']
    myDf3 = pandas.DataFrame(' ', index = myX2, columns = myColumns3)
    myXCounter = 0
    for i in myX3:
        myYCounter = myDf2['Row'].loc[i]
        if i < minCount:
            myDf3.iloc[i, myXCounter] = myDf2['Text'].loc[i]
        elif myDf2['Left'].loc[i] > myDf2['Left'].loc[i - 1]:
            myXCounter += 1
            myDf3.iloc[myYCounter, myXCounter] = ' '.join([str(myDf3.iloc[myYCounter, myXCounter]), str(myDf2['Text'].loc[i])])
        elif myDf2['Row'].loc[i] == myDf2['Row'].loc[i - 1]:
            myDf3.iloc[myYCounter, myXCounter] = ' '.join([str(myDf3.iloc[myYCounter, myXCounter]), str(myDf2['Text'].loc[i])])
        else:
            myDf3.iloc[myYCounter, myXCounter] = ' '.join([str(myDf3.iloc[myYCounter, myXCounter]), str(myDf2['Text'].loc[i])])
    myArrestsList = myDf3.values.tolist()
    for i in range(len(myArrestsList)):
        for j in range(len(myArrestsList[0])):
            myArrestsList[i][j] = myArrestsList[i][j].strip()
    for i in range(len(myArrestsList)):
        myArrestsList[i][6:10] = [' '.join(myArrestsList[i][6:10])]
    for i in range(len(myArrestsList)):
        for j in range(len(myArrestsList[0])):
            myArrestsList[i][j] = myArrestsList[i][j].strip()
    return myArrestsList

#creates database connection
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        return None

#creates table
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

#creates database and schema
def createDb(db_file):
    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn, ''' CREATE TABLE IF NOT EXISTS arrests (
                                  arrest_time TEXT,
                                  case_number TEXT,
                                  arrest_location TEXT,
                                  offense TEXT,
                                  arrestee_name TEXT,
                                  arrestee_birthday TEXT,
                                  arrestee_address TEXT,
                                  status TEXT,
                                  officer TEXT
                              ); ''')
        conn.close()
    else:
        print('Error!  No DB  connection.')

#populates database with extracted incidents
def populateDb(db_file, incident):
    conn = create_connection(db_file)
    if conn is not None:
        sql = ''' INSERT INTO arrests(arrest_time, case_number, arrest_location, offense, arrestee_name, arrestee_birthday, arrestee_address, status, officer)
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?) '''
        cur = conn.cursor()
        cur.execute(sql, incident)
        conn.commit()
        conn.close()
    else:
        print('Error!  No DB  connection.')

#prints a random tuple in the form of a string with a thorn character separating the attributes
def status(db_file):
    conn = create_connection(db_file)
    if conn is not None:
        sql = ''' SELECT * FROM arrests ORDER BY RANDOM() LIMIT 1 '''
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for r in rows:
            myList = list(r)
            myStr = "\u00FE".join(myList)
            print(myStr)
        conn.close()
        return myStr
    else:
        print('Error!  No DB  connection.')

