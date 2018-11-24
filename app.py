
#import dash components
import dash
import dash_html_components as html
import dash_core_components as dcc
import requests
import json
import dash_table_experiments as dt

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Define app layout
app.layout = html.Div([
    html.Div(dcc.Input(id='input-box', type='text')),
    html.Button('Analyze', id='button'),
    html.Div(id='output-container-button',
             children='Enter a sentence and press submit')
])

@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])
def update_output(n_clicks, value):
    #api endpoint
    url = "http://localhost:9000/feature_sentiment/?sentence={}".format(value)
    r = requests.get(url)
    aspect_terms = print(json.loads(r.text))

    return 'Aspect terms were extracted for the following sentence: value was "{}"'.format(
        aspect_terms)

if __name__ == '__main__':
    app.run_server(debug=True)

