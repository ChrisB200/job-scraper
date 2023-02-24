import threading, pymysql, json
import logging
logging.basicConfig(level=logging.WARNING)

# TODO: Need to add more error handling so the program doesn't crash.
# TODO: Need to update variable names.
# TODO: NEED TO LEARN HOW TO USE GIT AND GITHUB.

from companies import companies_list

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

file = open("listings.json", "w")
file.close()
run_companies(companies_list, 4)

#db instance identifier: database-1
#username: admin
#password: PythonAws2023
#port: 3306
#host: database-1.cm0g4ldq4qxz.eu-west-2.rds.amazonaws.com

connection = pymysql.connect(host="database-1.cm0g4ldq4qxz.eu-west-2.rds.amazonaws.com", user="admin", password="PythonAws2023")
cursor = connection.cursor()

with open("listings.json", "r") as file:
    listings = json.load(file)

connection.select_db("sys")

query = "INSERT INTO tblCompanies (jobID, companyName, jobTitle, link, postcode, latitude, longitude, employmentType, contractType, location, hoursPerWeek, salary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

cursor.execute("DELETE FROM tblCompanies")
connection.commit()

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