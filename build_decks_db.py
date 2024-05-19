import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import time  # import the time module
# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Ensure GUI is off
chrome_options.add_argument("enable-automation")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.page_load_strategy = 'eager'

prefs = {"profile.managed_default_content_settings.images": 2, "profile.managed_default_content_settings.stylesheets": 2}
chrome_options.add_experimental_option("prefs", prefs)
webdriver_service = Service(ChromeDriverManager().install())


driver = webdriver.Chrome(service=webdriver_service,options=chrome_options)
driver.set_page_load_timeout(30)  # Set timeout to 10 seconds
import time




def get_deck(link,driver):
    print(f'Gettin deck from {link}')
    start = time.time()
    link = f'https://www.mtggoldfish.com/{link}'
    driver.get(link)
    print('loaded')
    html_content = driver.page_source
    soup = BeautifulSoup(html_content)
    table = soup.find('table')
    rows =table.find_all('tr')
    ns = []
    cards = []
    links = []
    mana = []
    for row in rows:
        if len(row.find_all('td'))>2:
            cols = row.find_all('td')
            ns.append(cols[0].text[1:][:-1])
            card = cols[1].text[1:][:-1]
            link = cols[1].find('a',href=True)['href'][1:]
            cards.append(card)
            links.append(link)
            try:
                mana.append(str(cols[2]).split('"')[1].split(':')[1])
            except:
                mana.append(None)
    print('processed')
    end = time.time()
    print(end - start)
    time.sleep(1)
    return pd.DataFrame({'card':cards,'link':links,'mana':mana,'n':ns})


def get_deck_liks(n,driver):
    all_decks_links = []
    for i in range(1,n):
        try:
            start = time.time()
            link = f'https://www.mtggoldfish.com/deck/custom/commander?page={i}#paper'
            print(link)
            driver.get(link)
            print('loaded')
            html_content = driver.page_source
            soup = BeautifulSoup(html_content)
            links = soup.find_all('a',href=True)
            all_decks_links.extend([link['href'] for link in links if ('paper' in link['href']) and ('deck' in link['href']) and not ('custom' in link['href'])  ])
            end = time.time()
            print(end - start)
        except:
            print(f'issues with page {i}')

    return all_decks_links




deck_links = get_deck_liks(1000,driver)
import os
for link in deck_links:
    try:
        id = link.split('/')[2].split('#')[0]
        file_path= f'decks/{id}.csv'
        if not os.path.isfile(file_path):  
            df = get_deck(link,driver)
            df.to_csv(file_path)
        else:
            print(f'{file_path} already exists, skipping')
    except:
            print(f'issues with deck {link}')

driver.quit()