import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from slappy.fast5 import Fast5

from os import scandir


def layout_menu():
    return [
        html.Div(
            [
                "Path:",
                dcc.Input(value='', type='text', id='path', list='list-suggested-inputs',
                          style={'width': '65%'}),
                html.Button('Open', id='open'),
                dcc.Input(value='', type='hidden', id='hidden_path'),
            ],
            style={'width': '100%', 'verticalAlign': 'middle'}
        ),
        # html.Button('Open', id='open'),
        # html.Br(),
        
        DataTable(
            id='reads',
            columns=[{"name": 'Read', "id": 'name'}],
            data=[],
            style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
            style_table={'overflowY': 'scroll'},
            fixed_rows={'headers': True},
            style_cell={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
                'backgroundColor': 'grey',
            },
            filter_action="native",
        ),
        dcc.Dropdown(
            options=[{'label': '000', 'value': '000'}
                     ],
            id='basecalls',
            clearable=False,
            value='000',
            style={'zIndex': '1000'}
        ),
        html.Datalist([], id='list-suggested-inputs'),
        html.Embed(src='/logo.svg', style={'width': '100%', 'verticalAlign': 'middle','position':'absolute','bottom':0}, type='image/svg+xml'),

    ]


def menu_callbacks(app):
    @app.callback(
        Output(component_id='list-suggested-inputs', component_property='children'),
        [Input(component_id='path', component_property='value')]
    )
    def content_path(path):
        if path != '' and not path.endswith('/'):
            raise PreventUpdate
        ret = []
        try:
            for filepath in scandir(path if path != '' else '.'):
                if filepath.is_dir():
                    ret.append(html.Option(value=path + filepath.name + '/'))
                else:
                    if filepath.name.endswith('.fast5'):
                        ret.append(html.Option(value=path + filepath.name))
        except FileNotFoundError:
            raise PreventUpdate
        return ret
    
    @app.callback(
        [Output('reads', 'data'), Output('hidden_path', 'value'), Output('basecalls', 'options')],
        [Input('open', 'n_clicks')],
        [State('path', 'value')]
    )
    def prepare_file(_, path):
        if path == '':
            raise PreventUpdate
        fast5_file = Fast5(path)
        
        return [{'name': x[5:], 'id': x} for x in iter(fast5_file)], path, \
               [{'label': x[0], 'value': x[1]} for x in fast5_file.get_basecall_groups()]
