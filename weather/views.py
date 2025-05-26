from datetime import datetime
import os
import requests
from django.http import JsonResponse
from dotenv import load_dotenv
from django.shortcuts import render
from .models import CheckedCity, CityCounter
from datetime import date
from rest_framework import viewsets, generics
from django.forms.models import model_to_dict
from .serializers import CheckedCitySerializer, CityCounterSerializer

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
GEOCODE_API_KEY = os.getenv('GEOCODE_API_KEY')


# Функция для просмотра погоды
def index(request):
    if request.method == 'POST':
        city = request.POST['city']
        city = city.title()
        # Сохраняем город в сесию пользователя
        request.session['city'] = city
        # Получаем дату и записываем текущий запрос в историю
        today = date.today()
        entry = CheckedCity()
        entry.city = city
        entry.date = today
        entry.save()
        # Смотрим если этот город уже искали, если да то увеличиваем счетчик, если нет то делаем новый
        # Важно, "Москва" и "Moscow" будут иметь разные записи, к сожалению поправить это не смог
        if CityCounter.objects.filter(city__contains=city):
            counter = CityCounter.objects.filter(city__contains=city)[0]
            counter.count += 1
            counter.save()
        else:
            counter = CityCounter()
            counter.city = city
            counter.count = 1
            counter.save()
        language = request.POST['language']
        # порядок формата - API key, latitude, longitude
        weather_url = 'https://api.pirateweather.net/forecast/{}/{},{}?exclude=alerts,minutely,hourly&units=si'
        # порядок формата - Город, API key
        geocode_url = 'https://geocode.maps.co/search?q={}&api_key={}'

        current_weather_data, daily_forecast = fetch_forecast(city, weather_url, geocode_url, language)

        context = {
            'current_weather_data': current_weather_data,
            'daily_forecast': daily_forecast,
            'city': city,
            'language': language
        }
        # Если пользователь имеет сохраненный город, то передадим его, чтобы ставить как значение по умолчанию
        try:
            context['last_city'] = request.session['city']
        except KeyError:
            pass

        return render(request, 'index.html', context)
    else:
        # Если пользователь имеет сохраненный город, то передадим его, чтобы ставить как значение по умолчанию
        try:
            context = {
                'last_city': request.session['city']
            }
        except KeyError:
            context = {}
        return render(request, 'index.html', context)


# Функция для получения погоды
def fetch_forecast(city, weather_url, geocode_url, language):
    geo_response = requests.get(geocode_url.format(city, GEOCODE_API_KEY)).json()
    lat = geo_response[0]['lat']
    lon = geo_response[0]['lon']
    weather_response = requests.get(weather_url.format(WEATHER_API_KEY, lat, lon)).json()

    current_weather_data = {
        "city": city,
        "temperature": weather_response['currently']['temperature'],
        "description": weather_response['currently']['summary'],
        "icon": weather_response['currently']['icon']
    }

    daily_forecast = []
    for daily_data in weather_response['daily']['data'][1:]:
        daily_forecast.append({
            "day": (datetime.fromtimestamp(daily_data['time']).strftime("%A")),
            'min_temp': daily_data['temperatureMin'],
            'max_temp': daily_data['temperatureMax'],
            'description': daily_data['summary'],
            'icon': daily_data['icon']
        })

    if language == 'rus':
        translation_days = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье',
        }
        # К сожалению список не полный, ибо API не предоставляет все возможные варианты, в отличие от icon
        translation_description = {
            'Snow': 'Снег',
            'Clear': 'Ясно',
            'Cloudy': 'Облачно',
            'Partly Cloudy': 'Местами облачно',
            'Rain': 'Дождь',
            'Windy': 'Ветряно',
            'Possible drizzle': 'Возможен морось',
            'Drizzle': 'Морось',
            'Mostly Clear': 'В основном ясно',
            'Light rain': 'Слабый дождь',
            'Light rain and breezy': 'Слабый дождь и слабый ветер',
            'Overcast': 'Пасмурно',
            'Breezy': 'Слабый ветер',
            'Dry and clear': 'Сухо и ясно'
        }
        for data in daily_forecast:
            data['day'] = translation_days[data['day']]
            if data['description'][-1] == '.':
                data['description'] = data['description'][:-1]
            if data['description'] in translation_description:
                data['description'] = translation_description[data['description']]

        if current_weather_data['description'] in translation_description:
            current_weather_data['description'] = translation_description[current_weather_data['description']]

    return current_weather_data, daily_forecast


# функция для подсказок
def autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term').title()
        qs = CityCounter.objects.filter(city__istartswith=term)
        city_list = []
        for counter in qs:
            city_list.append(counter.city)
        return JsonResponse(city_list, safe=False)
    else:
        return JsonResponse('none', safe=False)


# Все что снизу связанно с RestAPI для статистики.
# Используются generics поскольку сама апишка очень проста.
class GetCityCounters(generics.ListAPIView):
    queryset = CityCounter.objects.all()
    serializer_class = CityCounterSerializer


class GetCityCounter(generics.RetrieveAPIView):
    queryset = CityCounter.objects.all()
    serializer_class = CityCounterSerializer
    lookup_field = 'city'


class GetCheckedCities(generics.ListAPIView):
    queryset = CheckedCity.objects.all()
    serializer_class = CheckedCitySerializer
