import _initpath
import os



import pyradox


import ideaoptions
from pyradox.token import make_token_string


def value_string(bonus, value):
    if bonus not in ideaoptions.bonus_types: print(bonus)
    if ideaoptions.is_beneficial(bonus, value):
        color = "green"
    else:
        color = "red"
    if ideaoptions.is_percent_bonus(bonus):
        return '{{%s|%+0.1f%%}}' % (color, value * 100.0)
    elif isinstance(value, int):
        return '{{%s|%+d}}'% (color, value)
    elif isinstance(value, float):
        return '{{%s|%+0.2f}}'% (color, value)
    else:
        return '{{%s|%s}}' % (color, make_token_string(value))

localisation_sources = ['EU4', 'text', 'modifers']

default_max_level = 4

result = ''

result += '{|class = "wikitable sortable mw-collapsible mw-collapsed"\n'
result += '! rowspan = "2" | Index !! rowspan = "2" | Bonus !! rowspan = "2" | Per level !! rowspan = "2" | Category !! colspan = "%d" | Cost \n' % default_max_level
result += '|-\n'
for i in range(default_max_level):
    result += '! %d !' % (i + 1)
result = result[:-1]
result += '\n'

idea_index = 0
for file_name, file_data in sorted(pyradox.txt.parse_dir(os.path.join(pyradox.get_game_directory('EU4'), 'common', 'custom_ideas'))):
    for idea_set in file_data.values():
        # start category
        
        for idea, idea_data in idea_set.items():
            if idea == 'category':
                power_type = idea_data.lower()
                continue

            # compile idea stats

            max_level = default_max_level
            costs = [0, 5, 15, 30] # cost indexed by level (0-based)
            for key, value in idea_data.items():
                if key in ('default', 'chance', 'enabled'):
                    continue
                elif key == 'max_level':
                    max_level = value
                elif 'level_cost_' in key:
                    level = int(key[len('level_cost_'):]) - 1
                    while level + 1> len(costs):
                        costs.append(0)
                    costs[level] = value
                else:
                    localized_key = (
                        pyradox.yml.get_localisation('modifier_%s' % key, game = 'EU4')
                        or pyradox.yml.get_localisation('yearly_%s' % key, game = 'EU4')
                        or pyradox.yml.get_localisation(key, game = 'EU4')
                        )
                    if not localized_key:
                        localized_key = pyradox.format.human_title(key)
                        print("Missing title: " + key + ' => ' + localized_key)
                    bonus_value_string = value_string(key, value)

            # write to string
            result += '|-\n'
            result += '| %s || %s || %s || {{icon|%s}} ' % (idea_index, localized_key, bonus_value_string, power_type)
            for i in range(default_max_level):
                if i < max_level:
                    result += '|| %d ' % costs[i]
                else:
                    result += '|| '
            result += '\n'
            idea_index += 1

result += '|}\n'

print(result)

