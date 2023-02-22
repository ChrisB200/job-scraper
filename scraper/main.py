import threading

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
    
    print("completed")

run_companies(companies_list, 4)

print("done")