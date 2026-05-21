import python_weather
import asyncio
import os


async def _fetch_weather(city):
    async with python_weather.Client(unit=python_weather.IMPERIAL) as c:
        return await c.get(city)


def get_weather(city="Chicago"):
    return str(asyncio.run(_fetch_weather(city)))


def search_images(query):
    from icrawler.builtin import GoogleImageCrawler
    os.makedirs("./images", exist_ok=True)
    for f in os.listdir("./images"):
        try:
            os.remove(os.path.join("./images", f))
        except OSError:
            pass
    crawler = GoogleImageCrawler(storage={"root_dir": "./images"})
    crawler.crawl(keyword=query, max_num=1)


def parse_command(command: str) -> dict:
    result = {}
    cmd = command.lower().strip()

    if "weather" in cmd:
        try:
            result["weather"] = get_weather()
        except Exception as e:
            result["weather_error"] = str(e)

    if "search" in cmd:
        query = cmd.split("-", 1)[1].strip() if "-" in cmd else cmd.replace("search", "").strip()
        try:
            search_images(query)
            result["search"] = f"Searched for: {query}"
        except Exception as e:
            result["search_error"] = str(e)

    for action in ("play", "pause", "skip", "previous", "spotify"):
        if action in cmd:
            try:
                import spot
                if action == "play":
                    spot.start_music()
                elif action == "pause":
                    spot.stop_music()
                elif action == "skip":
                    spot.skip_to_next()
                elif action == "previous":
                    spot.skip_to_previous()
                elif action == "spotify":
                    result["spotify"] = str(spot.get_current_playing_info())
                if action != "spotify":
                    result[action] = True
            except Exception as e:
                result[f"{action}_error"] = str(e)

    return result
