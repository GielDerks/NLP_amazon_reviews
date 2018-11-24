import os
from pymongo import MongoClient
import dash
import dash_html_components as html
import dash_core_components as dcc
import requests
import json
import pandas as pd
import numpy as np
import dash_table_experiments as dt

print()

# Get  MONGO_URL from either environment variable - if not available set local host
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://127.0.0.1:27017/"

# Making a Connection with MongoClient
client = MongoClient(MONGO_URL)

# Setting a Database
db = client.amazon

# Setting a Collection
collection = db.amazonappv2

# Set external css stylesheets
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "https://codepen.io/gielderks/pen/odryNY.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

# Load Metadata
metadata = pd.read_csv("/Users/gielderks/PycharmProjects/NLP_V2/laptop_review_data/laptop_metadata.csv")

# Load Laptop Reviews
reviews = pd.read_csv("/Users/gielderks/PycharmProjects/NLP_V2/laptop_review_data/laptops_reviews.csv")

# Load list of aspects
aspects_list = pd.read_csv("aspect_data.csv")

# List of unique product ids
unique_ids = list(metadata['asin'])

print(unique_ids)
# Create key value input for dropdown list
unique_ids_dict = []
for x in unique_ids:
    dict2 = {}
    dict2["label"] = x
    dict2["value"] = x
    unique_ids_dict.append(dict2)

# Build start data DataTable
pdata = collection.find_one({"name" : 'B00005IA5C'})
print(pdata)

# Get metadata
metadata = db.metadata.find_one({"asin" : 'B00005IA5C'})
price = db.metadata.find_one({"asin" : 'B00005IA5C'})['price']
imUrl = db.metadata.find_one({"asin" : 'B00005IA5C'})['imUrl']

# Get reviewdata
# Number of reviews
n_reviews = db.laptop_reviews.find({"asin": "B000RGG5EC"}).count()

# Build DataFrame
product_data = pd.DataFrame({"price" : [price], "n_reviews" : [n_reviews]})

print(product_data)

# Initalize Dash app (Flask based)
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Define app layout
app.layout = html.Div([

    html.Br([]),

    html.Div([

        html.Div([

            html.Div([
                html.H5(['Product Selection and Navigation'], id='text1'),
            ], className='gs-header gs-table-header padded'),

            html.Br([]),
            html.Br([]),

            html.Div([
                html.Div([

                    html.H6(['Use the slider to filter on Number of Reviews:'], id='text3'),
                ], className='six columns'),

                html.Div(dcc.RangeSlider(id='slider_n_reviews',
                                         count=1,
                                         marks=dict(zip([str(x) for x in list(np.arange(0,1000,250))], [str(x) for x in list(np.arange(0,1000,250))])),
                                         min=5,
                                         max=1000,
                                         step=25,
                                         value=[0, 1000]), className="six columns"),
            ], className='row'),

            html.Br([]),
            html.Br([]),
            html.Div([

                html.Div([

                    html.H6(['Use the slider to filter on Price Range:'], id='text4'),

                ], className='six columns'),

                html.Div(dcc.RangeSlider(id='slider_price',
                                         count=1,
                                         min=-0,
                                         max=3500,
                                         marks=dict(zip([str(x) for x in list(np.arange(0,3500,750))], ['$' + str(x) for x in list(np.arange(0,3500,750))])),
                                         step=25,
                                         value=[0, 3500])
                         , className="six columns"),

           ], className='row', style={'paddingBottom' : 20}),

            html.Div([
                html.Div([
                    html.H5(['Select a product from the dropdown:'], id='text5'),
                        ], className='eight columns'),
                html.Div([
                    html.H6([""], id='dynamic_text1'),
                  ], className='four columns', style={'paddingTop' : 10, 'textAlign': 'left'}),
            ], className='row', style={'paddingBottom': 10}),

            html.Div([
                html.Div(dcc.Dropdown(id='products',
                                      options=unique_ids_dict,
                                      value='B00FNPD1VW'),
                         className='twelve columns'),
               ], className='row', style={'paddingBottom' : 20}),

            html.Div([

                html.Div([
                    html.H5(['Product Info'], id='text6'),
                ], className='six columns', style={'textAlign': 'center'}),

                html.Div([
                    html.H5(['Product Preview'], id='text7'),
                ], className='six columns', style={'textAlign': 'center'}),


            ], className='row', style={'paddingBottom': 10}),


            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=product_data.to_dict('records'),
                        id='DT_product',
                        sortable=True,
                        editable=False,
                        filterable=False,
                        columns=['Price', 'N_reviews']),
                ], className="six columns"),

                html.Div([
                    html.Img(src=imUrl,
                             id='image1')  # 529 × 234 = 2,26
                ], className="six columns"),
            ], className='row', style={'paddingBottom' : 20 }),


        ], className="six columns padded"),


        html.Div([

            html.Div([

                html.H5(['General Product Information:'], id='text2'),
                ], className='gs-header gs-table-header padded'),

                html.Div([
                    html.Div([
                        html.H6(['Press Button to Filter on laptop specific aspects:'], id='text10'),
                    ], className='six columns', style={'paddingTop': 20}),
                    html.Div([
                        html.Button('Filter', id='button'),
                    ], className='three columns', style={'paddingTop': 15}),

                ], className='row'),


                html.Div([

                    html.Div([
                        html.H5(['Negative Aspects'], id='text8'),
                    ], className='six columns', style={'textAlign': 'center'}),

                    html.Div([
                        html.H5(['Positive Aspects'], id='text9'),
                    ], className='six columns', style={'textAlign': 'center'}),

                ], className='row', style={'paddingTop': 10}),

                html.Div([

                    html.Div([
                        dt.DataTable(
                            rows=product_data.to_dict('records'),
                            id='neg_aspects',
                            sortable=True,
                            editable=False,
                            filterable=False,
                            columns=['Aspects', 'Frequency']),
                    ], className="six columns", style={'paddingTop' : 5}),

                    html.Div([
                        dt.DataTable(
                            rows=product_data.to_dict('records'),
                            id='pos_aspects',
                            sortable=True,
                            editable=False,
                            filterable=False,
                            columns=['Aspects', 'Frequency']),
                    ], className="six columns", style={'paddingTop' : 5}),

            ], className='row', style={'paddingBottom' : 20}),

        ], className="six columns padded"),

    ], className='row padded'),

])


# Button Callback


# Dropdown to text callback
@app.callback(
    dash.dependencies.Output('products', 'options'),
    [dash.dependencies.Input('slider_n_reviews', 'value'),
     dash.dependencies.Input('slider_price', 'value')])
def slider_price(value_reviews, value_price):

    data = db.laptop_reviews.aggregate([
                                        {'$group' :
                                             { '_id' : '$asin', 'count' : {'$sum' : 1}}
                                         },
                                        {'$sort': {'count': -1}},

                                        {'$match': {'$or': [{'count': {'$gt': value_reviews[0], '$lt': value_reviews[1]}}]}}
                                        ])
    unique_ids_dict_pre= [x['_id'] for x in list(data)]


    price_data = db.metadata.aggregate( [ { '$match': { '$or': [ { 'price': { '$gt': value_price[0], '$lt': value_price[1] } } ] } } ] )

    p_data = [ x['asin'] for x in list(price_data)]


    #combine list of inputs
    unique_ids_dict_pre = list(set(p_data) & set(unique_ids_dict_pre))

    unique_ids_dict_updated =[]

    for x in unique_ids_dict_pre:

        updated_dict2 = {}
        updated_dict2["label"] = x
        updated_dict2["value"] = x

        unique_ids_dict_updated.append(updated_dict2)

    print('uni', unique_ids_dict_updated)

    return unique_ids_dict_updated


# Image callback
@app.callback(
    dash.dependencies.Output('image1', 'src'),
    [dash.dependencies.Input('products', 'value')])
def imgage_updater(value):
    imUrl = db.metadata.find_one({"asin": value})["imUrl"]
    return imUrl

# Text Callback
@app.callback(
    dash.dependencies.Output('dynamic_text1', 'children'),
    [dash.dependencies.Input('products', 'options')])
def update_slider2_test(options):
    return '[ {} out of {} shown ]'.format(str(len(options)), str(len(unique_ids)))


# Datatable Callback
@app.callback(
    dash.dependencies.Output('DT_product', 'rows'),
    [dash.dependencies.Input('products', 'value')])
def datatable(value):

    # Get metadata
    metadata = db.metadata.find_one({"asin": value})

    if metadata['price'] == "":
       price = "Not Available"
    else:
        price = metadata["price"]

    # Get reviewdata
    # Number of reviews
    n_reviews = db.laptop_reviews.find({"asin": value}).count()

    # Build DataFrame
    product_data = pd.DataFrame({"Price": [price], "N_reviews": [n_reviews]})

    return product_data.to_dict('records')

# Datatable Callback
@app.callback(
    dash.dependencies.Output('pos_aspects', 'rows'),
    [dash.dependencies.Input('products', 'value')])
def datatable_positive(value):

    # Get data from aspects collections
    p_aspects = collection.find_one({'name': value})
    pos_aspects = pd.DataFrame.from_dict(p_aspects['positive'], orient='index')
    pos_aspects = pos_aspects.sort_values(by=0, ascending=False)
    pos_aspects = pos_aspects.reset_index()
    pos_aspects.columns = ['Aspects', 'Frequency']

    return pos_aspects.to_dict('records')

# Datatable Callback
@app.callback(
    dash.dependencies.Output('neg_aspects', 'rows'),
    [dash.dependencies.Input('products', 'value')])
def datatable_negative(value):

    # Get data from aspects collections
    n_aspects = collection.find_one({'name': value})
    neg_aspects = pd.DataFrame.from_dict(n_aspects['negative'], orient='index')
    neg_aspects = neg_aspects.sort_values(by=0, ascending=True)
    neg_aspects = neg_aspects.reset_index()
    neg_aspects.columns = ['Aspects', 'Frequency']

    return neg_aspects.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)


