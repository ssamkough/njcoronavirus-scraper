# use "python" to run rather than "py"
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import csv
import re

def getNJCovidStats():
    driver = webdriver.Chrome()
    url = "https://maps.arcgis.com/apps/opsdashboard/index.html#/ec4bffd48f7e495182226eee7962b422"
    # url = "https://maps.arcgis.com/apps/MapSeries/index.html?appid=c2efd1898e48452e83d7218329e953d7"
    driver.get(url)

    timeout = 10
    try:
        featureListXpath = '//*[@id="ember20"]/div[2]/nav'
        elementPresence = EC.presence_of_element_located(
            (By.XPATH, featureListXpath))
        WebDriverWait(driver, timeout).until(elementPresence)
    except TimeoutException:
        print("Timed out waiting for page to load")
    finally:
        print("Page loaded")

    htmlPage = driver.page_source

    soup = BeautifulSoup(htmlPage, 'html.parser')
    featureList = soup.find_all("nav", class_="feature-list")

    # get date
    dateFeatureList = featureList[1]
    dateFeatureList = "<html>" + str(dateFeatureList) + "</html>"

    soup = BeautifulSoup(dateFeatureList, 'html.parser')
    innerDivDate = soup.find("div", class_="external-html")
    innerDivDate = "<html>" + str(innerDivDate) + "</html>"

    soup = BeautifulSoup(innerDivDate, 'html.parser')
    currDate = soup.find("strong")
    currDate = currDate.text[9:]

    # get cases
    caseFeatureList = featureList[2]
    caseFeatureList = "<html>" + str(caseFeatureList) + "</html>"

    countyObjList = []
    countyObj = {}
    soup = BeautifulSoup(caseFeatureList, 'html.parser')

    for emberElem in soup.find_all("span", class_=["flex-horizontal", "feature-list-item", "ember-view"]):
        feature = "<html>" + str(emberElem) + "</html>"
        soup = BeautifulSoup(feature, 'html.parser')
        strongElems = soup.find_all("strong")

        countyObj["name"] = strongElems[0].text.replace(" County", "")
        countyObj["cases"] = strongElems[3].text.replace(u"\xa0", u"")
        countyObj["cases"] = countyObj["cases"].replace(u"\"", u"")
        countyObj["cases"] = countyObj["cases"].replace(u",", u"")
        countyObj["cases"] = re.sub("\D", "", countyObj["cases"])
        countyObjList.append(countyObj)
        countyObj = {}

    # get other attributes
    soup = BeautifulSoup(htmlPage, 'html.parser')
    svgArr = soup.find_all("svg", class_="responsive-text-group")

    # get cases with no county
    casesNoCountyContainer = "<html>" + str(svgArr[1]) + "</html>"
    soup = BeautifulSoup(casesNoCountyContainer, 'html.parser')
    casesNoCounty = soup.find('text').text

    # get total cases
    totalCasesContainer = "<html>" + str(svgArr[5]) + "</html>"
    soup = BeautifulSoup(totalCasesContainer, 'html.parser')
    totalCases = soup.find('text').text

    # get total deaths
    totalDeathsContainer = "<html>" + str(svgArr[7]) + "</html>"
    soup = BeautifulSoup(totalDeathsContainer, 'html.parser')
    totalDeaths = soup.find('text').text

    driver.quit()

    # get description
    description = "As of " + currDate + ", " + totalCases + \
        " people have been confirmed to be tested positive in New Jersey across all 21 counties. There have been " + \
        totalDeaths + " confirmed deaths."
    print(description)

    # exporting and uploading
    with open('covid-cases.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['ID', 'Value'])

        for line in countyObjList:
            writer.writerow([line["name"], line["cases"]])


print("Press enter to get stats:")
input()
getNJCovidStats()
print("Press enter to exit...")
input()
