import os
import json
import base64
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from flask import send_from_directory

CHARACTER_DIR = "characters"
IMAGE_DIR = os.path.join(CHARACTER_DIR, 'images')
os.makedirs(CHARACTER_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

@app.server.route('/characters/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

attributes = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
skills = [
    "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History",
    "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception",
    "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival"
]
skill_to_attr = {
    "Acrobatics": "Dexterity", "Animal Handling": "Wisdom", "Arcana": "Intelligence",
    "Athletics": "Strength", "Deception": "Charisma", "History": "Intelligence",
    "Insight": "Wisdom", "Intimidation": "Charisma", "Investigation": "Intelligence",
    "Medicine": "Wisdom", "Nature": "Intelligence", "Perception": "Wisdom",
    "Performance": "Charisma", "Persuasion": "Charisma", "Religion": "Intelligence",
    "Sleight of Hand": "Dexterity", "Stealth": "Dexterity", "Survival": "Wisdom"
}

# Helper to get character list
def get_character_list():
    return [f.replace(".json", "") for f in os.listdir(CHARACTER_DIR) if f.endswith(".json")]

# Helper to load character data
def load_character(name):
    path = os.path.join(CHARACTER_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

# Create ability input with modifier display
def ability_input(attribute):
    attr_lower = attribute.lower()
    return dbc.Row(
        [
            dbc.Col(html.Label(attribute), width=4),
            dbc.Col(
                dbc.Input(id=f"{attr_lower}-score", type="number", min=1, max=30, step=1, value=10),
                width=4,
            ),
            dbc.Col(
                html.Div("0", id=f"{attr_lower}-mod", style={"textAlign": "center"}),
                width=4,
            ),
        ],
        className="mb-2",
    )

# Common textarea style with rounded corners
textarea_style = {
    "width": "100%",
    "white-space": "pre-wrap",
    "border-radius": "8px",
    "padding": "8px",
    "border": "1px solid #ccc",
    "flex": "1 1 auto",
    "min-height": "100px"
}

# Define main columns
ability_column = dbc.Col(
    html.Div([
        html.H5("Ability Scores"), 
        *[ability_input(attr) for attr in attributes],
        html.Div([
            html.H5("Equipment"),
            dcc.Textarea(
                id="equipment", 
                placeholder="List items here...", 
                style={**textarea_style},
                value=""
            ),
            html.H6("Currency", className="mt-2"),
            dbc.Row([
                dbc.Col(html.Label("CP"), width=3),
                dbc.Col(dbc.Input(id="cp", type="number", value=0), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(html.Label("SP"), width=3),
                dbc.Col(dbc.Input(id="sp", type="number", value=0), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(html.Label("EP"), width=3),
                dbc.Col(dbc.Input(id="ep", type="number", value=0), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(html.Label("GP"), width=3),
                dbc.Col(dbc.Input(id="gp", type="number", value=0), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(html.Label("PP"), width=3),
                dbc.Col(dbc.Input(id="pp", type="number", value=0), width=9)
            ], className="mb-2"),
        ], style={"display": "flex", "flexDirection": "column", "flex": "1"}),
    ], style={"height": "100%", "display": "flex", "flexDirection": "column"}),
    md=4,
)

middle_column = dbc.Col(
    [
        html.H5("Inspiration"), dbc.Checkbox(id="inspiration", value=False),
        html.H5("Proficiency Bonus"), dbc.Input(id="proficiency-bonus", type="number", value=2),
        html.H5("Saving Throws"),
        *[dbc.Row([
            dbc.Col(dbc.Checkbox(id=f"saving-{attr.lower()}-prof", value=False), width=1),
            dbc.Col(html.Label(attr), width=5),
            dbc.Col(
                html.Div(
                    id=f"saving-{attr.lower()}-mod",
                    style={"textAlign": "right", "fontSize": "1.1em", "fontWeight": "bold"}
                ),
                width=6
            )
        ], className="mb-1") for attr in attributes],
        html.H5("Skills"),
        *[dbc.Row([
            dbc.Col(dbc.Checkbox(id=f"skill-{skill.lower().replace(' ', '-')}-prof", value=False), width=1),
            dbc.Col(html.Label(f"{skill} ({skill_to_attr[skill][:3]})"), width=5),
            dbc.Col(
                html.Div(
                    id=f"skill-{skill.lower().replace(' ', '-')}-mod",
                    style={"textAlign": "right", "fontSize": "1.1em", "fontWeight": "bold"}
                ),
                width=6
            )
        ], className="mb-1") for skill in skills],
        html.H5("Passive Perception"), html.Div(id="passive-perception"),
    ],
    md=4,
)

combat_column = dbc.Col(
    html.Div([
        html.H5("Combat Stats"),
        dbc.Row([dbc.Col(html.Label("Armor Class"), width=5), dbc.Col(dbc.Input(id="armor-class", type="number", value=10), width=7)], className="mb-2"),
        dbc.Row([dbc.Col(html.Label("Initiative"), width=5), dbc.Col(html.Div(id="initiative"), width=7)], className="mb-2"),
        dbc.Row([dbc.Col(html.Label("Speed"), width=5), dbc.Col(dbc.Input(id="speed", type="number", value=30), width=7)], className="mb-2"),
        html.H5("Hit Points"),
        dbc.Row([dbc.Col(html.Label("Max HP"), width=5), dbc.Col(dbc.Input(id="hp-max", type="number", value=10), width=7)], className="mb-2"),
        dbc.Row([dbc.Col(html.Label("Current HP"), width=5), dbc.Col(dbc.Input(id="hp-current", type="number", value=10), width=7)], className="mb-2"),
        dbc.Row([dbc.Col(html.Label("Temp HP"), width=5), dbc.Col(dbc.Input(id="hp-temp", type="number", value=0), width=7)], className="mb-2"),
        html.H5("Hit Dice"),
        dbc.Row([dbc.Col(html.Label("Total"), width=5), dbc.Col(dbc.Input(id="hit-dice-total", type="text", value="1d8"), width=7)], className="mb-2"),
        dbc.Row([dbc.Col(html.Label("Current"), width=5), dbc.Col(dbc.Input(id="hit-dice-current", type="text", value="1d8"), width=7)], className="mb-2"),
        html.H5("Death Saves"),
        dbc.Row([
            dbc.Col(html.Label("Successes"), width=5),
            dbc.Col(
                html.Div([dbc.Checkbox(id=f"death-success-{i}", value=False, style={"marginRight": "10px"}) for i in range(3)], 
                style={"display": "flex", "flexDirection": "row"}),
                width=7
            )
        ], className="mb-2"),
        dbc.Row([
            dbc.Col(html.Label("Failures"), width=5),
            dbc.Col(
                html.Div([dbc.Checkbox(id=f"death-failure-{i}", value=False, style={"marginRight": "10px"}) for i in range(3)],
                style={"display": "flex", "flexDirection": "row"}),
                width=7
            )
        ], className="mb-2"),
        html.Div([
            html.H5("Attacks & Spellcasting"), 
            dcc.Textarea(
                id="attacks", 
                placeholder="Name | Bonus | Damage/Type", 
                style={**textarea_style},
                value=""
            ),
        ], style={"display": "flex", "flexDirection": "column", "flex": "1"}),
    ], style={"height": "100%", "display": "flex", "flexDirection": "column"}),
    md=4,
)

# Personality and features section
personality_row = dbc.Row(
    [
        dbc.Col([html.H5("Personality Traits"), 
                 dcc.Textarea(
                     id="personality-traits", 
                     style={**textarea_style, "height": "100px"},
                     value=""
                 )], md=3),
        dbc.Col([html.H5("Ideals"), 
                 dcc.Textarea(
                     id="ideals", 
                     style={**textarea_style, "height": "100px"},
                     value=""
                 )], md=3),
        dbc.Col([html.H5("Bonds"), 
                 dcc.Textarea(
                     id="bonds", 
                     style={**textarea_style, "height": "100px"},
                     value=""
                 )], md=3),
        dbc.Col([html.H5("Flaws"), 
                 dcc.Textarea(
                     id="flaws", 
                     style={**textarea_style, "height": "100px"},
                     value=""
                 )], md=3),
    ],
    className="mb-3",
)

features_traits = dbc.Row(
    [dbc.Col([html.H5("Features & Traits"), 
              dcc.Textarea(
                  id="features-traits", 
                  style={**textarea_style, "height": "200px"},
                  value=""
              )], md=12)],
    className="mb-3",
)

proficiencies_languages = dbc.Row(
    [dbc.Col([html.H5("Proficiencies & Languages"), 
              dcc.Textarea(
                  id="proficiencies-languages", 
                  style={**textarea_style, "height": "100px"},
                  value=""
              )], md=12)],
    className="mb-3",
)

# Main layout
app.layout = dbc.Container(
    [
        html.H1("D&D 5E Character Sheet", className="text-center mb-4"),
        dbc.Row(
            [
                # Left column with all character details
                dbc.Col([
                    # Character selection and controls
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(
                            id="character-select",
                            options=[{"label": c, "value": c} for c in get_character_list()],
                            placeholder="Select a character",
                            style={"color": "#000"}
                        ), md=4),
                        dbc.Col(dbc.Button("Create New", id="new-character", color="success"), md=2),
                        dbc.Col(dbc.Button("Save", id="save-character", color="primary"), md=2),
                        dbc.Col([
                            html.Div([
                                html.Div(
                                    id="health-bar-container",
                                    style={
                                        "width": "100%",
                                        "height": "38px",
                                        "backgroundColor": "#4a4a4a",
                                        "borderRadius": "8px",
                                        "overflow": "hidden",
                                        "position": "relative",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center"
                                    },
                                    children=[
                                        html.Div(
                                            id="health-bar",
                                            style={
                                                "width": "100%",
                                                "height": "100%",
                                                "backgroundColor": "#dc3545",
                                                "position": "absolute",
                                                "top": "0",
                                                "left": "0",
                                                "transition": "width 0.3s ease",
                                                "borderRadius": "8px",
                                            }
                                        ),
                                        html.Div(
                                            id="health-text",
                                            style={
                                                "color": "white",
                                                "zIndex": "1",
                                                "fontWeight": "bold",
                                                "position": "relative"
                                            }
                                        )
                                    ]
                                )
                            ], style={"position": "relative"})
                        ], md=4)
                    ], className="mb-3"),
                    
                    # Basic character info
                    dbc.Row([dbc.Col(dbc.Input(id="character-name", type="text", placeholder="Character Name"), md=12)], className="mb-3"),
                    dbc.Row([
                        dbc.Col([html.Label("Class & Level"), dbc.Input(id="class-level", type="text")], md=4),
                        dbc.Col([html.Label("Background"), dbc.Input(id="background", type="text")], md=4),
                        dbc.Col([html.Label("Player Name"), dbc.Input(id="player-name", type="text")], md=4)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([html.Label("Race"), dbc.Input(id="race", type="text")], md=4),
                        dbc.Col([html.Label("Alignment"), dbc.Input(id="alignment", type="text")], md=4),
                        dbc.Col([html.Label("Experience Points"), dbc.Input(id="xp", type="number", value=0)], md=4)
                    ], className="mb-3"),
                    
                    # Main character stats
                    dbc.Row(
                        [ability_column, middle_column, combat_column], 
                        className="mb-3",
                    ),
                    
                    # Character details
                    personality_row,
                    features_traits,
                    proficiencies_languages,
                    
                    # Status message
                    dbc.Alert(id="status-msg", is_open=False, duration=2000, className="mt-3"),
                    dcc.Store(id="image-path-store", data=None),
                ], md=9),
                
                # Right column with image and journal
                dbc.Col(
                    html.Div([
                        # Image upload section
                        html.Div([
                            dcc.Upload(
                                id="upload-image",
                                children=html.Div([
                                    html.Div([
                                        'Drag and Drop or ',
                                        html.A('Click to Upload', style={'textDecoration': 'underline', 'cursor': 'pointer'})
                                    ], id="upload-text", style={
                                        'width': '100%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '12px',
                                        'textAlign': 'center',
                                        'margin': '10px 0',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'overflow': 'hidden'
                                    }),
                                    html.Img(
                                        id="character-image",
                                        src="",
                                        style={
                                            "width": "100%",
                                            "height": "auto",
                                            "maxHeight": "300px",
                                            "marginBottom": "10px",
                                            "cursor": "pointer",
                                            "borderRadius": "12px",
                                            "overflow": "hidden"
                                        }
                                    ),
                                ]),
                                style={
                                    'width': '100%',
                                    'marginBottom': '20px'
                                },
                                multiple=False
                            ),
                        ], style={"flex": "0 0 auto"}),
                        
                        # Journal section
                        html.Div([
                            html.H5("Journal"),
                            dcc.Textarea(
                                id="character-journal", 
                                placeholder="Enter notes...", 
                                style={
                                    **textarea_style,
                                    "resize": "vertical",
                                    "height": "calc(100vh)",
                                },
                                value=""
                            ),
                        ], style={
                            "display": "flex", 
                            "flexDirection": "column", 
                            "flex": "1 1 auto",
                        }),
                    ], style={
                        "height": "calc(100vh - 120px)",
                        "display": "flex",
                        "flexDirection": "column",
                    }),
                    md=3,
                    style={"padding": "0 15px"}
                ),
            ],
            style={"minHeight": "calc(100vh - 120px)"}
        ),
    ],
    fluid=True,
    className="p-4",
)

# Callbacks

# Clear character select when creating new character
@app.callback(
    Output("character-select", "value"),
    Input("new-character", "n_clicks")
)
def clear_character_select(n_clicks):
    if n_clicks:
        return None
    return dash.no_update

# Update ability modifiers
@app.callback(
    [Output(f"{attr.lower()}-mod", "children") for attr in attributes],
    [Input(f"{attr.lower()}-score", "value") for attr in attributes]
)
def update_modifiers(*scores):
    return [(f"+{(score - 10) // 2}" if (score - 10) // 2 >= 0 else str((score - 10) // 2)) if score is not None else "0" for score in scores]

# Update saving throw modifiers
@app.callback(
    [Output(f"saving-{attr.lower()}-mod", "children") for attr in attributes],
    [Input(f"{attr.lower()}-score", "value") for attr in attributes] +
    [Input(f"saving-{attr.lower()}-prof", "value") for attr in attributes] +
    [Input("proficiency-bonus", "value")]
)
def update_saving_modifiers(*values):
    scores = values[:6]
    prof_checks = values[6:12]
    prof_bonus = values[12] if values[12] is not None else 0
    mods = [(score - 10) // 2 if score is not None else 0 for score in scores]
    saving_mods = [mod + (prof_bonus if prof_check else 0) for mod, prof_check in zip(mods, prof_checks)]
    return [(f"+{mod}" if mod >= 0 else str(mod)) for mod in saving_mods]

# Update skill modifiers
@app.callback(
    [Output(f"skill-{skill.lower().replace(' ', '-')}-mod", "children") for skill in skills],
    [Input(f"{attr.lower()}-score", "value") for attr in attributes] +
    [Input(f"skill-{skill.lower().replace(' ', '-')}-prof", "value") for skill in skills] +
    [Input("proficiency-bonus", "value")]
)
def update_skill_modifiers(*values):
    ability_scores = values[:6]
    prof_checks = values[6:6+len(skills)]
    prof_bonus = values[-1] if values[-1] is not None else 0
    ability_mods = {attr: (score - 10) // 2 if score is not None else 0 for attr, score in zip(attributes, ability_scores)}
    skill_mods = [ability_mods[skill_to_attr[skill]] + (prof_bonus if prof_check else 0) for skill, prof_check in zip(skills, prof_checks)]
    return [(f"+{mod}" if mod >= 0 else str(mod)) for mod in skill_mods]

# Update passive perception
@app.callback(
    Output("passive-perception", "children"),
    Input("skill-perception-mod", "children")
)
def update_passive_perception(perception_mod):
    return str(10 + int(perception_mod)) if perception_mod else "10"

# Update initiative
@app.callback(
    Output("initiative", "children"),
    Input("dexterity-score", "value")
)
def update_initiative(dex_score):
    mod = (dex_score - 10) // 2 if dex_score is not None else 0
    return str(mod)

# Modify the toggle_upload_visibility callback
@app.callback(
    [Output("upload-text", "style"),
     Output("character-image", "style"),
     Output("character-image", "src")],
    [Input("upload-image", "contents"),
     Input("image-path-store", "data")]
)
def toggle_upload_visibility(contents, image_path):
    text_style = {
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '12px',
        'textAlign': 'center',
        'margin': '10px 0',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'overflow': 'hidden'
    }
    
    image_style = {
        "width": "100%",
        "height": "auto",
        "maxHeight": "300px",
        "marginBottom": "10px",
        "cursor": "pointer",
        "borderRadius": "12px",
        "overflow": "hidden"
    }
    
    if contents is not None:
        text_style["display"] = "none"
        image_style["display"] = "block"
        return text_style, image_style, contents
    elif image_path is not None:
        text_style["display"] = "none"
        image_style["display"] = "block"
        return text_style, image_style, image_path
    else:
        text_style["display"] = "flex"
        image_style["display"] = "none"
        return text_style, image_style, ""

# Load character data
@app.callback(
    [
        Output("character-name", "value"), Output("class-level", "value"), Output("background", "value"),
        Output("player-name", "value"), Output("race", "value"), Output("alignment", "value"),
        Output("xp", "value"), Output("armor-class", "value"), Output("speed", "value"),
        Output("hp-max", "value"), Output("hp-current", "value"), Output("hp-temp", "value"),
        Output("hit-dice-total", "value"), Output("hit-dice-current", "value"), Output("attacks", "value"),
        Output("cp", "value"), Output("sp", "value"), Output("ep", "value"), Output("gp", "value"),
        Output("pp", "value"), Output("equipment", "value"), Output("personality-traits", "value"),
        Output("ideals", "value"), Output("bonds", "value"), Output("flaws", "value"),
        Output("features-traits", "value"), Output("proficiencies-languages", "value"),
        Output("character-journal", "value"), Output("inspiration", "value"),
        Output("proficiency-bonus", "value"), Output("image-path-store", "data")
    ] +
    [Output(f"{attr.lower()}-score", "value") for attr in attributes] +
    [Output(f"saving-{attr.lower()}-prof", "value") for attr in attributes] +
    [Output(f"skill-{skill.lower().replace(' ', '-')}-prof", "value") for skill in skills] +
    [Output(f"death-success-{i}", "value") for i in range(3)] +
    [Output(f"death-failure-{i}", "value") for i in range(3)],
    [Input("character-select", "value")]
)
def load_character_data(name):
    if not name:
        return (
            [""] * 7 + [10, 30, 10, 10, 0, "1d8", "1d8", "", 0, 0, 0, 0, 0, "", "", "", "", "", "", "", "", False, 2, None] +
            [10] * 6 + [False] * (6 + len(skills) + 6)
        )
    char_data = load_character(name)
    image_path = char_data.get("image_path", None)
    return (
        [
            char_data.get("name", ""), char_data.get("class_level", ""), char_data.get("background", ""),
            char_data.get("player_name", ""), char_data.get("race", ""), char_data.get("alignment", ""),
            char_data.get("xp", 0), char_data.get("armor_class", 10), char_data.get("speed", 30),
            char_data.get("hp_max", 10), char_data.get("hp_current", 10), char_data.get("hp_temp", 0),
            char_data.get("hit_dice_total", "1d8"), char_data.get("hit_dice_current", "1d8"),
            char_data.get("attacks", ""), char_data.get("cp", 0), char_data.get("sp", 0), char_data.get("ep", 0),
            char_data.get("gp", 0), char_data.get("pp", 0), char_data.get("equipment", ""),
            char_data.get("personality_traits", ""), char_data.get("ideals", ""), char_data.get("bonds", ""),
            char_data.get("flaws", ""), char_data.get("features_traits", ""),
            char_data.get("proficiencies_languages", ""), char_data.get("journal", ""),
            char_data.get("inspiration", False), char_data.get("proficiency_bonus", 2), image_path
        ] +
        [char_data.get(f"{attr.lower()}_score", 10) for attr in attributes] +
        [char_data.get(f"saving_{attr.lower()}_prof", False) for attr in attributes] +
        [char_data.get(f"skill_{skill.lower().replace(' ', '_')}_prof", False) for skill in skills] +
        [char_data.get(f"death_success_{i}", False) for i in range(3)] +
        [char_data.get(f"death_failure_{i}", False) for i in range(3)]
    )

# Save character data
@app.callback(
    [Output("status-msg", "children"), Output("status-msg", "is_open")],
    [Input("save-character", "n_clicks")],
    [
        State("character-name", "value"), State("class-level", "value"), State("background", "value"),
        State("player-name", "value"), State("race", "value"), State("alignment", "value"),
        State("xp", "value"), State("armor-class", "value"), State("speed", "value"),
        State("hp-max", "value"), State("hp-current", "value"), State("hp-temp", "value"),
        State("hit-dice-total", "value"), State("hit-dice-current", "value"), State("attacks", "value"),
        State("cp", "value"), State("sp", "value"), State("ep", "value"), State("gp", "value"),
        State("pp", "value"), State("equipment", "value"), State("personality-traits", "value"),
        State("ideals", "value"), State("bonds", "value"), State("flaws", "value"),
        State("features-traits", "value"), State("proficiencies-languages", "value"),
        State("character-journal", "value"), State("inspiration", "value"),
        State("proficiency-bonus", "value"), State("upload-image", "contents"),
        State("image-path-store", "data")
    ] +
    [State(f"{attr.lower()}-score", "value") for attr in attributes] +
    [State(f"saving-{attr.lower()}-prof", "value") for attr in attributes] +
    [State(f"skill-{skill.lower().replace(' ', '-')}-prof", "value") for skill in skills] +
    [State(f"death-success-{i}", "value") for i in range(3)] +
    [State(f"death-failure-{i}", "value") for i in range(3)]
)
def save_character(n_clicks, name, class_level, background, player_name, race, alignment, xp,
                   armor_class, speed, hp_max, hp_current, hp_temp, hit_dice_total, hit_dice_current,
                   attacks, cp, sp, ep, gp, pp, equipment, personality_traits, ideals, bonds, flaws,
                   features_traits, proficiencies_languages, journal, inspiration, proficiency_bonus,
                   contents, image_path_store, *states):
    if not n_clicks or not name:
        return "", False
    ability_scores = states[:6]
    saving_profs = states[6:12]
    skill_profs = states[12:12+len(skills)]
    death_successes = states[12+len(skills):15+len(skills)]
    death_failures = states[15+len(skills):18+len(skills)]
    char_data = {
        "name": name, "class_level": class_level, "background": background, "player_name": player_name,
        "race": race, "alignment": alignment, "xp": xp, "armor_class": armor_class, "speed": speed,
        "hp_max": hp_max, "hp_current": hp_current, "hp_temp": hp_temp, "hit_dice_total": hit_dice_total,
        "hit_dice_current": hit_dice_current, "attacks": attacks, "cp": cp, "sp": sp, "ep": ep,
        "gp": gp, "pp": pp, "equipment": equipment, "personality_traits": personality_traits,
        "ideals": ideals, "bonds": bonds, "flaws": flaws, "features_traits": features_traits,
        "proficiencies_languages": proficiencies_languages, "journal": journal,
        "inspiration": inspiration, "proficiency_bonus": proficiency_bonus,
    }
    for attr, score in zip(attributes, ability_scores):
        char_data[f"{attr.lower()}_score"] = score
    for attr, prof in zip(attributes, saving_profs):
        char_data[f"saving_{attr.lower()}_prof"] = prof
    for skill, prof in zip(skills, skill_profs):
        char_data[f"skill_{skill.lower().replace(' ', '_')}_prof"] = prof
    for i, success in enumerate(death_successes):
        char_data[f"death_success_{i}"] = success
    for i, failure in enumerate(death_failures):
        char_data[f"death_failure_{i}"] = failure
    if contents:
        content_type, content_string = contents.split(',')
        if 'image/' in content_type:
            ext = content_type.split('/')[-1].split(';')[0]
            filename = f"{name}.{ext}"
            filepath = os.path.join(IMAGE_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(content_string))
            char_data["image_path"] = f"/characters/images/{filename}"
    else:
        char_data["image_path"] = image_path_store
    with open(os.path.join(CHARACTER_DIR, f"{name}.json"), "w") as f:
        json.dump(char_data, f, indent=4)
    return f"Character '{name}' saved successfully!", True

# Add new callback for health bar
@app.callback(
    [
        Output("health-bar", "style"),
        Output("health-text", "children")
    ],
    [
        Input("hp-current", "value"),
        Input("hp-max", "value"),
        Input("hp-temp", "value")
    ]
)
def update_health_bar(current_hp, max_hp, temp_hp):
    if current_hp is None or max_hp is None or temp_hp is None:
        current_hp = 0
        max_hp = 1
        temp_hp = 0
    
    # Ensure we don't divide by zero
    if max_hp <= 0:
        max_hp = 1
    
    # Calculate health percentage
    health_percent = min(100, (current_hp / (max_hp + temp_hp)) * 100)
    
    # Determine color based on health percentage
    if health_percent <= 25:
        color = "#dc3545"  # Red
    elif health_percent <= 50:
        color = "#ffc107"  # Yellow
    else:
        color = "#28a745"  # Green
    
    # Update bar style
    bar_style = {
        "width": f"{health_percent}%",
        "height": "100%",
        "backgroundColor": color,
        "position": "absolute",
        "top": "0",
        "left": "0",
        "transition": "width 0.3s ease, background-color 0.3s ease",
        "borderRadius": "8px"
    }
    
    # Create health text
    health_text = f"{current_hp}/{max_hp + temp_hp}"
    
    return bar_style, health_text

# Run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8049)