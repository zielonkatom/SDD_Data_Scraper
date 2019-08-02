from seleniumrequests import Chrome
import time
import bs4
import requests
import csv


url = 'https://database.globalreporting.org'
webdriver = Chrome()
webdriver.implicitly_wait(2)


def scrape_table(max_page):
    """Scrape data for each page from 1 - max_page.'
    Gets necessary links for each organization and each report."""
    count_page = 0
    webdriver.get(url+'/search')
    #  Iterate next pages
    while count_page < max_page:
        main_page_soup = bs4.BeautifulSoup(webdriver.page_source, 'lxml')
        #  Find main table with data
        find_table = main_page_soup.find_all("tbody")[0]
        #  Get a link to company's details.
        organizations_data = find_table.find_all("a", class_="lead")
        # Find all reports links
        reports_data = find_table.select("a[href*=reports]")
        #  Scrape each company
        scrape_organization(organizations_data)
        # Scrape reports for each company
        scrape_reports(reports_data)
        #  Wait a bit
        time.sleep(1)
        #  Click next page to get another list of companies.
        python_button = webdriver.find_element_by_link_text("Next")
        python_button.click()
        # Counter for pages
        count_page += 1


def scrape_reports(report_data):
    """Go through every possible Organization link on the current page.
    Scrape all the data for each company and save it.
    Input: report links
    Output: File with scraped reports data"""
    for rep in report_data:
        # Empty list to store data.
        data_to_be_added = []
        rep_url = url+rep.get('href')
        rep_response = requests.get(rep_url, verify=False)
        rep_response_soup = bs4.BeautifulSoup(rep_response.content, 'lxml')
        #  Get Company name and append it
        org_name = rep_response_soup.find("h3", class_="text-default").text.strip()
        # Get report name
        rep_name = rep_response_soup.find_all('h1', class_='text-slim')[0].text.strip()
        # Get Publication year
        if rep_response_soup.find_all(text="Publication year:"):
            rep_year = rep_response_soup.find_all('span', class_='label label-info label-100')[0].text.strip()
        else:
            rep_year = "N/A"
        # Get Report type
        if rep_response_soup.find_all(text="Report type:"):
            rep_type = rep_response_soup.find_all('span', class_='label label-primary label-100')[0].text.strip()
        else:
            rep_type = "N/A"
        # Get Adherence lever
        if rep_response_soup.find_all(text="Adherence Level:"):
            rep_adh = rep_response_soup.find_all('span', class_='label label-success label-100')[0].text.strip()
        else:
            rep_adh = "N/A"
        # Save all the data to the list
        data_to_be_added.extend([org_name, rep_name, rep_year, rep_type, rep_adh])
        # Write the list to the file
        save_lines_csv('report_data.csv', data_to_be_added)


def scrape_organization(links_data):
    """Go through every possible Organization link on the current page.
    Scrape all the data for each company and save it
    Input: Organization links
    Output: File with scraped organizations data"""
    for link in links_data:
        data_to_be_added = []
        # Create a unique url link for each company and scrape it.
        organ_url = url+"/"+link.get('href')
        organ_response = requests.get(organ_url, verify=False)
        organ_response_soup = bs4.BeautifulSoup(organ_response.content, 'lxml')
        # Get Company name and append it
        organ_name = organ_response_soup.find("h1", class_="card-title")
        data_to_be_added.append(organ_name.text)
        # Get all the details from the table.
        organization_details = organ_response_soup.find_all("li", class_="list-group-item")
        # Iterate the data
        for detail in organization_details:
            data_to_be_added.append(detail.text.split(":")[-1].strip())
        # Now save scraped data as a line to the file.
        save_lines_csv('organ_data.csv', data_to_be_added)


def file_add_org_headers():
    """Create a organ_data.csv file with a header.."""
    header_org = ['Organization', 'Size', 'Type', 'Listed', 'Sector',
                  'Country', 'Country Status', 'Employees', 'Revenue',
                  'GRI GOLD', 'Stock listing code']

    with open('organ_data.csv', 'w', newline='') as csvfile:
        data_writer = csv.writer(csvfile, delimiter='|')
        data_writer.writerow(header_org)


def file_add_rep_headers():
    """Create a report_data.csv file with a header."""
    header_rep = ['Organization', 'Report Name', 'Publication year', 'Report type', 'Adherence level']

    with open('report_data.csv', 'w', newline='') as csvfile:
        data_writer = csv.writer(csvfile, delimiter='|')
        data_writer.writerow(header_rep)
        

def save_lines_csv(filename, data):
    """Write rows to the csv file."""
    with open(filename, 'a', encoding="utf-8", newline='') as csvfile:
        data_writer = csv.writer(csvfile, delimiter='|')
        data_writer.writerow(data)

        
def scrape():
    """Run main part"""
    #  Create a file to store org data
    file_add_org_headers()
    #  Create a file to store rep data
    file_add_rep_headers()
    #  Set the number of pages to scrape
    scrape_table(20)
    print("Scraping finished")
    webdriver.quit()


if __name__ == '__main__':
    scrape()
