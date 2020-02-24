import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from PIL import Image, ImageDraw, ImageFont

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)


def gen_monster(player, i):
    name = 'Monster #%d' % i
    id_gen = '%s-mon%d' % (player, i)
    output = html.Div([
        html.Label('%s Name' % name),
        dcc.Input(value='', type='text', id='%s-name' % id_gen),
        html.Label('%s Health' % name),
        dcc.Input(value=11, type='number', id='%s-health' % id_gen),
        html.Label('%s State' % name),
        dcc.RadioItems(
            options=[
                {'label': 'Alpha', 'value': 'alpha'},
                {'label': 'Hyper', 'value': 'hyper'}
            ],
            value='alpha',
            id='%s-state' % id_gen
        )
    ], style={'border': 'dotted 1px black'})
    return output


app.layout = html.Div(children=[
    html.H1(children='Monsterpocalypse Streaming Stats Manager'),

    html.Div([
        html.Div([
            html.Label('Left Player Name'),
            dcc.Input(value='Mark', type='text', id='lp-name'),
            gen_monster('lp', 1),
            html.Br(),
            gen_monster('lp', 2),
            html.Br(),
            gen_monster('lp', 3)
        ], style={'width': '300px'}),

        html.Br(),

        html.Div([
            html.Label('Right Player Name'),
            dcc.Input(value='Benjamin', type='text'),
            gen_monster('rp', 1),
            html.Br(),
            gen_monster('rp', 2),
            html.Br(),
            gen_monster('rp', 3)
        ], style={'width': '300px'})
    ], style={'columnCount': 2}),

    html.Div(id='dummy')
])

# one image for the left player
# one image for the right player
# write out transparent image of fixed size for 1/2/3 monster game
# write out real image for whatever size game is being played
# that way, images are always positioned correctly


@app.callback(
    Output('dummy', 'children'),
    [Input('lp-mon1-name', 'value'),
     Input('lp-mon1-health', 'value'),
     Input('lp-mon1-state', 'value'),
     Input('lp-mon2-name', 'value'),
     Input('lp-mon2-health', 'value'),
     Input('lp-mon2-state', 'value'),
     Input('lp-mon3-name', 'value'),
     Input('lp-mon3-health', 'value'),
     Input('lp-mon3-state', 'value'),
     Input('rp-mon1-name', 'value'),
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
def gen_image(lp1name, lp1health, lp1state,
              lp2name, lp2health, lp2state,
              lp3name, lp3health, lp3state,
              rp1name, rp1health, rp1state,
              rp2name, rp2health, rp2state,
              rp3name, rp3health, rp3state
              ):
    lp = [{'name': lp1name, 'health': lp1health, 'state': lp1state},
          {'name': lp2name, 'health': lp2health, 'state': lp2state},
          {'name': lp3name, 'health': lp3health, 'state': lp3state}]
    rp = [{'name': rp1name, 'health': rp1health, 'state': rp1state},
          {'name': rp2name, 'health': rp2health, 'state': rp2state},
          {'name': rp3name, 'health': rp3health, 'state': rp3state}]
    lp = [m for m in lp if m['name'] != '']
    rp = [m for m in rp if m['name'] != '']
    if len(lp) == len(rp):
        img = Image.new('RGBA', (800, 200), color=(255, 255, 255, 0))
        fnt = ImageFont.truetype('C://Windows//Fonts//BAUHS93.ttf', 24)
        d = ImageDraw.Draw(img)
        for lm in range(len(lp)):
            d.text((10, 50 + 100*lm),
                   '%s: %d' % (lp[lm]['name'], lp[lm]['health']),
                   font=fnt, fill=(0, 0, 0))
        for rm in range(len(rp)):
            d.text((410, 50 + 100*rm),
                   '%s: %d' % (rp[rm]['name'], rp[rm]['health']),
                   font=fnt, fill=(0, 0, 0))
        img.save('trial.png')
    return datetime.datetime.now()


if __name__ == '__main__':
    app.run_server(debug=True)
