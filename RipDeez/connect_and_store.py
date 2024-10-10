from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


# Function to retrieve all songs from the database
def get_all_songs(session):
    songs = session.query(Song).all()
    return songs


# Main function to demonstrate usage
if __name__ == "__main__":
    # Create the database and get a session
    Session = create_db()
    session = Session()

    # Example song data dictionary
    song_data = {
        "#": 1,
        "Song": "Shape of You",
        "Artist": "Ed Sheeran",
        "Album": "Divide",
        "Album_Pic": "https://example.com/album-pic.jpg",
        "Song_Time": "3:53",
        "Link": "https://music.apple.com/song-link"
    }

    # Insert the song into the database
    insert_song(session, song_data)

    # Retrieve and print all songs
    songs = get_all_songs(session)
    for song in songs:
        print(f"{song.number}: {song.song} by {song.artist} from the album {song.album}")

    # Close the session
    session.close()
