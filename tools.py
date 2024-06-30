import python_weather
import asyncio
import assist
from icrawler.builtin import GoogleImageCrawler
import os
import spot

async def get_weather(city_name):
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(city_name)
        return weather

def search(query):
    google_Crawler = GoogleImageCrawler(storage = {"root_dir": r'./images'})
    google_Crawler.crawl(keyword = query, max_num = 1)


def parse_command(command):
    if "weather" in command:
        weather_description = asyncio.run(get_weather("Chicago"))
        query = "System information: " + str(weather_description)
        print(query)
        response = assist.ask_question_memory(query)
        done = assist.TTS(response)

    if "search" in command:
        files = os.listdir("./images")
        [os.remove(os.path.join("./images", f))for f in files]
        query = command.split("-")[1]
        search(query)
    
    if "play" in command:
        spot.start_music()

    if "pause" in command:
        spot.stop_music()
    
    if "skip" in command:
        spot.skip_to_next()
    
    if "previous" in command:
        spot.skip_to_previous()
    
    if "spotify" in command:
        spotify_info = spot.get_current_playing_info()
        query = "System information: " + str(spotify_info)
        print(query)
        response = assist.ask_question_memory(query)
        done = assist.TTS(response)
        

    

        