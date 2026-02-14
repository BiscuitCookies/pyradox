import pyradox

slot_sizes = {
    'small' : 1,
    'point_defence' : 1,
    'medium' : 2,
    'torpedo' : 2,
    'large' : 4,
    'hangar' : 4,
    'extra_large' : 8,
    'titanic' : 16, #?
    'planet_killer' : 1,
    'engulf': 0, # TODO: find correct size
    }

slot_icons = {
    'small' : 's',
    'point_defence' : 'pd',
    'medium' : 'm',
    'torpedo' : 'g',
    'large' : 'l',
    'hangar' : 'h',
    'extra_large' : 'xl',
    'titanic' : 't',
    'planet_killer' : 'wd',
    }

def min_damage(weapon):
    if 'damage' in weapon:
       return weapon['damage']['min']
    else:
        return weapon.find('min_damage', 0)

def max_damage(weapon):
    if 'damage' in weapon:
        return weapon['damage']['max']
    else:
        return weapon.find('max_damage', 0)

def average_damage(weapon):
    return 0.5 * (min_damage(weapon) + max_damage(weapon))

def damage_string(k, weapon):
    return f'{min_damage(weapon)}–{max_damage(weapon)} ({average_damage(weapon)})'

def normalized_dps(weapon):
    if 'count' in weapon:
        count = weapon['count']
    else:
        count = 1
        
    dps_per_size = count * average_damage(weapon) / weapon.find('cooldown', 0) / slot_sizes[weapon.find('size', 0).lower()]
    
    effectiveness_numerator = (
        0.5 * weapon['hull_damage'] +
        0.25 * weapon['armor_damage'] * (1.0 - weapon['armor_penetration']) +
        0.25 * weapon['shield_damage'] * (1.0 - weapon['shield_penetration']))
    
    effectiveness_denominator = 0.5 + 0.25 * (1.0 - weapon['armor_penetration']) + 0.25 * (1.0 - weapon['shield_penetration'])
    
    accuracy_mult = weapon['accuracy']
    result = dps_per_size * accuracy_mult * effectiveness_numerator / effectiveness_denominator / effectiveness_denominator
    return result

def unnormalized_dps(weapon):
    return weapon.find('count', 1) * average_damage(weapon) / weapon.find('cooldown', 0) * weapon['accuracy']

def weapon_range(key, weapon):
    min_range = weapon.find('min_range', 0)
    max_range = weapon['range']

    return f'{round(min_range)}–{round(max_range)}'

def float_to_255(x):
    x = round(255.0 * x)
    return max(min(x, 255), 0)

def to_html_color(c):
    return '#%02x%02x%02x' % c

def special_color(key, ap, sp, hull_damage, armor_damage, shield_damage):
    if ap == 1.0 and sp == 1.0:
        r = 1.0
        g = 0.0
        b = 1.0
    else:
        hull = 1.0
        if hull_damage == 0:
            hull_damage = 1  # to prevent division by 0
        armor = armor_damage / hull_damage
        shield = shield_damage / hull_damage
        
        non_penetrating = [hull]
        if ap < 1.0:
            non_penetrating.append(armor)
        if sp < 1.0:
            non_penetrating.append(shield)

        m = max(non_penetrating)

        power = 2.0

        if ap < 1.0:
            r = 0.5 * (armor / m) ** power
        else:
            r = 1.0
        g = 0.5 * (hull / m) ** power
        if sp < 1.0:
            b = 0.5 * (shield / m) ** power
        else:
            b = 1.0

    c = (float_to_255(r), float_to_255(g), float_to_255(b))
    return to_html_color(c)

def special_description(key, weapon):
    hull = weapon['hull_damage']
    if hull is None or hull == '':
        hull = 0
    armor = weapon['armor_damage']
    if armor is None or armor == '':
        armor = 0
    shield = weapon['shield_damage']
    if shield is None or shield == '':
        shield = 0

    ap = weapon['armor_penetration']
    sp = weapon['shield_penetration']

    if ap == 1.0 and sp == 1.0:
        text = 'penetrating'
    elif ap == 1.0:
        text = 'armor-penetrating'
    elif sp == 1.0:
        text = 'shield-penetrating'
    elif hull > armor and hull > shield:
        text = 'anti-hull'
    elif armor > hull and armor > shield:
        text = 'anti-armor'
    elif shield > hull and shield > armor:
        text = 'anti-shield'
    else:
        return ''

    color = special_color(key, ap, sp, hull, armor, shield)

    result = ''
    result += '<p style="color:%s; font-weight:bold; text-align:right; margin:0;">%s</p>' % (color, text)
    return result
    
def special_string(key, weapon):
    #items = [special_description(key, weapon)]
    items = []

    if 'hull_damage' not in weapon:
        return ''
    if weapon['hull_damage'] != 1.0:
        items.append('%d%% hull damage' % (weapon['hull_damage'] * 100.0))

    if weapon['armor_damage'] != 1.0:
        items.append('%d%% armor damage' % (weapon['armor_damage'] * 100.0))

    if weapon['armor_penetration'] != 0.0:
        items.append('%d%% armor penetration' % (weapon['armor_penetration'] * 100.0))
    
    if weapon['shield_damage'] != 1.0:
        items.append('%d%% shield damage' % (weapon['shield_damage'] * 100.0))

    if weapon['shield_penetration'] != 0.0:
        items.append('%d%% shield penetration' % (weapon['shield_penetration'] * 100.0))
    
    result = '<br/>'.join(items)
    
    if len(items) > 2:
        percent = 200.0 / len(items)
        result = '<span style="font-size:%d%%;">%s</span>' % (percent, result)
    
    return result
    
def is_missile(key, weapon):
    if 'missile_health' not in weapon or not isinstance(weapon['missile_health'], (int, float)):
        return False
    return weapon['missile_health'] > 0.0

def is_mutation(key, weapon):
    return 'icon' in weapon and 'mutation' in weapon['icon']

def slot_string(key, weapon):
    return 'style="text-align: center;" | {{icon|slot %s}}' % slot_icons[weapon['size'].lower()]

def icon_and_name(k, v):
    name = pyradox.get_localisation(k, game = 'Stellaris')
    if 'icon' in v:
        icon = v['icon'].removeprefix('GFX_')
    elif 'prerequisites' in v:
        icon = v['prerequisites'].replace('_', ' ')
    else:
        icon = None

    if icon:
        icon_tag = '[[File:%s.png|26px]]' % icon
    else:
        icon_tag = ''

    return 'style="text-align: left;" | %s %s' % (icon_tag, name)
    
def icon_and_name_and_role(k, v):
    line_0 = icon_and_name(k, v)
    line_1 = special_description(k, v)
    
    if line_1 == '': return line_0
    else:
        return '%s<br/>%s' % (line_0, line_1)
    
def weapon_category(key, weapon):
    if weapon['type'] == 'instant':
        if weapon['tags']:
            return ', '.join(tag for tag in weapon.find_all('tags') if not tag.endswith('_slot'))
        else:
            return 'none'
    else: return weapon['type'] or 'none'
    
def sort_function(key, weapon):
    component_set = weapon['prerequisites'] or key
    return component_set, slot_sizes[weapon['size'].lower()]
