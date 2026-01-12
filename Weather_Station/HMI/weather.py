import requests

def get_current_temperature(lat, lon):
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        return data["current_weather"]["temperature"]

    except Exception as e:
        print("Weather error:", e)
        return None
