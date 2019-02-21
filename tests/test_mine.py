import pytest
from project0 import project0

url = 'http://normanpd.normanok.gov/filebrowser_download/657/2019-02-12%20Daily%20Arrest%20Summary.pdf'
file_name = 'myTempPDFTest.pdf'
incident0 = ['2/9/2019 13:30', '2019-00011024', '1215 E ROBINSON ST', 'PUBLIC INTOX / CONSUMING INTOX BEV - SPIRTS', 'MARK ANTHONY MONTANO II', '11/10/1992', 'HOMELESS', 'FDBDC (Jail)', '1827 - Atteberry;']
db_file = 'normanpdTest.db'

def test_download_sanity():
    myDownload = project0.fetchIncidents(url, file_name)
    assert myDownload is not None

def test_fields_incident_match():
    myList = project0.extractIncidents(file_name)
    assert myList[0] == incident0

def test_create_db_col_names():
    project0.createDb(db_file)
    conn = project0.create_connection(db_file)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(arrests)")
    myTemp = cur.fetchall()
    myList = []
    for i in range(len(myTemp)):
        myList.append(myTemp[i][1])
    colNames = ','.join(myList)
    conn.close()
    assert colNames == 'arrest_time,case_number,arrest_location,offense,arrestee_name,arrestee_birthday,arrestee_address,status,officer'

def test_populate_and_thorn():
    incidents = project0.extractIncidents(file_name)
    for i in range(len(incidents)):
        project0.populateDb(db_file, incidents[i])
    conn = project0.create_connection(db_file)
    cur = conn.cursor()
    sql = '''SELECT * FROM arrests ORDER BY ROWID ASC LIMIT 1'''
    cur.execute(sql)
    row = cur.fetchall()
    myList = list(row[0])
    myStr = project0.status(db_file)
    numThorn = myStr.count('\u00FE')
    conn.close()
    assert (myList, numThorn) == (incident0, 8)

