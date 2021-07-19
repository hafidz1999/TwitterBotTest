import csv
import time
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions

def get_tweet_data(card):
    """"extract data from tweet card"""
    username = card.find_element_by_xpath('.//span').text
    handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    try:
        postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except NoSuchElementException:
        return
    comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    text = comment + responding
    reply_cnt = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
    retweet_cnt = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    like_cnt = card.find_element_by_xpath('.//div[@data-testid="like"]').text

    tweet = (username, handle, postdate, text, reply_cnt, retweet_cnt, like_cnt)
    return tweet

#start webdriver edge
options = EdgeOptions()
options.add_argument("start-maximized")
options.use_chromium = True
driver = Edge(options=options)

#login
def account_info():
    with open('account_info.txt', 'r') as f:
        info = f.read().split()
        email = info[0]
        password = info[1]
    return email, password

email , password = account_info()

driver.get('https://www.twitter.com/login')
time.sleep(1)
username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
username.send_keys(email)
time.sleep(1)
my_password = driver.find_element_by_xpath('//input[@name="session[password]"]')
my_password.send_keys(password)
time.sleep(1)
my_password.send_keys(Keys.RETURN)
time.sleep(1)

#bypass verificator because too much attempt when testing the bot
def account_info_ver():
    with open('account_info_ver.txt', 'r') as g:
        info1 = g.read().split()
        email1 = info1[0]
        password1 = info1[1]
    return email1, password1

email1 , password1 = account_info_ver()

time.sleep(1)
username1 = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
username1.send_keys(email1)
time.sleep(1)
my_password1 = driver.find_element_by_xpath('//input[@name="session[password]"]')
my_password1.send_keys(password1)
time.sleep(1)
my_password1.send_keys(Keys.RETURN)
time.sleep(1)

#search input for 'shopping'
time.sleep(1)
search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
search_input.send_keys('Shopping')
time.sleep(1)
search_input.send_keys(Keys.RETURN)

#to 'latest' tab
#time.sleep(1)
#driver.find_element_by_link_text('Latest').click()

#get the tweet
data = []
tweet_ids = set()
last_position = driver.execute_script("return window.pageYOffset;")
scrolling = True

while len(data) <= 10:
    while scrolling:
        time.sleep(1)
        page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
        for card in page_cards[-15:]:
            tweet = get_tweet_data(card)
            if tweet:
                tweet_id = ''.join(tweet)
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    data.append(tweet)

        scroll_attempt = 0
        while True:
            # check position of scroll
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(1)
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1

                #end of scroll area
                if scroll_attempt >= 3:
                    scrolling = False
                    break
                else:
                    time.sleep(2)
            else:
                last_position = curr_position
                break

#Save data
time.sleep(1)
with open('tweet_shopping_scrap.csv', 'w', newline='', encoding='utf-8') as h:
    header = ['Username', 'Handle', 'Timestamp', 'Comments', 'Likes', 'Retweets', 'Text']
    writer = csv.writer(h)
    writer.writerow(header)
    writer.writerows(data)