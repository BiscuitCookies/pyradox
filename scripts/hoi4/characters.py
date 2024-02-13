import hoi4
import os
import re
import pyradox

characters = hoi4.load.get_characters()

for character in characters:
    character = characters[character]
    character['name_loc'] = pyradox.yml.get_localisation(character['name'], game = 'HoI4') or character['name']

columns = (
    ('id', '%(id)s'),
    ('name', '%(name_loc)s'),
    ('Adherents', '%(subideology)s')
)

out = open("out/characters.txt", "w", encoding = 'utf_8_sig')
out.write(pyradox.table.make_table(characters, 'wiki', columns))