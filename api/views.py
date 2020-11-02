from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import WeatherDataForm

import requests
import calendar 
from datetime import datetime, timedelta

import statistics 

def home(request):
    if request.method == 'GET':
        form = WeatherDataForm(request.GET)
        if form.is_valid():
            city = form.cleaned_data.get('city')
            period = form.cleaned_data.get('period')
            url = f'http://localhost:8000/api/v1/weather/?city_name={city}&period={period}'
            r = requests.get(url)
            data = r.json()

            graph_values = [ v for v in data['data'].values() ]

            form = WeatherDataForm()
            return render(request, 'api/home.html', {'form': form, 'cntx': data, 'graph': graph_values })
        else:
            url = f'http://localhost:8000/api/v1/weather/'
            r = requests.get(url)
            data = r.json()
            graph_values = [ v for v in data['data'].values() ]
            
            form = WeatherDataForm()
            return render(request, 'api/home.html', {'form': form, 'cntx': data, 'graph': graph_values })


@api_view(['GET'])
def api_view(request):

    api_key = '5b77aa9bcbb4556156fca77241cdf50c'
    city_name = ''
    period = ''

    ''' 
    Checking if user passed params in the url or get request 
    If none are sent, the app will use defaults for an example to the user    
    '''

    if request.query_params:
        city_name = str(request.query_params['city_name']).lower()
        period = str(request.query_params['period']).lower()
    else:
        city_name = 'cape town'
        period = 'tomorrow'

    ''' Setting up the public API URL that will be consumed by the weather app '''

    url = f'https://api.openweathermap.org/data/2.5/forecast?q={city_name}&units=metric&appid={api_key}'
    posts = requests.get(url)

    ''' Creating a context var to pass to our endpoint '''
    context = {}

    ''' Checking for a successful request '''
    if posts.status_code == 200:
        json_posts = posts.json()['list']

        ''' temp storage for the first iterations '''
        data = {}

        ''' The dates will be provided as periods in the front-end: [Today, Tomorrow, Tuesday...] '''
        dates = set( [i['dt_txt'][:10] for i in json_posts] )

        ''' Getting the data from the intervals for each day/period 
            This will be aggregated in the endpoint
        '''
        for date in dates:
            data[date+'_max_temps'] = []
            data[date+'_min_temps'] = []
            data[date+'_humidity'] = []
            for row in json_posts:
                if row['dt_txt'][:10] == date:
                    data[date+'_max_temps'].append(row['main']['temp_max'])
                    data[date+'_min_temps'].append(row['main']['temp_min'])
                    data[date+'_humidity'].append(row['main']['humidity'])

        ''' rsp_data will be a temp storage container 
            It will also house the aggregated data
        '''
        rsp_data = {}

        for date in dates:
            date_key = ''
            date_time_obj = datetime.strptime(date, '%Y-%m-%d')

            if date_time_obj.weekday() == datetime.today().weekday():
                date_key = 'today'
            elif date_time_obj.weekday() == (datetime.today() + timedelta(days=1) ).weekday() :
                date_key = 'tomorrow'
            else:
                date_key = (calendar.day_name[date_time_obj.weekday()]).lower()

            ''' Aggregating the data
                The app will provide 2 median values. One for Max and one for Mix temperatures
            '''
            rsp_data[date_key] = {
                'max': max(data.get(date+'_max_temps')),
                'min': min(data.get(date+'_min_temps')),
                'avg': round( sum(data.get(date+'_max_temps')) / len(data.get(date+'_max_temps')), 2),
                'median_max': round( statistics.median(data.get(date+'_max_temps')), 2),
                'median_min': round( statistics.median(data.get(date+'_min_temps')), 2),
                'humidity': round( sum(data.get(date+'_humidity')) / len(data.get(date+'_humidity')), 2)
            }        
        
        ''' The app continues to feed the context dictionary '''

        context['message'] = 'request successful'
        context['city'] = city_name
        context['period'] = period
        context['data'] = rsp_data.get(period)
    else:
        ''' If the request doesnt return a status of 200
            This could be due to the incorrect spelling of city or the city is not available in the public API
        '''
        context['message'] =  'request failed. please check your city'
    
    return Response(context)
