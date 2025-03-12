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

def total_cards(import_file):
    output = {}

    for record in import_file:
        if not record[2]:
            pitch = None
        else:
            pitch = record[2]

        if (record[1], pitch) not in output:
            output[(record[1], pitch)] = record[0]
        else:
            output[(record[1], pitch)] += record[0]
    
    return output

def get_card_library():
    library = requests.get("https://raw.githubusercontent.com/the-fab-cube/flesh-and-blood-cards/refs/heads/develop/json/english/card-flattened.json").json()
    
    for card in library:
        if card["pitch"] == '':
            card["pitch"] = None
        else:
            card["pitch"] = int(card["pitch"])
    
    return library

def get_sets(import_file):
    output = {}
    card_library = get_card_library()

    for record in import_file:
        sets = []
        for entry in card_library:
            if record[1].strip() == entry["name"] and record[3] == entry["pitch"]:
                if entry["set_id"] not in sets:
                    sets.append(entry["set_id"])
        
        if record[3] == 1:
            pitch = 'red'
        if record[3] == 2:
            pitch = 'yellow'
        if record[3] == 3:
            pitch = 'blue'
        if not record[3]:
            pitch = None

        if(record[1], pitch) not in output:
            output[(record[1], pitch)] = ', '.join(sets)

    return output


battle_box = fabrary_list_import("Battle Box.txt")
battle_box_summed = total_cards(battle_box)
battle_box_sets = get_sets(battle_box)

sum = pd.DataFrame.from_dict(battle_box_summed, orient="index",columns=["qty"])
set = pd.DataFrame.from_dict(battle_box_sets, orient="index",columns=["sets"])

final = pd.concat([sum, set], axis=1)
final = pd.concat([final, pd.DataFrame(final.index.to_list(), index=final.index, columns=["card", "pitch"])], axis=1)
final.loc[:,["card","pitch","qty","sets"]].to_clipboard(index=False)
