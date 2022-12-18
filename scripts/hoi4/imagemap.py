import hoi4
import csv
import os
import re
import collections


import pyradox


from PIL import Image

# province IDs to ignore
ignore = [13204]

date = pyradox.Time('1007.1.1')
#date = pyradox.Time('1939.8.14')


# Load states.
states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'))
countries = hoi4.load.get_countries()

# tag -> provinces

country_provinces = {}

for state in states.values():
    history = state['history'].at_time(date)
    controller = history['controller'] or history['owner']

    if controller not in country_provinces: country_provinces[controller] = []

    for province_id in state.find_all('provinces'):
        if not province_id in ignore:
            country_provinces[controller].append(province_id)

links = []
for tag, province_ids in country_provinces.items():
    link = '[[%s]]' % countries[tag]['name']
    links.append((province_ids, link))

province_map = pyradox.worldmap.ProvinceMap(game = 'HoI4')


print(province_map.generate_image('File:Political map.png|thumb|800px|center|Countries in 1936.', links))
