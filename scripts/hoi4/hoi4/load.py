import sys
import os
import pyradox
import re

def get_units(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    return pyradox.parse_merge('common/units', game = game, merge_levels = 1)['sub_units']

def get_technologies(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    return pyradox.parse_merge('common/technologies', game = game, merge_levels = 1)['technologies']

def get_equipments(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    return pyradox.parse_merge('common/units/equipment', game = game, merge_levels = 1)['equipments']

def get_ideologies(beta = False):
    return pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('HoI4')
                                , 'common', 'ideologies', '00_ideologies.txt'))['ideologies']
def get_ideas(beta = False):
    return pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'ideas'), merge_levels = 2)['ideas']

def get_characters(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    character = {}
    characters = {}
    characters_data = pyradox.parse_merge('common/characters', game = game, merge_levels = 1)['characters']
    for character_id in characters_data:
        character = characters_data[character_id]
        character['id'] = character_id
        character['name'] = characters_data['name'] or character_id
        subideology = []
        if 'country_leader' in character and 'ideology' in character['country_leader'] and character['country_leader']['ideology']:
            for countryleader in character.find_all('country_leader'):
                subideology.append(countryleader['ideology'])
        character['subideology'] = subideology
        characters[character_id] = character
    #print('TEST FOR {0}'.format(characters))
    return characters



def compute_country_tag_and_name(filename):
    m = re.match(r'.*([A-Z]{3})\s*-\s*(.*)\.txt$', filename)
    return m.group(1), m.group(2)

def get_countries(beta = False, date = '1007.1.1'):
    game = 'HoI4_beta' if beta else 'HoI4'
    charactersall = get_characters()
    ideologiesall = get_ideologies()
    ideologies = {}
    for ideo in ideologiesall:
        #print('TEST FOR {0} '.format(ideo))
        ideologies[ideo] = []
        for subideo in ideologiesall[ideo]['types']:
            ideologies[ideo].append(subideo)

    races = pyradox.txt.parse_file(
        os.path.join(pyradox.get_game_directory('HoI4'),
                 'common', 'ideas', '_race_pointers.txt'))['ideas']
    sciences = pyradox.txt.parse_file(
        os.path.join(pyradox.get_game_directory('HoI4'),
                 'common', 'ideas', '_city_research.txt'))['ideas']
    illiteracies = pyradox.txt.parse_file(
        os.path.join(pyradox.get_game_directory('HoI4'),
                 'common', 'ideas', '_lack_of_scientist_ideas.txt'))['ideas']
    poverties = pyradox.txt.parse_file(
        os.path.join(pyradox.get_game_directory('HoI4'),
                 'common', 'ideas', '_poverty_ideas.txt'))['ideas']
    societies = pyradox.txt.parse_file(
        os.path.join(pyradox.get_game_directory('HoI4'),
                 'common', 'ideas', '_society_development_ideas.txt'))['ideas']
    country_colors = {}
    country_color_file = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'countries', 'colors.txt'))
    countries = {}

    for filename, country in pyradox.txt.parse_dir(('history', 'countries'), game = game):
        country = country.at_time(date)
        tag, name = compute_country_tag_and_name(filename)
        country['tag'] = tag
        country['characters'] = country.find_all('recruit_character')

        if 'set_politics' in country and 'ruling_party' in country['set_politics'] and country['set_politics']['ruling_party']:
            ruling_party = country['set_politics']['ruling_party']
        else:
            ruling_party = 'neutrality'
        country['ruling_party'] = ruling_party
        done = False
        for recruit in country['characters']:
            for charsubid in charactersall[recruit]['subideology']:
                if charsubid in ideologies[ruling_party]:
                    country['ruling_subid'] = charsubid
                    country['ruling_subid_name'] = pyradox.yml.get_localisation(charsubid, game = game)
                    done = True
                    break
                if done: break
            if done: break

        if 'set_technology' in country:
            for tech in country['set_technology']:
                if tech in races['race_pointer']:
                    race = pyradox.yml.get_localisation(tech + '_type', game = game)
                    country['race'] = race
        if 'add_ideas' in country:
            for idea in country.find_all('add_ideas'):
                if idea in sciences['city_idea']:
                    country['science'] = idea
                elif idea in societies['society_development_idea']:
                    country['society'] =  idea
                elif idea in illiteracies['illiteracy_level_idea']:
                    country['illiteracy'] = idea
                elif idea in poverties['poverty_level_idea']:
                    country['poverty'] = idea

        country['race'] = country['race'] or 'unknown'
        country['science'] = country['science'] or 'proper_science_base'
        country['society'] = country['society'] or 'modern_society'
        country['illiteracy'] = country['illiteracy'] or 'no_lack_of_scientists'
        country['poverty'] = country['poverty'] or 'no_poverty'

        country['science'] = pyradox.yml.get_localisation(country['science'] , game = game)
        country['society'] = pyradox.yml.get_localisation(country['society'] , game = game)
        country['illiteracy'] = pyradox.yml.get_localisation(country['illiteracy'] , game = game)
        country['poverty'] = pyradox.yml.get_localisation(country['poverty'] , game = game)

        if tag in country_color_file:
            country_colors[tag] = country_color_file[tag].find('color').to_rgb()
        else:
            print('HACK FOR {0}'.format(tag))
            country_colors[tag] = (165, 102, 152)
        country_color = country_colors[tag]
        country['color'] = str(tuple(country_color)).replace('(','').replace(')','')

        localisation_key = '%s_%s' % (tag, ruling_party)
        country['name'] = pyradox.yml.get_localisation(localisation_key, game = game) or pyradox.yml.get_localisation(tag, game = game) or localisation_key
        countries[tag] = country

    return countries


def get_states(beta = False):
    game = 'HoI4_beta' if beta else 'HoI4'
    result = pyradox.parse_merge(['history', 'states'], game = 'HoI4')
    result.replaced_key_with_subkey('state', 'id')
    return result