# Download the helper library from https://www.twilio.com/docs/python/install
import os
import requests
import datetime as dt
from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime

chrome_options = Options()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--lang=en")
chrome_options.headless = True
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
 
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_IN-STOCK_SID']
auth_token = os.environ['TWILIO_IN-STOCK_AUTH_TOKEN']
client = Client(account_sid, auth_token)

# Get environment var for phone numbers
personal_num = os.environ['PERSONAL_NUM']
twilio_num = os.environ['TWILIO_IN-STOCK_NUM']

driver.get("https://www.quebec.ca/en/health/health-issues/a-z/2019-coronavirus/situation-coronavirus-in-quebec/")

# Date format functions
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# Get data with proper format
date = custom_strftime('%B {S}, %Y', datetime.now())

# Get general data
element = None
count = 0
while(element == None and count != 5):
    try:
        element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "c67129"))
        )
    except TimeoutException:
        count += 1
        driver.refresh()

if count >= 5:
    print("Max refresh general data!")


table1 = driver.find_element_by_id("c67129")
dailyStats = table1.find_elements_by_tag_name('tr')
data = dailyStats[-1].find_elements_by_tag_name('td')

# Create body message
bod = ("Quebec COVID-19 stats for " + date + ":\n" 
    + "Confirmed cases: " + data[1].text + "\n" 
    + "Deaths: " + data[2].text + "\n" 
    + "Hospitalizations: " + data[3].text + "\n" 
    + "ICU: " + data[4].text + "\n")

#for ele in data:
#    print(ele.text)

# Get Vaccine Data
driver.get("https://www.quebec.ca/en/health/health-issues/a-z/2019-coronavirus/situation-coronavirus-in-quebec/covid-19-vaccination-data/")
element = None
count = 0
while(element == None and count != 5):
    try:
        element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "contenttable"))
        )
    except TimeoutException:
        count += 1
        driver.refresh()

if count >= 5:
    print("Max refresh vaccine data!")

#table2 = driver.find_element_by_class_name("contenttable")
#vaccineStats = table2.find_elements_by_tag_name('tr')
#vaccinesAdmin = vaccineStats[1].find_element_by_tag_name('p')

#for ele in vaccineStats:
#    print(ele.text)

#bod = bod + ("Doses of vaccine: " + vaccinesAdmin.text + "\n")

print(bod)
driver.close()

message = client.messages \
        .create(
                body= bod,
                from_= twilio_num,
                to= personal_num
             )

#print(message.sid)
#print(message)

