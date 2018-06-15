#!/usr/bin/env python3
#
#Скрипт оценки достоверности дневного прогноза погоды в Москве сервиса Яндекс.Погода по сроку предсказания
#С использованием только стандартных модулей Python 3.6.5 32-bit Win 
#A script for assessing the reliability of the daily weather forecast in Moscow by Yandex.Weather on the date of prediction
#
#Copyright (C) 2018 dx-77 <d.x77@yandex.ru>.
#GitHub : https://github.com/dx-77
#
#This program is free software: you can redistribute it and/or modify it under the terms
#of the GNU General Public License as published by the Free Software Foundation,
#either version 3 of the License, or (at your option) any later version.
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#See the GNU General Public License for more details.
# 
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import urllib.request

CITY = 'moscow'
WEATHER_URL = 'https://yandex.ru/pogoda/'
CHARSET_URL = 'utf-8'
MAX_DAYS = 7
# Current Yandex Tags 15.06.2018
FACT_TEMP_TAG = '<div class="temp fact__temp"><span class="temp__value">'
NOW_DATE_TAG = '<time class="time fact__time" datetime="'
LOCATION_TAG = '<div class="location"><h1 class="title title_level_1">'  
FORECAST_DATE_TAG = '<time class="time forecast-briefly__date" datetime="'
FORECAST_TEMP_TAG = '<div class="temp forecast-briefly__temp forecast-briefly__temp_day"><span class="temp__value">'


def get_info(weather_page, tag, sym='<'):
    index = weather_page.find(tag) + len(tag)
    infostr = weather_page[index:index + 64]
    infostr = infostr[:infostr.find(sym)]

    return infostr


def check_actual_weather(weather_page):
    current_temp = get_info(weather_page, FACT_TEMP_TAG)
    current_date = get_info(weather_page, NOW_DATE_TAG, '"')
    location = get_info(weather_page, LOCATION_TAG)

    return(location, current_temp, current_date)


def save_weather(weather_page, now, filename):
    filename = filename + '.txt'
    try:
        data = []
        with open(filename, 'r') as f:
            count = 0
            for line in f:
                if line.split(';')[0].split()[0] == now.split()[0]: # Если сегодняшняя дата уже есть в файле
                    break
                data.append(line)
                count += 1
                if count == MAX_DAYS + 1:
                	data.pop(0)
                	break
    except:
        pass

    tag = 'Сегодня</div>' + FORECAST_DATE_TAG
    weather_page = weather_page[weather_page.find(tag) + len(tag):]
    weather_list = []
    for i in range(MAX_DAYS):
        weather_list.append((
            get_info(weather_page, FORECAST_DATE_TAG, '"').split()[0], 
            get_info(weather_page, FORECAST_TEMP_TAG)
        ))
        weather_page = weather_page[weather_page.find(FORECAST_TEMP_TAG) + len(FORECAST_TEMP_TAG):]

    try:
        with open(filename, 'w') as f:
            if data != []:
                for d in data:
                    f.write(d)

            f.write(now + ';')
            for wl in weather_list:
                f.write('%s %s;' % wl)
            f.write('\n')
        print('Прогноз успешно сохранен в файле "%s"' % filename)
    except Exception as e:
        print('Unable to save to file "%s"' % filename)
        print(e)
       

def load_weather(weather_page, now, filename, now_temp, days_to_load):
    if days_to_load > MAX_DAYS:
        days_to_load = MAX_DAYS
    filename = filename + '.txt'
    forecast_temp = []
    now_temp = float(now_temp)
    try:
        with open(filename, 'r') as f:
            for line in f:
                linelist = line.split(';')[1:-1]
                for s in linelist:
                    if s.split()[0] == now.split()[0]:
                        forecast_temp.append((line.split(';')[0], s)) # Дата прогноза и прогноз на сегодня
                        break
                    
        if forecast_temp == []:
        	print('Файл "%s" не содержит прогнозов на дату %s' % (filename, now.split()[0]))
        	return
        	
        for ft in forecast_temp[::-1]:
        	fc_temp = float(ft[1].split()[1])
        	if fc_temp:
        		percent = abs(now_temp*100/fc_temp - 100)
        	else:
        		percent = 999
        	print(
        		'Сегодняшняя погода отличается от предсказанной %s  на %0.1f%% (%0.1f гр.)' \
        		% (ft[0], percent, abs(fc_temp - now_temp))
        	)
    except Exception as e:
        print('Файл с прогнозами не существует, к нему нет доступа или он имеет неверный формат!'
              'Cannot read the file "%s"' % filename)
        print(e)
        return


def estimate(action='est', days_to_load=MAX_DAYS, url=WEATHER_URL, city=CITY, charset=CHARSET_URL):
    try:
        weather_page = urllib.request.urlopen(url + city).read().decode(charset)
    except Exception as e:
        print('Unable to open page "%s"' % (url + city))
        print(e)
        return
    location, current_temp, current_date = check_actual_weather(weather_page)

    if action == 'est':
        print('\nСейчас: %s \n%s: %s' % (current_date, location, current_temp))
        load_weather(weather_page, current_date, city, current_temp, days_to_load)
    elif action == 'chk':
        print('\nСейчас: %s \n%s: %s' % (current_date, location, current_temp))
    elif action == 'sv':
        save_weather(weather_page, current_date, city)
 

if __name__ == '__main__':
    print('CheckWeather version 0.5')
    while True:
        print('\n1. Оценить достоверность прогноза') # Check weather reliability
        print('2. Показать актуальную погоду') # Show actual weather
        print('3. Сохранить сегодняшний прогноз на %d дн.' % MAX_DAYS) # Save weather forecast to file
        print('4. Выход из программы') # Exit program
        num = input('Введите номер пункта меню (1, 2, 3 или 4) и нажмите Enter: ') # Input number
        if num == '1':
            estimate()
        elif num == '2':
            estimate('chk')
        elif num == '3':
            estimate('sv')
        elif num == '4':
            break
        else:
            print('Такой пункт меню отсутствует!') # There is no such number       