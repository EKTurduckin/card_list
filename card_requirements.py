import requests
import re
import pandas as pd
from pyperclip import paste
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

def import_list_urls(file_name = "decklist_urls.txt"):
    with open(file_name) as file:
        return file.readlines()

def copy_fabrary_list(url_list):
    raw_list = []
    
    for url in url_list:
        driver = webdriver.Chrome()
        driver.get(url)

        driver.implicitly_wait(5)

        click_ellipsis = driver.find_element(By.CLASS_NAME, "css-hczedi")
        click_ellipsis.click()

        list_to_clipboard = driver.find_element(By.XPATH, './/div[normalize-space()="Copy card list to clipboard"]')
        list_to_clipboard.click()

        sleep(1)

        driver.quit()

        raw_list.append(paste())

    return r"\n".join(raw_list)

def create_card_list(raw_list):
    card_pattern = re.compile("(\d)x ([^(\n]+)(?:\((\w+)\))?")

    decklist_extract = card_pattern.findall(raw_list)

    decklist_formatted = [
        [int(record[0]),
        record[1].strip(),
        int(1) if record[2] == 'red' else
        int(2) if record[2] == 'yellow' else
        int(3) if record[2] == 'blue' else
        int(0)
        ] for record in decklist_extract]
    
    return decklist_formatted

def get_card_library():
    card_sets = {}
    library = requests.get("https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/refs/heads/high-seas/json/english/card-flattened.json").json()

    for record in library:
        if record["pitch"] == "":
            record["pitch"] = 0
        else:
            record["pitch"] = int(record["pitch"])

    set_ids = [(record["name"], record["pitch"], record["set_id"]) for record in library]

    for card in set_ids:
        if (card[0], card[1]) not in card_sets:
            card_sets[(card[0], card[1])] = [card[2]]
        else:
            if card[2] not in card_sets[(card[0], card[1])]:
                card_sets[(card[0], card[1])].append(card[2])

    return card_sets

def aggregate_card(all_cards):
    card_agg = {}
    card_library = get_card_library()

    for record in all_cards:
        if (record[1], record[2]) not in card_agg:
            card_agg[(record[1], record[2])] = {"qty":int(record[0])}
                
        else:
            card_agg[(record[1], record[2])]["qty"] += int(record[0])

    for card, info in card_agg.items():
        info["sets"]= card_library.get(card)
        
    return card_agg

decklist_urls = import_list_urls()
raw_list = copy_fabrary_list(decklist_urls)
all_cards = create_card_list(raw_list)
cards_aggregated = aggregate_card(all_cards)

export = pd.DataFrame.from_dict(cards_aggregated, orient="index").rename_axis(index=["name","pitch"])

export.to_csv("cards.csv")