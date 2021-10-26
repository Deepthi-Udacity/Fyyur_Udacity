# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
import sys
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from model import *
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")

# ----------------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")

def venues():
    #This endpoint will list Venues grouped by City and State
    # called when user clicks on 'Venue' or 'Find a Venue' button
    #List venues in groups bu City and State
    statement = db.session.query(Venue.city, Venue.state).group_by(
        Venue.city, Venue.state
    )
    venueslist = db.session.execute(statement)
    areas = []
    for venue in venueslist:
        area = Area(
            city=venue.city,
            state=venue.state,
            venues=Venue.query.filter_by(city=venue.city, state=venue.state),
        )
        areas.append(area)
    return render_template("pages/venues.html", areas=areas)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    #This endpoint perform search on Venues based on the search term
    #Input= searchTerm
    #Output = List of venues that match the search term partially and case-insensitive
    searchTerm = request.form.get("search_term")
    search = "%{}%".format(searchTerm)
    query = db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike(search))
    data = query.all()
    count = query.count()
    response = SearchResponse(count=count, data=data)

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    #This endpoint will display the details of the Venue given venue_id
    #Input= venue_id
    #Output = Details of a venue with Past and Upcoming shows

    data = Venue.query.get(venue_id)
    results = db.session.query(Show,Artist.image_link,Artist.id,Artist.name).filter_by(venue_id=venue_id).join(Artist).all()
    past_shows =[]
    upcoming_shows = []
    for show in results:
        showdata = VenueShowResponse(
            artist_image_link=show.image_link,
            artist_id=show.id,
            artist_name=show.name,
            start_time=show.start_time,
        )
        if datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S") <= datetime.now():
            past_shows.append(showdata)
        else:
            upcoming_shows.append(showdata)
    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)
    
    response = VenueResponse(
        id=data.id,
        name=data.name,
        city=data.city,
        state=data.state,
        address=data.address,
        phone=data.phone,
        genres=data.genres,
        image_link=data.image_link,
        facebook_link=data.facebook_link,
        website=data.website_link,
        seeking_talent=data.seeking_talent,
        seeking_description=data.seeking_description,
        upcoming_shows_count=upcoming_shows_count,
        upcoming_shows=upcoming_shows,
        past_shows_count=past_shows_count,
        past_shows=past_shows,
    )

    return render_template("pages/show_venue.html", venue=response)

# ----------------------------------------------------------------------------#
#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    #This endpoint will display a form that will input all the 
    # details of a new Venue
    #Output = Form to input details of a new Venue
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    #This endpoint will submit the VenueForm and 
    # will create a new Venue in DB
    #Input = VenueForm
    #Output = Redirects to Home page on successful 
    # creation of the venue

    error = False
    name = ""
    try:
        form = VenueForm(request.form)
        if "seeking_talent" in request.form:
            seeking_talent = True
        else:
            seeking_talent = False
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_talent=seeking_talent,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())

    finally:
        db.session.close()
    if error:
        flash("An error occurred. Venue " + form.name.data + " could not be listed.")
    else:
        flash("Venue " + form.name.data + " was successfully listed!")
    return render_template("pages/home.html")


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    #This endpoint will display a form that will  display
    # details of the Venue for given venue_id prefilled
    #Output = Form to input details to edit the Venue
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    #This endpoint will submit the VenueForm and 
    # will edit the Venue for the given venue_id in DB
    #Input = VenueForm and venue_id
    #Output = Displays the Venue details page for given venue_id with 
    #editted data
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    if "seeking_talent" in request.form:
        venue.seeking_talent = True
    else:
        venue.seeking_talent = False
    venue.seeking_description = form.seeking_description.data
    db.session.merge(venue)
    db.session.commit()
    return redirect(url_for("show_venue", venue_id=venue_id))


@app.route("/venues/<int:venue_id>/delete", methods=["GET"])
def delete_venue(venue_id):
    #This endpoint will display a form that will provide the button  
    # delete a venue
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template("forms/delete_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/delete", methods=["POST"])
def delete_venue_submission(venue_id):
    #This endpoint will submit the VenueForm and 
    # will delete the Venue for the given venue_id in DB
    #Input = VenueForm and venue_id
    #Output = On successful deletion will return back to homepage
    error = False
    try:
        deleted_objects = Venue.__table__.delete().where(Venue.id.in_([venue_id]))
        db.session.execute(deleted_objects)
        db.session.commit()

    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True

    finally:
        db.session.close()
    if error:
        flash("An error occurred. Venue could not be deleted.")
        return redirect(url_for("show_venue", venue_id=venue_id))
    else:
        flash(" Venue deleted successfully!")
        return redirect(url_for("index"))

# ----------------------------------------------------------------------------#
#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    #This endpoint will list Artists from DB
    # called when user clicks on 'Artist' or 'Find a Artist' button

    artists = Artist.query.order_by("id").all()
    return render_template("pages/artists.html", artists=artists)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    #This endpoint perform search on Artists based on the search term
    #Input= searchTerm
    #Output = List of Artists that match the search term partially and case-insensitive

    searchTerm = request.form.get("search_term")
    search = "%{}%".format(searchTerm)
    query = db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike(search))
    data = query.all()
    count = query.count()
    response = SearchResponse(count=count, data=data)
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    #This endpoint will display the details of the Artist given artist_id
    #Input= artist_id
    #Output = Details of a Artist with Past and Upcoming shows

    results = db.session.query(Show,Venue.image_link,Venue.id,Venue.name).filter_by(artist_id=artist_id).join(Venue).all()
    past_shows =[]
    upcoming_shows = []
    for show in results:
        showdata = ArtistShowResponse(
            venue_image_link=show.image_link,
            venue_id=show.id,
            venue_name=show.name,
            start_time=show.start_time,
        )
        if datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S") <= datetime.now():
            past_shows.append(showdata)
        else:
            upcoming_shows.append(showdata)
    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)
    data=Artist.query.get(artist_id)
    response = ArtistResponse(
        id=data.id,
        name=data.name,
        city=data.city,
        state=data.state,
        phone=data.phone,
        genres=data.genres,
        image_link=data.image_link,
        facebook_link=data.facebook_link,
        website=data.website_link,
        seeking_venue=data.seeking_venue,
        seeking_description=data.seeking_description,
        upcoming_shows_count=upcoming_shows_count,
        upcoming_shows=upcoming_shows,
        past_shows_count=past_shows_count,
        past_shows=past_shows,
    )

    return render_template("pages/show_artist.html", artist=response)

# ----------------------------------------------------------------------------#
#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    #This endpoint will display a form that will  display
    # details of the Artist for given artist_id prefilled
    #Output = Form to input details to edit the Artist

    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    #This endpoint will submit the ArtistForm and 
    # will edit the Artist for the given artist_id in DB
    #Input = ArtistForm and artist_id
    #Output = Displays the Artist details page for given artist_id with 
    #editted data
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    if "seeking_venue" in request.form:
        artist.seeking_venue = True
    else:
        artist.seeking_venue = False
    artist.seeking_description = form.seeking_description.data
    db.session.merge(artist)
    db.session.commit()

    return redirect(url_for("show_artist", artist_id=artist_id))

# ----------------------------------------------------------------------------#
#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    #This endpoint will display a form that will input all the 
    # details of a new Artist
    #Output = Form to input details of a new Artist

    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    #This endpoint will submit the ArtistForm and 
    # will create a new Artist in DB
    #Input = ArtistForm
    #Output = Redirects to Home page on successful 
    # creation of the artist

    error = False
    name = ""
    try:
        form = ArtistForm(request.form)
        if "seeking_venue" in request.form:
            seeking_venue = True
        else:
            seeking_venue = False
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_venue=seeking_venue,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())

    finally:
        db.session.close()
    if error:
        flash("An error occurred. Artist " + name + " could not be listed.")
    else:
        flash("Artist " + name + " was successfully listed!")
    return render_template("pages/home.html")

# ----------------------------------------------------------------------------#
#  Shows
#  ----------------------------------------------------------------

@app.route("/shows")
def shows():
    #This endpoint will list Shows from DB
    # called when user clicks on 'Show' button
    #It displays Artist image and Venue details with Show timings
    result = (
        db.session.query(
            Venue.name.label("venue_name"),
            Artist.name.label("artist_name"),
            Artist.image_link,
            Show.c.venue_id,
            Show.c.artist_id,
            Show.c.start_time,
        )
        .filter(Show.c.venue_id == Venue.id)
        .filter(Show.c.artist_id == Artist.id)
        .all()
    )
    showData = []
    for show in result:
        showData.append(
            Shows(
                show.venue_id,
                show.venue_name,
                show.artist_id,
                show.artist_name,
                show.image_link,
                show.start_time,
            )
        )

    return render_template("pages/shows.html", shows=showData)


@app.route("/shows/create")
def create_shows():
    #This endpoint will display a form that will input all the 
    # details of a new Show
    #Output = Form to input details of a new Show

    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    #This endpoint will submit the ShowForm and 
    # will create a new Show in DB
    #Input = ShowForm
    #Output = Redirects to Home page on successful 
    # creation of the Show

    error = False
    try:
        form = ShowForm(request.form)
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        start_time = form.start_time.data
        venue = Venue.query.get(venue_id)
        artist = Artist.query.get(artist_id)
        venue.artists.append(artist)
        db.session.merge(venue)
        db.session.commit()
        statement = (
            Show.update()
            .where(Show.c.artist_id == artist_id, Show.c.venue_id == venue_id)
            .values(start_time=start_time)
        )
        db.session.execute(statement)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash("An error occurred. Show could not be listed.")
    else:
        flash("Show was successfully listed!")
    return render_template("pages/home.html")
    # called to create new shows in the db, upon submitting new show listing form


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
