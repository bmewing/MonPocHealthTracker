import datetime
import json
import argparse

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from PIL import Image, ImageDraw, ImageFont


def det_state(health, transition):
    if health <= transition:
        return "hyper"
    else:
        return "alpha"


def gen_monster_img(monsters, player):
    i = len(monsters)
    width = 400
    mon_fnt = ImageFont.truetype('font/MAL_DE_OJO.ttf', 48)
    hlt_fnt = ImageFont.truetype('font/HEADLINER.ttf', 60)

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
        tc = text_color[monsters[lm]['state']]
        d.text((20, 20 + 53 * lm),
               '%s:' % monsters[lm]['name'],
               font=mon_fnt, fill=tc)
        d.text((357, 20 + 50 * lm),
               str(monsters[lm]['health']),
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


def update_state(monster):
    if monster != '':
        relevant = [m for m in monster_data if m['name'] == monster]
        return relevant[0]['transition']
    else:
        return 6


def gen_image(lp1name, lp1h, lp1s,
              lp2name, lp2h, lp2s,
              lp3name, lp3h, lp3s,
              player='left'
              ):
    lp = [{'name': lp1name, 'health': lp1h, 'state': det_state(lp1h, lp1s)},
          {'name': lp2name, 'health': lp2h, 'state': det_state(lp2h, lp2s)},
          {'name': lp3name, 'health': lp3h, 'state': det_state(lp3h, lp3s)}]
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
        dcc.Input(value=11, type='number', id='%s-health' % id_gen),
        html.Br(),
        html.Label('Hyper Transition'),
        html.Br(),
        dcc.Input(value=6, type='number', id='%s-state' % id_gen),
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

app = dash.Dash(__name__)


app.layout = html.Div(children=[
    html.H1(children='Monsterpocalypse Streaming Stats Manager'),

    html.Div([
        html.Div([
            html.Label('Left Player Name: '),
            html.Br(),
            dcc.Input(value='Mark', type='text', id='lp-name'),
            html.P(),
            gen_monster('lp', 1),
            html.Br(),
            gen_monster('lp', 2),
            html.Br(),
            gen_monster('lp', 3)
        ], style={'width': '300px'}),

        html.Br(),

        html.Div([
            html.Label('Right Player Name: '),
            html.Br(),
            dcc.Input(value='Benjamin', type='text', id='rp-name'),
            html.P(),
            gen_monster('rp', 1),
            html.Br(),
            gen_monster('rp', 2),
            html.Br(),
            gen_monster('rp', 3)
        ], style={'width': '300px'})
    ], style={'columnCount': 2}),

    html.Div(id='dummy1'),
    html.Div(id='dummy2')
])


@app.callback(
    Output('rp-mon1-health', 'value'),
    [Input('rp-mon1-name', 'value')]
)
def rp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon1-state', 'value'),
    [Input('rp-mon1-name', 'value')]
)
def rp1state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('rp-mon2-health', 'value'),
    [Input('rp-mon2-name', 'value')]
)
def rp2health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon2-state', 'value'),
    [Input('rp-mon2-name', 'value')]
)
def rp2state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('rp-mon3-health', 'value'),
    [Input('rp-mon3-name', 'value')]
)
def rp3health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('rp-mon3-state', 'value'),
    [Input('rp-mon3-name', 'value')]
)
def rp3state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('lp-mon1-health', 'value'),
    [Input('lp-mon1-name', 'value')]
)
def lp1health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon1-state', 'value'),
    [Input('lp-mon1-name', 'value')]
)
def lp1state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('lp-mon2-health', 'value'),
    [Input('lp-mon2-name', 'value')]
)
def lp2health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon2-state', 'value'),
    [Input('lp-mon2-name', 'value')]
)
def lp2state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('lp-mon3-health', 'value'),
    [Input('lp-mon3-name', 'value')]
)
def lp3health(*a, **kwargs):
    return update_health(*a, **kwargs)


@app.callback(
    Output('lp-mon3-state', 'value'),
    [Input('lp-mon3-name', 'value')]
)
def lp3state(*a, **kwargs):
    return update_state(*a, **kwargs)


@app.callback(
    Output('dummy1', 'children'),
    [Input('lp-mon1-name', 'value'),
     Input('lp-mon1-health', 'value'),
     Input('lp-mon1-state', 'value'),
     Input('lp-mon2-name', 'value'),
     Input('lp-mon2-health', 'value'),
     Input('lp-mon2-state', 'value'),
     Input('lp-mon3-name', 'value'),
     Input('lp-mon3-health', 'value'),
     Input('lp-mon3-state', 'value')
     ]
)
def gen_left_image(*a, **kwargs):
    return gen_image(*a, **kwargs)


@app.callback(
    Output('dummy2', 'children'),
    [Input('rp-mon1-name', 'value'),
     Input('rp-mon1-health', 'value'),
     Input('rp-mon1-state', 'value'),
     Input('rp-mon2-name', 'value'),
     Input('rp-mon2-health', 'value'),
     Input('rp-mon2-state', 'value'),
     Input('rp-mon3-name', 'value'),
     Input('rp-mon3-health', 'value'),
     Input('rp-mon3-state', 'value')
     ]
)
def gen_right_image(*a, **kwargs):
    return gen_image(*a, **kwargs, player='right')


if __name__ == '__main__':
    app.run_server(debug=True)
