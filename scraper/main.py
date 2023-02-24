import threading
import pymysql
import json

from companies import companies_list
from logger import Logger

logger = Logger("info")

# Runs a specified amount of threads at a time
def run_companies(companies_list, number_of_threads):
    semaphore = threading.Semaphore(number_of_threads)
    threads = []
    for company in companies_list:
        semaphore.acquire()
        t = threading.Thread(target=company)
        t.start()
        threads.append(t)
        semaphore.release()
        
    for t in threads:
        t.join()

# Resets listings file before running it
file = open("listings.json", "w")
file.close()

# Runs companies from companies folder
run_companies(companies_list, 4)

# DATABASE INSERTION
connection = pymysql.connect(host="database-1.cm0g4ldq4qxz.eu-west-2.rds.amazonaws.com", user="admin", password="PythonAws2023")
cursor = connection.cursor()

# Reads JSON file
with open("listings.json", "r") as file:
    listings = json.load(file)

# Creates query structure
connection.select_db("sys")
query = "INSERT INTO tblCompanies (jobID, companyName, jobTitle, link, postcode, latitude, longitude, employmentType, contractType, location, hoursPerWeek, salary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

# Deletes previous records from tblCompanies
cursor.execute("DELETE FROM tblCompanies")
connection.commit()

# Inserts values into query structure
for listing in listings:
    values = (listing["Id"], 
              listing["Company"], 
              listing["Job Title "], 
              listing["Link"], 
              listing["Postcode"], 
              listing["Latitude"], 
              listing["Longitude"], 
              listing["Employment Type"], 
              listing["Contract Type"], 
              listing["Location"], 
              listing["Hours per Week"], 
              listing["Salary"])
    
    cursor.execute(query, values)
    connection.commit()