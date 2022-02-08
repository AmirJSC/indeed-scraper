import requests
import bs4
import datetime
import re
import pandas as pd
import sqlite3
from dash_code import visualize


main_url = 'https://ph.indeed.com'


def get_url(job, location):
    url = main_url + f'/jobs?q={job}&l={location}&sort=date'
    return url


def next_page():
    job_listings = main_soup.select('.pagination li a')
    try:
        #Pagination-list - Page 1, Page 2, Page 3, Page 4, Next
        #This will get the last pagination-list link (Next)
        next_page_url = main_url + job_listings[-1].get('href')
        return next_page_url
    except:
        return False


#Converts the date to YYYY-MM-DD
def date_conversion(date_posted):
    current_date = datetime.date.today()
    mo = re.compile(r'[\+]? day(s)? ago')
    if date_posted.lower() == 'just now':
        date_posted = current_date
    elif date_posted.lower() == 'today':
        date_posted = current_date
    elif date_posted.lower() == 'just posted':
        date_posted = current_date
    elif int(mo.sub('',date_posted)) < 30:
        days_ago = int(mo.sub('',date_posted))
        date_posted = current_date - datetime.timedelta(days=days_ago)
    else:
        return date_posted
    return date_posted

    
def scrape_data():
    # Select the job postings in the page
    job_listings = main_soup.select('a[data-hiring-event]')

    for job_listing in job_listings:
        data = list()
        job_title = job_listing.select_one('.jobTitle').getText()
        if job_title.startswith('new'):
            job_title = job_title.strip('new')
        data.append(job_title)
        try:
            company_name = job_listing.select_one('.companyName').getText()
        except:
            company_name = ''
        data.append(company_name)
        try:
            company_location = job_listing.select_one('.companyLocation').getText()
        except:
            company_location = ''
        data.append(company_location)
        try:
            salary = job_listing.select_one('.salary-snippet').getText()
        except:
            salary = ''
        data.append(salary)
        try:
            date_posted = job_listing.select_one('.date').getText()
            date_posted = date_conversion(date_posted)
        except:
            date_posted = ''
        data.append(date_posted)
        date_extracted = datetime.date.today()
        data.append(date_extracted)
        data = tuple(data)
        main_data.append(data)


def main_func(job, location):
    global main_soup
    global main_data
    global links
    links = list()
    main_data = list()

    # Get the first page
    url = get_url(job, location)
    links.append(url)
    r = requests.get(url)
    print(r.status_code)

    # save_html('C:\\Pythoncode\\tutorial\\indeed_data1', r.content)
    main_soup = bs4.BeautifulSoup(r.content, 'html.parser')

    while True:
        scrape_data()
        next_page_url = next_page()
        #This will break when it gets to the last pagination-list page as this 
        #page's url is already in the links list
        if next_page_url in links:
            break
        else:
            links.append(next_page_url)
        r = requests.get(next_page_url)
        main_soup = bs4.BeautifulSoup(r.content, 'html.parser')
    
    return main_data


def insert_data_to_sqlite(main_data):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS indeed_data
                    (id INTEGER PRIMARY KEY, job_title TEXT, company_name TEXT,
                    company_location TEXT, salary TEXT, date_posted DATE,
                    date_extracted DATE)''')

    cursor.executemany('''INSERT INTO indeed_data (job_title, company_name,
                       company_location, salary, date_posted, date_extracted) VALUES (?,?,?,?,?,?)''', main_data)
    cursor.execute('''DELETE FROM indeed_data WHERE id NOT IN (SELECT min(id) FROM indeed_data GROUP 
    BY job_title, company_location, company_name, salary, date_posted)''')

    #Exports sqlite to pandas
    db_df = pd.read_sql_query('SELECT * FROM indeed_data', conn)
    db_df.to_csv(f'{location}_{job}_jobs_db.csv', index=False)

    conn.commit()


if __name__ == '__main__':
    job = input('Enter the job postings to scrape: ')
    location = input('Enter the location of the job postings: ')
    # job search settings
    main_func(job, location)
    sql_database = f'{location}_{job}_jobs_db'
    conn = sqlite3.connect(f'{sql_database}.sqlite')
    insert_data_to_sqlite(main_data)
    visualize(f'{sql_database}.csv')


 
    
    


    


