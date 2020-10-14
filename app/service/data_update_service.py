import pymongo
from datetime import date, timedelta
from app.database.data_accessor import DataAccessor
from app.service.data_builder_service import build_data_from_date
from app.service.scalar_calculation_service import calculate_averages_for_distances, calculate_averages_for_seasons, calculate_averages_for_start_types, calculate_scalars_for_tracks
from app.service.stat_update_service import remove_old_stats, update_stats
from app.service.neural_network_service import train_neural_network

def init_db_connection():
    global track_accessor, distance_accessor, winter_accessor, type_accessor, performance_accessor

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



def update_database():
    delta = timedelta(days=1)
    date_to_start_from = _get_latest_date_in_the_database() + delta

    build_data_from_date(date_to_start_from)

    if date.today().day == 1:
        _remove_old_data()
        _recalculate_scalars()
        remove_old_stats()
        update_stats()
        train_neural_network()

def _recalculate_scalars():
    global track_accessor, distance_accessor, winter_accessor, type_accessor, performance_accessor

    track_accessor.collection.drop()
    distance_accessor.collection.drop()
    winter_accessor.collection.drop()
    type_accessor.collection.drop()

    calculate_scalars_for_tracks()
    calculate_averages_for_seasons()
    calculate_averages_for_distances()
    calculate_averages_for_start_types()




def _remove_old_data():
    global performance_accessor

    current_month = date.today().month
    current_year = date.today().year

    if current_month == 1:
        month_to_remove = 12
        year_to_remove = current_year - 2
    else:
        month_to_remove = current_month - 1
        year_to_remove = current_year - 1
    
    delete_query = {'month': month_to_remove, 'year': year_to_remove}
    performance_accessor.delete_many(delete_query)




def _get_latest_date_in_the_database():
    global performance_accessor

    latest_performance = list(performance_accessor.collection.find({'winner': True}).sort([("year", pymongo.DESCENDING), 
                                                                               ("month", pymongo.DESCENDING),
                                                                               ("day", pymongo.DESCENDING)]))[0]

    latest_date = date(latest_performance['year'], latest_performance['month'], latest_performance['day'])

    return latest_date
