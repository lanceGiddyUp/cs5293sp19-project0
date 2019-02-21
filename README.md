REFERENCES:

    1) Used this to understand tabula-py package:

        https://github.com/softhints/python/blob/master/notebooks/Python%20Extract%20Table%20from%20PDF.ipynb

    2) Used this to understand how to use sqlite in Python:

        http://www.sqlitetutorial.net/sqlite-python
        https://www.sqlite.org/index.html
        https://www.sqlite.org/pragma.html

    3) Used this to learn how to handle multiple asserts in one pytest method:

        https://stackoverflow.com/questions/43119776/can-i-handle-multiple-asserts-within-a-single-python-pytest-method

    4) Used this to help understand the thorn character in Python

        https://stackoverflow.com/questions/18192672/use-python-to-search-and-replace-thorn-%C3%BE-character-with-pipe

ASSUMPTIONS:

    1) Columns spacing and order will stay unchanged
    2) The left, top, and right border of text stays the same.  The bottom border can shrink or expand.

MODULES:

    1) urllib:  to download and save file
    1) tabula:  to extract text, location, and dimensions
    2) json:  to work with the json dictionary returned by tabula
    3) pandas:  to use dataframes
    4) sqlite:  to use sql databases

HOW TO USE:

    Before running I recommend:  rm normanpd.db normanpdTest.db unless you want to add records to those 2 databases.  My program addes those 2
    databases if they do not exist, but if they do exists records are added.

    From Linux command line enter:  pipenv run python project0/main.py --arrests <url>

        The url I tested most was:  http://normanpd.normanok.gov/filebrowser_download/657/2019-02-12%20Daily%20Arrest%20Summary.pdf

    This runs the main method passing a url to main.  Main then runs fetchIncidents to download and save the pdf locally.  ExtractIncidents
    then uses the pdf to scrape the data using tabula-py to find the locations, size, and text of all the text on the page in a given range.
    I also set the column spaces.  This could be an issue if the Norman PD changes the column spacing.  I deleted all of the extractions what
    had a top of 0 and a width of less than 2 (some of the pages had a small date and time stamp at the bottom, this is how I removed it).
    I then sorted the dataframe by left and top locations so I could use the left most column as my anchor point for relative distance calculations.
    It took a few iterations of sorting and shuffling the dataframes, but I ended up with a dataframe with all the text extractions with thier
    top location, left location, and row that when sorted I could place in a newly created empty dataframe with the same number of rows as
    the number of extractions with the minimum left location and the same number of columns as table attributes.  I then traversed both dataframes
    adding the text to the new dataframe based on its left location and its row based on relative vertical distance from left most columns.  If
    there were multiple extractions with the same left location and row, they were concatenated.  This built a dataframe with the same table as
    the pdf.  Then I converted the dataframe to lists preparing to add them to the database.

    Next I created a database, the schema, and populated the database with the lists and printed a random tuple that I converted to a string replacing
    the comma with a thorn character, \u00FE.

    I did not create an __init__.py file.  To run the methods outside of the main file: from project0 import project0.

HOW TO TEST:

    A test url was chosen and used for all the tests:  http://normanpd.normanok.gov/filebrowser_download/657/2019-02-12%20Daily%20Arrest%20Summary.pdf

    From the command line:  pipenv run python -m pytest

    The test file test_mine.py has 4 test methods:

        1) test_download_sanity()
            This tests to see if something was downloaded
        2) test_fields_incident_match()
            This tests to see if a custom list with the first row of the pdf matches the first element in the list after the extractIncident method
        3) test_create_db_col_names()
            This test to see if the column name in the created database match the heading from the pdf
        4) test_populate_and_thorn()
            This tests to see if the 1st row in the populated database matches the custom string that is the first row of the pdf and it tests
            to see if there are 11 thorn characters in the status return
