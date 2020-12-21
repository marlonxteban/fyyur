from datetime import datetime

def get_upcoming_shows(shows):
    return list(filter(lambda x: x.start_time > datetime.now(), shows))

def get_upcoming_shows_counter(shows):
    upcoming = filter(lambda x: x.start_time > datetime.now(), shows)
    return len(list(upcoming))

def get_venues_by_areas(area, venues):
    venues_by_area = list(filter(lambda x: x.city == area.city and x.state == area.state, venues))
    formatted_venues = []
    for venue in venues_by_area:
        formatted_venues.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": get_upcoming_shows_counter(venue.shows)
        })
    return formatted_venues