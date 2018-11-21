
import os  
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains

from slackclient import SlackClient
from datetime import date
import time
from time import gmtime, strftime, localtime
import datetime
import sys
import random
import pickle
import json
import subprocess
import io
from contextlib import redirect_stdout
import sys, traceback
from pathlib import Path
import argparse

class Actions(ActionChains):
    def wait(self, time_s: float):
        self._actions.append(lambda: time.sleep(time_s))
        return self

def arguments_from_sys():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--display_mode", help="run code in display mode", action="store_true")
	args = parser.parse_args()
	if args.display_mode:
		return args.display_mode
	else:
		return False

def login(browser):
	
	browser.get('https://www.instagram.com/accounts/login/')
	assert 'Instagram' in browser.title

	time.sleep(2)
	
	elem = browser.find_element_by_name('username')
	elem.clear()
	elem.send_keys(os.environ['IG_USERNAME'])

	elem = browser.find_element_by_name('password')
	elem.clear()
	elem.send_keys(os.environ['IG_PASSWORD'])

	elem = browser.find_element_by_xpath("//*[contains(text(), 'Log in')]")
	elem.click()

	browser.save_screenshot(sys.path[0] + '/debug/login_step.png')

def getLines(fileName):
	f = open(fileName)
	elements = f.readlines()
	f.close()
	return elements

def goToProfiles(browser, profileName):
	base_url = 'https://www.instagram.com/'
	profile_url = base_url + profileName
	browser.get(profile_url)

def findLastPicture(browser, profileName):
	href = ''
	image_id = '/?taken-by='
	profile_length = len(profileName.rstrip()[:-1]) + len(image_id)
	elems = browser.find_elements_by_xpath("//a[@href]")
	for elem in elems:
		elem_href = elem.get_attribute("href")
		if elem_href.find('/p/') >= 25:
			href = elem_href
			break
		else:
			continue
	print('href is ' + href)
	browser.get(href)

def get_comment_input(browser):
	#function used for the new commenting script
	comment_input = browser.find_elements_by_xpath('//textarea[@placeholder = "Add a comment…"]')
	if len(comment_input) <= 0:
		comment_input = browser.find_elements_by_xpath('//input[@placeholder = "Add a comment…"]')
	return comment_input

def commenting(browser, message = 'Lb'):
	# This work on the raspberry pi
	comment_input = get_comment_input(browser)
	if len(comment_input) > 0:
		comment_input[0].clear()
		comment_input = get_comment_input(browser)
		actions = ActionChains(browser)
		actions.move_to_element(comment_input[0])
		actions.click()
		actions.send_keys(message)
		actions.send_keys(Keys.ENTER)
		actions.perform()
	else:
		print('Warning: Comment Action Likely Failed:Comment Element {} not found'.format(comment_input))
	wait()
	return 1

def wait():
	time.sleep(random.uniform(2,5))

def run_time(txt = 'Unicorn!'):
	print('{} {}'.format(txt, strftime("%Y-%m-%d %H:%M:%S", localtime())))

def generate_message(source_path):
	messages = getLines(source_path +'/insta_comments.txt')
	message = random.choice(messages)
	return message.strip()

def browser_object(source_path, display_mode):
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
	
	chromedriver = os.environ['CHROMEDRIVER_PATH']
	chrome_options = Options() 
	chrome_options.binary_location = "{}".format(os.environ['CHROME_BINARY_PATH'])
	chrome_options.add_argument(f'user-agent={user_agent}')
	chrome_options.add_argument('window-size=1200x600')
	if display_mode == False:
		chrome_options.add_argument("--headless")
	browser = webdriver.Chrome(chromedriver, chrome_options=chrome_options)

	return browser

def cookie_handling(browser, display_mode):
	browser.get('https://www.instagram.com')
	cookie_path = 'source/FbCookies_chrome.pkl'

	if Path(cookie_path).is_file():
		with open(cookie_path) as cookiefile:
			cookies = json.load(cookiefile)
			for cookie in cookies:
				browser.add_cookie(cookie) #chrome
		browser.get('https://www.instagram.com/')
		try:
			browser.find_element_by_xpath("//*[contains(text(), 'Log in')]")
			login(browser)
			wait()
			with open(cookie_path, 'w') as outfile:
				json.dump(browser.get_cookies(), outfile)
			return 'Cookie failed. Old school login'
		except:
			return 'Cookie Login'
	else:
		login(browser)
		with open(cookie_path, 'w') as outfile:
			json.dump(browser.get_cookies(), outfile)
		return 'Cannot find cookies. Old school login'

def post_on_slack(message):
	slack_token = os.environ['SLACK_TOKEN']
	sc = SlackClient(slack_token)
	sc.api_call("chat.postMessage",channel = "instabot",text = message)
	return True

def commenting_main_code(source_path, display_mode):
	browser = browser_object(source_path, display_mode)
	print(cookie_handling(browser, display_mode))
	try:
		for i, profile in enumerate(getLines(source_path + '/profilelist.txt')):
			wait()
			print(profile)
			goToProfiles(browser, profile)
			wait()
			findLastPicture(browser, profile)
			wait()
			message = generate_message(source_path)
			commenting(browser, message)
			browser.save_screenshot(sys.path[0] + f'/debug/screen_comment_{i}.png')
			wait()
			print('commented {} on {} profile'.format(message, profile.strip()))
		browser.quit()
	except Exception as e:
		print(e)
		browser.save_screenshot(sys.path[0] + '/debug/runfail_screenshot.png')
		browser.quit()

if __name__ == "__main__":
	source_path = sys.path[0] +'/source'
	display_mode = arguments_from_sys()
	try:
		with io.StringIO() as buf, redirect_stdout(buf): #used to store output values
			run_time('Instastart')
			commenting_main_code(source_path, display_mode)
			run_time('InstaEnd')
			output = buf.getvalue() #Get values from stdr output
		if 'SLACK_TOKEN' in os.environ:
			post_on_slack("```{}```".format(output)) #post output values on Slack
		else:
			print(output)
	except Exception as e:
		print(e)
		if 'SLACK_TOKEN' in os.environ:
			post_on_slack('Slack bot failed running with error: \n ```{}```'.format(traceback.format_exc()))
		else:
			print('Slack bot failed running with error: \n ```{}```'.format(traceback.format_exc()))
