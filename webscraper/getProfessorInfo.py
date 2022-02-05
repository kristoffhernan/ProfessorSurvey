

# import libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import config
import pandas as pd
import os
import re


#-----------------------------------------------------------#
# getDriver(url, wndOrmac=0): decides whether to use the 
# settings on the mac or pc, then calls the chrome driver
#-----------------------------------------------------------#
def getDriver(url, wndOrmac=0):
    if wndOrmac == 0:
        myfile = "chromedriver.exe"
        mydir = config.wndDriverDir
    else:
        myfile = "chromedriver"
        mydir = config.macDriverDir

    full_file = os.path.join(mydir, myfile) 

    driver = webdriver.Chrome(full_file) 

    # https://stackoverflow.com/questions/53441658/selenium-in-python-nosuchelementexception-message-no-such-element-unable-to
    # prevents the code from executing before page loads
    driver.maximize_window() # For maximizing window
    driver.implicitly_wait(40) # gives an implicit wait for 40 seconds
    driver.get(url)

    return driver



def getCollegeList(driver):
    wait = WebDriverWait(driver,15)
    
    path = '//mat-panel-title[@class="mat-expansion-panel-header-title ng-tns-c82-{num}"]'
    numb = 14
    list_colleges = []

    # grabs a list of all colleges from the main page
    while True:
        try:
            college_element = wait.until(EC.visibility_of_element_located((By.XPATH, path.format(num = numb)))).text
            # get just the plain college, not ID name
            college = re.sub(r"\([^()]*\)", "", college_element).strip()
            list_colleges.append(college)
            numb += 2
        except (TimeoutException, WebDriverException) as e:
            print("Last department reached")
            break

    # print to check kthe list of colleges
    print(list_colleges)
    return list_colleges


#-----------------------------------------------------------#
# findElements(driver): grabs all the professors names,
# title, dept, email and college and puts it into a df
#-----------------------------------------------------------#
def findElements(driver,search_title_filter, list_colleges):
    wait = WebDriverWait(driver,15)
    
    # empty ls to keep temp data
    temp_data = []

    # loops through each college and grabs the professors from that college
    for college in list_colleges:
        college_filter = wait.until(EC.element_to_be_clickable((By.XPATH, '//mat-placeholder[contains(text(),"Organization/Department")]/../../../input')))
        # driver.find_element(By.XPATH, '//mat-placeholder[contains(text(),"Organization/Department")]/../../../input')
        college_filter.clear()
        college_filter.send_keys(college)
    
        title_filter = wait.until(EC.element_to_be_clickable((By.XPATH, '//mat-placeholder[contains(text(),"Title")]/../../../input')))
        # driver.find_element(By.XPATH, '//mat-placeholder[contains(text(),"Title")]/../../../input')
        title_filter.clear()
        title_filter.send_keys(search_title_filter)

        title_filter.send_keys(Keys.RETURN)

        while True:
            try:
                # checking that all elements are present on the DOM of a page and visible before putting them into variable and looping through
                mat_cards = wait.until(EC.visibility_of_all_elements_located((By.XPATH,'//div[@class="column ng-star-inserted"]')))
                print(f"{college} page is ready!")

                # https://blog.furas.pl/python-selenium-scraping-incomplete-data-gb.html
                # loops through parent mat-cards 
                for card in mat_cards:
                    try: 
                        # uses the card element to find the name
                        name = card.find_element(By.XPATH, './/h5').text
                    except:
                        # if there isnt a name to go with the matcard, then give the name NA
                        name = 'NAN'

                    try:
                        email = card.find_element(By.XPATH, './/a[contains(text(),"ucr.edu")]').text
                    except:
                        email = 'NAN'

                    try:
                        title = card.find_element(By.XPATH, './/em').text
                    except:
                        title = 'NAN'

                    try:
                        department = card.find_element(By.XPATH, './/mat-card-content//strong[not(contains(text(),"Secondary"))]').text
                    except:
                        department = 'NAN'

                    temp_data.append([name,email,title,department,college])

                try:
                    next = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@aria-label="Next page"]')))
                    next.click()
                    print("Navigating to Next Page")

                except (TimeoutException, WebDriverException):
                    # if there isnt a next page, break the loop 
                    print("Last page reached, on to the next College")
                    break

            except (TimeoutException,NoSuchElementException):
                print(f"Loading took too much time and/or no {search_title_filter} on page!")
                break

    temp_df = pd.DataFrame(temp_data,columns=['FullName','Email','Title','Department','College'])
    return temp_df


#-----------------------------------------------------------#
# main(): calls the previous functions, states which website 
# to scrape and saves the df as a csv 
#-----------------------------------------------------------#
def main():
    url = 'https://profiles.ucr.edu/app/home'

    # getDriver(url,0=pc 1=mac)
    driver = getDriver(url, 0)

    list_colleges = getCollegeList(driver)

    df = findElements(driver,'Professor',list_colleges)
    # review df
    print(df.head())
    print(df.shape)

    df1 = findElements(driver,'Lecturer',list_colleges)
    # review df
    print(df1.head())
    print(df1.shape)

    comb = [df,df1]
    results = pd.concat(comb)

    # all pages finished
    # close page
    driver.close()
    driver.quit()

    # convert df to csv
    results.to_csv(config.dataDir, index = False, header=True)


# call main
main()