# Monsterpocalypse Health Tracker

Since I started streaming Monsterpocalypse games I play with my son on Twitch, I've been trying to 
up the quality of the stream. One thing I noticed Privateer Press had was some health tracking info
visible on the stream. This is my attempt at replicating that behavior.

## Usage

Simplest usage is to install the requirements and then run the app.

```bash
pip install -r requirements
python app.py
```

There are two flags that can be set when launching the app. First, you can set the output directory.
If this is not set, it defaults to the current location, `-o` or `--output` allows you to modify 
that behavior.

```bash
python app.py -o /u/9yomonpoc/images/
```

Additionally, you can specify a different location for the JSON file with the monster data. Note
the app assumes a specific format for this data, but if you choose to keep that data in a different
location, you can specify it with `-m` or `--monsters`. Probably won't ever be needed.

```bash
python app.py -m /u/9yomonpoc/raw_monsters.json
```

## What does it do?

When you run the app a Plot.ly Dash dashboard will start running at http://127.0.0.1:8050/. 
from here you can set player names and pick what monsters you're playing with. Monster names are
selected from a dropdown and their maximum health and their Hyper transition point are loaded from
`monsters.json` (or another file if you specified it). Each time you make a change for the right 
or left player, the app will create 3 image files at the location specified (the current directory
if not specified with `-o`), `left_1.png`, `left_2.png`, `left_3.png` (replacing `left` with `right`
as relevant). These files respectively correspond to a 1, 2 or 3 monster game. If playing a 1 
monster game, then the 2 and 3 monster game images will be filled with transparency, for a 2 monster 
game the 1 and 3 files are filled with transparency, etc. This is to allow me to have all variants
loaded in OBS at all times with no conflicts.

On the computer managing the stream, you can then have this app open alongside OBS and use the native
numeric up/down arrows next to the health to track health status throughout the game. Once health
reaches the Hyper transition point, the text color for that monsters name will change from blue to
yellow as a visual cue for viewers. Health points are always shown in black.

## What does it not do?

* It doesn't do anything to validate input - you can increase health above maximum, change the 
hyper transition, etc.

* It doesn't help you play better

* It doesn't get you more followers 
