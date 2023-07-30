'''
Crawl Media Bias/Fact Check website to obtain media bias ratings.
Reference: https://github.com/avalanchesiqi/youtube-crosstalk/blob/main/crawler/1_scrape_mbfc_ratings.py

Input data: 
    None
    
Output:
    Data/Sec_5_3_Media_Domain_Bias/mbfc_ratings.csv
        It contains Title, Category, Image, Country, URL, Domain, Factuality, Credibility, Traffic of media outlets

Usage:
    `python Sec_5_3_Media_Domain_Bias/1_mbfc/1_scrape_mbfc_ratings.py`
'''

import time, requests, re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

MBFC_SOURCE_URL = 'https://mediabiasfactcheck.com/{page}/'

def get_domain(url):
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[len('www.'):]
    return domain


def main():
    fout = open('Data/Sec_5_3_Media_Domain_Bias/mbfc_ratings.csv', 'w')
    fout.write('Title,Category,Img,Country,URL,Domain,Factuality,Credibility,Traffic\n')

    ideology_pages = ['left', 'leftcenter', 'center', 'right-center', 'right', 'fake-news']
    ideology_labels = ['left', 'center-left', 'center', 'center-right', 'right', 'fake-news']
    for ideology_page, ideology_label in zip(ideology_pages, ideology_labels):
        response = requests.get(MBFC_SOURCE_URL.format(page=ideology_page))
        soup = BeautifulSoup(response.text, 'lxml')
        page_table = soup.find('table', {'id': 'mbfc-table'}).find_all('tr')
        for page in page_table:
            try:
                # getting the information for each website
                page = page.find('a', href=True).get('href')

                response2 = requests.get(MBFC_SOURCE_URL.format(page=page))
                html = re.sub(r'<br>|<p>|</p>', '\n', response2.text)
                soup2 = BeautifulSoup(html, 'lxml')
                source_title = soup2.find('h1', {'class': 'page-title'}).text
                # remove dash, comma, and consecutive spaces
                source_title = re.sub('[+,-]', '', source_title).strip()
                print('source title:', source_title)
                print('source ideology:', ideology_label)

                ideology_img = soup2.find_all('img')
                img_filename = ''
                for img in ideology_img:
                    img_url = img.get('data-orig-file')
                    if img_url:
                        if 'mediabiasfactcheck.com/wp-content/uploads/2016/12' in img_url:
                            img_filename = img_url.rsplit('/', 1)[1].split('?', 1)[0]
                            print('ideology img:', img_filename)
                            break

                country = 'NA'
                website_url = 'NA'
                domain = 'NA'
                factual_report = 'NA'
                credibility_rating = 'NA'
                populartiy_level = 'NA'
                for line in soup2.text.split('\n'):
                    country_pattern = r'Country:\s[a-zA-Z]+'
                    source_pattern = r'Sources?:\shttps?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    factual_pattern = r'Factual Reporting:\s[a-zA-Z]+'
                    credible_pattern = r'MBFC Credibility Rating:\s[a-zA-Z]+'
                    popularity_pattern = r"Traffic/Popularity:\s[a-zA-Z]+"
                    if bool(re.match(country_pattern, line)):
                        country = line.rstrip().split(':')[1].split('(')[0].strip()
                        if country == 'Unknown':
                            country = 'NA'
                        elif country == 'USA':
                            country = 'United States'
                    elif bool(re.match(source_pattern, line)):
                        website_url = line.rstrip().split(':', 1)[1].strip()
                        domain = get_domain(website_url)
                    elif bool(re.match(factual_pattern, line)):
                        factual_report = line.rstrip().split(':')[1].strip()
                    elif bool(re.match(credible_pattern, line)):
                        credibility_rating = line.rstrip().split(':')[1].strip()
                    elif bool(re.match(popularity_pattern, line)):
                        populartiy_level = line.rstrip().split(':')[1].strip()

                print('country:', country)
                print('website url:', website_url)
                print('domain:', domain)
                print('factuality: ', factual_report)
                print('credibility: ', credibility_rating)
                print('popularity: ', populartiy_level)

                fout.write('{0},{1},{2},{3},{4},{5},{6},{7},{8}\n'
                           .format(source_title, ideology_label, img_filename,
                                   country, website_url, domain, factual_report, credibility_rating, populartiy_level))
                print()
                time.sleep(1)
            except Exception as e:
                print('>>> failed crawling with messages:', str(e))
                continue

    fout.close()


if __name__ == '__main__':
    main()
