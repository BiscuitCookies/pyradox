import hoi4
import os
import re
import pyradox

ideologies = hoi4.load.get_ideologies()
countries = hoi4.load.get_countries()
demo = {}
comm = {}
fasc = {}
neut = {}
democratic = pyradox.Tree()
communism = pyradox.Tree()
fascism = pyradox.Tree()
neutrality = pyradox.Tree()
adherents = pyradox.Tree()
allide = pyradox.Tree()
old = ''

democratics = ideologies['democratic']
communisms = ideologies['communism']
fascisms = ideologies['fascism']
neutralitys = ideologies['neutrality']

def compute_country_tag_and_name(filename):
    m = re.match('.*([A-Z]{3})\.txt$', filename)
    return m.group(1)

for filename, characters in pyradox.txt.parse_dir(('common', 'characters'), game = 'HoI4'):
    tag = compute_country_tag_and_name(filename)
    #print('TEST FOR {0}'.format(characters))
    chars = characters['characters']
    for character in chars:
        character = chars[character]
        if 'country_leader' in character and 'ideology' in character['country_leader'] and character['country_leader']['ideology']:
            ideology = character['country_leader']['ideology']
            key = character['name'] or character
            name = pyradox.yml.get_localisation(key, game = 'HoI4')
            country = countries[tag]
            countryloc = country['name']
            if adherents[ideology]:
                old = adherents[ideology]
            adherent = '{{flag|%s|%s}}' % (countryloc, name)
            adherents[ideology] = old + '\n' + adherent

for type in democratics['types']:
    demo['name'] = pyradox.yml.get_localisation(type, game = 'HoI4') or type
    demo['desc'] = pyradox.yml.get_localisation(type +'_desc', game = 'HoI4')
    allide[type] = demo['name']
    demo['adherents'] = adherents[type]
    democratic[type] = demo
for type in communisms['types']:
    comm['name'] = pyradox.yml.get_localisation(type, game = 'HoI4') or type
    comm['desc'] = pyradox.yml.get_localisation(type +'_desc', game = 'HoI4')
    allide[type] = comm['name']
    comm['adherents'] = adherents[type]
    communism[type] = comm
for type in fascisms['types']:
    fasc['name'] = pyradox.yml.get_localisation(type, game = 'HoI4') or type
    fasc['desc'] = pyradox.yml.get_localisation(type +'_desc', game = 'HoI4')
    allide[type] = fasc['name']
    fasc['adherents'] = adherents[type]
    fascism[type] = fasc
for type in neutralitys['types']:
    neut['name'] = pyradox.yml.get_localisation(type, game = 'HoI4') or type
    neut['desc'] = pyradox.yml.get_localisation(type +'_desc', game = 'HoI4')
    allide[type] = neut['name']
    neut['adherents'] = adherents[type]
    neutrality[type] = neut



columns = (
    ('Subideology', '%(name)s'),
    ('Description', '%(desc)s'),
    ('Adherents', '%(adherents)s')
)

out = open("out/democratic.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.table.make_table(democratic, 'wiki', columns,
                                     sort_function = lambda key, value: value['name'],
                                     table_style = None))
out.close()
out = open("out/communism.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.table.make_table(communism, 'wiki', columns,
                                     sort_function = lambda key, value: value['name'],
                                     table_style = None))
out.close()
out = open("out/fascism.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.table.make_table(fascism, 'wiki', columns,
                                     sort_function = lambda key, value: value['name'],
                                     table_style = None))
out.close()
out = open("out/neutrality.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.table.make_table(neutrality, 'wiki', columns,
                                     sort_function = lambda key, value: value['name'],
                                     table_style = None))
out.close()
print(allide)
