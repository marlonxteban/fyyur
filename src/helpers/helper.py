from datetime import datetime

def get_upcoming_shows(shows):
    return list(filter(lambda x: x.start_time > datetime.now(), shows))

def get_upcoming_shows_counter(shows):
    upcoming = get_upcoming_shows(shows)
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

def get_past_shows(shows):
    return list(filter(lambda x: x.start_time <= datetime.now(), shows))

def get_formatted_past_shows(shows):
    return _format_show(get_past_shows(shows))

def get_formatted_upcoming_shows(shows):
    return _format_show(get_upcoming_shows(shows))

def get_past_shows_counter(shows):
    past = get_past_shows(shows)
    return len(list(past))

def get_genres_list(genders):
    return genders.split(",")

def _format_show(shows):
    formatted_shows = []
    for show in shows:
        formatted_shows.append(
            {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time
            }
        )
    return formatted_shows