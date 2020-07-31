from app.database.data_accessor import DataAccessor
from app.service.scalar_calculation_service import calculate_scalars_for_tracks, calculate_averages_for_distances, calculate_averages_for_seasons, calculate_averages_for_start_types
from app.service.coach_service import analyze_coach
from app.analyzer.start_list_analyzer import get_todays_horses
#result = analyze_coach('Petri Salmela', 'Sv', 7, 28)
#print(result)
import pymongo
from app.service.data_update_service import _recalculate_scalars, init_db_connection
import os

mail = os.environ['RECEIVER_MAIL']
print(mail)
