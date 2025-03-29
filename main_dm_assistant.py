import os
import random
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from ollama_interface import OllamaInterface

if os.path.exists("notes.txt"):
    with open("notes.txt", "r", encoding="utf-8") as f:
        initial_notes = f.read()
else:
    initial_notes = ""

SYSTEM_PROMPT = ("You are a Dungeon Master Assistant AI, dedicated solely to discussing and assisting with "
                 "Dungeons & Dragons (D&D). You will provide assistance and rule help, campaign ideas, character "
                 "development, world-building suggestions, encounter balancing, NPC creation, and rules clarifications "
                 "based on D&D mechanics. Your responses must always remain within the context of D&D and never stray "
                 "into unrelated topics. Focus on creativity, improvisation, and adherence to D&D lore and mechanics "
                 "when relevant. Dont mention D&D and the user already knows you are a D&D assistant. Responses must be "
                 "as straight forward as possible with all being under 200 words. Only respond with sentances, no dot "
                 "points, tables or other formatted elements. The context provided is important to the current workings "
                 "of the game followed by a /n and the previous user and assistant chat history.")

ollama_client = OllamaInterface("gemma3:1b", SYSTEM_PROMPT)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, 
                        'dark.css'])

GLOBAL_STYLE = {
    'backgroundColor': '#1a1a1a',
    'color': '#FFFFFF',
    'fontFamily': 'Arial, sans-serif',
    'fontSize': '16px',
    'padding': '10px'
}

ROUNDED_STYLE = {'borderRadius': '8px'}

app.layout = html.Div([
    dcc.Store(id="effects-store", data=[]),
    dcc.Store(id="chat-store", data=[]),
    dcc.Interval(id="notepad-interval", interval=30000, n_intervals=0),
    html.Div(
        style={'display': 'flex', 'height': '100vh', 'gap': '10px'},
        children=[
            html.Div(
                style={
                    'width': '65%', 
                    'padding': '20px', 
                    'backgroundColor': '#2c2c2c',
                    'borderRight': '1px solid #444',
                    **ROUNDED_STYLE,
                    'display': 'flex',
                    'flexDirection': 'column',
                    'height': '100%'
                },
                children=[
                    html.Div([
                        html.H2("D&D Companion", style={'color': '#FFFFFF', 'margin': '0', 'textAlign': 'center'}),
                        html.Div([
                            html.Span(id="dice-result", style={'marginRight': '10px', 'fontWeight': 'bold'}),
                            html.Button(
                                html.Img(
                                    src='/assets/roll.png',  
                                    style={'width': '100%', 'height': '100%', 'objectFit': 'contain'}
                                ),
                                id="roll-button",
                                n_clicks=0,
                                style={
                                    'backgroundColor': 'transparent',
                                    'border': 'none',
                                    'width': '5vw',
                                    'height': '5vw',
                                    'minWidth': '40px',
                                    'minHeight': '40px',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    **ROUNDED_STYLE
                                }
                            ),

                            dcc.Dropdown(
                                id='dice-type',
                                options=[
                                    {'label': 'd4', 'value': 'd4'},
                                    {'label': 'd6', 'value': 'd6'},
                                    {'label': 'd8', 'value': 'd8'},
                                    {'label': 'd10', 'value': 'd10'},
                                    {'label': 'd12', 'value': 'd12'},
                                    {'label': 'd20', 'value': 'd20'},
                                ],
                                value='d20',
                                clearable=False,
                                style={'width': '100px', 'marginLeft': '10px', 'color': 'black'}
                            ),
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginLeft': 'auto'})
                    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between'}),
                    html.H4("Active Effects", style={'color': '#FFFFFF'}),
                    html.Div(
                        id="effects-display",
                        style={
                            'border': '1px solid #444',
                            'padding': '10px',
                            'minHeight': '100px',
                            'backgroundColor': '#1a1a1a',
                            **ROUNDED_STYLE
                        }
                    ),
                    html.Br(),
                    html.Div([
                        dcc.Input(
                            id="effect-character", type="text",
                            placeholder="Character Name", 
                            style={
                                'width': '35%', 
                                'backgroundColor': '#333', 
                                'color': '#FFFFFF', 
                                'border': '1px solid #444',
                                **ROUNDED_STYLE
                            }
                        ),
                        dcc.Input(
                            id="effect-name", type="text",
                            placeholder="Effect Name", 
                            style={
                                'width': '30%', 
                                'marginLeft': '10px',
                                'backgroundColor': '#333', 
                                'color': '#FFFFFF', 
                                'border': '1px solid #444',
                                **ROUNDED_STYLE
                            }
                        ),
                        dcc.Input(
                            id="effect-duration", type="number",
                            placeholder="Turns", min=1,
                            style={
                                'width': '10%',  
                                'marginLeft': '10px', 
                                'backgroundColor': '#333', 
                                'color': '#FFFFFF', 
                                'border': '1px solid #444',
                                **ROUNDED_STYLE
                            }
                        ),
                        html.Button(
                            "Add Effect", id="add-effect", n_clicks=0,
                            style={
                                'marginLeft': '10px',
                                'width': '15%',  
                                'backgroundColor': '#0d6efd',
                                'color': '#FFFFFF', 
                                'border': 'none',
                                **ROUNDED_STYLE
                            }
                        ),
                        html.Button(
                            "Next Turn", id="next-turn", n_clicks=0,
                            style={
                                'marginLeft': '10px',
                                'width': '15%',  
                                'backgroundColor': '#28a745',
                                'color': '#FFFFFF', 
                                'border': 'none',
                                **ROUNDED_STYLE
                            }
                        )
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    html.Br(),
                    html.Div([
                        html.H4("Notepad", style={'color': '#FFFFFF'}),
                        dcc.Textarea(
                            id="notepad", 
                            placeholder="Write your notes here...", 
                            value=initial_notes,
                            style={
                                'width': '100%', 
                                'height': '100%',  
                                'backgroundColor': '#333', 
                                'color': '#fff', 
                                'border': '1px solid #444',
                                **ROUNDED_STYLE
                            }
                        )
                    ], style={'flex': '1', 'marginBottom': '40px'})
                ]
            ),
            html.Div(
                style={
                    'width': '35%', 
                    'padding': '20px',
                    'backgroundColor': '#2c2c2c',
                    'borderLeft': '1px solid #444',
                    'display': 'flex', 
                    'flexDirection': 'column',
                    **ROUNDED_STYLE
                },
                children=[
                    html.H4("D&D Assistant", style={'color': '#FFFFFF', 'textAlign': 'center'}),
                    html.Div(
                        id="chat-display",
                        style={
                            'flex': '1', 
                            'border': '1px solid #444',
                            'padding': '10px', 
                            'overflowY': 'scroll',
                            'marginBottom': '10px',
                            'backgroundColor': '#1a1a1a',
                            **ROUNDED_STYLE
                        }
                    ),
                    html.Div([
                        dcc.Input(
                            id="chat-input", type="text",
                            placeholder="Ask a D&D question...", 
                            style={
                                'width': '70%', 
                                'backgroundColor': '#333', 
                                'color': '#FFFFFF', 
                                'border': '1px solid #444',
                                **ROUNDED_STYLE
                            },
                            n_submit=0
                        ),
                        html.Button(
                            "Send", id="send-button", n_clicks=0,
                            style={
                                'width': '14%', 
                                'marginLeft': '2%',
                                'backgroundColor': '#0d6efd',
                                'color': '#FFFFFF', 
                                'border': 'none',
                                **ROUNDED_STYLE
                            }
                        ),
                        html.Button(
                            "Clear", id="clear-transcript-button", n_clicks=0,
                            style={
                                'width': '14%', 
                                'marginLeft': '2%', 
                                'backgroundColor': '#FFA500',
                                'color': '#FFFFFF', 
                                'border': 'none',
                                **ROUNDED_STYLE
                            }
                        )
                    ], style={'display': 'flex'})
                ]
            )
        ]
    )
], style=GLOBAL_STYLE)

@app.callback(
    Output("dice-result", "children"),
    Input("roll-button", "n_clicks"),
    State("dice-type", "value")
)
def roll_dice(n_clicks, dice_value):
    if not n_clicks:
        return ""
    sides = int(dice_value[1:])
    result = random.randint(1, sides)
    return f"{result}"

@app.callback(
    Output("effects-store", "data"),
    [Input("add-effect", "n_clicks"), Input("next-turn", "n_clicks")],
    [State("effect-character", "value"),
     State("effect-name", "value"),
     State("effect-duration", "value"),
     State("effects-store", "data")],
    prevent_initial_call=True
)
def update_effects(add_clicks, turn_clicks, character_name, effect_name, effect_duration, effects):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == "add-effect":
        if effect_name and effect_duration:
            effects.append({
                "character": character_name or "Unknown",
                "name": effect_name, 
                "turns": int(effect_duration)
            })
    elif triggered_id == "next-turn":
        updated_effects = []
        for effect in effects:
            new_turns = effect["turns"] - 1
            if new_turns > 0:
                updated_effects.append({
                    "character": effect.get("character", "Unknown"),
                    "name": effect["name"], 
                    "turns": new_turns
                })
        effects = updated_effects
    return effects

@app.callback(
    Output("effects-display", "children"),
    Input("effects-store", "data")
)
def update_effects_display(effects):
    if not effects:
        return "No active effects."
    return [
        html.Div(
            f"{effect.get('character', 'Unknown')}: {effect['name']} – {effect['turns']} turn(s) remaining", 
            style={'padding': '5px 0', 'borderBottom': '1px solid #444'}
        )
        for effect in effects
    ]

@app.callback(
    Output("chat-store", "data"),
    [Input("send-button", "n_clicks"),
     Input("chat-input", "n_submit"),
     Input("clear-transcript-button", "n_clicks")],
    [State("chat-input", "value"), State("chat-store", "data")],
    prevent_initial_call=True
)
def update_or_clear_chat(n_send, n_submit, n_clear_transcript, user_msg, chat_history):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "clear-transcript-button":
        handle_transcripts()
        return []
    
    if user_msg:
        chat_history.append({"sender": "DM", "message": user_msg})
        chat_history.append({"sender": "DM Assist", "message": "Thinking...", "is_loading": True})
        
        with open("notes.txt", "r", encoding="utf-8") as notes_file:
            notes_content = notes_file.read()
        
        with open("dm_assistant_transcripts.txt", "r", encoding="utf-8") as transcripts_file:
            transcripts_content = transcripts_file.read()
        
        context = notes_content + "\n" + transcripts_content
        
        response = ollama_client.send_input(user_msg, context=context)
        chat_history[-1] = {"sender": "DM Assist", "message": response}
        with open("dm_assistant_transcripts.txt", "a", encoding="utf-8") as f:
            f.write("User: " + user_msg + "\n")
            f.write("DM Assist: " + response + "\n")
    return chat_history

@app.callback(
    Output("chat-display", "children"),
    Input("chat-store", "data")
)
def update_chat_display(chat_history):
    if not chat_history:
        return "No messages yet."
    
    chat_elements = []
    for msg in chat_history:
        style = {'margin': '5px 0', 'borderBottom': '1px solid #444'}
        if msg.get("is_loading", False):
            message_content = html.Div([
                html.I(className="fas fa-spinner fa-spin", style={'marginRight': '10px', 'color': '#888'}),
                html.Span("Thinking...", style={'color': '#888', 'fontStyle': 'italic'})
            ])
            chat_elements.append(html.Div([
                html.Span(f"{msg['sender']}: ", style={'marginRight': '5px'}),
                message_content
            ], style=style))
        else:
            chat_elements.append(html.Div(f"{msg['sender']}: {msg['message']}", style=style))
    return chat_elements

@app.callback(
    Output("chat-input", "value"),
    [Input("send-button", "n_clicks"), Input("chat-input", "n_submit")],
    prevent_initial_call=True
)
def clear_input(n_clicks, n_submit):
    return ""

@app.callback(
    Output("notepad", "value"),
    Input("notepad-interval", "n_intervals"),
    State("notepad", "value"),
    prevent_initial_call=True
)
def autosave_notepad(n_intervals, note_text):
    if note_text is None:
        note_text = ""
    with open("notes.txt", "w", encoding="utf-8") as f:
        f.write(note_text)
    return note_text

def handle_transcripts():
    # Create the file if it doesn't exist
    if not os.path.exists("dm_assistant_transcripts.txt"):
        with open("dm_assistant_transcripts.txt", "w", encoding="utf-8") as f:
            f.write("")
    else:
        # Existing logic for handling transcripts
        with open("dm_assistant_transcripts.txt", "r", encoding="utf-8") as transcripts_file:
            transcripts_content = transcripts_file.read()
        with open("dm_assistant_transcripts.old", "a", encoding="utf-8") as old_transcripts_file:
            old_transcripts_file.write(transcripts_content)
    
        with open("dm_assistant_transcripts.txt", "w", encoding="utf-8") as transcripts_file:
            transcripts_file.write("")

if __name__ == '__main__':
    handle_transcripts()  # Call the new function
    app.run(host='0.0.0.0', port=8048)
