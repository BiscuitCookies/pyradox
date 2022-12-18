import hoi4
import re
import os


import pyradox


economics = pyradox.txt.parse_file(
    os.path.join(pyradox.get_game_directory('HoI4'),
                 'common', 'ideas', '_economic.txt'))['ideas']

countries = hoi4.load.get_countries()

for tag, country in countries.items():
    if 'add_ideas' in country:
        for idea in country.find_all('add_ideas'):
            if idea in economics['economy']:
                country['economy'] = idea
            elif idea in economics['trade_laws']:
                country['trade_laws'] = idea
    country['economy'] = country['economy'] or 'civilian_economy'
    country['trade_laws'] = country['trade_laws'] or 'export_focus'

columns = [
    ('Country', '%(name)s'),
    ('Tag', '%(tag)s'),
    ('Economy', '%(economy)s'),
    ('Trade', '%(trade_laws)s'),
    ]

out = open("out/initial_laws.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.table.make_table(countries, 'wiki', columns,
                                     sort_function = lambda key, value: value['name'],
                                     table_style = None))
out.close()
