import warnings
warnings.filterwarnings("ignore")
# Dash
from dash import Dash, html, dcc, Input, Output, State, callback_context,ctx
from dash.exceptions import PreventUpdate
# Dash community libraries
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
# Data management
import pandas as pd
import numpy_financial as npf

# Plots
import plotly_express as px

from utils.calc_szenarios import calculate_performance


# App configuration
# Icons from iconify, see https://icon-sets.iconify.design

app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{'name': 'viewport', 'inhalt': 'width=device-width, initial-scale=1'},
          ],
          )
server = app.server

# App configuration
# Icons from iconify, see https://icon-sets.iconify.design

app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{'name': 'viewport', 'inhalt': 'width=device-width, initial-scale=1'},
          ],
          )
server = app.server

app.title = 'Szenarienvergleich'

wetter_typ=['Jetzt Normal'
,'Jetzt Kalt'
,'Jetzt Warm'
,'zukunft Normal'
,'zukunft Kalt'
,'zukunft Warm']

button_info = dbc.Button(
    html.Div(id='button_info_content',children=[DashIconify(icon='ph:info',width=50,height=30,),html.Div('Info')]),
    id='button_info',
    outline=False,
    color='light',
    style={'text-transform': 'none',
        'border': 'none',
        'background': 'none',
        'color': 'white',
        'cursor': 'pointer'
    },
)
button_calc1 = dbc.Button(
    html.Div(children=[DashIconify(icon='ph:info',width=50,height=30,),html.Div('Berechne Ausgangssystem')]),
    id='start_calc',
    color='secondary',
    outline=True,
    style={"borderWidth": "2px"}
)
button_calc2 = dbc.Button(
    html.Div(children=[DashIconify(icon='ph:info',width=50,height=30,),html.Div('Berechne Ausgangssystem')]),
    id='start_calc2',
    color='secondary',
    outline=True,
    style={"borderWidth": "2px"}
)

header=dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                     html.Img(src="assets/Allgemeines_Logo.ico",)
                    ],
                    )
                ],
                align='center',
                ),
            ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4('Energiesystem HS-Emden-Leer'),
                    ],
                    id='app-title'
                    )
                ],
                align='left',
                ),
            ]),
        dbc.Row([
            dbc.Col([
                dbc.NavbarToggler(id='navbar-toggler'),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(button_info),
                        dcc.ConfirmDialog(id='info_dialog'),
                        ],
                        navbar=True,
                        ),
                    id='navbar-collapse',
                    navbar=True,
                    ),
                ],
                
                ),
            ],
            align='right',
            ),
        ],
        fluid=True,
        ),
    dark=True,
    color='#9cc5ce',
    sticky='top'
    )


container_system=dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Ausgangssystem"),
                        dbc.Label("PV-Größe (kWp)"),
                        dcc.Slider(min=40,max=1700,step=10,id="pv-size-input",marks={40: '40 kWp', 1500: '1500 kWp'} ,persistence='local', tooltip={"placement": "bottom", "always_visible": False}),
                        
                        dbc.Label("Windkraftanlage"),
                         dcc.Dropdown(id='wka-dropdown',
                            options=['Aus', 'Ein'],
                            placeholder='Wähle eine Option', persistence='local'),

                        dbc.Label("BHKW Regelung"),
                        dcc.Dropdown(id='dropdown',
                            options=['Aus', 'wärmegeführt', 'stromgeführt', 'bedarfsorientiert'],
                            placeholder='Wähle eine Option', persistence='local'),
                        
                        dbc.Label("Wärmepumpe"),
                        dcc.Dropdown(id='wp-slider',
                            options=[
                                'Aus', 'Luft/Wasser 200', 'Luft/Wasser 400',
                                'Luft/Wasser 600', 'Luft/Wasser 800', 'Luft/Wasser 1000',
                                'Sole/Wasser 200', 'Sole/Wasser 400', 'Sole/Wasser 600',
                                'Sole/Wasser 800', 'Sole/Wasser 1000'],
                            placeholder='Wähle eine Option', persistence='local'),
                        dbc.Label("Vorlauftemperatur: "),html.Br(),
                        dcc.Input(
                            id='vorlauftemperatur-input',
                            type='number',
                            value=55,  # Beispielwert für die Vorlauftemperatur
                            min=30,
                            max=100,
                            step=5),
                        html.Br(),
                        dbc.Label("Effizienz Gastherme"),html.Br(),
                        dcc.Input(
                            id='effizienz-gastherme',
                            type='number',
                            value=90,  # Beispielwert für die Vorlauftemperatur
                            min=85,
                            max=100,
                            step=1),
                        html.Br(),
                        dbc.Label("Wärmebedarfssenkung [%]"),html.Br(),
                        dcc.Input(
                            id='wärmebedarfssenkung',
                            type='number',
                            value=0,  # Beispielwert für die Vorlauftemperatur
                            min=0,
                            max=50,
                            step=5),
                        html.Br(),
                        html.Br(),
                        button_calc1
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.H3("Zielsystem"),
                        dbc.Label("PV-Größe (kWp)"),
                        dcc.Slider(min=40,max=1700,step=10,id="pv-size-input2",marks={40: '40 kWp', 1500: '1500 kWp'} ,persistence='local', tooltip={"placement": "bottom", "always_visible": False}),
                        
                        dbc.Label("Windkraftanlage"),
                         dcc.Dropdown(id='wka-dropdown2',
                            options=['Aus', 'Ein'],
                            placeholder='Wähle eine Option', persistence='local'),

                        dbc.Label("BHKW Regelung"),
                        dcc.Dropdown(id='dropdown2',
                            options=['Aus', 'wärmegeführt', 'stromgeführt', 'bedarfsorientiert'],
                            placeholder='Wähle eine Option', persistence='local'),
                        
                        dbc.Label("Wärmepumpe"),
                        dcc.Dropdown(id='wp-slider2',
                            options=[
                                'Aus', 'Luft/Wasser 200', 'Luft/Wasser 400',
                                'Luft/Wasser 600', 'Luft/Wasser 800', 'Luft/Wasser 1000',
                                'Sole/Wasser 200', 'Sole/Wasser 400', 'Sole/Wasser 600',
                                'Sole/Wasser 800', 'Sole/Wasser 1000'],
                            placeholder='Wähle eine Option', persistence='local'),
                        dbc.Label("Vorlauftemperatur: "),html.Br(),
                        dcc.Input(
                            id='vorlauftemperatur-input2',
                            type='number',
                            value=55,  # Beispielwert für die Vorlauftemperatur
                            min=30,
                            max=100,
                            step=5),
                        html.Br(),
                        dbc.Label("Effizienz Gastherme"),html.Br(),
                        dcc.Input(
                            id='effizienz-gastherme2',
                            type='number',
                            value=90,  # Beispielwert für die Vorlauftemperatur
                            min=85,
                            max=100,
                            step=1),
                        html.Br(),
                        dbc.Label("Wärmebedarfssenkung [%]"),html.Br(),
                        dcc.Input(
                            id='wärmebedarfssenkung2',
                            type='number',
                            value=0,  # Beispielwert für die Vorlauftemperatur
                            min=0,
                            max=50,
                            step=5),
                        html.Br(),
                        html.Br(),
                        button_calc2
                    ],
                    width=6,
                ),
            ],
        ),
    ],
    fluid=False,
)
container_performance=dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Systemvergleich"),
                        dcc.Store(id='sys1_store'),
                        dcc.Store(id='sys2_store'),
                        html.Div(id='performance', children='Führe im System zunächst beide Berechnungen aus.')
                       
                    ],
                    width=12,
                )
            ],
        ),
    ],
    fluid=False,
)
container_economy=dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Investitionspreis in €: "),
                        html.Br(),
                        dcc.Input(
                            id='invest',
                            type='number',
                            value=0,  # Beispielwert für die Vorlauftemperatur
                            min=0,
                            step=1000),
                        html.Br(),
                    ])]),
        dbc.Row([
                dbc.Col([
                        html.Br(),
                        dbc.Label("Strompreis zwischen 2025 und 2030"),
                        dcc.Slider(
                            min=10,
                            max=40,
                            step=0.5,
                            id="strom_now",
                            marks={10: '10 ct/kWh', 30: '30 ct/kWh'},
                            value=22,
                            persistence='local',
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                        html.Br(),
                        dbc.Label("Gaspreis zwischen 2025 und 2030"),
                        dcc.Slider(
                            min=3,
                            max=15,
                            step=0.1,
                            id="gas_now",
                            marks={3: '3 ct/kWh', 12: '12 ct/kWh'},
                            value=7,
                            persistence='local',
                            tooltip={"placement": "bottom", "always_visible": False})
                        
                    ],width=6),

                    dbc.Col([
                        html.Br(),
                        dbc.Label("Strompreis zwischen 2031 und 2045"),
                        dcc.Slider(
                            min=10,
                            max=40,
                            step=0.5,
                            id="strom_future",
                            marks={10: '10 ct/kWh', 30: '30 ct/kWh'},
                            value=20,
                            persistence='local',
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                        html.Br(),
                        dbc.Label("Gaspreis zwischen 2031 und 2035"),
                        dcc.Slider(
                            min=3,
                            max=15,
                            step=0.1,
                            id="gas_future",
                            marks={3: '3 ct/kWh', 12: '12 ct/kWh'},
                            value=10,
                            persistence='local',
                            tooltip={"placement": "bottom", "always_visible": False})
                        
                    ],width=6)
            ],
        ),
    ],
    fluid=False,
)


accordion = dmc.Accordion(
    style={"marginLeft": "10%","marginRight": "10%"},
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl("System",
                        icon=DashIconify(
                        icon="mingcute:settings-6-line",
                        color='#0069ae',
                        width=20,
                    ),),
                dmc.AccordionPanel(container_system
                ),
            ],
            value="system",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Performance",
                        icon=DashIconify(
                        icon="iconoir:energy-usage-window",
                        color='#0069ae',
                        width=20,
                    )),
                dmc.AccordionPanel(
                    container_performance
                ),
            ],
            value="performance",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Ökonomie",
                        icon=DashIconify(
                        icon="entypo:line-graph",
                        color='#0069ae',
                        width=20,
                    )),
                dmc.AccordionPanel(
                   [container_economy,html.Br(),
                    html.Div(id='cashflow')
                   ]
                ),
            ],
            value="economy",
        ),
    ],
)
layout = html.Div(id='app-page-content',children=[header,html.Br(),accordion])
app.layout=layout

@app.callback(
    Output('invest', 'value'),
    State('pv-size-input', 'value'),
    State('wp-slider', 'value'),
    State('effizienz-gastherme', 'value'),
    Input('start_calc', 'n_clicks'),
    State('pv-size-input2', 'value'),
    State('wka-dropdown2', 'value'),
    State('wp-slider2', 'value'),
    State('effizienz-gastherme2', 'value'),
    Input('start_calc2', 'n_clicks')
    )
def calc_invest(pv_size, wp_slider, effizienz_gastherme, n, pv_size2, wka_dropdown2, wp_slider2, effizienz_gastherme2, n2):
    pv_invest=(pv_size2-pv_size)*1_200
    if wka_dropdown2=='Ein':
        wka_invest=100_000
    else:
        wka_invest=0
    if wp_slider.split(' ')[0].startswith('Aus'):
        if wp_slider2.split(' ')[0].startswith('Aus')==0:
            if wp_slider2.split(' ')[1].startswith('S'):
                wp_invest=(int(wp_slider2.split(' ')[1]))*1500
            else:
                wp_invest=(int(wp_slider2.split(' ')[1]))*1000
        else:
            wp_invest=0
    else:
        wp_invest=0
    invest_gas=(effizienz_gastherme2-effizienz_gastherme)*500
    return invest_gas+wp_invest+wka_invest+pv_invest


@app.callback(
    Output('sys1_store', 'data'),
    State('pv-size-input', 'value'),
    State('wka-dropdown', 'value'),
    State('dropdown', 'value'),
    State('wp-slider', 'value'),
    State('vorlauftemperatur-input', 'value'),
    State('effizienz-gastherme', 'value'),
    State('wärmebedarfssenkung', 'value'),
    Input('start_calc', 'n_clicks')
    )

def calc_system1(pv_size, wka_dropdown, bhkw_regelung, wp_slider, vorlauftemperatur, effizienz_gastherme, wärmebedarfssenkung, n):
    if n==None:
        raise PreventUpdate
    min_cop=3
    Wetter_jahr=[]
    Wert=[]
    Einheit=[]
    System=[]
    df=pd.read_csv('src/Output_data/Eingangsdaten_simulation.csv', index_col=0)
    df.index=pd.date_range(start='01/01/2022', end='01/01/2023',freq='15min')[0:35040]
    for weather_typ in wetter_typ:
        if weather_typ.startswith('Jetzt'):
            wetter_time='2015'
            emissionen_strom=150/1_000_000
        else:
            wetter_time='2045'
            emissionen_strom=17/1_000_000
        if weather_typ.endswith('l'):
            weather_type='a_'
        elif weather_typ.endswith('t'):
            weather_type='w_'
        elif weather_typ.endswith('m'):
            weather_type='s_'
        weather=pd.read_csv('src/Input_data/Wetterdaten/TRY_1_'+weather_type+wetter_time+'_15min.csv', index_col=0)
        weather.index=pd.date_range(start='01/01/2022', end='01/01/2023',freq='15min')[0:35040]
        df['PV_Süd [W]']=weather['PV_Süd [W]']
        df['PV_West [W]']=weather['PV_West [W]']
        df['PV_Ost [W]']=weather['PV_Ost [W]']
        df['PV - Vorhanden [W]']=weather['PV - Vorhanden [W]']
        weather_day=weather.resample('D').mean()
        df['Temperatur Luft [°C]']=weather['temperature [degC]']
        for day in weather_day.index:
            df.loc[str(day.date()),'Tages-Durchschnittstemperatur [°C]']=df.loc[str(day.date()),'Temperatur Luft [°C]'].mean()
        df.loc[df['Tages-Durchschnittstemperatur [°C]']>12.1, 'Raumwämebedarf [W]']=0
        df.loc[df['Tages-Durchschnittstemperatur [°C]']<12.1, 'Raumwämebedarf [W]']=(20-df.loc[df['Tages-Durchschnittstemperatur [°C]']<12.1, 'Temperatur Luft [°C]'])*43739
        df['Raumwämebedarf [W]']=df['Raumwämebedarf [W]']+df['BHKW Strom [W]']*1.13
        df['Raumwämebedarf [W]']=df['Raumwämebedarf [W]']*(1-wärmebedarfssenkung/100)
        p_el_max, e_gf, e_gs, e_gas,p_gas_max, volllaststunden, sjaz, E_el_gesamterzeugung, E_el_hp=calculate_performance(df, wka_dropdown, bhkw_regelung, pv_size, wp_slider, effizienz_gastherme, vorlauftemperatur, min_cop)
        emissionen=-e_gf*emissionen_strom+e_gs*emissionen_strom+e_gas*200.8/1_000_000
        Wetter_jahr.append(weather_typ)
        Wert.append(round(e_gs,0))
        Einheit.append('Netzbezug [kWh]')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(e_gf,0))
        Einheit.append('Netzeinspeisung [kWh]')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(e_gas,0))
        Einheit.append('Gasbezug [kWh]')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(p_el_max,0))
        Einheit.append('maximaler Netzbezug [kW]')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(p_gas_max,0))
        Einheit.append('maximaler Gasbezug [kW]')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(volllaststunden,0))
        Einheit.append('Volllaststunden BHKW [h]')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(sjaz,2))
        Einheit.append('JAZ Wärmepumpe')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round((1703025.025+E_el_hp-e_gs)/(1703025.025+E_el_hp)*100,2))
        Einheit.append('Autarkiegrad [%]')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round((E_el_gesamterzeugung-e_gf)/E_el_gesamterzeugung*100,2))
        Einheit.append('Eigenverbrauchsanteil [%]')
        System.append('Augangssystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(emissionen,0))
        Einheit.append('Treibhausgasemissionen [t]')
        System.append('Augangssystem')
    data = {'Wert': Wert,
        'Einheit': Einheit,
        'Wetter': Wetter_jahr,
        'System': System}
    return data

@app.callback(
    Output('sys2_store', 'data'),
    State('pv-size-input2', 'value'),
    State('wka-dropdown2', 'value'),
    State('dropdown2', 'value'),
    State('wp-slider2', 'value'),
    State('vorlauftemperatur-input2', 'value'),
    State('effizienz-gastherme2', 'value'),
    State('wärmebedarfssenkung2', 'value'),
    Input('start_calc2', 'n_clicks')
    )

def calc_system2(pv_size, wka_dropdown, bhkw_regelung, wp_slider, vorlauftemperatur, effizienz_gastherme, wärmebedarfssenkung, n):
    if n==None:
        raise PreventUpdate
    min_cop=3
    Wetter_jahr=[]
    Wert=[]
    Einheit=[]
    System=[]
    df=pd.read_csv('src/Output_data/Eingangsdaten_simulation.csv', index_col=0)
    df.index=pd.date_range(start='01/01/2022', end='01/01/2023',freq='15min')[0:35040]
    for weather_typ in wetter_typ:
        if weather_typ.startswith('Jetzt'):
            wetter_time='2015'
            emissionen_strom=150/1_000_000
        else:
            wetter_time='2045'
            emissionen_strom=17/1_000_000
        if weather_typ.endswith('l'):
            weather_type='a_'
        elif weather_typ.endswith('t'):
            weather_type='w_'
        elif weather_typ.endswith('m'):
            weather_type='s_'
        weather=pd.read_csv('src/Input_data/Wetterdaten/TRY_1_'+weather_type+wetter_time+'_15min.csv', index_col=0)
        weather.index=pd.date_range(start='01/01/2022', end='01/01/2023',freq='15min')[0:35040]
        df['PV_Süd [W]']=weather['PV_Süd [W]']
        df['PV_West [W]']=weather['PV_West [W]']
        df['PV_Ost [W]']=weather['PV_Ost [W]']
        df['PV - Vorhanden [W]']=weather['PV - Vorhanden [W]']
        weather_day=weather.resample('D').mean()
        df['Temperatur Luft [°C]']=weather['temperature [degC]']
        for day in weather_day.index:
            df.loc[str(day.date()),'Tages-Durchschnittstemperatur [°C]']=df.loc[str(day.date()),'Temperatur Luft [°C]'].mean()
        df.loc[df['Tages-Durchschnittstemperatur [°C]']>12.1, 'Raumwämebedarf [W]']=0
        df.loc[df['Tages-Durchschnittstemperatur [°C]']<12.1, 'Raumwämebedarf [W]']=(20-df.loc[df['Tages-Durchschnittstemperatur [°C]']<12.1, 'Temperatur Luft [°C]'])*43739
        df['Raumwämebedarf [W]']=df['Raumwämebedarf [W]']+df['BHKW Strom [W]']*1.13
        df['Raumwämebedarf [W]']=df['Raumwämebedarf [W]']*(1-wärmebedarfssenkung/100)
        p_el_max, e_gf, e_gs, e_gas,p_gas_max, volllaststunden, sjaz, E_el_gesamterzeugung, E_el_hp=calculate_performance(df, wka_dropdown, bhkw_regelung, pv_size, wp_slider, effizienz_gastherme, vorlauftemperatur, min_cop)
        emissionen=-e_gf*emissionen_strom+e_gs*emissionen_strom+e_gas*200.8/1_000_000
        Wetter_jahr.append(weather_typ)
        Wert.append(round(e_gs,0))
        Einheit.append('Netzbezug [kWh]')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(e_gf,0))
        Einheit.append('Netzeinspeisung [kWh]')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(e_gas,0))
        Einheit.append('Gasbezug [kWh]')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(p_el_max,0))
        Einheit.append('maximaler Netzbezug [kW]')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(p_gas_max,0))
        Einheit.append('maximaler Gasbezug [kW]')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(volllaststunden,0))
        Einheit.append('Volllaststunden BHKW [h]')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(sjaz,2))
        Einheit.append('JAZ Wärmepumpe')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round((1703025.025+E_el_hp-e_gs)/(1703025.025+E_el_hp)*100,2))
        Einheit.append('Autarkiegrad [%]')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round((E_el_gesamterzeugung-e_gf)/E_el_gesamterzeugung*100,2))
        Einheit.append('Eigenverbrauchsanteil [%]')
        System.append('Zielsystem')
        Wetter_jahr.append(weather_typ)
        Wert.append(round(emissionen,0))
        Einheit.append('Treibhausgasemissionen [t]')
        System.append('Zielsystem')
    data = {'Wert': Wert,
        'Einheit': Einheit,
        'Wetter': Wetter_jahr,
        'System': System}
    return data

@app.callback(
    Output('performance', 'children'),
    Input('sys1_store', 'data'),
    Input('sys2_store', 'data'),
    )
def show_performance(data1, data2):
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    df=pd.concat([df1,df2])
    df.loc[df['Wetter']=='Jetzt Normal','Wetter']='Bis 2030 - normales Wetter'
    df.loc[df['Wetter']=='Jetzt Kalt','Wetter']='Bis 2030 - extremer Winter'
    df.loc[df['Wetter']=='Jetzt Warm','Wetter']='Bis 2030 - extremer Sommer'
    df.loc[df['Wetter']=='zukunft Normal','Wetter']='Ab 2030 - normales Wetter'
    df.loc[df['Wetter']=='zukunft Kalt','Wetter']='Ab 2030 - extremer Winter'
    df.loc[df['Wetter']=='zukunft Warm','Wetter']='Ab 2030 - extremer Sommer'
    fig=px.scatter(df, x='Wetter', y='Wert', color='Einheit', symbol='System')
    fig.update_traces(marker_size=10)
    fig.update_layout(scattermode="group")
    return dcc.Graph(figure=fig)

@app.callback(
    Output('cashflow', 'children'),
    Input('sys1_store', 'data'),
    Input('sys2_store', 'data'),
    Input('invest', 'value'),
    Input('strom_now', 'value'),
    Input('gas_now', 'value'),
    Input('strom_future', 'value'),
    Input('gas_future', 'value'),
    )

def calc_cashflow(data1, data2, invest, strom_now, gas_now, strom_future, gas_future):
    if (data1 is None) or (data2 is None):
        raise PreventUpdate
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    
    stromgesamt_now=(df1.loc[(df1['Einheit']=='Netzbezug [kWh]')&(df1['Wetter']=='Jetzt Normal'),'Wert'].values[0]*4+
    df1.loc[(df1['Einheit']=='Netzbezug [kWh]')&(df1['Wetter']=='Jetzt Kalt'),'Wert'].values[0]*1+
    df1.loc[(df1['Einheit']=='Netzbezug [kWh]')&(df1['Wetter']=='Jetzt Warm'),'Wert'].values[0]*1)*strom_now/600

    stromeinspeisunggesamt_now = (df1.loc[(df1['Einheit']=='Netzeinspeisung [kWh]')&(df1['Wetter']=='Jetzt Normal'),'Wert'].values[0]*4+
    df1.loc[(df1['Einheit']=='Netzeinspeisung [kWh]')&(df1['Wetter']=='Jetzt Kalt'),'Wert'].values[0]*1+
    df1.loc[(df1['Einheit']=='Netzeinspeisung [kWh]')&(df1['Wetter']=='Jetzt Warm'),'Wert'].values[0]*1)*0.062/6

    gasgesamt_now = (df1.loc[(df1['Einheit']=='Gasbezug [kWh]')&(df1['Wetter']=='Jetzt Normal'),'Wert'].values[0]*4+
    df1.loc[(df1['Einheit']=='Gasbezug [kWh]')&(df1['Wetter']=='Jetzt Kalt'),'Wert'].values[0]*1+
    df1.loc[(df1['Einheit']=='Gasbezug [kWh]')&(df1['Wetter']=='Jetzt Warm'),'Wert'].values[0]*1)*gas_now/600

    stromgesamt_future=(df1.loc[(df1['Einheit']=='Netzbezug [kWh]')&(df1['Wetter']=='zukunft Normal'),'Wert'].values[0]*8+
    df1.loc[(df1['Einheit']=='Netzbezug [kWh]')&(df1['Wetter']=='zukunft Kalt'),'Wert'].values[0]*3+
    df1.loc[(df1['Einheit']=='Netzbezug [kWh]')&(df1['Wetter']=='zukunft Warm'),'Wert'].values[0]*3)*strom_future/1400

    stromeinspeisunggesamt_future = (df1.loc[(df1['Einheit']=='Netzeinspeisung [kWh]')&(df1['Wetter']=='zukunft Normal'),'Wert'].values[0]*8+
    df1.loc[(df1['Einheit']=='Netzeinspeisung [kWh]')&(df1['Wetter']=='zukunft Kalt'),'Wert'].values[0]*3+
    df1.loc[(df1['Einheit']=='Netzeinspeisung [kWh]')&(df1['Wetter']=='zukunft Warm'),'Wert'].values[0]*3)*0.062/14

    gasgesamt_future = (df1.loc[(df1['Einheit']=='Gasbezug [kWh]')&(df1['Wetter']=='zukunft Normal'),'Wert'].values[0]*8+
    df1.loc[(df1['Einheit']=='Gasbezug [kWh]')&(df1['Wetter']=='zukunft Kalt'),'Wert'].values[0]*3+
    df1.loc[(df1['Einheit']=='Gasbezug [kWh]')&(df1['Wetter']=='zukunft Warm'),'Wert'].values[0]*3)*gas_future/1400

    energiekosten_ausgang=[(stromgesamt_now-stromeinspeisunggesamt_now+gasgesamt_now)]*6+[(stromgesamt_future-stromeinspeisunggesamt_future+gasgesamt_future)]*14

    stromgesamt_now=(df2.loc[(df2['Einheit']=='Netzbezug [kWh]')&(df2['Wetter']=='Jetzt Normal'),'Wert'].values[0]*4+
    df2.loc[(df2['Einheit']=='Netzbezug [kWh]')&(df2['Wetter']=='Jetzt Kalt'),'Wert'].values[0]*1+
    df2.loc[(df2['Einheit']=='Netzbezug [kWh]')&(df2['Wetter']=='Jetzt Warm'),'Wert'].values[0]*1)*strom_now/600

    stromeinspeisunggesamt_now = (df2.loc[(df2['Einheit']=='Netzeinspeisung [kWh]')&(df2['Wetter']=='Jetzt Normal'),'Wert'].values[0]*4+
    df2.loc[(df2['Einheit']=='Netzeinspeisung [kWh]')&(df2['Wetter']=='Jetzt Kalt'),'Wert'].values[0]*1+
    df2.loc[(df2['Einheit']=='Netzeinspeisung [kWh]')&(df2['Wetter']=='Jetzt Warm'),'Wert'].values[0]*1)*0.062/6

    gasgesamt_now = (df2.loc[(df2['Einheit']=='Gasbezug [kWh]')&(df2['Wetter']=='Jetzt Normal'),'Wert'].values[0]*4+
    df2.loc[(df2['Einheit']=='Gasbezug [kWh]')&(df2['Wetter']=='Jetzt Kalt'),'Wert'].values[0]*1+
    df2.loc[(df2['Einheit']=='Gasbezug [kWh]')&(df2['Wetter']=='Jetzt Warm'),'Wert'].values[0]*1)*gas_now/600

    stromgesamt_future=(df2.loc[(df2['Einheit']=='Netzbezug [kWh]')&(df2['Wetter']=='zukunft Normal'),'Wert'].values[0]*8+
    df2.loc[(df2['Einheit']=='Netzbezug [kWh]')&(df2['Wetter']=='zukunft Kalt'),'Wert'].values[0]*3+
    df2.loc[(df2['Einheit']=='Netzbezug [kWh]')&(df2['Wetter']=='zukunft Warm'),'Wert'].values[0]*3)*strom_future/1400

    stromeinspeisunggesamt_future = (df2.loc[(df2['Einheit']=='Netzeinspeisung [kWh]')&(df2['Wetter']=='zukunft Normal'),'Wert'].values[0]*8+
    df2.loc[(df2['Einheit']=='Netzeinspeisung [kWh]')&(df2['Wetter']=='zukunft Kalt'),'Wert'].values[0]*3+
    df2.loc[(df2['Einheit']=='Netzeinspeisung [kWh]')&(df2['Wetter']=='zukunft Warm'),'Wert'].values[0]*3)*0.062/14

    gasgesamt_future = (df2.loc[(df2['Einheit']=='Gasbezug [kWh]')&(df2['Wetter']=='zukunft Normal'),'Wert'].values[0]*8+
    df2.loc[(df2['Einheit']=='Gasbezug [kWh]')&(df2['Wetter']=='zukunft Kalt'),'Wert'].values[0]*3+
    df2.loc[(df2['Einheit']=='Gasbezug [kWh]')&(df2['Wetter']=='zukunft Warm'),'Wert'].values[0]*3)*gas_future/1400
    
    energiekosten_zielsystem=[(stromgesamt_now-stromeinspeisunggesamt_now+gasgesamt_now)]*6+[(stromgesamt_future-stromeinspeisunggesamt_future+gasgesamt_future)]*14
    df=pd.DataFrame()
    df['Energiekosten Ausgangssystem']=energiekosten_ausgang
    df['Energiekosten Zielsystem']=energiekosten_zielsystem
    df['Cashflow']=df['Energiekosten Ausgangssystem']-df['Energiekosten Zielsystem']
    df.index=range(2025,2045,1)
    fig=px.line(df)
    df.loc[df.index.values==2025,'Cashflow']=df.loc[df.index.values==2025,'Cashflow']-invest
    NPV = npf.npv(0.03, df['Cashflow'].values)
    IRR = npf.irr(df['Cashflow'].values)
    fig.update_layout(title='Die Investition hat einen Kapitalwert in Höhe von ' + str(int(round(NPV,0)))+ ' € und eine internen Zinsfuß in Höhe von '+ str(round(IRR*100,1))+ ' %.',
                    xaxis_title='Jahr',
                    yaxis_title='[€]')
    return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
