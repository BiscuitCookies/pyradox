import pyradox


def name(k, v):
    return pyradox.get_localisation(k, game='Stellaris')

def icon_and_name(k, v):
    name_loc = pyradox.get_localisation(k, game='Stellaris')
    icon = v['icon'].removeprefix('GFX_specimen_')

    return '[[File:Specimen %s.png|50px]] %s' % (icon.lower(), name_loc)

def description(k, specimen):
    short = pyradox.get_localisation(k + '_desc_short', game='Stellaris')
    details = pyradox.get_localisation(k + '_desc_details', game='Stellaris')
    return f' {{{{desc small|{short}. {details}}}}}'

def rarity(k, specimen):
    formats = {'common': '{{tech|repeat|Common}}',
               'epic': '{{tech|rare|Epic}}',
               'exceptional': '{{yellow|Exceptional}}',
               'rare': '{{blue|Rare}}',
               }
    return formats[specimen['inline_script']['RARITY']]

def effects(k, specimen):
    result = [f'<pre>{section.prettyprint()}</pre>' for section in specimen.find_all('triggered_country_modifier')]
    if len(result) > 0:
        prefix = '{{green|AAA}}'
    else:
        prefix = ''
    for resource_section in specimen.find_all('resources'):
        for resource_key, production_value in resource_section['produces'].items():
            loc = pyradox.get_localisation(resource_key, game='Stellaris')
            result.append(f'{{{{icon|{loc.lower().removesuffix(" research")}}}}} {{{{green|+{production_value}}}}} {loc}')
    return prefix + '<br />\n'.join(result)
