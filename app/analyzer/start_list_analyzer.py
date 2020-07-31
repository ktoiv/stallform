from datetime import date

from app.service.horse_performance_service import fetch_cards_for_date, fetch_races_for_card, fetch_horses_for_future_race
from app.service.coach_service import analyze_coach
from app.service.horse_service import normalize_prev_starts, calculate_horses_money_for_race, init_scalars, calculate_horse_win_with_shoes, calculate_horse_win


def get_todays_horses():
    cards = fetch_cards_for_date(date.today())
    init_scalars()

    card_list = []

    cards = list(filter(lambda c: c['country'] == 'SE', cards))

    for card in cards:
        print('Generating %s...' % card['trackName'])
        races = fetch_races_for_card(card)
        card['races'] = [_handle_race(race, card['trackAbbreviation']) for race in races]
        card_list.append(card)
        break
    
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
    horse_dict['horse_win_rate_with_shoes'] = calculate_horse_win_with_shoes(horse)
    horse_dict['horse_win_rate'] = calculate_horse_win(horse)

    del horse_dict['prev_starts']
    del horse_dict['stats']

    return horse_dict