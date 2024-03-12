# -*- coding: utf-8 -*-
'''
Created on Tue Mar 30 16:43:12 2021

@author: Leandro
'''

import dash
import requests
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import datetime
import pytz
import sqlite3

app = dash.Dash(
    __name__, 
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
)
server = app.server
app.title = 'Cuenca-SASD'

#Armado de diccionario con las estaciones hidrométricas de la cuenca
estaciones_hidrometricas = {
    'A° Las Piedras - Rep. del Libano': {
            'arroyo': 'Las Piedras',
            'unid': 3348,
            'key': 12,
            'table': 'alturas_all',
            'Lat': -34.7383417,
            'Long': -58.3096056,
            'color': '#1264EF',
            'Interseccion': 'República del Libano',
            'alerta_amarilla': 3,
            'alerta_naranja': 4,
            'alerta_roja': 4.5,
            'escalado': 3.2, #2.15,
            'name_sim': 'LP_Libano'},
    'A° Las Piedras - Av. Monteverde': {
            'arroyo': 'Las Piedras',
            'unid': 26201,
            'key': 29,
            'table': 'alturas_all',
            'Lat': -34.783421,
            'Long': -58.298648,
            'color': '#0BB910',
            'Interseccion': 'Av. Gobernador Monteverde',
            'alerta_amarilla': 3,
            'alerta_naranja': 4,
            'alerta_roja': 4.5,
            'escalado': 2.78,
            'name_sim': 'LP_Monteverde'},
    'A° San Francisco - Av. Montevideo': {
            'arroyo': 'San Francisco',
            'unid': 3349,
            'key': 9, #5,
            'table': 'alturas_all',
            'Lat': -34.7277556,
            'Long': -58.3200389,
            'color': '#E0713A',
            'Interseccion': 'Av. Montevideo',
            'alerta_amarilla': 3,
            'alerta_naranja': 4,
            'alerta_roja': 4.5,
            'escalado': 3.3, #2.03,
            'name_sim': 'SF_Montevideo'},
    'A° San Francisco - Dr. Torre': {
            'arroyo': 'San Francisco',
            'unid': 3349,
            'key': 8,
            'table': 'alturas_all',
            'Lat': -34.765609,
            'Long': -58.323036,
            'color': '#E0D83A',
            'Interseccion': '896',
            'alerta_amarilla': 3,
            'alerta_naranja': 4,
            'alerta_roja': 4.5,
            'escalado': 2.72,
            'name_sim': 'SF_DrTorre'},
    'Canal Santo Domingo - EB Olmos': {
            'arroyo': 'Santo Domingo',
            'unid': 3349,
            'key': 11,
            'table': 'alturas_all',
            'Lat': -34.687666,
            'Long': -58.3239342,
            'color': '#33FFFF',
            'Interseccion': 'San Isidro',
            'alerta_amarilla': 3,
            'alerta_naranja': 4,
            'alerta_roja': 4.5,
            'escalado': 3.5,
            'name_sim': 'SD_Olmos'},
    'Arroyo Galindez - Parque Finky': {
            'arroyo': 'Galindez',
            'unid': 3349,
            'key': 13,
            'table': 'alturas_all',
            'Lat': -34.788203,
            'Long': -58.3986461,
            'color': '#E20E1B',
            'Interseccion': 'Santa Maria',
            'alerta_amarilla': 3,
            'alerta_naranja': 4,
            'alerta_roja': 4.5,
            'escalado': 2.4,
            'name_sim': 'Finky'}}

# Función de lectura de datos y llenado de diccionario
def Niveles_Arroyos(date_i, date_f):
    for estacion in estaciones_hidrometricas.keys():      
        if estaciones_hidrometricas[estacion]['key'] in [29, 8]:
            req = 'http://api.fdx-ingenieria.com.ar/api_new?user=pabloegarcia@gmail.com&site_id=' + str(estaciones_hidrometricas[estacion]['key']) + '&query=filter_site&date=' + date_i + '@' + date_f
            data = requests.get(req)
            json_data = data.json()
            niveles = []
            print(estacion)
            if len(json_data) != 0:
                niveles = pd.DataFrame(json_data)
                niveles['fecha'] = pd.to_datetime(niveles['hora'])
                niveles = niveles.set_index('fecha').tz_localize(tz='America/Buenos_Aires')
                niveles = niveles.drop(labels=['id','marca', 'modelo', 'serie', 'latitude', 'longitude', 'name', 'hora'], axis = 1)
                niveles['nivel'] = niveles['nivel'].astype(float) - estaciones_hidrometricas[estacion]['escalado']
                niveles['nivel'].replace(estaciones_hidrometricas[estacion]['escalado'], '', inplace=True)
                print(niveles)
                niveles = niveles.sort_index()
                estaciones_hidrometricas[estacion].update({'serie': niveles})
            else:
                niveles = pd.DataFrame(data= {'nivel':[]})
                estaciones_hidrometricas[estacion].update({'serie': niveles})

        else:
            req = 'http://69.28.90.79:5000/api/rango?topic=telemetria_' + str(estaciones_hidrometricas[estacion]['key']) + '/nivel&fecha_inicio=' + date_i + '&fecha_fin=' + date_f
            data = requests.get(req)
            json_data = data.json()
            niveles = []
            print(estacion)
            if len(json_data) != 0:
                niveles = pd.DataFrame(json_data)
                niveles['fecha'] = pd.to_datetime(niveles['time'])
                niveles = niveles.set_index('fecha').tz_localize(tz='GMT+0').tz_convert(tz='America/Buenos_Aires')
                #niveles = niveles.drop(labels=['id','marca', 'modelo', 'serie', 'latitude', 'longitude', 'name', 'hora'], axis = 1)
                niveles['Nivel'] = estaciones_hidrometricas[estacion]['escalado'] -  niveles['Nivel'].astype(float)
                niveles['Nivel'].replace(estaciones_hidrometricas[estacion]['escalado'], '', inplace=True)
                niveles.rename(columns={'Nivel': 'nivel'}, inplace=True)
                print(niveles)
                niveles = niveles.sort_index()
                estaciones_hidrometricas[estacion].update({'serie': niveles})
            else:
                niveles = pd.DataFrame(data= {'nivel':[]})
                estaciones_hidrometricas[estacion].update({'serie': niveles})

        #print(estaciones_hidrometricas[estacion]['serie'])
        #niveles.to_csv(estacion + '.csv')
    return ()

escala_temporal = pd.DataFrame({'label': ['30 días', '7 días', '5 días', '3 días', '2 días', '1 día', '12 horas', '6 horas', '3 horas', '1 hora'],
                   'value': [24*30, 24*7, 24*5, 24*3, 24*2, 24, 12, 6, 3, 1]})

# Llama a función de lectura de niveles de arroyos en la BBDD
t_30 = (datetime.datetime.now(pytz.timezone('America/Buenos_Aires')) - datetime.timedelta(days=30)).strftime('%Y-%m-%d 00%H:%M:%S')
t_now = (datetime.datetime.now(pytz.timezone('America/Buenos_Aires')) + datetime.timedelta(days=1)).strftime('%Y-%m-%d 00%H:%M:%S')
Niveles_Arroyos(t_30, t_now)

try:
    e1 = estaciones_hidrometricas['A° Las Piedras - Rep. del Libano']['serie']['nivel'][-1]
    t1 = estaciones_hidrometricas['A° Las Piedras - Rep. del Libano']['serie']['nivel'].index[-1].strftime('Último dato: %H:%M %d-%m-%Y')
except:
    e1 = 999
    t1 = 'Sin datos'

try:
    e2 = estaciones_hidrometricas['A° Las Piedras - Av. Monteverde']['serie']['nivel'][-1]
    t2 = estaciones_hidrometricas['A° Las Piedras - Av. Monteverde']['serie']['nivel'].index[-1].strftime('Último dato: %H:%M %d-%m-%Y')
except:
    e2 = 999
    t2 = 'Sin datos'
    
try:
    e3 = estaciones_hidrometricas['A° San Francisco - Av. Montevideo']['serie']['nivel'][-1]
    t3 = estaciones_hidrometricas['A° San Francisco - Av. Montevideo']['serie']['nivel'].index[-1].strftime('Último dato: %H:%M %d-%m-%Y')
except:
    e3 = 999
    t3 = 'Sin datos'
    
try:
    e4 = estaciones_hidrometricas['A° San Francisco - Dr. Torre']['serie']['nivel'][-1]
    t4 = estaciones_hidrometricas['A° San Francisco - Dr. Torre']['serie']['nivel'].index[-1].strftime('Último dato: %H:%M %d-%m-%Y')
except:
    e4 = 999
    t4 = 'Sin datos'
  
#Código html  
app.layout = html.Div(
    children=[
        html.Div(
            className='row',
            children=[
                html.Div(
                    id='banner',
                    className='banner',
                    children=[
                        html.Div(
                            id='banner-text',
                            children=[
                                html.H4('Cuenca Sarandí - Santo Domingo'),
                                html.P(['Panel desarrollado por el INA en conjunto con el SMN para el seguimiento experimental de crecidas', 
                                        html.Br(), 
                                        'en los arroyos San Francisco y Las Piedras para los municipios de Quilmes y Almirante Brown.']),
                            ],
                        ),
                        html.Div(
                            id='banner-logo',
                            children=[
                                html.Img(id='logo_Quilmes', src=app.get_asset_url('quilmes_logo.png'),
                                    style={'marginRight':'20px', 'size':'130px',
                                    }
                                ),
                                html.Img(id='logo_Brown', src=app.get_asset_url('brown_logo.png'),
                                    style={'marginRight':'20px',
                                    }
                                ),
                                html.Img(id='logo_INA', src=app.get_asset_url('ina_logo.png'),
                                    style={'marginRight':'20px',
                                    }
                                ),
                                html.Img(id='logo_SMN', src=app.get_asset_url('smn_logo.png'),
                                    style={'marginRight':'20px',
                                    }
                                ),
                            ],
                        ),
                    ],
                ),        
                html.Div(
                    id='serie',
                    className = 'eleven columns',
                    children=[
                        html.Div(
                            dcc.Graph(id='graph-niveles',
                            ),
                        )
                    ], 
                    style={'margin-bottom': '0px', 'margin-top': '5px' }
                ),
                html.Div(
                    className = 'six columns',
                    children=[  
                        dcc.Slider(
                            id='escala-temporal',
                            min=0,
                            max=9,
                            step=None,
                            marks={
                                0: '30 días',
                                1: '7 días',
                                2: '5 días',
                                3: '3 días',
                                4: '2 días',
                                5: '1 día',
                                6: '12 horas',
                                7: '6 horas',
                                8: '3 horas',
                                9: '1hora',
                            },
                            value=5
                        ),
                    ],
                    style={'margin-bottom': '10px', 'margin-top': '10px' }
                ), 
            ],
        ),
        html.Div(
            id = 'info-container',
            className = 'row container-display',
            children=[
                html.Div(
                    id='bottom1',
                    className = 'three columns',
                    children=[
                        html.Div(  
                            [html.H5('{:.2f}'.format(e2)),
                             html.P('A° Las Piedras y Av. Monteverde'),
                             html.P(t2)],
                            id='LP1',
                            className='mini_container_LP1',
                        ),
                    ],
                ),
                html.Div(
                    id='bottom2',
                    className = 'three columns',
                    children=[
                        html.Div(
                            [html.H5('{:.2f}'.format(e1)),
                             html.P('A° Las Piedras y Rep. del Libano'),
                             html.P(t1)],
                            id='LP2',
                            className='mini_container_LP2',
                        ),
                    ],
                ),
               html.Div(
                    id='bottom3',
                    className = 'three columns',
                    children=[
                        html.Div(
                            [html.H5('{:.2f}'.format(e3)),
                             html.P('A° San Francisco y Av. Montevideo'),
                             html.P(t3)],
                             id='SF1',
                            className='mini_container_SF1',
                        ),
                    ],
                ),
               html.Div(
                    id='bottom4',
                    className = 'three columns',
                    children=[
                        html.Div(
                            [html.H5('{:.2f}'.format(e4)),
                             html.P('A° San Francisco y Dr. Torre'),
                             html.P(t4)],
                             id='SF2',
                            className='mini_container_SF2',
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            children=[
                dcc.Interval(
                     id='interval_component',
                     interval=1*1000*60*10,
                     n_intervals=0,
                ),
                html.Div(
                    id='ultima-act',
                ),
            ],
        ),
    ],  
)


#Callback de gráfico de nivel
@app.callback(
    Output('graph-niveles', 'figure'),
    [Input('escala-temporal', 'value'),
     Input('interval_component', 'n_intervals')])
def tempo_figure_niveles(tempo_value, n):
    tempo = int(escala_temporal['value'][tempo_value])
    now = datetime.datetime.now(pytz.timezone('America/Buenos_Aires'))
    begin = now - datetime.timedelta(hours=tempo)
    traces = []
    for estacion in estaciones_hidrometricas.keys():
        traces.append(dict(
            x=estaciones_hidrometricas[estacion]['serie'].index,
            y=estaciones_hidrometricas[estacion]['serie']['nivel'],
            mode='lines',
            opacity=1,
            line={'color': estaciones_hidrometricas[estacion]['color'], 'width':3},
            width=8,
            name=estacion))
    return {
        'data': traces,
        'layout': dict(
            xaxis={'range': [begin, now], 'tickangle': 0, 'zerolinecolor': 'ligthgray', 'gridcolor': '#6B6766', 'tickformat':'%H:%M <br> %d-%m-%Y'},
            yaxis={'title': 'Nivel Hidrométrico (m)', 'range': [-0.2, 3.2], 'tickvals':[0, 0.5, 1, 1.5, 2, 2.5, 3], 'title.standoff':10, 'mirror':'all', 'gridcolor': '#6B6766'},
            height=410,
            automargint=True,
            margin={'b': 40, 't': 5, 'r': 10},
            legend={'font': {'color': 'lightgray' ,'size':16}, 'orientation': 'h', 'x': 0, 'y': 1.1},
            hovermode='closest',
            transition = {'duration': 0},
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            font={'color': 'lightgray', 'size': 14},
        )
    }

#Callback de actualización de diccionario de datos hidrométricos
#Se llama a la función que lee toda la tabla. Idealmente se debería buscar el último dato, completar y comparar para ver si hay alguno nuevo.
@app.callback(
    Output('ultima-act', 'children'),
    [Input('interval_component', 'n_intervals')])
def update_table(n):
    t_30 = (datetime.datetime.now(pytz.timezone('America/Buenos_Aires')) - datetime.timedelta(days=30)).strftime('%Y-%m-%d 00%H:%M:%S')
    t_now = (datetime.datetime.now(pytz.timezone('America/Buenos_Aires')) + datetime.timedelta(days=1)).strftime('%Y-%m-%d 00%H:%M:%S')
    Niveles_Arroyos(t_30, t_now)
    #print(datetime.datetime.now(pytz.timezone('America/Buenos_Aires')).strftime('%Y-%m-%d %H:%M:%S'), n)
    return 

    
if __name__ == '__main__':
    app.run_server(debug=True)