import datetime

import requests


class WeatherFinder:
    def __init__(self, api_key, city_id, model, model_data):
        self.key = api_key
        self.city_id = city_id
        self.model = model
        self.model_data = model_data

    def get_weather(self):
        if self.get_location():
            return True
        else:
            return False

    def get_location(self):
        city = self.model.objects.get(id=self.city_id)
        URL = f'http://api.openweathermap.org/data/2.5/weather?q={city.name}&appid={self.key}'
        response = requests.get(URL)
        if response.status_code == 404:
            self.model.objects.get(pk=self.city_id).delete()
            return False
        else:
            response = response.json()
            data = {
                'city_id': city,
                'lon': response['coord']['lon'],
                'lat': response['coord']['lat']
            }
            return self.one_call(data)

    def one_call(self, data):
        URL = f'https://api.openweathermap.org/data/2.5/onecall?lat={data["lat"]}&lon={data["lon"]}&units=metric&exclude=current,minutely,hourly&appid={self.key}'
        response = requests.get(URL)
        response = response.json()
        for day in response['daily']:
            temp_date = datetime.datetime.fromtimestamp(day['dt'])
            data.update({
                "weather": day['weather'][0]['main'],
                "date": temp_date.strftime('%Y-%m-%d'),
                "temp": day['temp']['day'],
                "pressure": day['pressure'],
                "humidity": day['humidity'],
                "wind_speed": day['wind_speed'],
            })

            if self.model_data.objects.filter(date=temp_date.strftime('%Y-%m-%d')).filter(city_id=self.city_id).exists():
                continue
            else:
                self.model_data(**data).save()

        return True
