from datetime import datetime, timedelta, date
from app.database.data_accessor import DataAccessor
from app.service.horse_performance_service import fetch_cards_for_date, fetch_races_for_card, fetch_horses_for_race, fetch_winner_and_time_for_race

def _create_db_dict(date, card, race, horse, winner, time):
    horse['track'] = card['trackAbbreviation']
    horse['winner'] = horse['startNumber'] == winner

    if horse['winner']:
        horse['time'] = time
    else:
        horse['time'] = -1

    horse['rear_shoes'] = horse['rearShoes'] == 'HAS_SHOES'
    horse['front_shoes'] = horse['frontShoes'] == 'HAS_SHOES'

    horse['year'] = date.year
    horse['day'] = date.day
    horse['month'] = date.month

    if race['breed']:
        horse['breed'] = race['breed']
    else:
        horse['breed'] = 'L'


    horse['car_start'] = race['startType'] == 'CAR_START'
    
    del horse['rearShoes']
    del horse['frontShoes']

    return horse

def add_dates_performances_to_database(date, data_accessor):

    cards = fetch_cards_for_date(date)

    cards = list(filter(lambda card: card['country'] == 'SE', cards))

    performance_list = []

    for card in cards:

        races = fetch_races_for_card(card)

        for race in races:
            horses = fetch_horses_for_race(race)
            winner, time = fetch_winner_and_time_for_race(race)

            race_performances = []

            for horse in horses:
                try:
                   horse_dict = _create_db_dict(date, card, race, horse, winner, time) 
                   race_performances.append(horse_dict)
                except KeyError:
                    continue

            performance_list.extend(race_performances)

    
    data_accessor.insert_many(performance_list)


def build_data_from_date(start_date):

    data_accessor = DataAccessor('stallform', 'horse_performances')
    data_accessor.connect()

    today = date.today()
    delta = timedelta(days=1)

    while start_date < today:
        add_dates_performances_to_database(start_date, data_accessor)

        start_date = start_date + delta