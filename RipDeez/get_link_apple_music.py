from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from connect_and_store import create_db, insert_song
from sqlalchemy.orm import sessionmaker


# Function to initialize WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def _switch_to_iframe(driver: webdriver.Chrome(), timeout: int = 5):
    try:
        iframe = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((
            By.TAG_NAME, 'iframe'
        )))
        driver.switch_to.frame(iframe)
    except TimeoutException:
        print("Could not switch to the iframe.")


# Function to search for songs and display them for selection
def search_song_and_select(driver, song_name):
    driver.get('https://www.deezer.com/us/channels/explore/')  # Navigate to Apple Music homepage

    # Search for the song
    search_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((
        By.XPATH, '//input[@type="search"]'
    )))
    search_box.send_keys(song_name)
    search_box.send_keys(Keys.ENTER)

    time.sleep(3)  # Give time for search results to load

    # Select the Songs link
    try:
        songs_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((
            By.XPATH, '//*[@id="scrollable-page"]/main/div/div[2]/div[5]/div/div[1]/div/h2/button'
        )))
        songs_button.click()
    except TimeoutException:
        print("Couldn't locate the Songs button, are you sure the search yielded resutls?")

    # Scrape all songs from the results
    all_songs = ''
    try:
        all_songs = WebDriverWait(driver, 5).until(EC.presence_of_element_located((
            By.CLASS_NAME, 'songs-list-row'
        )))
        all_songs = driver.find_elements(By.CLASS_NAME, 'songs-list-row')
    except TimeoutException:
        print("Couldn't locate the songs")

    if all_songs:
        # Open the database connection and create the table if it isn't created yet
        Session = sessionmaker(bind=create_db())
        session = Session()
        # Loop through each <li> and print the song
        for i, song in enumerate(all_songs, start=1):
            album_pic = song.find_element(By.TAG_NAME, 'source').get_attribute('srcset')
            album_pic = album_pic.split(",")[-1].split(" ")[0]  # Get the larger image source
            song_name = song.find_element(By.CLASS_NAME, 'songs-list__col--song')
            song_artist = song.find_element(By.CLASS_NAME, 'songs-list__col--secondary')
            song_album = song.find_element(By.CLASS_NAME, 'songs-list__col--tertiary')
            song_time = song.find_element(By.CLASS_NAME, 'songs-list__col--time')
            song_link = song_name.find_element(By.TAG_NAME, 'a').get_attribute('href')

            song_data = {
                'Song': song_name.text,
                'Artist': song_artist.text,
                'Album': song_album.text,
                'Album_Pic': album_pic,
                'Song_Time': song_time.text,
                'Link': song_link
            }
            insert_song(session, song_data)


    # Let the user select a song by index
    try:
        selected_index = int(input("\nEnter the number of the song you want to select: ")) - 1
        if selected_index < 0 or selected_index >= len(songs):
            print("Invalid selection. Please choose a number from the list.")
            return None
        selected_song = songs[selected_index]
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None

    selected_song.click()  # Navigate to the selected song's page
    time.sleep(3)  # Wait for the page to load

    # Get the share button/link
    share_button = driver.find_element(By.XPATH, "//button[@title='Share']")
    share_button.click()

    time.sleep(2)  # Wait for the share modal to appear

    share_link = driver.find_element(By.XPATH, "//input[@type='text']").get_attribute("value")
    return share_link


# Function to scrape all song links from a playlist
def get_playlist_song_links(driver, playlist_url):
    driver.get(playlist_url)  # Navigate to the playlist page

    time.sleep(5)  # Wait for the playlist page to load

    # Scrape all the song links in the playlist
    song_elements = driver.find_elements(By.XPATH, "//div[@role='rowgroup']//a")
    if not song_elements:
        print("No songs found in the playlist. Please check the playlist URL.")
        return []

    song_links = [song.get_attribute("href") for song in song_elements]
    return song_links


# # Main function to demonstrate usage
# if __name__ == "__main__":
#     driver = setup_driver()
