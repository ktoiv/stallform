
from app.database.data_accessor import DataAccessor

import pandas as pd

da = DataAccessor('stallform', 'horse_performances')
da.connect()

driver_da = DataAccessor('stallform', 'driver_stats')
driver_da.connect()

data = da.find({})

coach_da = DataAccessor('stallform', 'coach_stats')
coach_da.connect()

df = pd.DataFrame(data)

def remove_old_stats():
    global coach_da, driver_da

    coach_da.delete_many({})
    driver_da.delete_many({})


def update_stats():
    global da, coach_da, driver_da

    columns_to_remove = ['_id', 'horseName', 'startNumber',
        'driverOutfitColor', 'driverRacingColors',
       'coachNameInitials', 'track', 'time',
       'year', 'day', 'driverChangeName', 'driverChangeNameInitials',
       'mobileStartRecord', 'handicapRaceRecord']



    for column in columns_to_remove:
        del df[column]



    drivers = df.driverName.unique()
    coaches = df.coachName.unique()

    driver_list = [handle_wins_and_races(driver, 'driverName', df) for driver in drivers]
    coach_list = [handle_wins_and_races(coach, 'coachName', df) for coach in coaches]

    coach_da.insert_many(coach_list)
    driver_da.insert_many(driver_list)


def handle_wins_and_races(name, column, d):
    win_mask = (d[column] == name) & (d['winner'] == True)
    wins = len(d[win_mask])
    races_mask = d[column] == name
    races = len(d[races_mask])
    
    if races == 0:
        win_percentage = 0
    else:
        win_percentage = (wins / races) * 100
    
    return {'name': name, 'total': races, 'win%': round(win_percentage, 2)}