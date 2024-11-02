from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from connect_and_store import Song, DB_PATH  # Import the Song model
from get_link import search_song_and_select

# Initialize Flask app
app = Flask(__name__)

# Database setup
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
session = Session()


# Home page with search functionality
@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get the search term from the form
        search_term = request.form.get('search_term')

        # Query the database for songs that match the search term (song, artist, or album)
        results = session.query(Song).filter(
            (Song.song.ilike(f"%{search_term}%")) |
            (Song.artist.ilike(f"%{search_term}%")) |
            (Song.album.ilike(f"%{search_term}%"))
        ).all()

        # If no results are found, call the external `search_and_select` function
        if not results:
            print("No results found in the database, calling external search...")
            external_results = search_and_select(search_term)

            # Insert external results into the database
            if external_results:
                for song_data in external_results:
                    insert_song(session, song_data)

                # Query the database again to get the newly inserted songs
                results = session.query(Song).filter(
                    (Song.song.ilike(f"%{search_term}%")) |
                    (Song.artist.ilike(f"%{search_term}%")) |
                    (Song.album.ilike(f"%{search_term}%"))
                ).all()

        # Render the search result page with the results
        return render_template('search.html', songs=results, search_term=search_term)

    # Default to just showing the search form with no results
    return render_template('search.html', songs=[], search_term='')


# Route to return the link for the selected song
@app.route('/get_link/<int:song_id>', methods=['GET'])
def get_link(song_id):
    # Find the song by its ID
    song = session.query(Song).filter_by(number=song_id).first()

    # Redirect or show the link in some way
    if song:
        return f"Link to the song: <a href='{song.link}' target='_blank'>{song.link}</a>"
    return "Song not found", 404


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
