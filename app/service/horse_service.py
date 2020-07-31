from app.database.data_accessor import DataAccessor
from datetime import datetime


def init_scalars():
    global track_scalars, winter_scalar, distance_scalars, type_scalar, performance_accessor

    track_accessor = DataAccessor('stallform', 'track_scalars')
    track_accessor.connect()

    distance_accessor = DataAccessor('stallform', 'distance_scalars')
    distance_accessor.connect()

    winter_accessor = DataAccessor('stallform', 'season_scalars')
    winter_accessor.connect()

    type_accessor = DataAccessor('stallform', 'type_scalars')
    type_accessor.connect()

    performance_accessor = DataAccessor('stallform', 'horse_performances')
    performance_accessor.connect()

    track_scalars = {d['track']: d['scalar'] for d in track_accessor.find({})}
    winter_scalar = winter_accessor.find_one({'season': 'WINTER'})['scalar']
    distance_scalars = {d['distance']: d['scalar'] for d in distance_accessor.find({})}
    type_scalar = type_accessor.find_one({'start_type': 'VOLT'})['scalar']

def normalize_prev_starts(horse):
    global track_scalars, winter_scalar, distance_scalars, type_scalar

    starts = horse['prev_starts']

    normalized_times = []

    for start in starts:
        race_date = datetime.strptime(start['shortMeetDate'], '%d.%m.%y')
        normalized_times.append(_normalize_time(start['kmTime'], start['distance'], race_date.month, start['trackCode']))
    return normalized_times


def _normalize_time(time, distance, month, track):
    global track_scalars, winter_scalar, distance_scalars, type_scalar

    letters_to_remove = '-axklm'

    if 'a' in time:
        car_start = True
    else:
        car_start = False


    for letter in letters_to_remove:
        time = time.replace(letter, '')
    
    time = time.replace(',', '.')
    try:
        time = float(time)
    except:
        return -1

    if distance < 1700:
        time_scalar = distance_scalars['SHORT']
    elif distance > 2200 and distance <= 2700:
        time_scalar = distance_scalars['MID_LONG'] 
    elif distance > 2700:
        time_scalar = distance_scalars['LONG']
    else:
        time_scalar = 1

    time = time * time_scalar

    if not car_start:
        time = time * type_scalar
    
    if month < 4 or month > 10:
        time = time * winter_scalar
    
    return round(time, 1)

def calculate_horses_money_for_race(horse):
    current_year_starts = horse['stats']['currentYear']['starts']

    if current_year_starts == 0:
        current_year_money_for_start = -1  # -1 so that no starts is different than having started without earning any money
    else:
        current_year_money_for_start = (horse['stats']['currentYear']['winMoney'] / 100) / current_year_starts
    
    total_starts = horse['stats']['total']['starts']

    if total_starts == 0:
        total_money_for_start = -1
    else:
        total_money_for_start = (horse['stats']['total']['winMoney'] / 100) / total_starts
    
    return {'total': round(total_money_for_start, 2), 'current_year': round(current_year_money_for_start, 2)}


def calculate_horse_win(horse):
    global performance_accessor

    query = {'horseName': horse['name']}

    total_count = performance_accessor.count(query)

    if total_count == 0:
        return -1
    
    query['winner'] = True

    win_count = performance_accessor.count(query)

    return round((win_count / total_count) * 100, 1)    

def calculate_horse_win_with_shoes(horse):
    global performance_accessor

    query = {'horseName': horse['name'], 'rear_shoes': horse['rear_shoes'], 'front_shoes': horse['front_shoes']}

    total_count = performance_accessor.count(query)

    if total_count == 0:
        return -1
    
    query['winner'] = True

    win_count = performance_accessor.count(query)

    return round((win_count / total_count) * 100, 1)