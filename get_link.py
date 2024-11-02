from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchAttributeException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from connect_and_store import create_db, insert_song
from sqlalchemy.orm import sessionmaker

chrome_path = 'Q:/Development/Web Scraping/Chrome/chromedriver.exe'


# Function to initialize WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(chrome_path), options=options)
    return driver


def _switch_to_iframe(driver: webdriver.Chrome(), timeout: int = 5):
    try:
        iframe = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((
            By.TAG_NAME, 'iframe'
        )))
        driver.switch_to.frame(iframe)
    except TimeoutException:
        print("Could not switch to the iframe.")


def wait_for_element(driver, time_to_wait, by_type, by_element):
    try:
        if by_type == 'CSS_SELECTOR':
            element = WebDriverWait(driver, time_to_wait).until(EC.presence_of_element_located((
                By.CSS_SELECTOR, by_element
            )))
        elif by_type == 'XPATH':
            element = WebDriverWait(driver, time_to_wait).until(EC.presence_of_element_located((
                By.XPATH, by_element
            )))
        elif by_type == 'CLASS':
            element = WebDriverWait(driver, time_to_wait).until(EC.presence_of_element_located((
                By.CLASS_NAME, by_element
            )))
        elif by_type == 'TAG':
            element = WebDriverWait(driver, time_to_wait).until(EC.presence_of_element_located((
                By.TAG_NAME, by_element
            )))
        elif by_type == 'ID':
            element = WebDriverWait(driver, time_to_wait).until(EC.presence_of_element_located((
                By.ID, by_element
            )))
        else:
            return print("By type is not valid.")
        return element
    except TimeoutException:
        print("Could not locate the element.")


# Function to search for songs and display them for selection
def search_song_and_select(driver, song_name):
    driver = setup_driver()
    song_name = "Get Crazy"

    base_url = 'https://www.deezer.com'

    # Try and search through http first
    song_url = base_url + '/search/' + '%20'.join(song_name.split(' '))
    driver.get(song_url)

    # Accept cookies if pop-up is there
    accept_cookies = wait_for_element(driver, 5, 'ID', 'gdpr-btn-accept-all')
    if accept_cookies:
        accept_cookies.click()

    # time.sleep(3)  # Give time for search results to load

    # Click the tracks tab
    track_tab = wait_for_element(driver, 5, 'XPATH', "//a[text()='Tracks']")
    if track_tab:
        track_tab.click()

    # driver.get(base_url + '/us/channels/explore/')


    # Scrape all songs from the results
    all_songs = ''
    all_songs = wait_for_element(driver, 5, 'XPATH', "//div[@role='rowgroup']")
    time.sleep(3)
    if all_songs:
        all_songs = driver.find_elements(By.XPATH, "//div[@role='row']")

        # Open the database connection and create the table if it isn't created yet
        Session = sessionmaker(bind=create_db())
        session = Session()
        # Loop through each <li> and print the song
        for i, song in enumerate(all_songs, start=1):
            song_artist, song_name, album_pic, song_link = None, None, None, None
            # Click the info button
            song_info_button = song.find_element(By.CLASS_NAME, 'popper-wrapper')
            if song_info_button:
                song_info_button.click()
                time.sleep(2)
                share_div = driver.find_element(By.CLASS_NAME, 'popper')
                share_button = share_div.find_element(By.XPATH, "//span[text()='Share']")
                if share_button:
                    share_button.click()
                    time.sleep(2)
                    # Get the modal and information within (easier than scraping the DIVs and gets a larger image)
                    share_modal = driver.find_element(By.ID, 'modal_sharebox')
                    album_pic = share_modal.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    song_name = share_modal.find_element(By.ID, 'share-title').text
                    song_artist = share_modal.find_element(By.ID, 'share-subtitle').text.split("by")[-1].lstrip()
                    song_link = share_modal.find_element(By.ID, 'share-input').get_attribute('value')
                    # Close the Model
                    close_button = share_modal.find_element(By.ID, 'modal-close')
                    if close_button:
                        close_button.click()
                else:
                    print("Share button not found, maybe remapped?")
            else:
                print("Share info button not found, maybe remapped?")
            # Song Album, Song Time, Song Popularity are not within the modal
            if not album_pic:
                album_pic = song.find_element(By.TAG_NAME, 'img').get_attribute('src')  # thumbnail
            if not song_artist:
                song_artist = song.find_elements(By.XPATH, "//a[@data-testid='artist']")
            if not song_name:
                song_name = song.find_element(By.XPATH, "//span[@data-testid='title']")
            song_album = song.find_element(By.XPATH, "//a[@data-testid='album']").text
            song_time = song.find_element(By.XPATH, "//span[@data-testid='duration']").text
            song_pop = song.find_element(By.XPATH, "//div[@data-testid='popularity']").get_attribute('aria-label')
            song_pop = float(song_pop.split(":")[-1].split("/")[0].strip(" "))

            song_data = {
                'Song': song_name,
                'Artist': song_artist,
                'Album': song_album,
                'Album_Pic': album_pic,
                'Song_Time': song_time,
                'Link': song_link,
                'Popularity': song_pop
            }
            print(song_data)
            break
            # insert_song(session, song_data)


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


# Main function to demonstrate usage
if __name__ == "__main__":
    driver = setup_driver()


    if logged_in:
        # Search for a song and select from a list of results
        song_name = input("Enter the name of the song you want to search for: ")
        song_share_link = search_song_and_select(driver, song_name)
        if song_share_link:
            print(f"Share link for the selected song: {song_share_link}")

        # Get all song links from a playlist
        playlist_url = "https://music.apple.com/us/playlist/example-playlist-url"  # Replace with a real playlist URL
        playlist_song_links = get_playlist_song_links(driver, playlist_url)

        print(f"Song links from the playlist: {playlist_song_links}")

    driver.quit()
