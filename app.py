# Krijg text uit docx in Uploads en plak dat in een div

import dash
import dash_html_components as html
import dash_core_components as dcc
from flask import Flask
from dash.exceptions import PreventUpdate

import heapq
import numpy as np
from os import listdir

import os

from helper import get_docx_text, save_file, uploaded_files, file_download_link, remove_files, get_file_names, cosine_sim, generate_unique_path, remove_directory


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=external_stylesheets)

app.title = "CV vacature match"

app.layout = html.Div([
    html.H1(children="Vacature CV Match", style={"textAlign": "center"}),
    html.H2("Word (*.docx) Upload bak"),
    dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Sleep je Word bestanden hierin of klik hierop en selecteer."]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.H2("Jouw Word bestanden:"),
        html.Ul(id="file-list"),
        html.Div(id="text-1", style={'display': 'none'}), #, style={'display': 'none'}
        html.Div(id="text-2", style={'display': 'none'}), #, style={'display': 'none'}
        html.Div(id="upload_dir", style={'display': 'none'}),
    html.Button('Check!', id='button'),
    html.Div(id='output-container-button',
             children='Upload je vacature en je motivatie en druk op de knop.'),
    html.P(' '),
    html.H2("Wat doet deze site?"),
    html.P('In ieder geval slaan we je bestanden niet op. Eenmaal je CV en Vacature met elkaar laten matchen, worden ze meteen verwijderd. \
            Hierdoor hoef je je geen zorgen te maken om je privacy.'),
    html.P('Met jouw 2 bestanden gecombineerd met tekst analyse technieken die ook voor Machine Learning doeleinden worden gebruikt \
            kunnen we jou helpen met je CV. We berekenen de cosine similarity door alle woorden in je CV en in de vacature \
            te analyseren. We geven vervolgens de individuele woorden in beide bestanden een score. Deze score gebruiken we weer om de \
            overeenkomsten tussen je CV en de vacature te vinden.'),
    html.P('De cosine similarity is een getal tussen de 0 en de 1. Het is geen percentage aan overkomsten hoewel het misschien \
            wel zo lijkt. In feite is het de cosinus tussen alle woord-frequenties in beide bestanden. \
            Onze wereld is 3-D, de wereld van een computer kan multi-multi-multi-D zijn. Elk woord krijgt zijn eigen as. \
            Als alle assen dezelfde waarde zouden hebben, is de cosinus 1. Als de assen totaal ongelijk zouden zijn, \
            is de cosinus 0.'),
    html.P('Voordat we de tekst daadwerkelijk analyseren, halen we eerst de interpuncties uit de tekst. Dat \
            zou namelijk de cosinus te positief beinvloeden. Ook brengen we de woorden terug naar de stam (van stam + t) en \
            zetten we alle hoofdletters om in kleine letters. Zo weten we zeker dat we de juiste overeenkomsten kunnen vinden.'),
    html.P('Deze site is nog volop in ontwikkeling en er zullen snel nieuwe features woorden toegevoegd. \
            Denk aan een overzicht van de belangrijkste zinnen in de vacature zodat je jouw CV er beter op kunt aanpassen.')
      
    
    ], style={"padding-left":"25%", "padding-right":"25%"}, # "max-width": "500px", 'columnCount': 2, "textAlign": "Center",
)

def get_text(UPLOAD_DIRECTORY):
    '''Function to get text from uploaded files used in first callback'''
    text1 = '' # create two empty strings
    text2 = ''
    names = get_file_names(UPLOAD_DIRECTORY)
    if len(names) == 1:
        text1 = get_docx_text(names[0])
    if len(names) == 2:
        text1 = get_docx_text(names[0])
        text2 = get_docx_text(names[1])
    if len(names) > 2:
        text1 = "Teveel bestanden..."
    
    return(text1, text2)


def get_similarity(file1, file2):
    '''Function to get similarity used in second callback'''
    
    similarity = cosine_sim(file1, file2)
    if similarity < 0.1:
        advice = "Je CV en de vacature hebben weinig met elkaar te maken"
    if similarity > 0.1 and similarity < 0.25:
        advice = "De CV en de vacature hebben wel wat overeenkomsten"
    if similarity > 0.25 and similarity < 0.8:
        advice = "De CV en de vacature hebben veel met elkaar te maken"
    if similarity > 0.8:
        advice = "Je CV en de vacature zijn bijna of volledig identiek"
    return(similarity, advice)

# First callback
@app.callback([
    dash.dependencies.Output("file-list",  "children"),
    dash.dependencies.Output("text-1", "children"),
    dash.dependencies.Output("text-2", "children"),
    dash.dependencies.Output("upload_dir", "children")],
    [dash.dependencies.Input("upload-data", "filename"), dash.dependencies.Input("upload-data", "contents")]    
)

def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    UPLOAD_DIRECTORY = generate_unique_path()
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        #UPLOAD_DIRECTORY = generate_unique_path()
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data, UPLOAD_DIRECTORY)

    files = uploaded_files(UPLOAD_DIRECTORY)
    if len(files) == 0:
        val1 = [html.Li("Nog helemaal leeg...")]
    else:
        val1 = [html.Li(file_download_link(filename)) for filename in files]
    
    text1, text2 = get_text(UPLOAD_DIRECTORY)
        #print('de som van files = ', np.sum(names))
        #print(names)
        #print("===================================")
        
    return([val1, text1, text2, UPLOAD_DIRECTORY]) 


# Second callback

@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks'),
     dash.dependencies.Input('text-1', 'children'),
     dash.dependencies.Input('text-2', 'children'),
     dash.dependencies.Input('upload_dir', 'children')
    ],
    )
def update_output2(n_clicks, text1, text2, upload_dir):
    if n_clicks == None:
        raise PreventUpdate

    if n_clicks == 1:
        
        #names = get_file_names() # get the files
        similarity, advice = get_similarity(text1, text2) # check similarity

        #wf_vac = get_full_function(names[0], names[1])
        n_clicks = None # reset counter
    #path = get_upload_dir()
    print(upload_dir)
    remove_files(upload_dir) # remove files
    remove_directory(upload_dir)

    return('De cosinus similariteit is %.3f (1 is perfect, 0 is geen similariteit). ' % similarity, advice)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080)