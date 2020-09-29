import datetime
import json
import argparse
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from PIL import Image, ImageDraw, ImageFont


def det_state(health, transition):
    try:
        if health <= transition:
            return "hyper"
        else:
            return "alpha"
    except KeyError:
        return "alpha"


def gen_single_monster(mon=None, player='left', input_dir=None):
    if input_dir is None:
        input_dir = args.input_dir

    if mon is None:
        img = Image.new('RGBA', (320, 320), color=(255, 255, 255, 0))
    else:
        mon_fnt = ImageFont.truetype('font/thunder.ttf', 30)
        hlt_fnt = ImageFont.truetype('font/thunder.ttf', 48)

        img = Image.open('{dir}{player}_background.png'.format(dir=input_dir, player=player))
        name = mon['name']
        state = mon['state']
        monster_health = str(mon['health'])
        try:
            face = Image.open('{dir}profiles/{state}/{name}.png'.format(
                dir=input_dir,
                state=state,
                name=name
            ))
            if player == 'right':
                face = face.transpose(Image.FLIP_LEFT_RIGHT)
        except FileNotFoundError:
            face = Image.open('{dir}profiles/{state}/unknown.png'.format(
                dir=input_dir,
                state=state,
                name=name
            ))
        heart = Image.open('{dir}{state}_heart.png'.format(dir=input_dir, state=state))
        if player == 'right':
            heart_coord = (212, 217)
            heart2_coord = (15, 217)
        else:
            heart_coord = (15, 220)
            heart2_coord = (215, 220)
        img.paste(face, (10, 10), face)
        img.paste(heart, heart_coord, heart)
        d = ImageDraw.Draw(img)

        if mon['bif'] >= 0 and state == 'hyper':
            img.paste(heart, heart2_coord, heart)
            d.text((heart2_coord[0] + 32, heart2_coord[1] + 20),
                   str(mon['bif']),
                   font=hlt_fnt, fill=(0, 0, 0))

        d.text((15, 15),
               re.sub(r'[ \-]', '\n', name),
               font=mon_fnt, fill=(0, 0, 0))
        d.text((heart_coord[0] + 20, heart_coord[1]+10),
               monster_health,
               font=hlt_fnt, fill=(0, 0, 0))

    return img


def gen_monster_img(monsters, player):
    for lm in range(3):
        try:
            mon = monsters[lm]
        except IndexError:
            mon = None
        this_im = gen_single_monster(mon, player)
        this_im.save('{dir}{player}_{i}.png'.format(dir=args.output_dir, player=player, i=lm+1))


def update_health(monster):
    if monster != '':
        relevant = [m for m in monster_data if m['name'] == monster]
        return relevant[0]['health']
    else:
        return 11


def update_transition(monster):
    if monster != '':
        relevant = [m for m in monster_data if m['name'] == monster]
        return relevant[0]['transition']
    else:
        return 6


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


def gen_image(lp1name, lp1h, lp1t, lp1b,
              lp2name, lp2h, lp2t, lp2b,
              lp3name, lp3h, lp3t, lp3b,
              player='left'
              ):
    lp = [{'name': lp1name, 'health': lp1h, 'state': det_state(lp1h, lp1t), 'bif': lp1b},
          {'name': lp2name, 'health': lp2h, 'state': det_state(lp2h, lp2t), 'bif': lp2b},
          {'name': lp3name, 'health': lp3h, 'state': det_state(lp3h, lp3t), 'bif': lp3b}]
    lp = [m for m in lp if m['name'] != '']
    gen_monster_img(lp, player)
    return datetime.datetime.now()


def gen_monster_input(player, i):
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
        dcc.Input(value=11, type='number', min=0, id='%s-health' % id_gen),
        html.Div([html.Br(),
                  html.Label('Bifurcation Health'),
                  html.Br(),
                  dcc.Input(value=-1, type='number', min=-1, max=-1, id='%s-bifurcation' % id_gen)],
                 id='%s-bif-div' % id_gen,
                 hidden=True),
        html.Label('Transition'),
        html.Br(),
        dcc.Input(value=6, type='number', min=0, id='%s-transition' % id_gen),
    ], style={'border': 'dotted 1px black',
              'padding': '10px'})
    return output


parser = argparse.ArgumentParser(description='Generate health tracking badges for '
                                             'Monsterpocalypse to be used in a Twitch stream')
parser.add_argument('-o', '--output', dest='output_dir', help='Output directory to store badges',
                    required=False, default='output/')
parser.add_argument('-i', '--input', dest='input_dir', help='Input directory with monster images',
                    required=False, default='images/')
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
            html.Tr([html.Td(gen_monster_input(p, 1), style={'width': '300px'}) for p in ['lp', 'rp']]),
            html.Tr([html.Td(gen_monster_input(p, 2)) for p in ['lp', 'rp']]),
            html.Tr([html.Td(gen_monster_input(p, 3)) for p in ['lp', 'rp']])
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
    Output('rp-mon1-health', 'value'),
    [Input('rp-mon1-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon1-transition', 'value'),
    [Input('rp-mon1-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_transition(*a, **kwargs)


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
    Output('rp-mon2-health', 'value'),
    [Input('rp-mon2-name', 'value')]
)
def rp2health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon2-transition', 'value'),
    [Input('rp-mon2-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_transition(*a, **kwargs)


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
    Output('rp-mon3-health', 'value'),
    [Input('rp-mon3-name', 'value')]
)
def rp3health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon3-transition', 'value'),
    [Input('rp-mon3-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_transition(*a, **kwargs)


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
    Output('lp-mon1-health', 'value'),
    [Input('lp-mon1-name', 'value')]
)
def lp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon1-transition', 'value'),
    [Input('lp-mon1-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_transition(*a, **kwargs)


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
    Output('lp-mon2-health', 'value'),
    [Input('lp-mon2-name', 'value')]
)
def lp2health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon2-transition', 'value'),
    [Input('lp-mon2-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_transition(*a, **kwargs)


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
    Output('lp-mon3-health', 'value'),
    [Input('lp-mon3-name', 'value')]
)
def lp3health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon3-transition', 'value'),
    [Input('lp-mon3-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_transition(*a, **kwargs)


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
     Input('lp-mon1-transition', 'value'),
     Input('lp-mon1-bifurcation', 'value'),
     Input('lp-mon2-name', 'value'),
     Input('lp-mon2-health', 'value'),
     Input('lp-mon2-transition', 'value'),
     Input('lp-mon2-bifurcation', 'value'),
     Input('lp-mon3-name', 'value'),
     Input('lp-mon3-health', 'value'),
     Input('lp-mon3-transition', 'value'),
     Input('lp-mon3-bifurcation', 'value')
     ]
)
def gen_left_image(*a, **kwargs):
    return gen_image(*a, **kwargs)


@app.callback(
    Output('dummy2', 'children'),
    [Input('rp-mon1-name', 'value'),
     Input('rp-mon1-health', 'value'),
     Input('rp-mon1-transition', 'value'),
     Input('rp-mon1-bifurcation', 'value'),
     Input('rp-mon2-name', 'value'),
     Input('rp-mon2-health', 'value'),
     Input('rp-mon2-transition', 'value'),
     Input('rp-mon2-bifurcation', 'value'),
     Input('rp-mon3-name', 'value'),
     Input('rp-mon3-health', 'value'),
     Input('rp-mon3-transition', 'value'),
     Input('rp-mon3-bifurcation', 'value')
     ]
)
def gen_right_image(*a, **kwargs):
    return gen_image(*a, **kwargs, player='right')


if __name__ == '__main__':
    app.run_server(debug=True)
