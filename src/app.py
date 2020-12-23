#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
import magicattr
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from helpers import helper

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'

    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)
    artist = db.relationship('Artist', backref=db.backref('shows', lazy =True))
    venue = db.relationship('Venue', backref=db.backref('shows', lazy =True))

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  areas_query = db.session.query(db.func.count(Venue.id).label('venues_count'), Venue.city, Venue.state).group_by(Venue.city, Venue.state)
  areas = areas_query.all()
  venues = db.session.query(Venue).all()
  data = []

  for area in areas:
    data.append(
      {
        "city": area.city,
        "state": area.state,
        "venues": helper.get_venues_by_areas(area, venues)
      }
    )

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.like('%'+search_term+'%')).all()
  response = {
    "count": len(venues),
    "data": []
  }

  for venue in venues:
    response["data"].append(
      {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": helper.get_upcoming_shows_counter(venue.shows)
      }
    )

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first()
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": helper.get_genres_list(venue.genres),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": helper.get_formatted_past_shows(venue.shows),
    "upcoming_shows": helper.get_formatted_upcoming_shows(venue.shows),
    "past_shows_count": helper.get_past_shows_counter(venue.shows),
    "upcoming_shows_count": helper.get_upcoming_shows_counter(venue.shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    new_venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'],
    phone = request.form['phone'],
    genres = request.form.get('genres', ''),
    facebook_link = request.form.get('facebook_link', ''),
    website = request.form.get('website',''),
    image_link = request.form.get('image_link', ''),
    seeking_talent = request.form.get('seeking_talent', False),
    seeking_description = request.form.get('seeking_description', '')
    )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('Venue ' + request.form['name'] + ' could not be listed!')
    flash(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  response = {
    "count": len(artists),
    "data": []
  }

  for artist in artists:
    response["data"].append(
      {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": helper.get_upcoming_shows_counter(artist.shows)
      }
    )

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": helper.get_genres_list(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": helper.get_formatted_past_shows_for_artist(artist.shows),
    "upcoming_shows": helper.get_formatted_upcoming_shows_for_artist(artist.shows),
    "past_shows_count": helper.get_past_shows_counter(artist.shows),
    "upcoming_shows_count": helper.get_upcoming_shows_counter(artist.shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  raw_artist = Artist.query.filter_by(id=artist_id).first()
  attribs = list(filter(lambda a: not a.startswith('_'), dir(raw_artist)))
  for attrib in attribs:
    if hasattr(form, attrib):
      magicattr.set(form, attrib+'.data', getattr(raw_artist, attrib, ''))

  artist = vars(raw_artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  try:
    artist.name = request.form.get("name", "")
    artist.city = request.form.get("city", "")
    artist.state = request.form.get("state", "")
    artist.genres = request.form.get("genres", "")
    artist.phone = request.form.get("phone", "")
    artist.image_link = request.form.get("image_link", "")
    artist.facebook_link = request.form.get("facebook_link", "")
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  raw_venue = Venue.query.filter_by(id=venue_id).first()
  attribs = list(filter(lambda a: not a.startswith('_'), dir(raw_venue)))
  for attrib in attribs:
    if hasattr(form, attrib):
      magicattr.set(form, attrib+'.data', getattr(raw_venue, attrib, ''))

  venue = vars(raw_venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  try:
    venue.name = request.form.get("name", "")
    venue.city = request.form.get("city", "")
    venue.state = request.form.get("state", "")
    venue.genres = request.form.get("genres", "")
    venue.phone = request.form.get("phone", "")
    venue.image_link = request.form.get("image_link", "")
    venue.facebook_link = request.form.get("facebook_link", "")
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    new_artist = Artist(
    name = request.form.get('name',''),
    city = request.form.get('city',''),
    state = request.form.get('state',''),
    phone = request.form.get('phone',''),
    genres = request.form.get('genres', ''),
    facebook_link = request.form.get('facebook_link', ''),
    website = request.form.get('website',''),
    image_link = request.form.get('image_link', ''),
    seeking_venue = request.form.get('seeking_venue', False),
    seeking_description = request.form.get('seeking_description', '')
    )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('Artist ' + request.form['name'] + ' could not be listed!')
    flash(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []

  for show in shows:
    data.append(
      {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      }
    )
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    new_show = Show(
    artist_id = request.form.get('artist_id',''),
    venue_id = request.form.get('venue_id',''),
    start_time = request.form.get('start_time', datetime.now()),
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed')
    flash(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
