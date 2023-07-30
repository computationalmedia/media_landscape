'''
Scrape AllSides website to obtain its media bias ratings.

Input data:
    None
    
Output:
    Data/Sec_5_3_Media_Domain_Bias/allsides_media_to_bias.pickle
        AllSides ratings on the media outlets
    Data/Sec_5_3_Media_Domain_Bias/allsides_media_to_comm_feed.pickle
        Community feedback on ratings
    
    Note: the ratings here are on media outlets, not domains.
        
Usage:
    `python Sec_5_3_Media_Domain_Bias/2_allsides/1_scrape_allsides.py`
'''


import time
from bs4 import BeautifulSoup

import pickle
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

ALLSIDES_SOURCE_URL = 'https://www.allsides.com/media-bias/ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B%5D=1&field_news_source_type_tid%5B%5D=2&field_news_source_type_tid%5B%5D=3&field_news_source_type_tid%5B%5D=4&field_news_source_type_tid%5B%5D=5&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title='

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(ALLSIDES_SOURCE_URL)

SCROLL_PAUSE_TIME = 2.0

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
count = 10
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    print("new height: ", new_height)
    if new_height == last_height:
        count -= 1
        if count == 0:
            break
    
    last_height = new_height


page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
media_and_bias = soup.find_all(['td'], {'class': ["views-field views-field-title source-title", "views-field views-field-field-bias-image"] })

community_feedback_w_dup = soup.find_all("span", {"class": ["agree", "disagree" ]})
community_feedback = []
for i in range(0, len(community_feedback_w_dup), 4):
    community_feedback.append( community_feedback_w_dup[i].text)
    community_feedback.append( community_feedback_w_dup[i+1].text )

media_to_bias = {}
media_to_comm_feed = {}

for i in range(0, len(media_and_bias), 2):
    media = media_and_bias[i].text.strip()
    bias = media_and_bias[i+1].find("img")['alt'].replace("AllSides Media Bias Rating: ", "")
    
    media_to_bias[media] = bias
    media_to_comm_feed[media] = [ int(community_feedback[i]), int(community_feedback[i+1]) ]

print(media_to_bias)

# with open(f"Data/Sec_5_3_Media_Domain_Bias/allsides_media_to_bias.pickle", "wb") as f:
#     pickle.dump(media_to_bias, f)
    
# with open(f"Data/Sec_5_3_Media_Domain_Bias/allsides_media_to_comm_feed.pickle", "wb") as f:
#     pickle.dump(media_to_comm_feed, f)

