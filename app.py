import dash
from dash import dash_table
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.io as pio
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import numpy as np 
import time
import requests_cache
from whitenoise import WhiteNoise
import os



pio.templates["custom_dark"] = pio.templates["plotly_dark"]
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)



# set the paper_bgcolor and the plot_bgcolor to a new color
pio.templates["custom_dark"]['layout']['paper_bgcolor'] = 'rgba(0,0,0,0)'
pio.templates["custom_dark"]['layout']['plot_bgcolor'] = 'rgba(0,0,0,0)'

# you may also want to change gridline colors if you are modifying background
pio.templates['custom_dark']['layout']['yaxis']['gridcolor'] = '#4f687d'
pio.templates['custom_dark']['layout']['xaxis']['gridcolor'] = '#4f687d'


CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

pio.templates.default = 'custom_dark'
#style = '/assets/style.css'
#font_awesome = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
meta_tags = [{"name": "viewport", "content": "width=device-width"}]
#external_stylesheets = [style, meta_tags, font_awesome, dbc.themes.BOOTSTRAP]
external_stylesheets = [meta_tags, dbc.themes.BOOTSTRAP]

data = pd.read_csv("dash_space_x.csv")


max_payload = data['Payload Mass(kg)'].max()
min_payload = data['Payload Mass(kg)'].min()



uniquelaunchsites = data['Launch Site'].unique().tolist()
lsites = []
lsites.append({'label': 'All Sites', 'value': 'All Sites'})
for site in uniquelaunchsites:
    lsites.append({'label': site, 'value': site})


soptions = [
    {"label": "Industry", "value": "Industry"},
    {"label": "Continent", "value": "Continent"},
]


palette =['#9c4a3c','#8C9B3C','#d27702','#ffe709','#9e8d77','#395112','#9c4a3c','#efddc9','#206169']

important_df = pd.read_pickle('data_df.pkl')
#important_df = pickdf

#important_df['customers']=important_df.customers.str.replace('\[|\]','')
important_df['norad_id']=important_df.norad_id.str.replace('\[|\]','')
important_df.drop('coords', axis=1, inplace=True)
#Basic Launches Information
completed_missions = important_df[important_df.upcoming == False].flight_number.count()
upcoming_missions = important_df[important_df.upcoming == True].flight_number.count()
landing_intent_missions = important_df[important_df.landing_intent == True].flight_number.count()
land_success_missions = important_df[important_df.land_success == True].flight_number.count()

#graph styling variables
#plot_color = 'rgb(62, 64, 70)'
#paper_color = 'rgb(62, 64, 70)'
#font_dict = dict(size=14, color= 'rgb(198, 200, 209)')



# Launch success/failure data grab------------------------------------------------------------
def launch_sites(data):
        sitesdata = data[['Launch Site', 'Launch outcome']]
        sites_df = pd.DataFrame(data = sitesdata, columns = ['Launch Site', 'Success'])
        sites_df['launch_site_success'] = data.Class
        unique_sites = sites_df['Launch Site'].unique()
        launch_site_dict = {}
        for year in unique_sites:
            launch_site_dict[year] = {}
            launch_site_dict[year]['Launches'] = sites_df.loc[sites_df['Launch Site'] == year, 'Launch Site'].count()
            launch_site_dict[year]['Failures'] = sites_df.loc[(sites_df['Launch Site'] == year) & (sites_df.launch_site_success == False), 'launch_site_success'].count()
            launch_site_dict[year]['Success'] = sites_df.loc[(sites_df['Launch Site'] == year) & (sites_df.launch_site_success == True), 'launch_site_success'].count()
        launch_site_df = pd.DataFrame.from_dict(data = launch_site_dict, orient = 'index', columns = ['launches', 'failures', 'success'])
        launch_site_df= pd.DataFrame(launch_site_dict).T
        launch_site_df['Percent Success'] =((launch_site_df['Success']/(launch_site_df['Success']+launch_site_df['Failures']))*100).round(2)
        return launch_site_df

launch_site_df = launch_sites(data)

ccafs = launch_site_df.loc['CCAFS','Percent Success']
vafb = launch_site_df.loc['VAFB','Percent Success']
ksc = launch_site_df.loc['KSC','Percent Success']
capecav = launch_site_df.loc['Cape Canaveral','Percent Success']
ccsfs = launch_site_df.loc['CCSFS','Percent Success']
vsfb = launch_site_df.loc['VSFB','Percent Success']

fig1 = go.Figure(data=[
    go.Bar(
        name='Failures', 
        x=launch_site_df.index, 
        y=launch_site_df.Failures,
        marker_color = '#9c4a3c', 
        texttemplate = '',
        hovertemplate = '<i>Launches</i>: %{y}'+'<br><b>Year</b>: %{x}<br>'+'Percent Change: %<b>%{text:.2f}</b>',
        marker_pattern_shape="x"),
    go.Bar(
        name='Successes', 
        x=launch_site_df.index, 
        y=launch_site_df.Success, 
        marker_color = '#8C9B3C', 
        text=launch_site_df['Percent Success'].round(2), 
        hovertemplate = '<i>Launches</i>: %{y}'+'<br><b>Year</b>: %{x}<br>'+'Percent Change: %<b>%{text:.2f}</b>',
        marker_pattern_shape=".")
])
fig1.update_layout(
    barmode='stack',
    title = 'Success/Failures in Launch<br>(2010-2022)',
    title_x=.5,
    uniformtext_mode='hide'
    )




#Launch Customers Pie Chart-------------------------------------------------------------------
customers = important_df.customers
all_customers = []
for cust in customers:
    for c in cust:
        all_customers.append(c)
customers_set = set(all_customers)

customers_dict = {}
for item in customers_set:
    customers_dict[item] = all_customers.count(item)

customers_df = pd.DataFrame.from_dict(data = customers_dict, orient = 'index', columns = ['Launches'])

fig2 = px.pie(customers_df, values='Launches', names=customers_df.index, title='SpaceX Customers and Number of Launches')
fig2.update_traces(textposition='inside', textinfo='percent+label')
fig2.update_layout(
    font = dict(color= 'rgb(198, 200, 209)')
    )

#Launches by Nation----------------------------------------------------------------------------
nations = important_df.nationality
unique_nations = nations.unique().tolist()
nations_list = nations.tolist()

nations_dict = {}
for item in unique_nations:
    nations_dict[item] = nations_list.count(item)

nations_df = pd.DataFrame.from_dict(data = nations_dict, orient = 'index', columns = ['Nations'])
fig3 = px.pie(nations_df, values='Nations', names=nations_df.index, title='Nation Launches')
fig3.update_traces(textposition='inside', textinfo='percent+label')
fig3.update_layout(
    font = dict(size=14, color= 'rgb(198, 200, 209)')
    )


#Creating dictionary for video viewing. Altering nomenclature in video links to include 'embed'...
video_df = important_df.loc[important_df['video_link'].notnull(), ['launch_year','mission_name', 'video_link','is_tentative', 'launch_success', 
'details', 'landing_intent', 'land_success', 'landing_type', 'landing_vehicle', 'nationality', 'manufacturer', 
'payload_id', 'payload_type', 'payload_mass_lbs', 'reference_system', 'semi_major_axis_km', 'eccentricity',
'periapsis_km','apoapsis_km','inclination_deg','period_min','lifespan_years','regime', 'site_name_long']]

video_df.columns =video_df.columns.str.replace('_',' ').str.title()


video_df_items = ['Is Tentative',
       'Launch Success', 'Landing Intent', 'Land Success',
       'Landing Type', 'Landing Vehicle', 'Nationality', 'Manufacturer',
       'Payload Id', 'Payload Type', 'Payload Mass Lbs', 'Reference System','Details']
#,'semi_major_axis_km', 'eccentricity',
#'periapsis_km','apoapsis_km','inclination_deg','period_min','lifespan_years','regime', 'site_name_long'



def youtube_link(word):
    if 'feature' in word:
        for i in range(0,len(word)):
            if i < len(word) - 1 :
                if (word[i] == "v") & (word[i+1] == '='):
                    first_place = i + 2
                if word[i] == '&':
                    last_place = i
    elif 'youtube' in word:
        last_place = len(word)
        for i in range(0,len(word)):
            if word[i] == "=":
                first_place = i + 1
            if word[i] == '&':
                last_place = i + 1
    elif 'youtu.be' in word:
        last_place = len(word)
        for i in range(0,len(word)):
            if word[i] == 'e':
                first_place = i + 2
    return 'https://www.youtube.com/embed/' + word[first_place: last_place]

video_df['Video Link'] = video_df['Video Link'].map(youtube_link)
first_video_df = video_df.rename({'Mission Name' : 'label', 'Video Link': 'value'}, axis = 'columns')
first_video_dict = first_video_df.to_dict('records')
video_dict = video_df.groupby('Launch Year').apply(lambda s: s.drop('Launch Year', 1).to_dict('records')).to_dict()

#Row creation function for individual mission data
def cardDiv(updateVar):
    return html.Div(className = 'detail-block', children = [
                html.Div(className = 'detail-var', children = updateVar),
                html.Div(id = updateVar)
            ])

cardDivs1 = []
for item in video_df_items:
    cardDivs1.append(cardDiv(item))

cardDivs = cardDivs1[:-1]
cardDivs1 = cardDivs1[-1:]
def callbackOutputs(idVar):
    return Output(idVar, 'children')

missionCallbacks = []
for item in video_df_items:
    missionCallbacks.append(callbackOutputs(item))

#manufacturer - orbit graph creation
manufacturer_reference = important_df[['manufacturer', 'orbit']]
manufacturers = manufacturer_reference.manufacturer.unique()
manufacturers = [i for i in manufacturers if i] 
orbits = manufacturer_reference.orbit.unique()
orbits_dict = {}
for item in manufacturers:
    orbits_dict[item] = {}
    for orbit in orbits:
        orbits_dict[item][orbit] =  manufacturer_reference[(manufacturer_reference.manufacturer == item) & (manufacturer_reference.orbit == orbit)].orbit.count()
#Landing Tab-----------------------------------------------------------------------------------

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title = 'SpaceX Dashboard', update_title="3...2...1...", assets_folder="assets")

server = app.server
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/')


banner = dbc.Row(
    html.Img(src=app.get_asset_url('img/spacexbanner.jpeg'),
    className='banner'))

header = dbc.Row(html.Div(children=[
        html.Img(src=app.get_asset_url('img/spacex_transparent_logo.png'),
                 className='title_image'
                 ),
        html.H1('SpaceX Missions',
                className='title'
                ),
    ], className='logo_title'),className='header')
    
headerImage = dbc.Row(html.Div(html.Img(src=app.get_asset_url('img/logo.png'),
    className='banner'),className='logo_img'),className='header')

pie_row = html.Div(
                [html.P('Total Successful Launches: By Site', style={
                    'textAlign': 'center'
                }),
                html.Div(id='dropdown_div', children=[
                    dcc.Dropdown(id='site_dropdown', 
                    options=lsites, 
                    placeholder='Select a Launch Site here', 
                    searchable=True,
                    clearable=False, style={'color':'aliceblue','width':'100%'}, 
                    value='All Sites'),
                ], className='dropdown_site'),
                ], className='pie_controls')
            


scatter_row= html.Div([
                html.P('Payload(1000 (kg)', style={
                    'textAlign': 'center'
                }),
                dcc.RangeSlider(
                    id='payload_slider',
                    #vertical=True,
                    min=0,
                    max=10000,
                    step=1000,
                    marks={
                        0: '0',
                        2000: '2',
                        4000: '4',
                        6000: '6',
                        8000: '8',
                        10000: '10'
                    },
                    value=[min_payload, max_payload],
                    className='range_slider'),
            ],className='scatter_controls')

sidebar = html.Div(
    [
        html.H2('Parameters', style=TEXT_STYLE),
        html.Hr()
    ],
    className='sidebar',
)


#content_third_row = dbc.Row(
#    [
#        dbc.Col(
#            dcc.Graph(id='success-pie-chart'), md=6,
#        ),
#        dbc.Col(
#            dcc.Graph(id='success-payload-scatter-chart'), md=6
#        )
#    ]
#)

content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='success-sun-chart'), md=12
        ),
        
    ]
)

content = html.Div(
    [
        
        
        #content_first_row,
        #content_second_row,
        #content_third_row,
        content_fourth_row
    ],
    style=CONTENT_STYLE
)


#landingtab = dbc.Tab(label='General Metrics', children=[sidebar, content])


#Tab 1-----------------------------------------------------------------------------------

tab1 = dbc.Tab(label='Insights', children=[    
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("General Information", style = {'textAlign': 'center'}),
                        html.Div(
                        [   html.Div([html.P("Completed Missions: "), html.Div(completed_missions, className = 'info-num')], className = 'info'),
                            html.Div([html.P("Planned Missions Coming Up: "), html.Div(upcoming_missions, className = 'info-num')], className = 'info'),
                            html.Div([html.P("Number of Misions with a Landing Intent: "), html.Div(landing_intent_missions, className = 'info-num')], className = 'info'),
                            html.Div([html.P("Number of Missions with a Successful Land: "), html.Div(land_success_missions, className = 'info-num')], className = 'info'),
                        ], className = 'info-div'),
                    ], className = 'gen-info')
                ],className='geninfo-div'),
                
                #content_third_row,
                html.Div(className = 'graph-grid', children = 
                    [
                        html.Div(children=[
                            pie_row,
                            dcc.Graph(id='success-pie-chart')], className = 'small_graph'),
                        html.Div(children=[
                            scatter_row,
                            dcc.Graph(id='success-payload-scatter-chart')], className = 'small_graph'),
                        html.Div(children=[
                            dcc.RadioItems(id='cl_dropdown', options=soptions, value='Industry', style={'text-align': 'left', 'padding-left': '1.5rem'}),
                            dcc.Graph(id='success-sun-chart')], className = 'small_graph'),
                        html.Div(children=[
                            html.Br(),
                            dcc.Graph(id='success-line-chart'),
                            ], className = 'small_graph'),
                        
                        ]),
                    
                ]),
            ], className = "Tab_One")


#Tab 2-----------------------------------------------------------------------------------

tab2 = dbc.Tab(label='Site Map', children=[    
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Each Site's Success Ratio"),
                        html.H4(),
                        html.Div(children=
                        [   html.Div([html.P("CCAFS: "), html.Div(ccafs, className = 'info-num')], className = 'info'),
                            html.Div([html.P("VAFB: "), html.Div(vafb, className = 'info-num')], className = 'info'),
                            html.Div([html.P("KSC: "), html.Div(ksc, className = 'info-num')], className = 'info'),
                            html.Div([html.P("Cape Canaveral: "), html.Div(capecav, className = 'info-num')], className = 'info'),
                            html.Div([html.P("CCSFS: "), html.Div(ccsfs, className = 'info-num')], className = 'info'),
                            html.Div([html.P("VSFB: "), html.Div(vsfb, className = 'info-num')], className = 'info'),
                        ], className = 'info-div'),
                    ], className = 'gen-info'),
                ]),
      
                #content_third_row,
                html.Div(className = 'map_div', children = 
                    [
                        html.Div(children=[
                            html.H4("Florida", className='header4'),
                            html.Div(html.Iframe(id='map_fl',srcDoc= open('assets/florida_sites.html','r').read(),width='90%',height='500px', className = 'responsive-iframe')),
                            ], className = 'frame-container'),
                        html.Hr(),
                        html.Div(children=[
                            html.H4("California", className='header4'),
                            html.Div(html.Iframe(id='map_ca',srcDoc= open('assets/cali_sites.html','r').read(),width='90%',height='500px)', className = 'responsive-iframe')),
                            ], className = 'frame-container'),
                        ]),
                    
                ]),
            ], className = "Tab_One")

#Tab 3-----------------------------------------------------------------------------------


tab3 = dcc.Tab(label='Mission Info', className = 'custom-tab', selected_className = 'custom-tab--selected', children=[  
            html.Div(className = 'video-page', children = [
                html.Div(className = 'selection_row', children = [
                    html.Div(className = 'selection-box', children = [
                        html.H2("Mission Selection"),
                        html.Div(className = "mission_selection", children = [
                            html.Div(className = 'launch_year_dropdown', children = [
                                dbc.Label("Choose a Launch Year", html_for = "launches_years"), 
                                dcc.Dropdown(className = 'video-dropdown', id='launches_years', options=[{'label': k, 'value': k} for k in video_dict.keys()], value = '2016'),
                            ]),
                            html.Div(className = 'middle-space'),
                            html.Div(className = 'mission_dropdown', children = [
                                dbc.Label("Choose a Mission", html_for = "missions"), 
                                dcc.Dropdown(className = 'video-dropdown', id = 'missions', value = 'SES-9')
                            ]),
                        ])
                    ])
                ]),
                html.Div(className = 'lower-half', children = [
                    html.Div(className = 'video-div', children = [
                        html.H2('The Launch'),
                        html.Iframe(className = "mission_video", id='frame', src=None)
                    ]),
                    html.Div(className = 'middle-piece'),
                    html.Div(className = 'video-details', children = [
                        html.H2(className = 'mission-h1', children = 'Mission Details'),
                        html.Div(className = 'card-divs', children = cardDivs)
                    ]),
                    html.Div(className ='mission-summary', children=[
                        html.Div(className = 'card-div1', children = cardDivs1),
                    ]
                    )
                ]),
            ])
        ])

#Tab 4-----------------------------------------------------------------------------------


tab4 = dcc.Tab(label='Raw Data', className = 'custom-tab', selected_className = 'custom-tab--selected', children=[
            html.Div(className = 'dt-div', children = [
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in data.columns],
                    data=data.to_dict('records'),
                    style_cell = {
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'color': 'white',
                        'backgroundColor': '#30404D'
                    },
                    style_table = {
                        'overflowX': 'auto',
                        'overflowY': 'auto',
                        'max_height': '80vh',
                        'max_width': '95vw'
                    },
                    style_header={
                        'backgroundColor': 'rgb(58, 60, 65)',
                        'fontWeight': 'bold'
                    },
                    tooltip_data=[
                        { column: {'value': str(value), 'type': 'markdown'}
                            for column, value in row.items()
                        } for row in data.to_dict('rows')
                    ],
                    css=[{
                        'selector': '.dash-table-tooltip',
                        'rule': 'background-color: grey; font-family: monospace; color: white'
                        }],
                    tooltip_duration=None
                ),
                html.Div(className = 'bot-div')
            ])
        ])



footer = html.Footer(id="footer",
                            className="section",
                            children=[html.A('Portfolio ', href='https://www.taylorsegell.com'),
                                html.P(
                                    children=[
                                        
                                        html.Span('Data From:'),
                                        html.A('SpaceX API',href="https://github.com/r-spacex/SpaceX-API")
                                    ])])
#App Construction-----------------------------------------------------------------------------------

#app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])
app.layout= html.Div(className = 'main-div', 
        children =[headerImage,
               dbc.Tabs(children=[tab1,tab2, tab3,tab4], className='zetabs'),footer])


#Callbacks-----------------------------------------------------------------------------------


@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site_dropdown', component_property='value')]
)
def update_graph(site_dropdown):
    labels = {'0':'Failure', '1': 'Successful'}
    if (site_dropdown == 'All Sites'):
        piepalette = ['#8C9B3C','#608A2E','#8A7C2E','#c7c9a9','#9B703C','#9c4a3c']
        lsdf = data.groupby(['Launch Site']).agg({'Class':['mean','sum','count']})
        lsdf['Perecent Success']=lsdf[('Class',   'sum')]/lsdf[('Class',   'sum')].sum()*100
        lsdf['Failed Missions'] = lsdf[('Class',   'count')]-lsdf[('Class',   'sum')]
        lsdf['Perecent Failure']=lsdf['Failed Missions']/lsdf['Failed Missions'].sum()*100
        lsdf['Successful Missions'] = lsdf[('Class',   'sum')]
        lsdf['Total Missions'] = lsdf[('Class',   'count')]
        lsdf=lsdf.iloc[:,3:].droplevel(level=1, axis=1).reset_index()
        fig2 = go.Figure(go.Pie(labels=lsdf['Launch Site'], values=lsdf['Successful Missions'], marker_colors=piepalette,
            hole=.35,customdata=lsdf[['Failed Missions', 'Total Missions']]))#,labels={'Total Missions':'Total Missions'}))
        fig2.update_traces(hovertemplate='Launch Site: %{label}<br>Failed/Total Missions: %{customdata}<br>Successful Missions: %{value}')
        fig2.update_traces(textposition='outside',
                                        textinfo='percent+label',
                                        marker=dict(line=dict(color='#000000',
                                                                width=4)),
                                        pull=[0.05, 0,0,0,0,0])
                                        # rotation=180 )
        fig2.update_layout(legend=dict({'traceorder': 'normal'}),
                                        legend_title_text='Result')
    else:
        df = data.loc[data['Launch Site'] == site_dropdown]
        def newLegend(fig, newNames):
            newLabels = []
            for item in newNames:
                for i, elem in enumerate(fig.data[0].labels):
                    if elem == item:
                        #fig.data[0].labels[i] = newNames[item]
                        newLabels.append(newNames[item])
            fig.data[0].labels = np.array(newLabels)
            return(fig)

        fig2 = px.pie(data,values='Class',
                                    names='Class',
                                    color='Class',
                                    color_discrete_sequence=palette,
                                    hole=0.35)
        fig2.update_traces(textposition='outside',
                                        textinfo='percent+label',
                                        marker=dict(line=dict(color='#000000',
                                                                width=4)),
                                        pull=[0.05, 0])
                                        # rotation=180 )
        fig2.update_layout(legend=dict({'traceorder': 'normal'}
                                                    ),
                                        legend_title_text='Result')
        # custom function set to work
        fig2=newLegend(fig2, {0:"Failed",1:"Success"})
        
  
    return fig2


@app.callback(Output(component_id='success-payload-scatter-chart',component_property='figure'),[Input(component_id='site_dropdown',component_property='value'),Input(component_id="payload_slider", component_property="value")])

def update_scattergraph(site_dropdown, payload_slider):
    data['Booster Model'] = data['Booster Family']
    data['Booster Family'] = data['Booster Family'].astype(str).str[:5]
    
    if site_dropdown == 'All Sites':
        low, high = payload_slider
        df = data
        mask = (df['Payload Mass(kg)'] > low) & (
            df['Payload Mass(kg)'] < high)
        fig = px.scatter(
            df[mask],x="Date", y="Payload Mass(kg)", 
            color="Booster Family",
            color_discrete_sequence=palette,
            hover_data=['Payload Mass(kg)', 'Date'])
    else:
        low, high = payload_slider
        df = data.loc[data['Launch Site'] == site_dropdown]
        mask = (df['Payload Mass(kg)'] > low) & (
            df['Payload Mass(kg)'] < high)
        fig = px.scatter(
            df[mask],x="Date", y="Payload Mass(kg)", 
            color="Booster Family",
            color_discrete_sequence=palette,
            hover_data=['Payload Mass(kg)', 'Date'])
    return fig


@app.callback(Output(component_id='success-sun-chart', component_property='figure'),[Input(component_id='site_dropdown', component_property='value'),Input(component_id='cl_dropdown', component_property='value')])

def update_graph(site_dropdown, cl_dropdown):
    if site_dropdown == 'All Sites':
        if cl_dropdown == ['Industry']:
            df = data
            con = df.groupby(['Ownership', 'Continent','Industry','Country','Company']).agg({'Flight No.':'count', 'Class':'mean'})
            cont = pd.DataFrame(con)
            cont=cont.reset_index()
            
            fig = px.sunburst(cont, path=['Ownership', cl_dropdown,'Company'], values='Flight No.', color='Class', color_continuous_scale=[(0, '#9c4a3c'), (1, '#8C9B3C')])
            fig.update_traces(hovertemplate='<b>%{label} </b> <br> Flights: %{value}<br> Success Rate: %{color:.2f}')
            fig.update_layout(title='Launch Success By '+cl_dropdown+' at '+site_dropdown, title_x=.5)
        else:
            df = data
            con = df.groupby(['Ownership', 'Continent','Industry','Country','Company']).agg({'Flight No.':'count', 'Class':'mean'})
            cont = pd.DataFrame(con)
            cont=cont.reset_index()
            
            fig = px.sunburst(cont, path=['Ownership', cl_dropdown,'Company'], values='Flight No.', color='Class', color_continuous_scale=[(0, '#9c4a3c'), (1, '#8C9B3C')])
            fig.update_traces(hovertemplate='<b>%{label} </b> <br> Flights: %{value}<br> Success Rate: %{color:.2f}')
            fig.update_layout(title='Launch Success By '+cl_dropdown+' at '+site_dropdown, title_x=.5)   
    else:
        if cl_dropdown == ['Industry']:
            df = data.loc[data['Launch Site'] == site_dropdown]
            con = df.groupby(['Ownership', 'Continent','Industry','Country','Company']).agg({'Flight No.':'count', 'Class':'mean'})
            cont = pd.DataFrame(con)
            cont=cont.reset_index()
            #px.treemap(cont.dropna(), path=['Ownership', 'Industry','Company'], values='Flight No.', color='Industry')
            fig = px.sunburst(cont, path=['Ownership', cl_dropdown,'Company'], values='Flight No.', color='Class', color_continuous_scale=[(0, '#9c4a3c'), (1, '#8C9B3C')])
            fig.update_traces(hovertemplate='<b>%{label} </b> <br> Flights: %{value}<br> Success Rate: %{color:.2f}')
            fig.update_layout(title='Launch Success By '+cl_dropdown+' at '+site_dropdown, title_x=.5)
        else: 
            df = data.loc[data['Launch Site'] == site_dropdown]
            con = df.groupby(['Ownership', 'Continent','Industry','Country','Company']).agg({'Flight No.':'count', 'Class':'mean', 'Payload Mass(kg)':'mean'})
            cont = pd.DataFrame(con)
            cont=cont.reset_index()
            fig = px.sunburst(cont, path=['Ownership', cl_dropdown,'Company'], values='Flight No.', color='Class', color_continuous_scale=[(0, '#9c4a3c'), (1, '#8C9B3C')])
            fig.update_traces(hovertemplate='<b>%{label} </b> <br> Flights: %{value}<br> Success Rate: %{color:.2f}')
            fig.update_layout(title='Launch Success By '+cl_dropdown+' at '+site_dropdown, title_x=.5)
    return fig


@app.callback(
    Output(component_id='success-line-chart', component_property='figure'),
    Input(component_id='site_dropdown', component_property='value'))
def update_barchart(site_dropdown):
    def launch_fun(data):
        dates = [datetime.strptime(x,'%Y-%m-%d') for x in data.Date]
        years = [ x.year for x in dates]
        year_fail_df = pd.DataFrame(data = years, columns = ['Years'])
        year_fail_df['launch_success'] = data.Class
        unique_years = year_fail_df['Years'].unique()
        launch_dict = {}
        for year in unique_years:
            launch_dict[year] = {}
            launch_dict[year]['Launches'] = year_fail_df.loc[year_fail_df.Years == year, 'Years'].count()
            launch_dict[year]['Failures'] = year_fail_df.loc[(year_fail_df.Years == year) & (year_fail_df.launch_success == False), 'launch_success'].count()
            launch_dict[year]['Success'] = year_fail_df.loc[(year_fail_df.Years == year) & (year_fail_df.launch_success == True), 'launch_success'].count()
        launch_df = pd.DataFrame.from_dict(data = launch_dict, orient = 'index', columns = ['launches', 'failures', 'success'])
        launch_df= pd.DataFrame(launch_dict).T
        launch_df['Percent Change(Success)'] =launch_df['Success'].pct_change().round(4)*100
        launch_df['Percent Change(Failure)'] =launch_df['Failures'].pct_change().round(4)*100
        return launch_df
    

    if site_dropdown == 'All Sites':
        launch_df = launch_fun(data)
        fig1 = go.Figure(data=[
            go.Bar(
                name='Failures', 
                x=launch_df.index, 
                y=launch_df.Failures,
                marker_color = '#9c4a3c', 
                text=launch_df['Percent Change(Failure)'],
                texttemplate = '',
                hovertemplate = '<i>Launches</i>: %{y}'+'<br><b>Year</b>: %{x}<br>'+'Percent Change: %<b>%{text:.2f}</b>',
                marker_pattern_shape="x"),
            go.Bar(
                name='Successes', 
                x=launch_df.index, 
                y=launch_df.Success, 
                marker_color = '#8C9B3C', 
                text=launch_df['Percent Change(Success)'].round(2), 
                hovertemplate = '<i>Launches</i>: %{y}'+'<br><b>Year</b>: %{x}<br>'+'Percent Change: %<b>%{text:.2f}</b>',
                marker_pattern_shape=".")
        ])

        fig1.update_layout(
            barmode='stack',
            title = 'Success/Failures in Launch<br>(2010-2022)',
            title_x=.5,
            uniformtext_mode='hide'
            )
    else:
        df = data.loc[data['Launch Site'] == site_dropdown]
        launch_df = launch_fun(df)

        fig1 = go.Figure(data=[
            go.Bar(
                name='Failures', 
                x=launch_df.index, 
                y=launch_df.Failures,
                marker_color = '#9c4a3c', 
                text=launch_df['Percent Change(Failure)'],
                texttemplate = '',
                hovertemplate = '<i>Launches</i>: %{y}'+'<br><b>Year</b>: %{x}<br>'+'Percent Change: %<b>%{text:.2f}</b>',
                marker_pattern_shape="x"),
            go.Bar(
                name='Successes', 
                x=launch_df.index, 
                y=launch_df.Success, 
                marker_color = '#8C9B3C', 
                text=launch_df['Percent Change(Success)'].round(2), 
                hovertemplate = '<i>Launches</i>: %{y}'+'<br><b>Year</b>: %{x}<br>'+'Percent Change: %<b>%{text:.2f}</b>',
                marker_pattern_shape=".")
        ])
        fig1.update_layout(
            barmode='stack',
            title = 'Success/Failures in Launch<br> Site: '+site_dropdown+'(2010-2022)',
            title_x=.5,
            uniformtext_mode='hide'
            )
    return fig1


@app.callback(
    Output('missions', 'options'),
    [Input('launches_years', 'value')]
)
def select_mission(selected_year):
    return [{'label': v['Mission Name'], 'value' : v['Mission Name']} for v in video_dict[selected_year]]

@app.callback(Output('frame', 'src'),[Input('missions', 'value'),Input('launches_years', 'value')])

def select_video(mission_value, year_value):
    for key in video_dict[year_value]:
        if key['Mission Name'] == mission_value:
            src = key['Video Link']
    return src

@app.callback(
    [Output('Is Tentative', 'children'),
    Output('Launch Success', 'children'),
    Output('Landing Intent', 'children'),
    Output('Land Success', 'children'),
    Output('Landing Type', 'children'),
    Output('Landing Vehicle', 'children'),
    Output('Nationality', 'children'),
    Output('Manufacturer', 'children'),
    Output('Payload Id', 'children'),
    Output('Payload Type', 'children'),
    Output('Payload Mass Lbs', 'children'),
    Output('Reference System', 'children')],
    [Input('missions', 'value'),
    Input('launches_years', 'value')]
)
def missionDetail(mission_value, year_value):
    for key in video_dict[year_value]:
        if key['Mission Name'] == mission_value:
            tentativeVar = key['Is Tentative']
            successVar = key['Launch Success']
            
            intentVar = key['Landing Intent']
            landSucVar = key['Land Success']
            landTypeVar = key['Landing Type']
            landVehVar = key['Landing Vehicle']
            nationVar = key['Nationality']
            manuVar = key['Manufacturer']
            payIdVar = key['Payload Id']
            payTypeVar = key['Payload Type']
            payMassVar = key['Payload Mass Lbs']
            referenceVar = key['Reference System']
    return "{}".format(tentativeVar), "{}".format(successVar), "{}".format(intentVar), "{}".format(landSucVar), "{}".format(landTypeVar), "{}".format(landVehVar), "{}".format(nationVar), "{}".format(manuVar), "{}".format(payIdVar), "{}".format(payTypeVar), "{}".format(payMassVar), "{}".format(referenceVar)#, "{}".format(failReasonVar),

@app.callback(
    Output('Details', 'children'),
    [Input('missions', 'value'),
    Input('launches_years', 'value')]
)
  
def summaryDetail(mission_value, year_value):
    for key in video_dict[year_value]:
        if key['Mission Name'] == mission_value:
            SummVar = key['Details']
    return "{}".format(SummVar)



if __name__ == '__main__':
    app.run_server(debug=True)
