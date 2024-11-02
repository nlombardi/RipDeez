from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

BASE_PATH = Path(__file__).resolve().parent
DATA_PATH = BASE_PATH / 'Data'
DATA_PATH.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_PATH / 'songs.db'


# Create a base class using declarative_base
Base = declarative_base()


# Define the Song model which maps to the 'songs' table
class Song(Base):
    __tablename__ = 'songs'

    number = Column(Integer, primary_key=True, autoincrement=True)  # This will store the song's number, acts as a primary key
    song = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=False)
    album_pic = Column(String, nullable=True)
    song_time = Column(String, nullable=False)
    link = Column(String, nullable=False)

    # Add a unique constraint on (song, artist, album) to avoid duplicates
    __table_args__ = (UniqueConstraint('song', 'artist', 'album', name='_song_artist_album_uc'),)


# Function to create the database and initialize the table
def create_db():
    # Connect to SQLite database (or create it)
    engine = create_engine(f'sqlite:///{DB_PATH}')

    # Create all tables that are mapped by SQLAlchemy models
    Base.metadata.create_all(engine)
    #
    # Session = sessionmaker(bind=engine)

    # Return the session factory
    return engine


# Function to insert a song into the database
def insert_song(session, song_data):
    try:
        # Create a new Song object using the song_data dictionary
        new_song = Song(
            song=song_data['Song'],
            artist=song_data['Artist'],
            album=song_data['Album'],
            album_pic=song_data['Album_Pic'],
            song_time=song_data['Song_Time'],
            link=song_data['Link']
        )
        # Add the new song to the session and commit it to the database
        session.add(new_song)
        session.commit()
    except IntegrityError as e:
        # If the song (song, artist, album) already exists in the database then sqlalchemy will raise IntegrityError
        session.rollback()  # rollback the addition


# Function to retrieve all songs from the database
def get_all_songs(session):
    songs = session.query(Song).all()
    return songs

#
# # Main function to demonstrate usage
# if __name__ == "__main__":
#     # Create the database and get a session
#     engine = create_db()
#     session = Session(engine)
#
#     # Example song data dictionary
#     song_data = {
#         "#": 1,
#         "Song": "Shape of You",
#         "Artist": "Ed Sheeran",
#         "Album": "Divide",
#         "Album_Pic": "https://example.com/album-pic.jpg",
#         "Song_Time": "3:53",
#         "Link": "https://music.apple.com/song-link"
#     }
#
#     # Insert the song into the database
#     insert_song(session, song_data)
#
#     # Retrieve and print all songs
#     songs = get_all_songs(session)
#     for song in songs:
#         print(f"{song.number}: {song.song} by {song.artist} from the album {song.album}")
#
#     # Close the session
#     session.close()
