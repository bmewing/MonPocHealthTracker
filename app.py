import datetime
import json
import argparse

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from PIL import Image, ImageDraw, ImageFont


def det_state(name, health):
    try:
        if health <= monster_transitions[name]:
            return "hyper"
        else:
            return "alpha"
    except KeyError:
        return "alpha"


def gen_monster_img(monsters, player):
    i = len(monsters)
    width = 400
    mon_fnt = ImageFont.truetype('font/MAL_DE_OJO.ttf', 48)
    hlt_fnt = ImageFont.truetype('font/HEADLINER_2.ttf', 60)

    text_color = {
        'alpha': (9, 0, 171),
        'hyper': (163, 158, 0)
    }

    height1 = 84
    height2 = 137
    height3 = 190

    img1 = Image.new('RGBA', (width, height1), color=(255, 255, 255, 0))
    img2 = Image.new('RGBA', (width, height2), color=(255, 255, 255, 0))
    img3 = Image.new('RGBA', (width, height3), color=(255, 255, 255, 0))

    if i == 1:
        height = height1
        img1 = Image.new('RGB', (width, height), color=(166, 0, 22))
        d = ImageDraw.Draw(img1)
    elif i == 2:
        height = height2
        img2 = Image.new('RGB', (width, height), color=(166, 0, 22))
        d = ImageDraw.Draw(img2)
    elif i == 3:
        height = height3
        img3 = Image.new('RGB', (width, height), color=(166, 0, 22))
        d = ImageDraw.Draw(img3)
    else:
        return ''
    d.rectangle((10, 10, width-10, height-10), fill=(230, 209, 214), outline=(191, 124, 36))

    for lm in range(len(monsters)):
        monster_health = str(monsters[lm]['health'])
        shift = 0
        if monsters[lm]['bif'] >= 0 and monsters[lm]['state'] == 'hyper':
            monster_health = str(monsters[lm]['health']) + ' i ' + str(monsters[lm]['bif'])
            print(monster_health)
            shift = -60
        tc = text_color[monsters[lm]['state']]
        d.text((20, 20 + 53 * lm),
               '%s:' % monsters[lm]['name'],
               font=mon_fnt, fill=tc)
        d.text((357+shift, 20 + 50 * lm),
               monster_health,
               font=hlt_fnt, fill=(0, 0, 0))

    img1.save(args.output_dir+player+'_1.png')
    img2.save(args.output_dir+player+'_2.png')
    img3.save(args.output_dir+player+'_3.png')


def update_health(monster):
    if monster != '':
        relevant = [m for m in monster_data if m['name'] == monster]
        return relevant[0]['health']
    else:
        return 11


def set_bifurcation_visibility(monster):
    hidden = True
    if monster != '':
        relevant = [m for m in monster_data if m['name'] == monster]
        try:
            if relevant[0]['bifurcate']:
                hidden = False
        except KeyError:
            hidden = True
    return hidden


def update_bifurcation(monster):
    bif_health = -1
    if monster != '':
        relevant = [m for m in monster_data if m['name'] == monster]
        try:
            if relevant[0]['bifurcate']:
                bif_health = relevant[0]['transition']
        except KeyError:
            bif_health = -1
    return bif_health


def update_state(monster):
    if monster != '':
        return 'Hyper Transition Point: '+str(monster_transitions[monster])
    else:
        return ''


def gen_image(lp1name, lp1h, lp1b,
              lp2name, lp2h, lp2b,
              lp3name, lp3h, lp3b,
              player='left'
              ):
    lp = [{'name': lp1name, 'health': lp1h, 'state': det_state(lp1name, lp1h), 'bif': lp1b},
          {'name': lp2name, 'health': lp2h, 'state': det_state(lp2name, lp2h), 'bif': lp2b},
          {'name': lp3name, 'health': lp3h, 'state': det_state(lp3name, lp3h), 'bif': lp3b}]
    lp = [m for m in lp if m['name'] != '']
    gen_monster_img(lp, player)
    return datetime.datetime.now()


def gen_monster(player, i):
    name = 'Monster #%d:  ' % i
    id_gen = '%s-mon%d' % (player, i)
    output = html.Div([
        html.Label('%s Name   ' % name),
        html.Br(),
        dcc.Dropdown(
            options=monster_names,
            value='',
            id='%s-name' % id_gen
        ),
        html.Br(),
        html.Label('Health'),
        html.Br(),
        dcc.Input(value=11, type='number', min=0, max=11, id='%s-health' % id_gen),
        html.Br(),
        html.Div(id='%s-state' % id_gen),
        html.Div([html.Br(),
                  html.Label('Bifurcation Health'),
                  html.Br(),
                  dcc.Input(value=-1, type='number', min=-1, max=-1, id='%s-bifurcation' % id_gen)],
                 id='%s-bif-div' % id_gen,
                 hidden=True)
    ], style={'border': 'dotted 1px black',
              'padding': '10px'})
    return output


parser = argparse.ArgumentParser(description='Generate health tracking badges for '
                                             'Monsterpocalypse to be used in a Twitch stream')
parser.add_argument('-o', '--output', dest='output_dir', help='Output directory to store badges',
                    required=False, default='')
parser.add_argument('-m', '--monsters', dest='monster_file', help='JSON file with monster data',
                    required=False, default='monsters.json')

args = parser.parse_args()

with open(args.monster_file, 'r') as monster_names_file:
    monster_data = json.load(monster_names_file)
monster_names = [{'label': m['name'], 'value': m['name']} for m in monster_data]
monster_names.append({'label': 'None', 'value': ''})
monster_transitions = {m['name']: m['transition'] for m in monster_data}

app = dash.Dash(__name__)


app.layout = html.Div(children=[
    html.H1(children='Monsterpocalypse Streaming Stats Manager'),
    html.Table(
        [
            html.Tr([
                html.Th(["Left Player"]),
                html.Th(["Right Player"])
            ]),
            html.Tr([html.Td(gen_monster(p, 1), style={'width': '300px'}) for p in ['lp', 'rp']]),
            html.Tr([html.Td(gen_monster(p, 2)) for p in ['lp', 'rp']]),
            html.Tr([html.Td(gen_monster(p, 3)) for p in ['lp', 'rp']])
        ]
    ),
    html.Br(),
    html.Br(),
    html.Div(id='dummy1', style={'color': 'white'}),
    html.Div(id='dummy2', style={'color': 'white'})
])


#######
# Right Player, First Monster
#######

@app.callback(
    Output('rp-mon1-health', 'max'),
    [Input('rp-mon1-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon1-health', 'value'),
    [Input('rp-mon1-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon1-state', 'children'),
    [Input('rp-mon1-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('rp-mon1-bifurcation', 'max'),
    [Input('rp-mon1-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('rp-mon1-bifurcation', 'value'),
    [Input('rp-mon1-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('rp-mon1-bif-div', 'hidden'),
    [Input('rp-mon1-name', 'value')]
)
def rp1state(*a, **kwargs):
    return set_bifurcation_visibility(*a, **kwargs)


#######
# Right Player, Second Monster
#######

@app.callback(
    Output('rp-mon2-health', 'max'),
    [Input('rp-mon2-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon2-health', 'value'),
    [Input('rp-mon2-name', 'value')]
)
def rp2health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon2-state', 'children'),
    [Input('rp-mon2-name', 'value')]
)
def rp2state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('rp-mon2-bifurcation', 'max'),
    [Input('rp-mon2-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('rp-mon2-bifurcation', 'value'),
    [Input('rp-mon2-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('rp-mon2-bif-div', 'hidden'),
    [Input('rp-mon2-name', 'value')]
)
def rp1state(*a, **kwargs):
    return set_bifurcation_visibility(*a, **kwargs)


#######
# Right Player, Third Monster
#######

@app.callback(
    Output('rp-mon3-health', 'max'),
    [Input('rp-mon3-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon3-health', 'value'),
    [Input('rp-mon3-name', 'value')]
)
def rp3health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon3-state', 'children'),
    [Input('rp-mon3-name', 'value')]
)
def rp3state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('rp-mon3-bifurcation', 'max'),
    [Input('rp-mon3-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('rp-mon3-bifurcation', 'value'),
    [Input('rp-mon3-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('rp-mon3-bif-div', 'hidden'),
    [Input('rp-mon3-name', 'value')]
)
def rp1state(*a, **kwargs):
    return set_bifurcation_visibility(*a, **kwargs)


#######
# Left Player, First Monster
#######

@app.callback(
    Output('lp-mon1-health', 'max'),
    [Input('lp-mon1-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon1-health', 'value'),
    [Input('lp-mon1-name', 'value')]
)
def lp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon1-state', 'children'),
    [Input('lp-mon1-name', 'value')]
)
def lp1state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('lp-mon1-bifurcation', 'max'),
    [Input('lp-mon1-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('lp-mon1-bifurcation', 'value'),
    [Input('lp-mon1-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('lp-mon1-bif-div', 'hidden'),
    [Input('lp-mon1-name', 'value')]
)
def rp1state(*a, **kwargs):
    return set_bifurcation_visibility(*a, **kwargs)


#######
# Left Player, Second Monster
#######

@app.callback(
    Output('lp-mon2-health', 'max'),
    [Input('lp-mon2-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon2-health', 'value'),
    [Input('lp-mon2-name', 'value')]
)
def lp2health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon2-state', 'children'),
    [Input('lp-mon2-name', 'value')]
)
def lp2state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('lp-mon2-bifurcation', 'max'),
    [Input('lp-mon2-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('lp-mon2-bifurcation', 'value'),
    [Input('lp-mon2-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('lp-mon2-bif-div', 'hidden'),
    [Input('lp-mon2-name', 'value')]
)
def rp1state(*a, **kwargs):
    return set_bifurcation_visibility(*a, **kwargs)


#######
# Left Player, Third Monster
#######

@app.callback(
    Output('lp-mon3-health', 'max'),
    [Input('lp-mon3-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon3-health', 'value'),
    [Input('lp-mon3-name', 'value')]
)
def lp3health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon3-state', 'children'),
    [Input('lp-mon3-name', 'value')]
)
def lp3state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('lp-mon3-bifurcation', 'max'),
    [Input('lp-mon3-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('lp-mon3-bifurcation', 'value'),
    [Input('lp-mon3-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_bifurcation(*a, **kwargs)


@app.callback(
    Output('lp-mon3-bif-div', 'hidden'),
    [Input('lp-mon3-name', 'value')]
)
def rp1state(*a, **kwargs):
    return set_bifurcation_visibility(*a, **kwargs)


#######
# Image Generation
#######

@app.callback(
    Output('dummy1', 'children'),
    [Input('lp-mon1-name', 'value'),
     Input('lp-mon1-health', 'value'),
     Input('lp-mon1-bifurcation', 'value'),
     Input('lp-mon2-name', 'value'),
     Input('lp-mon2-health', 'value'),
     Input('lp-mon2-bifurcation', 'value'),
     Input('lp-mon3-name', 'value'),
     Input('lp-mon3-health', 'value'),
     Input('lp-mon3-bifurcation', 'value')
     ]
)
def gen_left_image(*a, **kwargs):
    return gen_image(*a, **kwargs)


@app.callback(
    Output('dummy2', 'children'),
    [Input('rp-mon1-name', 'value'),
     Input('rp-mon1-health', 'value'),
     Input('rp-mon1-bifurcation', 'value'),
     Input('rp-mon2-name', 'value'),
     Input('rp-mon2-health', 'value'),
     Input('rp-mon2-bifurcation', 'value'),
     Input('rp-mon3-name', 'value'),
     Input('rp-mon3-health', 'value'),
     Input('rp-mon3-bifurcation', 'value')
     ]
)
def gen_right_image(*a, **kwargs):
    return gen_image(*a, **kwargs, player='right')


if __name__ == '__main__':
    app.run_server(debug=True)
