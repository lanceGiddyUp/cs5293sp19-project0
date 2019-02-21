# -*- coding: utf-8 -*-

# url:  http://normanpd.normanok.gov/filebrowser_download/657/Public%20Records%20Archive/January%202019/2019-01-01%20Daily%20Arrest%20Summary.pdf
#
# url:  http://normanpd.normanok.gov/filebrowser_download/657/2019-02-12%20Daily%20Arrest%20Summary.pdf

# Example main.py
import argparse
import project0

db_file = 'normanpd.db'
file_name = 'myTempPDF.pdf'

def main(url):
    # Download data
    file = project0.fetchIncidents(url, file_name)

    # Extract Data
    #incidents = project0.extractIncidents(url)
    incidents = project0.extractIncidents(file_name)

    # Create Dataase
    db = project0.createDb(db_file)

    # Insert Data
    for i in range(len(incidents)):
        project0.populateDb(db_file, incidents[i])

    # Print Status
    project0.status(db_file)

    print("test")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--arrests", type=str, required=True, help="The arrest summary url.")
    args = parser.parse_args()
    if args.arrests:
        main(args.arrests)

