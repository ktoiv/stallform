import requests
import json
from app.utils.constants import headers, veikkaus_api_base_url


card_attributes_to_delete = [
    'cancelled',
    'currentRaceNumber',
    'currentRaceStatus',
    'currentRaceStartTime',
    'firstRaceStart',
    'future',
    'lastRaceOfficial',
    'lunchRaces',
    'meetDate',
    'minutesToPost',
    'priority',
    'raceType',
    'trackNumber',
    'mainPerformance',
    'totoPools',
    'epgStartTime',
    'epgStopTime',
    'epgChannel',
    'jackpotPools',
    'bonusPools'
]

horse_attributes_to_delete = [
    "runnerId", 
    "raceId",
    "scratched",
    "prize",
    "frontShoesChanged",
    "rearShoesChanged",
    "sire",
    "dam",
    "damSire",
    "horseAge",
    "birthDate",
    "gender",
    "color",
    "driverNameInitials",
    "driverOutfitColor"
    "driverRacingColors"
    "coachNameInitials",
    "ownerName",
    "stats",
    "prevStarts"
]

def fetch_cards_for_date(date):
    veikkaus_api_card_url = '/api/toto-info/v1/cards/date/'

    url = f'{veikkaus_api_base_url}{veikkaus_api_card_url}{date.strftime("%Y-%m-%d")}'
    response = requests.get(url, headers=headers)
    json_card_list = json.loads(response.text)['collection']
    

    cards = [trim_json_card(json_card) for json_card in json_card_list]
    return cards

def trim_json_card(json_card):
    global card_attributes_to_delete

    for attribute in card_attributes_to_delete:
        if attribute in json_card:
            del json_card[attribute]
    
    return json_card



def fetch_races_for_card(card):
    veikkaus_api_race_url = f"/api/toto-info/v1/card/{card['cardId']}/races"
    url = f'{veikkaus_api_base_url}{veikkaus_api_race_url}'
    response = requests.get(url, headers=headers)
    json_race_list = json.loads(response.text)['collection']

    races = [trim_json_race(json_race) for json_race in json_race_list]
    return races

    

def trim_json_race(json_race):
    race_attributes_to_delete = ['cardId', 'seriesSpecification', 'raceStatus', 'firstPrize', 'startTime', 'toteResultString', 'raceRider', 'trackProfile', 'trackSurface']

    for attribute in race_attributes_to_delete:
        if attribute in json_race:
            del json_race[attribute]
    
    return json_race
    


def fetch_horses_for_race(race):
    veikkaus_api_horses_url = f"/api/toto-info/v1/race/{race['raceId']}/runners"
    url = f'{veikkaus_api_base_url}{veikkaus_api_horses_url}'
    response = requests.get(url, headers=headers)
    json_horse_list = json.loads(response.text)['collection']

    horses = [trim_json_horse(json_horse) for json_horse in json_horse_list]

    return horses


def trim_json_horse(json_horse):
    global horse_attributes_to_delete

    for attribute in horse_attributes_to_delete:
        if attribute in json_horse:
            del json_horse[attribute]

    return json_horse

def fetch_horses_for_future_race(race):
    veikkaus_api_horses_url = f"/api/toto-info/v1/race/{race['raceId']}/runners"
    url = f'{veikkaus_api_base_url}{veikkaus_api_horses_url}'
    response = requests.get(url, headers=headers)
    json_horse_list = json.loads(response.text)['collection']

    horses = [trim_horse_to_analyze(json_horse) for json_horse in json_horse_list]

    return horses


def trim_horse_to_analyze(json_horse):
    result = {}
    result['start_number'] = json_horse['startNumber']
    result['name'] = json_horse['horseName']
    result['coach_name'] = json_horse['coachName']
    result['driver_name'] = json_horse['driverName']
    result['stats'] = json_horse['stats']
    result['prev_starts'] = json_horse['prevStarts']
    result['front_shoes'] = json_horse['frontShoes'] == 'HAS_SHOES'
    result['rear_shoes'] = json_horse['rearShoes'] == 'HAS_SHOES'

    return result



def fetch_winner_and_time_for_race(race):
    veikkaus_api_result_url = f"/api/toto-info/v1/race/{race['raceId']}/results"

    url = f"{veikkaus_api_base_url}{veikkaus_api_result_url}"
    response = requests.get(url, headers=headers)
    json_result = json.loads(response.text) 
    
    if len(json_result['results']) == 0:
        return -1, -1
    
    winning_performance = json_result['results'][0]

    if 'startNumber' in winning_performance:
        winner = winning_performance['startNumber']
    else:
        winner = -1

    if 'kmTime' in winning_performance:
        time = winning_performance['kmTime']

        replacable_letters = '-axklm'

        for letter in replacable_letters:
            time = time.replace(letter, '')

        try:
            time = time.replace(',', '.')
            time = float(time)
            
        except:
            time = -1
    else:
        time = -1

    return winner, time