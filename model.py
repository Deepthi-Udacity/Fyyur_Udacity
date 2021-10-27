from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    def __repr__(self):
      return f'<Artist: {self.id} - {self.name} from {self.city},{self.state}>'

class Area:
    def __init__(self, city, state,venues):
      self.city = city
      self.state = state
      self.venues = venues

class SearchResponse:
    def __init__(self, count, data):
      self.count = count
      self.data = data

class VenueResponse:
    def __init__(self, id, name,city,state, address,phone,genres, image_link,facebook_link,website,seeking_talent,seeking_description,upcoming_shows_count,upcoming_shows,past_shows_count,past_shows):
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

class VenueShowResponse:
    def __init__(self, artist_image_link, artist_id,artist_name,start_time):
        self.artist_image_link = artist_image_link
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.start_time = start_time

class ArtistResponse:
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

class ArtistShowResponse:
    def __init__(self, venue_image_link, venue_id,venue_name,start_time):
      self.venue_image_link = venue_image_link
      self.venue_id = venue_id
      self.venue_name = venue_name
      self.start_time = start_time

class Shows:
    def __init__(self, venue_id, venue_name, artist_id, artist_name, artist_image_link, start_time):
      self.venue_id = venue_id
      self.venue_name = venue_name
      self.artist_id = artist_id
      self.artist_name = artist_name
      self.artist_image_link = artist_image_link
      self.start_time = start_time