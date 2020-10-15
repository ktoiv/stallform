from datetime import date, datetime

from app.database.data_accessor import DataAccessor
from app.service.horse_performance_service import fetch_cards_for_date, fetch_races_for_card, fetch_horses_for_future_race
from app.service.coach_service import analyze_coach
from app.service.horse_service import normalize_prev_starts, calculate_horses_money_for_race, init_scalars, calculate_horse_win_with_shoes, calculate_horse_win

import numpy as np
import pickle

coach_da = DataAccessor('stallform', 'coach_stats')
coach_da.connect()

driver_da = DataAccessor('stallform', 'driver_stats')
driver_da.connect()

file = open('nn_model', 'rb')

model = pickle.load(file)

file.close()


def get_todays_horses():
    cards = fetch_cards_for_date(date.today())
    init_scalars()

    card_list = []

    cards = list(filter(lambda c: c['country'] == 'SE', cards))

    for card in cards:
        races = fetch_races_for_card(card)
        card['races'] = [_handle_race(race, card['trackAbbreviation']) for race in races]
        card_list.append(card)
    return card_list
            
            
def _handle_race(race, track):
    print('race %d...' % race['number'])
    race_dict = {}
    race_dict.update(race) 
    horses = fetch_horses_for_future_race(race)
    race_dict['horses'] = [_handle_horse(horse, track) for horse in horses]

    return race_dict
                
                
def _handle_horse(horse, track):
    horse_dict = analyze_coach(horse['coach_name'], horse['driver_name'], track, date.today().month, date.today().day)
    horse_dict.update(calculate_horses_money_for_race(horse))
    horse_dict.update(horse)
    horse_dict['normalized_times'] = normalize_prev_starts(horse)

    times = [time for time in horse_dict['normalized_times'] if time != -1]
    horse_dict['avg_time'] = round((sum(times) / len(times)), 1)

    horse_dict['horse_win_rate_with_shoes'] = calculate_horse_win_with_shoes(horse)
    horse_dict['horse_win_rate'] = calculate_horse_win(horse)
    del horse_dict['prev_starts']
    del horse_dict['stats']
    horse_dict['prediction'] = _predict_horse_win(horse_dict)

    return horse_dict    

def _predict_horse_win(horse_dict):
    global coach_da, driver_da, model
    driver_d = driver_da.find_one({'name': horse_dict['driver_name']})
        
    if driver_d:
        horse_dict['driver_win%'] = driver_d['win%']
        horse_dict['driver_total'] = driver_d['total']
    else:
        _default_to_zero(horse_dict, ['driver_win%', 'driver_total'])
        
    coach_d = coach_da.find_one({'name': horse_dict['coach_name']})
        
    if coach_d:
        horse_dict['coach_win%'] = coach_d['win%']
        horse_dict['coach_total'] = coach_d['total']
    else:
        _default_to_zero(horse_dict, ['coach_win%', 'coach_total'])
    
    today = datetime.today()
    horse_dict['month'] = today.month
    
    horse_prediction_data = _get_numeric_values_from_horse(horse_dict)
    predictions = model.predict(np.array([horse_prediction_data]))
    
    return round(predictions[0][0] * 100, 2) 
    
        

def _default_to_zero(horse_dict, columns):
    for column in columns:
        horse_dict[column] = 0
    
    return horse_dict

def _get_numeric_values_from_horse(horse):
    columns_to_save = ['start_track', 'distance', 'rear_shoes', 'front_shoes', 'month', 'breed' ,'car_start', 'coach_total' ,'coach_win%','driver_total','driver_win%']
    
    th = {}
    for c in columns_to_save:
        th[c] = horse[c]
    
    th['breed'] = int(th['breed'] == 'L')
    th['front_shoes'] = int(th['front_shoes'])
    th['rear_shoes'] = int(th['rear_shoes'])
    th['car_start'] = int(th['car_start'])

    
    return np.array([
     th['start_track'],
     th['distance'],
     th['rear_shoes'],
     th['front_shoes'],
     th['month'],
     th['breed'],
     th['car_start'],
     th['coach_total'],
     th['coach_win%'],
     th['driver_total'],
     th['driver_win%']])