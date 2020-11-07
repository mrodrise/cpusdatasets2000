from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import platform
from CpuData import CpuData


def driver_config():

    # If there's any option to configure add here.
    chrome_options = Options()
    # Adding headless mode.
    chrome_options.add_argument("--headless")
    # Detecting current OS to use the correct driver path.
    os = platform.system()
    print("Detected OS:", os)

    # Start chromedriver.
    if os == "Windows":
        inner_driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=chrome_options)
    else:
        inner_driver = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)

    return inner_driver


def get_info_cpus(driver_inner, year_inner):
    # Added delay to prevent 429 errors, and webscrapping being detected.
    t0 = time.time()
    # Loading current year page.
    driver_inner.get(f"https://www.techpowerup.com/cpu-specs/?released={year_inner}&sort=name")
    # Waiting to required web element to load.
    try:
        WebDriverWait(driver_inner, 5).until(lambda s: s.find_element_by_class_name("processors").is_displayed())
    except TimeoutException:
        print("ERROR - TimeoutException: Webpage can't be loaded.")
        return None

    # Getting response delay
    response_delay = time.time() - t0

    # Creating the soup using BeautifulSoup
    soup_inner = BeautifulSoup(driver.page_source, "lxml")

    # Variable used to count the number of CPUs in a year.
    j = 0

    # Searching for the CPU table trying to find the link to detail page.
    for table in soup_inner.select("table.processors"):
        for detail_link in table.select("a"):
            # print(detail_link['href'])
            cpu = CpuData('https://www.techpowerup.com'+detail_link['href'])
            cpu.store_data(dataset_path, include_headers, create_images, img_as_path)
            j += 1
            # Waiting for the delay to avoid 429 codes.
            time.sleep(2*60)
            if j % 100 == 0:
                time.sleep(5*60)

    print("A total of: ", j, " links where found.")

    # Waiting for the delay to avoid 429 codes.
    time.sleep(10 * response_delay)


if __name__ == '__main__':

    # Creating driver object
    driver = driver_config()

    # Opening main CPU webpage there's where we are going to find the data.
    driver.get(f"https://www.techpowerup.com/cpu-specs/?sort=name")

    # Waiting for years selector to load.
    try:
        WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name("processors").is_displayed())
    except TimeoutException:
        print("ERROR - TimeoutException: Webpage can't be loaded.")

    # Creating the soup using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "lxml")

    # Getting years selector
    course_page = soup.find(id='released')

    # Loading possible years.
    years = []
    i = 0
    for year_selector in course_page.find_all("option"):
        if i > 0:
            # print(year_selector['value'])
            years.append(year_selector['value'])
        i = i + 1

    print("Years ", years)

    # Ask for options and selected years
    dataset_path = input("Default path (\"D\") or custom:")
    if dataset_path == "D" or len(dataset_path) < 2:
        dataset_path = 'dataset.csv'
    img_as_path = input("Img as path in dataset (\"Y\") or as BS4 (\"N\") (BS4 could lead to broken lines in dataset):")
    if img_as_path == 'N':
        img_as_path = False
    else:
        img_as_path = True
    create_images = input("Generate images (\"Y\"/\"N\"):")
    if create_images == "N":
        create_images = False
    else:
        create_images = True
    include_headers = input("Include headers (\"Y\"/\"N\"):")
    if include_headers == "N":
        include_headers = False
    else:
        include_headers = True
    selected_years = input("As default dataset will contain all the loaded years, if you prefer to pick just some "
                           "years write them separated by coma for example (2010,2011,2012):")
    if len(selected_years) > 2:
        selected_years_list = selected_years.split(',')
        selected_years_list_clean = []
        for year in selected_years_list:
            if year in years and year not in selected_years_list_clean:
                selected_years_list_clean.append(year)
            else:
                print('Year '+year+' has been removed, incorrect input or not available.')
        if len(selected_years_list_clean) < 1:
            print('Not even 1 year was available, all years will be downloaded.')
            selected_years = None
    else:
        selected_years = None

    # Getting all info from all CPUs in all years.
    for year in years:
        print("***************************")
        print("Year to load: ", year)
        print("***************************")
        search_keyword = year
        get_info_cpus(driver, year)

    # Close the driver.
    driver.close()
