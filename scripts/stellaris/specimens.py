
import _initpath

import pyradox
import os

import stellaris.specimen
from pyradox.filetype.table import WikiDialect

specimens_path = os.path.join(
    pyradox.get_game_directory('Stellaris'),
    'common',
    'specimens')


result_data = {}
for key, value in pyradox.txt.parse_merge(specimens_path, game ='Stellaris').items():
    value['name'] = stellaris.specimen.name(key, value)
    if value['type'] not in result_data:
        result_data[value['type']] = pyradox.Tree()
    result_data[value['type']][key] = value

column_specs = [
    ('Specimen', stellaris.specimen.icon_and_name),
    ('Rarity', stellaris.specimen.rarity),
    ('Effects', stellaris.specimen.effects),
    ('Found from', ''),
    ('width=50% | Description', stellaris.specimen.description),
    ]


class dialect(WikiDialect):
    pass

dialect.row_cell_begin = lambda s: ''

dialect.row_begin = lambda row: f'|- id="{row["name"]}"\n| '
dialect.row_delimiter = '\n'
dialect.row_cell_delimiter = '\n| '

result = ''
for category in ['aesthetic_wonder', 'historical_item', 'xeno_geology']:
    data = result_data[category]
    category_loc = {'aesthetic_wonder': 'Aesthetic Wonders', 'historical_item': 'Galactic History', 'xeno_geology': 'Xeno Geology'}[category]
    result += f'== {category_loc} ==\n'
    result += pyradox.filetype.table.make_table(data, dialect, column_specs, table_classes=['mildtable'], table_style='')
    result += '\n'
with open('out/specimens.wiki.txt', 'w') as outfile:
    outfile.write(result)

