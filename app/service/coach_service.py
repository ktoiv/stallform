from datetime import date
from app.database.data_accessor import DataAccessor

performance_accessor = DataAccessor('stallform', 'horse_performances')
performance_accessor.connect()

def analyze_coach(coach, driver, track, month, day):
    win_percentage = _calculate_win_percentage_for_coach(coach)
    win_percentage_for_month = _calculate_win_percentage_for_coach_month(coach, month, day)
    win_percentage_at_track = _calculate_win_percentage_for_coach_at_track(coach, track)
    win_percentage_with_driver = _calculate_win_percentage_for_coach_and_driver(coach, driver)
    return {'win_rate': win_percentage, "win_rate_month": win_percentage_for_month, 'win_rate_track': win_percentage_at_track, 'win_rate_with_driver' : win_percentage_with_driver}


def _calculate_win_percentage_for_coach(coach):
    global performance_accessor

    total_query = {'coachName': coach}
    total_count = performance_accessor.count(total_query)

    if total_count == 0:
        return -1

    win_query = {'coachName': coach, 'winner': True}
    win_count = performance_accessor.count(win_query)

    return round((win_count / total_count) * 100, 2)

def _calculate_win_percentage_for_coach_month(coach, month, day):
    global performance_accessor
    year = date.today().year
    
    if month == 1:
        year -= 1
        prev_month = 12
    else:
        prev_month = month - 1

    prev_month_query = {'coachName': coach, 'day': {'$gte': day}, 'month': prev_month}
    current_month_query = {'coachName': coach, 'month': month}

    total_count = performance_accessor.count(prev_month_query) + performance_accessor.count(current_month_query)

    if total_count == 0:
        return -1

    prev_month_query['winner'] = True
    current_month_query['winner'] = True

    win_count = performance_accessor.count(prev_month_query) + performance_accessor.count(current_month_query)

    return round((win_count / total_count) * 100, 2)


def _calculate_win_percentage_for_coach_at_track(coach, track):
    global performance_accessor

    query = {'coachName': coach, 'track': track}

    total_count = performance_accessor.count(query)

    if total_count == 0:
        return -1

    query['winner'] = True

    win_count = performance_accessor.count(query)

    return round((win_count / total_count) * 100, 2)


def _calculate_win_percentage_for_coach_and_driver(coach, driver):
    global performance_accessor

    query = {'coachName': coach, 'driverName': driver}

    total_count = performance_accessor.count(query)

    if total_count == 0:
        return -1

    query['winner'] = True

    win_count = performance_accessor.count(query)

    return round((win_count / total_count) * 100, 2)