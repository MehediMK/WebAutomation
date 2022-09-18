# import requirement library
import requests
from bs4 import BeautifulSoup as soup

# library for selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
service_obj = Service(executable_path='D:/Mehedi/w3/selenium/chromedriver.exe')
import time

# library for mysql
import pymysql
from db import *
connection = pymysql.connect(host=host,user=user,passwd=password,db=db)
cursor = connection.cursor()


# all data here
final_output = dict()


# assign url
def get_content(site_url):
  url = site_url
  # get ur content
  html = requests.get(url).content
  return soup(html,'html.parser')


# here call get_content function for start page html content
sp = get_content('https://www.kayak.co.in/')


# get all Location name
locations = []
for name in sp.find_all(class_='P_Ok-wrapper'):
  # all location append in the list
  locations.append(name.find(class_="P_Ok-title").get_text())

# main div for location(index can be change)
# sp.find_all(class_='P_Ok-wrapper')[5]

# display all location for choice location
for location in range(len(locations)):
  print(location+1,"-",locations[location])



# here user enter location number to find location details
locationNumber = int(input('Enter you location Number: '))
if len(locations)<locationNumber:
  locationNumber = int(input("Please Enter valid Number: "))
else:
  find_location = sp.find_all(class_='P_Ok-wrapper')[locationNumber-1].find(class_="P_Ok-title").get_text()
  print("You choice: "+find_location)


# find hotel url
hotel_url = "https://www.kayak.co.in"+sp.find_all(class_='P_Ok-wrapper')[locationNumber-1].find(class_='P_Ok-header-links').find_all('span')[2].find('a').get('href')
print(hotel_url)


# here will get hotels list by location
second_page = get_content(hotel_url)
print("second_page")

# target hotes list body
hotels_items_body = second_page.find(class_="c09SH-right-side").find(class_="c44F").find_all(class_='soom')

# get all hotels name
hotels_name = list()
for h_len in range(len(hotels_items_body)):
  # get hotel name one by one
  hotel_name = hotels_items_body[h_len].find(class_='soom-description').find('a').get_text()
  # append hotel name in list
  hotels_name.append(hotel_name)
  # display hotels for choice nubmer
  print(str(h_len+1)+"- "+hotel_name)


# take input hotel number from user
hotel_number = int(input("Enter hotel Nuber: "))

# this variable assign for valid input check 
again_input = True

while again_input:
  if (hotel_number>len(hotels_name)):
    hotel_number = int(input("Please Enter valid number: "))
  else:
    again_input=False
    
get_hotel_name = hotels_items_body[hotel_number-1].find(class_='soom-description').find('a').get_text()
print("Hotel Name:",get_hotel_name)

# =============HOTEL NAME STORED==================
final_output['hotel_name'] = get_hotel_name


# get hotel details url
hotel_url = hotels_items_body[hotel_number-1].find(class_='soom-description').find('a').get('href')

hotel_details_url = ""
if hotel_url != '#':
  hotel_details_url = "https://www.kayak.co.in"+hotel_url
  # print hotel url
  print("Hotel Detail Page URL:",hotel_details_url)
else:
  print("Hotel Details url Not Found")



# get hotel id from url
import re
get_hotel_id = int(''.join(re.findall("\d", hotel_details_url)))
print("Hotel ID:",get_hotel_id)

# =========HOTEL ID STORED=============
final_output['hotel_id'] = get_hotel_id

# get hotes detail page content by url
hotel_details_page = get_content(hotel_details_url).prettify()
print("hotel_details_page")



# =======Start selenium===============

driver = webdriver.Chrome(service = service_obj)

# function for open browser
def start_driver(details_url):
    driver.get(details_url)
    driver.maximize_window()
    driver.implicitly_wait(3)

def maindriver():
    
    # open popup window
    driver.find_element(By.CLASS_NAME,value='FH8P-main-thumbnail').click()
    # get all buttons
    button = driver.find_element(By.CLASS_NAME,value='DTct-categories-container').find_elements(By.CLASS_NAME,value='DTct-category')

    time.sleep(3)
    button[0].click()
    # get button image number and if section for grater then 1
    image_number = int(button[0].find_element(By.TAG_NAME,value='span').text)
    print("Total Image:",image_number)
    lists = driver.find_element(By.CLASS_NAME,value="ZVFD-dots-container").find_elements(By.TAG_NAME,value='button')
    
    hotel_label = list()
    hotel_image_url = list()
    # here try to getting all images
    for i in range(len(lists)):
        if len(lists) >11:

            time.sleep(3)
            # if i==0:
            #   lists[i].click()
            # get image tag
            query = lists[i].find_element(By.TAG_NAME,value='img')
            print(i+1,") {Alt : '",query.get_attribute('alt'),"', Src : '",query.get_attribute('src'),"}")
            label = query.get_attribute('alt')
            image_url = query.get_attribute('src')
            hotel_label.append(label)
            hotel_image_url.append(image_url)
            if (len(lists)-1)>i:
                lists[i+1].click()

        else:
            query = lists[i].find_element(By.TAG_NAME,value='img')
            print(i+1,") {Alt : '",query.get_attribute('alt'),"', Src : '",query.get_attribute('src'),"}")
            
            label = query.get_attribute('alt')
            image_url = query.get_attribute('src')
            hotel_label.append(label)
            hotel_image_url.append(image_url)
    
    final_output['hotel_label'] = hotel_label
    final_output['hotel_image_url'] = hotel_image_url
    

    print("Hotel Labels: ",hotel_label,"\nHotel Image URLs:",hotel_image_url)


        


def stop_driver():
    time.sleep(4)
    driver.quit()

if __name__ == '__main__':
    start_driver(hotel_details_url)
    maindriver()
    stop_driver()

    print(final_output)

# ============databse=========

# query = "select * from hotel;"

for co in range(len(final_output['hotel_image_url'])):
    dbquery = f"insert into hotel (name,hotelid,label,imageurl) values('{final_output['hotel_name']}',{final_output['hotel_id']},'{final_output['hotel_label'][co]}','{final_output['hotel_image_url'][co]}');"

    cursor.execute(dbquery)

print(cursor.rowcount," Successfully inserted")
connection.commit()
connection.close()