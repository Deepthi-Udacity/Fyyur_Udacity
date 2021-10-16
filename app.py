#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import logging
import sys
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (Flask, flash, redirect, render_template, request,
                   url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

Show = db.Table('show',
    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
    db.Column('start_time', db.String)
)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean , default = False)
    seeking_description = db.Column(db.String(200))
    artists = db.relationship('Artist', secondary=Show, backref=db.backref('venues', lazy=True))

    def __repr__(self):
      return f'<Venue: {self.id} - {self.name} at {self.city},{self.state}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean , default = False)
    seeking_description = db.Column(db.String(200))
    available_from_time = db.Column(db.String())
    available_to_time = db.Column(db.String())

    def __repr__(self):
      return f'<Artist: {self.id} - {self.name} from {self.city},{self.state}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  statement = db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state)
  venueslist = db.session.execute(statement)
  class Area:
    def __init__(self, city, state,venues):
      self.city = city
      self.state = state
      self.venues = venues
  areas =[]
  for venue in venueslist :
    area = Area(city=venue.city,state=venue.state, 
      venues = Venue.query.filter_by(city=venue.city,state=venue.state))
    areas.append(area)
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  class Response:
    def __init__(self, count, data):
      self.count = count
      self.data = data
  searchTerm=request.form.get('search_term')
  search = "%{}%".format(searchTerm)
  query = db.session.query(Venue.id,Venue.name).filter(Venue.name.ilike(search))
  data = query.all()
  count = query.count()
  response = Response(count=count,data = data)
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  class Response:
    def __init__(self, id, name,city,state, address,phone,genres, image_link,facebook_link,website,
    seeking_talent,seeking_description,upcoming_shows_count,upcoming_shows,past_shows_count,past_shows):
      self.id = id
      self.name = name
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.genres = genres
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.website = website
      self.seeking_talent = seeking_talent
      self.seeking_description = seeking_description
      self.upcoming_shows_count = upcoming_shows_count
      self.upcoming_shows = upcoming_shows
      self.past_shows_count = past_shows_count
      self.past_shows = past_shows
  class ShowResponse:
    def __init__(self, artist_image_link, artist_id,artist_name,start_time):
      self.artist_image_link = artist_image_link
      self.artist_id = artist_id
      self.artist_name = artist_name
      self.start_time = start_time
  data = Venue.query.get(venue_id)
  statement = db.session.query(Show).filter_by(venue_id=venue_id)
  shows = db.session.execute(statement)
  past_shows = []
  upcoming_shows=[]
  past_shows_count = 0
  upcoming_shows_count = 0
  for show in shows:
    dateTime1 = datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S")
    today = datetime.now()
    artist=Artist.query.get(show.artist_id)
    showdata = ShowResponse(artist_image_link= artist.image_link ,artist_id= artist.id,
      artist_name= artist.name ,start_time= show.start_time)
    if dateTime1 <= today:
      past_shows.append(showdata)
      past_shows_count = past_shows_count+1
    else :
      upcoming_shows.append(showdata)
      upcoming_shows_count =upcoming_shows_count+1

  response = Response(id= data.id, name= data.name,city= data.city, state= data.state , address= data.address,phone= data.phone ,
      genres= data.genres , image_link= data.image_link ,facebook_link= data.facebook_link ,website= data.website_link ,
      seeking_talent= data.seeking_talent ,seeking_description= data.seeking_description ,upcoming_shows_count= upcoming_shows_count,upcoming_shows=upcoming_shows,
      past_shows_count= past_shows_count,past_shows=past_shows)
  
  return render_template('pages/show_venue.html', venue=response)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  name = ''
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    if 'seeking_talent' in request.form:
        seeking_talent = True
    else:
        seeking_talent = False
    seeking_description = request.form['seeking_description']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, 
    genres=genres, image_link=image_link, facebook_link=facebook_link, website_link=website_link,
    seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  
  finally:
    db.session.close()
  if error :
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  else :
    flash('Venue ' + name + ' was successfully listed!')
  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue=Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.genres = request.form['genres']
  venue.image_link = request.form['image_link']
  venue.facebook_link = request.form['facebook_link']
  venue.website_link = request.form['website_link']
  if request.form['seeking_talent'] == 'y':
    venue.seeking_talent = True
  else :
    venue.seeking_talent = False
  venue.seeking_description = request.form['seeking_description']
  db.session.add(venue)
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/delete_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue_submission(venue_id):
  error = False
  name = ''
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
    
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True

  finally:
    db.session.close()
  if error :
    flash('An error occurred. Venue ' + name + ' could not be deleted.')
    return redirect(url_for('show_venue', venue_id=venue_id))
  else :
    return redirect(url_for('index'))
  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists=Artist.query.order_by('id').all()
  # TODO: replace with real data returned from querying the database
  
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  class Response:
    def __init__(self, count, data):
      self.count = count
      self.data = data
  searchTerm=request.form.get('search_term')
  search = "%{}%".format(searchTerm)
  query = db.session.query(Artist.id,Artist.name).filter(Artist.name.ilike(search))
  data = query.all()
  count = query.count()
  response = Response(count=count,data = data)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  class Response:
    def __init__(self, id, name,city,state,phone,genres, image_link,facebook_link,website,
    seeking_venue,seeking_description,upcoming_shows_count,upcoming_shows,past_shows_count,past_shows):
      self.id = id
      self.name = name
      self.city = city
      self.state = state
      self.phone = phone
      self.genres = genres
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.website = website
      self.seeking_venue = seeking_venue
      self.seeking_description = seeking_description
      self.upcoming_shows_count = upcoming_shows_count
      self.upcoming_shows = upcoming_shows
      self.past_shows_count = past_shows_count
      self.past_shows = past_shows
  class ShowResponse:
    def __init__(self, venue_image_link, venue_id,venue_name,start_time):
      self.venue_image_link = venue_image_link
      self.venue_id = venue_id
      self.venue_name = venue_name
      self.start_time = start_time
  data = Artist.query.get(artist_id)
  statement = db.session.query(Show).filter_by(artist_id=artist_id)
  shows = db.session.execute(statement)
  past_shows = []
  upcoming_shows=[]
  past_shows_count = 0
  upcoming_shows_count = 0
  for show in shows:
    dateTime1 = datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S")
    today = datetime.now()
    venue=Venue.query.get(show.venue_id)
    showdata = ShowResponse(venue_image_link= venue.image_link ,venue_id= venue.id,
      venue_name= venue.name ,start_time= show.start_time)
    if dateTime1 <= today:
      past_shows.append(showdata)
      past_shows_count = past_shows_count+1
    else :
      upcoming_shows.append(showdata)
      upcoming_shows_count =upcoming_shows_count+1

  response = Response(id= data.id, name= data.name,city= data.city, state= data.state ,phone= data.phone ,
      genres= data.genres , image_link= data.image_link ,facebook_link= data.facebook_link ,website= data.website_link ,
      seeking_venue= data.seeking_venue ,seeking_description= data.seeking_description ,upcoming_shows_count= upcoming_shows_count,upcoming_shows=upcoming_shows,
      past_shows_count= past_shows_count,past_shows=past_shows)
  
  return render_template('pages/show_artist.html', artist=response)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id): 
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form['genres']
  artist.image_link = request.form['image_link']
  artist.facebook_link = request.form['facebook_link']
  artist.website_link = request.form['website_link']
  if request.form['seeking_venue'] == 'y':
    artist.seeking_venue = True
  else :
    artist.seeking_venue = False
  artist.seeking_description = request.form['seeking_description']
  db.session.add(artist)
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  name = ''
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    if 'seeking_venue' in request.form:
        seeking_venue = True
    else:
        seeking_venue = False
    seeking_description = request.form['seeking_description']
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link,
     facebook_link=facebook_link, website_link=website_link,seeking_venue=seeking_venue, 
     seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  
  finally:
    db.session.close()
  if error :
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  else :
    flash('Artist ' + name + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  result = db.session.query(Venue.name.label("venue_name"), Artist.name.label("artist_name"),
        Artist.image_link, Show.c.venue_id, Show.c.artist_id, Show.c.start_time).filter(
        Show.c.venue_id == Venue.id).filter(Show.c.artist_id == Artist.id).all()
  showData = []
  class Shows:
    def __init__(self, venue_id, venue_name, artist_id, artist_name, artist_image_link, start_time):
      self.venue_id = venue_id
      self.venue_name = venue_name
      self.artist_id = artist_id
      self.artist_name = artist_name
      self.artist_image_link = artist_image_link
      self.start_time = start_time
  for show in result:
    showData.append(Shows(show.venue_id,show.venue_name,show.artist_id, show.artist_name, show.image_link,
    show.start_time))
  
  return render_template('pages/shows.html', shows=showData)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    venue = Venue.query.get(venue_id)
    artist = Artist.query.get(artist_id) 
    venue.artists.append(artist)
    db.session.add(venue)
    db.session.commit()
    statement = Show.update().where(Show.c.artist_id == artist_id ,Show.c.venue_id == venue_id).values(start_time=start_time)
    db.session.execute(statement)
    db.session.commit()   
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error :
    flash('An error occurred. Show could not be listed.')
  else :
    flash('Show was successfully listed!')
  return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form


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
