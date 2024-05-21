# -*- coding: utf-8 -*-
import pickle
import numpy as np
import pandas as pd
import pathlib
import yaml
import json
import plotly.express as px
import plotly.subplots as sp
import plotly.io as pio
pio.renderers.default = 'browser'
pd.options.plotting.backend = "plotly"

from emhass.retrieve_hass import RetrieveHass
from emhass.optimization import Optimization
from emhass.forecast import Forecast
from emhass.utils import get_root, get_yaml_parse, get_days_list, get_logger, treat_runtimeparams

# the root folder
root = str(get_root(__file__, num_parent=2))
emhass_conf = {}
emhass_conf['config_path'] = pathlib.Path(root) / 'config_emhass.yaml'
emhass_conf['data_path'] = pathlib.Path(root) / 'data/'
emhass_conf['root_path'] = pathlib.Path(root)

# create logger
logger, ch = get_logger(__name__, emhass_conf, save_to_file=False)

if __name__ == '__main__':
    get_data_from_file = True
    params = None
    show_figures = True
    template = 'presentation'
    
    with open(emhass_conf['config_path'], 'r') as file:
        params = yaml.load(file, Loader=yaml.FullLoader)
    params.update({
        'params_secrets': {
            'hass_url': 'http://supervisor/core/api',
            'long_lived_token': '${SUPERVISOR_TOKEN}',
            'time_zone': 'Europe/Paris',
            'lat': 45.83,
            'lon': 6.86,
            'alt': 4807.8
        }
        })
    runtimeparams = {
        'pv_power_forecast':[531, 2166, 2983, 3287, 3795, 4127, 4280, 4411, 4382, 4288, 4160, 3898, 3511, 2969, 2413, 1848, 1247, 599, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 526],
        'load_power_forecast':[1794, 368, 61, 460, 107, 819, 496, 492, 400, 739, 789, 1148, 844, 851, 896, 646, 904, 806, 1163, 1705, 2057, 2280, 1979, 1110, 1091, 953, 875, 653, 865, 1488, 307, 199, 189, 232, 199, 178, 212, 186, 150, 111, 167,1794, 368, 61, 460, 107, 819, 496],
        'load_cost_forecast':[0.32, 0.21, 0.19, 0.25, 0.22, 0.21, 0.22, 0.21, 0.12, 0.21, 0.17, 0.12, 0.41, 0.41, 0.42, 0.44, 0.58, 0.7, 0.87, 1.19, 1.19, 0.87, 0.92, 0.87, 0.44, 0.37, 0.41, 0.4, 0.45, 0.39, 0.38, 0.35, 0.38, 0.33, 0.38, 0.28, 0.27, 0.22, 0.22, 0.22,0.32, 0.21, 0.19, 0.25, 0.22, 0.21, 0.22, 0.21],
        'prod_price_forecast':[0.2, 0.1, 0.09, 0.14, 0.1, 0.09, 0.1, 0.09, 0.01, 0.09, 0.05, 0.01, 0.33, 0.33, 0.33, 0.35, 0.48, 0.58, 0.74, 1.04, 1.04, 0.74, 0.79, 0.74, 0.32, 0.26, 0.29, 0.28, 0.33, 0.27, 0.27, 0.23, 0.26, 0.21, 0.26, 0.17, 0.17, 0.12, 0.12, 0.12,0.2, 0.1, 0.09, 0.14, 0.1, 0.09, 0.1, 0.09],
    }
    runtimeparams_json = json.dumps(runtimeparams)
    params['passed_data'] = runtimeparams
    params_json = json.dumps(params)
    retrieve_hass_conf, optim_conf, plant_conf = get_yaml_parse(
        emhass_conf, use_secrets=False, params=params_json)
    set_type = "dayahead-optim"
    params, retrieve_hass_conf, optim_conf, plant_conf = treat_runtimeparams(
        runtimeparams_json, params_json, retrieve_hass_conf, 
        optim_conf, plant_conf, set_type, logger)
    rh = RetrieveHass(
        retrieve_hass_conf['hass_url'], retrieve_hass_conf['long_lived_token'], 
        retrieve_hass_conf['freq'], retrieve_hass_conf['time_zone'],
        params, emhass_conf, logger)
    if get_data_from_file:
        with open((emhass_conf['data_path'] / 'test_df_final.pkl'), 'rb') as inp:
            rh.df_final, days_list, var_list = pickle.load(inp)
        retrieve_hass_conf['var_load'] = str(var_list[0])
        retrieve_hass_conf['var_PV'] = str(var_list[1])
        retrieve_hass_conf['var_interp'] = [retrieve_hass_conf['var_PV'], retrieve_hass_conf['var_load']]
        retrieve_hass_conf['var_replace_zero'] = [retrieve_hass_conf['var_PV']]
    else:
        days_list = get_days_list(retrieve_hass_conf['days_to_retrieve'])
        var_list = [retrieve_hass_conf['var_load'], retrieve_hass_conf['var_PV']]
        rh.get_data(days_list, var_list, minimal_response=False, significant_changes_only=False)
    rh.prepare_data(
        retrieve_hass_conf['var_load'], load_negative = retrieve_hass_conf['load_negative'],
        set_zero_min = retrieve_hass_conf['set_zero_min'], 
        var_replace_zero = retrieve_hass_conf['var_replace_zero'], 
        var_interp = retrieve_hass_conf['var_interp'])
    df_input_data = rh.df_final.copy()
    fcst = Forecast(
        retrieve_hass_conf, optim_conf, plant_conf, 
        params_json, emhass_conf, logger, get_data_from_file=True)

    P_PV_forecast = fcst.get_weather_forecast(method='list')
    df_input_data.index = P_PV_forecast.index
    df_input_data.index.freq = rh.df_final.index.freq
    P_load_forecast = fcst.get_load_forecast(method='list')
    df_input_data = pd.concat([P_PV_forecast, P_load_forecast], axis=1)
    df_input_data.columns = ['P_PV_forecast', 'P_load_forecast']

    df_input_data = fcst.get_load_cost_forecast(df_input_data, method='list')
    df_input_data = fcst.get_prod_price_forecast(df_input_data, method='list')
    # Set special debug cases
    optim_conf.update({'treat_def_as_semi_cont': [True, True]})
    optim_conf.update({'set_def_constant': [False, False]})
    # optim_conf.update({'P_deferrable_nom': [[500.0, 1000.0, 1000.0, 500.0], 750.0]})
    
    optim_conf.update({'set_use_battery': True})
    optim_conf.update({'set_nocharge_from_grid': False})
    optim_conf.update({'set_battery_dynamic': True})
    optim_conf.update({'set_nodischarge_to_grid': True})
    
    optim_conf.update({'inverter_is_hybrid': True})

    df_input_data.loc[df_input_data.index[25:30],'unit_prod_price'] = -0.07
    df_input_data['P_PV_forecast'] = df_input_data['P_PV_forecast']*2
    P_PV_forecast = P_PV_forecast*2
    
    costfun = 'profit'
    opt = Optimization(retrieve_hass_conf, optim_conf, plant_conf, 
                       fcst.var_load_cost, fcst.var_prod_price,  
                       costfun, emhass_conf, logger)
    opt_res_dayahead = opt.perform_dayahead_forecast_optim(
        df_input_data, P_PV_forecast, P_load_forecast)
    
    # Let's plot the input data
    fig_inputs_dah = df_input_data.plot()
    fig_inputs_dah.layout.template = template
    fig_inputs_dah.update_yaxes(title_text = "Powers (W) and Costs(EUR)")
    fig_inputs_dah.update_xaxes(title_text = "Time")
    if show_figures:
        fig_inputs_dah.show()
    
    vars_to_plot = ['P_deferrable0', 'P_deferrable1','P_grid', 'P_PV', 'P_PV_curtailment']
    if optim_conf['inverter_is_hybrid']:
        vars_to_plot = vars_to_plot + ['P_hybrid_inverter']
    if optim_conf['set_use_battery']:
        vars_to_plot = vars_to_plot + ['P_batt']
    fig_res_dah = opt_res_dayahead[vars_to_plot].plot() # 'P_def_start_0', 'P_def_start_1', 'P_def_bin2_0', 'P_def_bin2_1'
    fig_res_dah.layout.template = template
    fig_res_dah.update_yaxes(title_text = "Powers (W)")
    fig_res_dah.update_xaxes(title_text = "Time")
    if show_figures:
        fig_res_dah.show()
    
    print("System with: PV, two deferrable loads, dayahead optimization, profit >> total cost function sum: "+\
        str(opt_res_dayahead['cost_profit'].sum())+", Status: "+opt_res_dayahead['optim_status'].unique().item())
    