import hoi4
import re
import os
import hoi4


import pyradox

game = 'HoI4'

countries = hoi4.load.get_countries()
total = pyradox.Tree()

states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'history', 'states'))
state_categories = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4mod'), 'common', 'state_category'),
                                         verbose=False, merge_levels = 1)

state_categories = state_categories['state_categories']


for state in states.values():
    history = state['history']
    tag = history['owner']
    country = countries[tag]


    country['states'] = (country['states'] or 0) + 1
    total['states'] = (total['states'] or 0) + 1

    state_category_key = state['state_category']
    building_slots = state_categories[state_category_key]['local_building_slots'] or 0
    country['building_slots'] = (country['building_slots'] or 0) + building_slots
    total['building_slots'] = (total['building_slots'] or 0) + building_slots

    if 'manpower' in state:
        if (tag in history.find_all('add_core_of')
            or (tag in ['RAJ', 'SIK'])
            or (state['id'] < 200 and state['id'] != 124)):
            manpower_key = 'core_manpower'
        else:
            manpower_key = 'non_core_manpower'
        country[manpower_key] = (country[manpower_key] or 0) + state['manpower']
        total[manpower_key] = (total[manpower_key] or 0) + state['manpower']

    if 'resources' in state:
        for resource, quantity in state['resources'].items():
            country[resource] = (country[resource] or 0) + quantity
            total[resource] = (total[resource] or 0) + quantity

    for _, vp_value in history.find_all('victory_points', tuple_length = 2):
        country['victory_points'] = (country['victory_points'] or 0) + vp_value
        total['victory_points'] = (total['victory_points'] or 0) + vp_value
        country['indvidual_vp'] = (country['indvidual_vp'] or 0) + 1
        total['indvidual_vp'] = (total['indvidual_vp'] or 0) + 1

    if 'buildings' in history:
        for building, quantity in history['buildings'].items():
            if isinstance(building, str):
                country[building] = (country[building] or 0) + quantity
                total[building] = (total[building] or 0) + quantity
            else:
                # province buildings
                for building, quantity in quantity.items():
                    country[building] = (country[building] or 0) + quantity
                    total[building] = (total[building] or 0) + quantity

countriesrelease = {}
countriesstart = {}
for tag in countries:
    country = countries[tag]
    if country['states'] is not None:
        countriesstart[tag] = countries[tag]
    else:
        countriesrelease[tag] = countries[tag]

for state in states.values():
    history = state['history']
    for tag in history.find_all('add_core_of'):
        if tag in countriesrelease:
            country = countriesrelease[tag]
            country['states'] = (country['states'] or 0) + 1

            state_category_key = state['state_category']
            building_slots = state_categories[state_category_key]['local_building_slots'] or 0
            country['building_slots'] = (country['building_slots'] or 0) + building_slots

            if 'manpower' in state:
                manpower_key = 'core_manpower'
                country[manpower_key] = (country[manpower_key] or 0) + state['manpower']

            if 'resources' in state:
                for resource, quantity in state['resources'].items():
                    country[resource] = (country[resource] or 0) + quantity

            for _, vp_value in history.find_all('victory_points', tuple_length = 2):
                country['victory_points'] = (country['victory_points'] or 0) + vp_value
                country['indvidual_vp'] = (country['indvidual_vp'] or 0) + 1

            if 'buildings' in history:
                for building, quantity in history['buildings'].items():
                    if isinstance(building, str):
                        country[building] = (country[building] or 0) + quantity
                    else:
                        # province buildings
                        for building, quantity in quantity.items():
                            country[building] = (country[building] or 0) + quantity

def sum_keys_function(*sum_keys):
    def result_function(k, v):
        return '%d' % sum((v[sum_key] or 0) for sum_key in sum_keys)
    return result_function

columns = (
    ('','{{CT| col = %(color)s '),
    ('Country', 'name = %(name)s '),
    ('Tag', 'tag = %(tag)s '),
    ('Ruling ideology', lambda k, v: 'id = %s ' % (v['ruling_party']).title()),
    ('Ruling party',  lambda k, v: ('subid = %s ' % (v['ruling_subid'])) if 'ruling_subid' in v else ''),
    ('States', 'stat = %(states)d '),
    ('Research slots', lambda k, v: 'rs = %d ' % (v['set_research_slots'] or 2)),
    ('Core population (M)', lambda k, v: ('pop = %0.2f ' % (v['core_manpower'] / 1e6)) if 'core_manpower' in v else '' ),
    ('Non-core population (M)', lambda k, v: ('ncore = %0.2f ' % (v['non_core_manpower'] / 1e6)) if 'non_core_manpower' in v else '' ),
    ('Victory point', 'vp = %(indvidual_vp)d '),
    ('Victory points', 'vps = %(victory_points)d '),
    ('Building slots', 'bs = %(building_slots)d '),
    ('{{icon|MIC}}', lambda k, v: 'mil = %d ' % (v['arms_factory'] or 0)),
    ('{{icon|NIC}}', lambda k, v: 'nav = %d ' % (v['dockyard'] or 0)),
    ('{{icon|CIC}}', lambda k, v: 'civ = %d ' % (v['industrial_complex'] or 0)),
    ('{{icon|Oil}}', lambda k, v: 'oil = %d ' % (v['oil'] or 0)),
    ('{{icon|Aluminium}}', lambda k, v: 'alu = %d ' % (v['aluminium'] or 0)),
    ('{{icon|Rubber}}', lambda k, v: 'rub = %d ' % (v['rubber'] or 0)),
    ('{{icon|Tungsten}}', lambda k, v: 'tun = %d ' % (v['tungsten'] or 0)),
    ('{{icon|Steel}}', lambda k, v: 'ste = %d ' % (v['steel'] or 0)),
    ('{{icon|Chromium}}', lambda k, v: 'chr = %d ' % (v['chromium'] or 0)),
    ('{{icon|Crystals}}', lambda k, v: 'cry = %d ' % (v['crystals'] or 0)),
    #('Air base levels', '%(air_base)d'),
    #('Naval base levels', '%(naval_base)d'),
    ('Science base', 'sci = %(science)s '),
    ('Societal development', 'soc = %(society)s '),
    ('Illiteracy', 'ill = %(illiteracy)s '),
    ('Poverty', 'pov = %(poverty)s '),
    ('Race', 'race = %(race)s '),
    ('Notes','}}')
    )

out = open("out/countriesstart.txt", "w", encoding='utf-8')
out.write(pyradox.table.make_table(countriesstart, 'template', columns, sort_function = lambda key, value: value['name']))
out.close()

out = open("out/countriesrelease.txt", "w", encoding='utf-8')
out.write(pyradox.table.make_table(countriesrelease, 'template', columns, sort_function = lambda key, value: value['name']))
out.close()

print(total)
