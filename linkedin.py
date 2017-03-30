import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from seleniumrequests import Firefox
import time
from time import sleep
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from threading import Thread
import threading
import copy
import csv


my_email = "nlyu2@illinois.edu"
my_pass = "756251901"
my_data_size = 5 #input
my_total_thread = 3 #input
my_ready = -my_total_thread 
my_counter = 0


class myThread (threading.Thread):
	def __init__(self, threadID, driver):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.driver = driver
	
	def run(self):
		global my_data_size, my_ready, my_total_thread
		print("thread ", self.threadID, " start....")
		driver_to_alumini(self.driver)

		name_button = get_person(self.driver)
		
		name_button_str = int((self.threadID - 1) * len(name_button) / my_total_thread)
		name_button_end = int((self.threadID) * len(name_button) / my_total_thread)
		name_button = name_button[name_button_str:name_button_end]

		print("completing geting data, data size is: ", len(name_button))
		print("waiting for the other thread to be completed....")
		threadLock.acquire()
		my_ready = my_ready + 1
		threadLock.release()

		while(my_ready < 0):
			sleep(1)

		print(self.threadID, "start scrapying...")
		get_personal_info_all_parent(self.driver, name_button)
		self.driver.quit()



def init_driver():
	firefox_profile = webdriver.FirefoxProfile()
	firefox_profile.set_preference('permissions.default.image', 2)
	firefox_profile.set_preference("permissions.default.stylesheet", 2);
	firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
	return webdriver.Firefox(firefox_profile=firefox_profile) 


def driver_to_alumini(driver):
	url = "https://www.linkedin.com"
	driver.get(url)

	#2. login in
	login(driver)
	waitForLoad(driver, 1.0)

	#3. get in to uiuc alumini page
	driver.get("https://www.linkedin.com/school/2650/alumni?filterByOption=graduated")
	waitForLoad(driver, 1.0)


def waitForLoad(driver, wait_time):
    elem = driver.find_element_by_tag_name("html")
    count = 0
    while True:
        count += 1
        if count > wait_time:
            return
        time.sleep(1)
        try:
            elem == driver.find_element_by_tag_name("html")
        except StaleElementReferenceException:
            return


def start():
	html = urlopen("https://www.linkedin.com")
	bsObj = BeautifulSoup(html, "html.parser")
	allText = bsObj.findAll("input",{"name":"checksum"})
	checksum=allText[0]['value']
	url="https://secure31.omnimagnet.com/uialumninetwork.org/magnet_sso.php?checksum="+checksum
	return url


def login(driver):
	driver.implicitly_wait(10)
	email = driver.find_element_by_id("login-email")
	password = driver.find_element_by_id("login-password")
	button = driver.find_element_by_id("login-submit")

	email.send_keys(my_email)
	password.send_keys(my_pass)

	button.click()
	return


def sparce_text(i):
	i = i.replace('\nLife Member', '')
	i = i.replace('   ', '\n') 
	return i  


def get_person(driver):
	start= time.time()

	while(True):
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		waitForLoad(driver, 0.5)
		end = time.time()
		if(end - start >= my_data_size):
			break
	name_button=driver.find_elements_by_xpath("//a[@class='Sans-17px-black-85%-semibold']")
	return name_button



def get_personal_info_all_parent(driver, name_button):
	#print("thread begin....")
	window_main = driver.window_handles[0]
	for i in range(0, 3): #................................................
		name_button[i].click()
		print("getting ", i, " person")
		waitForLoad(driver, 1.0)
		window_cur = driver.window_handles[1]
		driver.switch_to_window(window_cur)
		waitForLoad(driver, 1.0)

		get_personal_info(driver, i)
		driver.close()
		driver.switch_to_window(window_main)


def get_personal_info_all_child(driver, name_button):
	#print("thread child begin....")
	window_main = driver.window_handles[0]
	for i in range(0, 3):
		a = name_button[i].get_attribute("href")
		driver.get(a)
		waitForLoad(driver, 2.0)

		get_personal_info(driver, i)

		driver.switch_to_window(window_main)
		driver.close()


def get_personal_info(driver, i):
	global my_counter

	driver.execute_script("window.scrollTo(0, 1500);")
	
	try:
		driver.implicitly_wait(5)
		result_name = driver.find_element_by_xpath("//h1[@class='pv-top-card-section__name Sans-26px-black-85% mb1']")
		result_main = driver.find_element_by_xpath("//section[@class='pv-profile-section experience-section ember-view']")
		result_text = result_main.find_elements_by_xpath("//h3[@class='Sans-17px-black-85%-semibold']")
		result_text1 = result_main.find_elements_by_xpath("//span[@class='pv-position-entity__secondary-title pv-entity__secondary-title Sans-15px-black-55%']")
	except:
		driver.execute_script("window.scrollTo(0, 1800);")

	try:
		driver.implicitly_wait(5)
		result_name = driver.find_element_by_xpath("//h1[@class='pv-top-card-section__name Sans-26px-black-85% mb1']")
		result_main = driver.find_element_by_xpath("//section[@class='pv-profile-section experience-section ember-view']")
		result_text = result_main.find_elements_by_xpath("//h3[@class='Sans-17px-black-85%-semibold']")
		result_text1 = result_main.find_elements_by_xpath("//span[@class='pv-position-entity__secondary-title pv-entity__secondary-title Sans-15px-black-55%']")
	except:
		with csvLock:
			spamwriter.writerow([str(my_counter), result_name.text])
			my_counter += 1
			spamwriter.writerow(['NO INFO'])
			spamwriter.writerow([])  
		return False

	with csvLock:
		spamwriter.writerow([str(my_counter), result_name.text])
		my_counter += 1
		for j in range(0, min(len(result_text), len(result_text1))):
			spamwriter.writerow([result_text[j].text, result_text1[j].text])
		spamwriter.writerow([])   	
	return True


#main 
print('project start1')

#create firfox explorer
threadLock = threading.Lock()
csvLock = threading.Lock()

spamwriter = csv.writer(open('result_final.csv', 'w'), delimiter=',', quoting=csv.QUOTE_MINIMAL)

driver = []
for i in range(my_total_thread):
	driver_temp = init_driver()
	driver.append(driver_temp)

thread = []
for i in range(my_total_thread):
	thread_temp = myThread(i+1, driver[i])
	thread.append(thread_temp)

for i in range(my_total_thread):
	thread[i].start()

for i in range(my_total_thread):
	thread[i].join()
