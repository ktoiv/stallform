
from app.database.data_accessor import DataAccessor
import numpy as np

performance_accessor = DataAccessor(db_name="stallform", collection_name="horse_performances")
performance_accessor.connect()

def calculate_scalars_for_tracks():
    global performance_accessor

    track_accessor = DataAccessor(db_name="stallform", collection_name="track_scalars")
    track_accessor.connect()

    #Use Solvalla-track as the base
    base = _get_avg_for_track("Sv")

    tracks = performance_accessor.distinct("track")
    track_scalars = [{"track": track, "scalar": base / _get_avg_for_track(track)} for track in tracks]

    track_accessor.insert_many(track_scalars)

def _get_avg_for_track(track_abbrevation):
    query = {"track": track_abbrevation, "winner": True, "car_start": True, "distance":{"$gt": 1700, "$lte": 2200}}

    track_avg = __get_avg_times_for_query(query)

    return round(track_avg, 2)


def calculate_averages_for_distances():
    distance_accessor = DataAccessor(db_name="stallform", collection_name="distance_scalars")
    distance_accessor.connect()

    distances = ["SHORT", "NORMAL", "MID_LONG", "LONG"]
    base = _get_avg_for_distance('NORMAL')

    distance_scalars = [{"distance": distance, "scalar": base / _get_avg_for_distance(distance)} for distance in distances]
    distance_accessor.insert_many(distance_scalars)


def _get_avg_for_distance(distance):

    if distance == 'SHORT':
        distance_query = {"$lte": 1700}
    elif distance == 'NORMAL':
        distance_query = {"$gt": 1700, "$lte": 2200}
    elif distance == 'MID_LONG':
        distance_query = {"$gt": 2200, "$lte": 2700}
    elif distance == 'LONG':
        distance_query = {"$gt": 2700}    

    query = {"winner": True, "car_start": True, "distance": distance_query}

    distance_avg = __get_avg_times_for_query(query)

    return distance_avg


def calculate_averages_for_seasons():
    season_accessor = DataAccessor(db_name="stallform", collection_name="season_scalars")
    season_accessor.connect()
    seasons = ['WINTER', 'SUMMER']

    base = _get_avg_for_season('SUMMER')

    season_scalars = [{'season': season, 'scalar': base / _get_avg_for_season(season)} for season in seasons]
    season_accessor.insert_many(season_scalars)


def _get_avg_for_season(season):
    if season == 'SUMMER':
        month_query = {"$gt": 3, "$lt": 11 }
    elif season == 'WINTER':
        month_query = {"$not": {"$gt": 3, "$lt": 11 }}
    query = {"winner": True, "car_start": True, "month": month_query, "distance":{"$gt": 1700, "$lte": 2200}}
    season_avg = __get_avg_times_for_query(query)
    return season_avg

def calculate_averages_for_start_types():
    type_accessor = DataAccessor(db_name="stallform", collection_name="type_scalars")
    type_accessor.connect()
    types = ['VOLT', 'CAR']

    base = _get_avg_for_start_type('CAR')

    type_scalars = [{'start_type': t, 'scalar': base / _get_avg_for_start_type(t)} for t in types]
    type_accessor.insert_many(type_scalars)

def _get_avg_for_start_type(start_type):
    if start_type == 'VOLT':
        car_start = False
    elif start_type == 'CAR':
        car_start = True

    query = {"winner": True, "car_start": car_start, "distance":{"$gt": 1700, "$lte": 2200}}
    type_avg = __get_avg_times_for_query(query)
    return type_avg



def __get_avg_times_for_query(query):
    global performance_accessor
    performances_with_times = performance_accessor.find(query)

    times = map(lambda performance: performance["time"], performances_with_times)
    times = list(filter(lambda time: time != -1, times))
    np_times = np.array(times)
    if len(np_times) < 1:
        return 1
    return np.mean(np_times)