import hoi4
import re
import os
import json
import hoi4
import pyradox

date = '1007.1.1'

beta = False

if beta:
    game = 'HoI4_beta'
else:
    game = 'HoI4'

localisation_sources = ['state_names']

countries = hoi4.load.get_countries()

states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory(game), 'history', 'states'))
state_categories = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4mod'), 'common', 'state_category'),
                                         verbose=False, merge_levels = 1)

state_categories = state_categories['state_categories']



for state in states.values():
    history = state['history'].at_time(date, merge_levels = -1)
    # if state['id'] == 50: print('state50', history)
    state['owner'] = history['owner']
    state['owner_name'] = countries[history['owner']]['name']
    state['human_name'] = pyradox.yml.get_localisation(state['name'], game = game)

    state['cores_name'] = '<ul style="list-style:none; margin:0;">'
    for core in history.find_all('add_core_of'):
        human_core = countries[core]['name']
        flag_core = ' <li>{{flag|%s|wrap = yes}}</li>' % human_core
        state['cores_name'] += flag_core
    state['cores_name'] += '</ul>'

    state['claims_name'] = ''
    #i hate this solution
    state_claims_counter = 0
    for i in history.find_all('add_claim_by'):
        state_claims_counter += 1

    if state_claims_counter > 0:
        state['claims_name'] = '<ul style="list-style:none; margin:0;">'
        for claim in history.find_all('add_claim_by'):
            human_claim = countries[claim]['name']
            flag_claim = ' <li>{{flag|%s|wrap = yes}}</li>' % human_claim
            state['claims_name'] += flag_claim
        state['claims_name'] += '</ul>'

    country = countries[state['owner']]

    country['states'] = (country['states'] or 0) + 1

    state['state_category_name'] = pyradox.yml.get_localisation(state['state_category'], game = game)

    state_category_key = state['state_category']
    state['building_slots'] = state_categories[state_category_key]['local_building_slots'] or 0
    country['building_slots'] = (country['building_slots'] or 0) + state['building_slots']

    if 'resources' in state:
        for resource, quantity in state['resources'].items():
            state[resource] = quantity
    state['indvidual_vp_total'] = 0
    for _, victory_points in history.find_all('victory_points', tuple_length = 2):
            state['indvidual_vp_total'] = (state['indvidual_vp_total'] or 0) + 1
            state['victory_point_total'] = (state['victory_point_total'] or 0) + victory_points

    if 'buildings' in history:
        for building, quantity in history['buildings'].items():
            if isinstance(building, str):
                state[building] = (state[building] or 0) + quantity
            else:
                # province buildings
                for building, quantity in quantity.items():
                    state[building] = (state[building] or 0) + quantity

def sum_keys_function(*sum_keys):
    def result_function(k, v):
        return '%d' % sum((v[sum_key] or 0) for sum_key in sum_keys)
    return result_function

columns = (
    ('Name', '%(human_name)s'),
    ('ID', '%(id)s'),
    ('Country', '{{flag|%(owner_name)s|wrap = yes}}'),
    # ('Tag', '%(owner)s'),
    ('{{Icon|vp|width=20px}}', '%(victory_point_total)d(%(indvidual_vp_total)d)'),
    ('{{Icon|pop|(M)|width=20px}}', lambda k, v: '%0.2f' % ((v['manpower'] or 0) / 1e6) ),
    ('{{Icon|infra|width=20px}}', '%(infrastructure)d'),
    ('State category', '%(state_category_name)s'),
    ('{{Icon|Building slot|width=20px}}', '%(building_slots)d'),
    ('{{Icon|MIC|width=20px}}', '%(arms_factory)d'),
    ('{{Icon|NIC|width=20px}}', '%(dockyard)d'),
    ('{{Icon|CIC|width=20px}}', '%(industrial_complex)d'),
    # ('Total factories', sum_keys_function('arms_factory', 'dockyard', 'industrial_complex')),
    ('{{Icon|Oil|width=20px}}', '%(oil)d'),
    ('{{Icon|Aluminium|width=20px}}', '%(aluminium)d'),
    ('{{Icon|Rubber|width=20px}}', '%(rubber)d'),
    ('{{Icon|Tungsten|width=20px}}', '%(tungsten)d'),
    ('{{Icon|Steel|width=20px}}', '%(steel)d'),
    ('{{Icon|Chromium|width=20px}}', '%(chromium)d'),
    ('{{Icon|Crystal|width=20px}}', '%(crystals)d'),
    # ('Total resources', sum_keys_function('oil', 'aluminium', 'rubber', 'tungsten', 'steel', 'chromium')),
    ('{{Icon|Air base|width=20px}}', '%(air_base)d'),
    ('{{Icon|Naval base|width=20px}}', '%(naval_base)d'),
    ('Cores', '%(cores_name)s'),
    ('Claims', '%(claims_name)s'),
    )

if beta:
    out_filename = "out/states_beta.txt"
else:
    out_filename = "out/states.txt"
with open(out_filename, "w", encoding='utf-8') as out:
    out.write(pyradox.table.make_table(states, 'wiki', columns, sort_function = lambda key, value: value['id']))

if beta:
    csv_filename = "out/states_beta.csv"
else:
    csv_filename = "out/states.csv"

pyradox.csv.write_tree(states, csv_filename, columns, 'excel', sort_function = lambda key, value: value['id'])

if beta:
    json_filename = "out/states_beta.json"
else:
    json_filename = "out/states.json"

with open(json_filename, 'w', encoding='utf-8') as f:
    pyradox.json.dump_tree(states.replace_key_with_subkey('state', 'id'), f)
