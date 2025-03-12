import re
import requests
import pandas as pd

def fabrary_list_import(file):

    with open(file, encoding="utf-8") as file:
        battle_box = file.read()

    card_pattern = re.compile("(\d)x ([^(\n]+)(?:\((\w+)\))?")

    card_list = [[int(count), card, pitch] for count, card, pitch in re.findall(card_pattern, battle_box)]

    for idx, record in enumerate(card_list):
        if record[2] == '':
            card_list[idx].append(None)
        elif record[2] == 'red':
            card_list[idx].append(int(1))
        elif record[2] == 'yellow':
            card_list[idx].append(int(2))
        elif record[2] == 'blue':
            card_list[idx].append(int(3))
            
    return card_list

def get_card_library():
    library = requests.get("https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/refs/heads/develop/json/english/card-flattened.json").json()
    
    for card in library:
        if card["pitch"] == '':
            card["pitch"] = None
        else:
            card["pitch"] = int(card["pitch"])
    
    return library

battle_box = fabrary_list_import("Battle Box.txt")
card_library = get_card_library()

for card in battle_box:
    sets = []
    for entry in card_library:
        if card[1].strip() == entry["name"] and card[3] == entry["pitch"]:
            if entry["set_id"] not in sets:
                sets.append(entry["set_id"])
    card.append(sets)

battle_box_df = pd.DataFrame().from_records(battle_box, columns=["qty","name","pitch_name","pitch_value","sets"])

battle_box_df.to_clipboard(index=False)
