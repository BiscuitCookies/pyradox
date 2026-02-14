import _initpath
import pyradox
import os
import copy
import math

import stellaris.weapon
from pyradox.filetype.table import WikiDialect

csv_data = pyradox.csv.parse_merge(['common',
                                   'component_templates'],
                                  game = 'Stellaris')

txt_data = pyradox.parse_merge(['common',
                                'component_templates'], game = 'Stellaris')

total_data = pyradox.Tree()

for weapon in txt_data.find_all('weapon_component_template'):
    if weapon['hidden']: continue
    key = weapon['key']
    weapon_csv = csv_data[key]
    if weapon_csv['hull_damage'] in (None, '', '0.'):
        weapon_csv['hull_damage'] = 0
    if weapon_csv['armor_damage'] in (None, '', '0.'):
        weapon_csv['armor_damage'] = 0
    if weapon_csv['shield_damage'] in (None, '', '0.'):
        weapon_csv['shield_damage'] = 0
    total_data[key] = weapon + weapon_csv

column_specs = [
    # ('Weapon/Role', stellaris.weapon.icon_and_name_and_role),
    ('Weapon', stellaris.weapon.icon_and_name),
    ('Size', stellaris.weapon.slot_string),
    # ('{{icon|minerals}}<br/>Cost', '%(cost)d'),
    ('{{icon|power}}<br/>Power', lambda k, v: str(abs(v.find('power', 0)) if v.find('power', 0) != '' else '')),
    # ('{{icon|damage}}<br/>Average<br/>damage', lambda k, v: '%0.1f' % stellaris.weapon.average_damage(v)),
    ('{{icon|damage}}<br/>Damage per hit<br/>(average)', stellaris.weapon.damage_string),
    ('{{icon|time}}<br/>Cooldown', '%(cooldown).2f'),
    ('{{icon|weapons range}}<br/>Range', stellaris.weapon.weapon_range),
    ('{{icon|ship accuracy}}<br/>Accuracy', lambda k, v: '%d%%' % (v.find('accuracy', 0) * 100.0)),
    ('{{icon|tracking}}<br/>Tracking', lambda k, v: '%d%%' % (v.find('tracking', 0) * 100.0)),
    # ('{{icon|damage}}/{{icon|time}}<br/>Normalized DPS', lambda k, v: '%0.2f' % stellaris.weapon.normalized_dps(v)),
    ('{{icon|damage}}/{{icon|time}}<br/>Average damage', lambda k, v: '%0.2f' % stellaris.weapon.unnormalized_dps(v)),
    ('Modifiers', stellaris.weapon.special_string),
    ]

missile_specs = [
    # ('Weapon/Role', stellaris.weapon.icon_and_name_and_role),
    ('Weapon', stellaris.weapon.icon_and_name),
    ('Size', stellaris.weapon.slot_string),
    # ('{{icon|minerals}}<br/>Cost', '%(cost)d'),
    ('{{icon|power}}<br/>Power', lambda k, v: str(abs(v.find('power', 0)) if v.find('power', 0) != '' else '')),
    # ('{{icon|damage}}<br/>Average<br/>damage', lambda k, v: '%0.1f' % stellaris.weapon.average_damage(v)),
    ('{{icon|damage}}<br/>Damage per hit<br/>(average)', stellaris.weapon.damage_string),
    ('{{icon|time}}<br/>Cooldown', '%(cooldown).2f'),
    ('{{icon|weapons range}}<br/>Range', stellaris.weapon.weapon_range),
    ('{{icon|ship accuracy}}<br/>Accuracy', lambda k, v: '%d%%' % (v['accuracy'] * 100.0)),
    ('{{icon|tracking}}<br/>Tracking', lambda k, v: '%d%%' % (v['tracking'] * 100.0)),
    ('{{icon|damage}}/{{icon|time}}<br/>Average damage', lambda k, v: '%0.2f' % stellaris.weapon.unnormalized_dps(v)),
    ('Modifiers', stellaris.weapon.special_string),
    ('{{icon|ship health}}<br/>Hull', '%(missile_health)d'),
    ('{{icon|evasion}}<br/>Evasion', lambda k, v: '%d%%' % (v['missile_evasion'] * 100.0)),
    ('{{icon|ship speed}}<br/>Speed', '%(missile_speed)d'),
    ('retargeting range', '%(missile_retarget_range)d'),
    ('Armor', '%(missile_armor).1f'),
    #('Shield', '%(missile_shield).1f'),
    ]

class dialect(WikiDialect):
    pass

# to allow custom styles
dialect.row_cell_begin = lambda s: ''

with open('out/weapons.wiki.txt', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_table(total_data, dialect, column_specs))

with open('out/weapons_split.wiki.txt', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_tables(
        total_data, dialect,
        column_specs = column_specs,
        filter_function = lambda k, v: not stellaris.weapon.is_missile(k, v) and not stellaris.weapon.is_mutation(k, v),
        split_function = stellaris.weapon.weapon_category,
        add_headers = True,
        sort_function = stellaris.weapon.sort_function,
        table_classes = ["wikitable sortable"])) 

with open('out/mutations_split.wiki.txt', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_tables(
        total_data, dialect,
        column_specs = [column for column in column_specs if 'Power' not in column[0]],
        filter_function = lambda k, v: stellaris.weapon.is_mutation(k, v) and not stellaris.weapon.is_missile(k, v),
        split_function = stellaris.weapon.weapon_category,
        add_headers = True,
        sort_function = stellaris.weapon.sort_function,
        table_classes = ["wikitable sortable"]))

with open('out/mutations_missiles.wiki.txt', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_table(
        total_data, dialect,
        column_specs = [column for column in missile_specs if 'Power' not in column[0]],
        filter_function = lambda k, v: stellaris.weapon.is_mutation(k, v) and stellaris.weapon.is_missile(k, v),
        sort_function = stellaris.weapon.sort_function,
        table_classes = ["wikitable sortable"]))

with open('out/missiles.wiki.txt', 'w') as outfile:
    outfile.write(pyradox.filetype.table.make_table(
        total_data, dialect,
        missile_specs,
        filter_function = lambda k, v: stellaris.weapon.is_missile(k, v) and not stellaris.weapon.is_mutation(k, v) ,
        sort_function = stellaris.weapon.sort_function,
        table_classes = ["wikitable sortable"]))   
