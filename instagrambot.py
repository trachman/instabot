import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from sys import argv as args
""" this is practice dev area for the instagram bot """

class Bot:
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.driver = webdriver.Chrome()
		url = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
		path_to_login = '/html/body/div[1]/section/main/div/article/div/div[1]/div/form/div[4]/button'
		path_to_login = '/html/body/div[1]/section/main/div/article/div/div[1]/div/form/div[4]/button'
		path_to_dismiss = '/html/body/div[4]/div/div/div[3]/button[2]'
		path_to_mypage = '/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[5]/a'
		self.driver.get(url)
		time.sleep(1)
		self.driver.find_element_by_name('username').send_keys(self.username)
		self.driver.find_element_by_name('password').send_keys(self.password)	
		self.driver.find_element_by_xpath(path_to_login).click()
		time.sleep(5)
		self.driver.find_element_by_xpath(path_to_dismiss).click()
		self.driver.find_element_by_xpath(path_to_mypage).click()
		time.sleep(5)

	def quit_driver(self):
		""" shuts down the driver """
		self.driver.quit() 

	def go_home_from_list(self):
		""" return home from the pop-up list view """
		exit_path = "/html/body/div[4]/div/div[1]/div/div[2]/button"
		self.driver.find_element_by_xpath(exit_path).click()
		time.sleep(1)

	"""
	The next two methods are to scrape my following and follower lists
	"""
	def get_followers(self):
		self.driver.find_element_by_xpath("//a[contains(@href, '/followers')]").click()
		time.sleep(3)
		scroll_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]")
		last_ht, ht = 0,1
		while last_ht != ht:
			last_ht = ht 
			time.sleep(3)
			ht = self.driver.execute_script(
			"""
			arguments[0].scrollTo(0, arguments[0].scrollHeight);
			return arguments[0].scrollHeight;
			""", scroll_box)
		time.sleep(3)
		initial_list_of_followers = self.driver.find_elements_by_xpath("/html/body/div[4]/div/div[2]/ul")
		list_of_followers = initial_list_of_followers[0].find_elements_by_tag_name("a")
		cleaned = []
		for name in list_of_followers:
			if name.text != "":
				cleaned.append(name.text)
		self.go_home_from_list() 
		return cleaned

	def get_following(self):
		self.driver.find_element_by_xpath("//a[contains(@href, '/following')]").click()
		time.sleep(3)
		scroll_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]")
		last_ht, ht = 0,1
		while last_ht != ht:
			last_ht = ht 
			time.sleep(3)
			ht = self.driver.execute_script(
			"""
			arguments[0].scrollTo(0, arguments[0].scrollHeight);
			return arguments[0].scrollHeight;
			""", scroll_box)
		time.sleep(3)
		initial_list_of_following = self.driver.find_elements_by_xpath("/html/body/div[4]/div/div[2]/ul")
		list_of_following = initial_list_of_following[0].find_elements_by_tag_name("a")
		cleaned = []
		for name in list_of_following:
			if name.text != "":
				cleaned.append(name.text)
		self.go_home_from_list() 
		return cleaned

	def write_to_db(self, file_location, data):
		""" writes and formats data """
		with open(file_location, 'w+') as file:
			for i, line in enumerate(data):
				if i == len(data)-1:
					file.write(line)
				else:
					file.write(line + '\n')
	
	""" 
	Following two functions are pointer functions which tells write_to_db where and what to write
	"""
	def update_follower_db(self, file_location):
		current_followers = self.get_followers()
		self.write_to_db(file_location, current_followers)

	def update_following_db(self, file_location):
		current_following = self.get_following()
		self.write_to_db(file_location, current_following)	

	def db_shutdown(self):
		""" gets run only when unfollowers are checked and updated """
		db_location = '/Users/tristanrachman/Dev/Dashboard/instagram_database/'
		new_files = [db_location+'followers.txt', db_location+'following.txt']
		legacy_files = [db_location+'previous_followers.txt', db_location+'previous_following.txt']
		for i, file in enumerate(new_files):
			shutil.copy(file, legacy_files[i])

	def clean(self, arr):
		""" Helper method to clean elements of arrays with '\n' appended to them """
		cleaned = []
		for item in arr:
			cleaned.append(item.split('\n')[0])
		return cleaned

	def update_no_follow_back(self):
		current_followers = '/Users/tristanrachman/Dev/Dashboard/instagram_database/followers.txt'
		current_following = '/Users/tristanrachman/Dev/Dashboard/instagram_database/following.txt'
		no_follow_back = '/Users/tristanrachman/Dev/Dashboard/instagram_database/usersthatdontfollowback.txt'

		with open(current_followers, 'r') as file:
			followers_dirty = file.readlines()
		with open(current_following, 'r') as file:
			following_dirty = file.readlines()

		followers = self.clean(followers_dirty)
		following = self.clean(following_dirty)
		guilty = []
		for name in following:
			if name not in followers:
				guilty.append(name)
		
		with open(no_follow_back, 'w+') as file:
			for i, name in enumerate(guilty):
				if i == len(guilty)-1:
					file.write(name)
				else:
					file.write(name+'\n')

	def update_unfollowers(self):
		""" Update unfollowers """
		current_followers = '/Users/tristanrachman/Dev/Dashboard/instagram_database/followers.txt'
		legacy_followers = '/Users/tristanrachman/Dev/Dashboard/instagram_database/previous_followers.txt'
		unfollowers = '/Users/tristanrachman/Dev/Dashboard/instagram_database/unfollowers.txt'
		
		with open(current_followers, 'r') as file:
			current_followers_ls_dirty = file.readlines()
		with open(legacy_followers, 'r') as file:
			legacy_followers_ls_dirty = file.readlines()
		with open(unfollowers, 'r') as file:
			unfollowers_ls_dirty = file.readlines()
		
		current_followers_ls = self.clean(current_followers_ls_dirty)
		legacy_followers_ls = self.clean(legacy_followers_ls_dirty)
		unfollowers_ls = self.clean(unfollowers_ls_dirty)

		guilty = []
		for name in legacy_followers_ls:
			if name not in current_followers_ls:
				guilty.append(name)
				print(name)

		with open(unfollowers, 'a') as file:
			for i, name in enumerate(guilty):
				if name not in unfollowers_ls:
					if i == 0 and len(unfollowers_ls) == 0:
						file.write(name)
					else:
						file.write('\n'+name)

if __name__ == "__main__":
	""" Database locations """
	current_followers = '/Users/tristanrachman/Dev/Dashboard/instagram_database/followers.txt'
	current_following = '/Users/tristanrachman/Dev/Dashboard/instagram_database/following.txt'
	unfollowers = '/Users/tristanrachman/Dev/Dashboard/instagram_database/unfollowers.txt'
	
	""" Methods """
	# a slice of the first two user entered arguments
	username, password = args[1:3]
	print(username, password)
	# instabot = Bot(username, password)
	# instabot.update_follower_db(current_followers)
	# instabot.update_following_db(current_following)
	# instabot.update_unfollowers()
	# instabot.update_no_follow_back()
	
	# closing process
	# time.sleep(2)
	# instabot.db_shutdown()
	# instabot.quit_driver()

	"""
	TODO:
	- create a map to store as much personal account data as possible on everyone
	- login system to check other accounts, use database to organize by account, aka create a new db if a new account is used to login
	- unfollowers list
	- who you follow but they don't follow you back 
	- incorporate password hashing into this

	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	code snippets which may be useful later on 
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# seems to be no suggested at this moment, save this code here just incase the suggested comes back to instagram
		# suggested = driver.find_element_by_xpath("//h4[contains(text(), 'Suggestions')]")
		# driver.execute_script('arguments[0].scrollIntoView()', suggested)
	"""
