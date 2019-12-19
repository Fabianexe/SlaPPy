import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from slappy.fast5 import Fast5
from slappy.search import search
import dash_bootstrap_components as dbc

from os import scandir


def layout_menu():
    return [dbc.Container([
        
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(value='', type='text', id='path', list='list-suggested-inputs'),
                    xs=8,
                    md=9,
                ),
                dbc.Col(
                    [
                        dbc.Button('Open', id='open'),
                        dcc.Input(value='', type='hidden', id='hidden_path'),
                    ],
                    xs=3
                ),
            
            ],
            justify='end',
            no_gutters=True,
        ),
        dbc.Row(
            [
                dbc.Col(
                    DataTable(
                        id='reads',
                        columns=[{"name": 'Read', "id": 'name'}],
                        data=[],
                        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
                        style_table={'overflowY': 'scroll', 'width': '100%'},
                        fixed_rows={'headers': True, },
                        style_cell={
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            'backgroundColor': 'grey',
                        },
                        filter_action="native",
                    ),
                )
            ],
        ),
        dbc.Row(
            [
                dbc.Select(
                    options=[{'label': '000', 'value': '000'}
                             ],
                    id='basecalls',
                    value='000',
                
                ),
            ],
        ),
        dbc.Row(
            dbc.Button("Search Sequence", id="open_search", ),
            justify='end',
        ),
    ]),
        html.Datalist([], id='list-suggested-inputs'),
        create_search_modal(),
    ]


def layout_menu_old():
    return [
        html.Div(
            [
                dbc.Input(value='', type='text', id='path', list='list-suggested-inputs',
                          style={'width': '70%', 'position': 'absolute', 'left': 0}),
                dbc.Button('Open', id='open', style={'position': 'absolute', 'right': 0}),
                dcc.Input(value='', type='hidden', id='hidden_path'),
            ],
            style={'width': '100%', 'verticalAlign': 'middle'}
        ),
        # html.Button('Open', id='open'),
        # html.Br(),
        html.Div(
            [
                DataTable(
                    id='reads',
                    columns=[{"name": 'Read', "id": 'name'}],
                    data=[],
                    style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
                    style_table={'overflowY': 'scroll'},
                    fixed_rows={'headers': True, },
                    style_cell={
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                        'backgroundColor': 'grey',
                    },
                    filter_action="native",
                ),
            ],
            style={'marginTop': '40px'}
        ),
        html.Div(
            [
                dbc.Select(
                    options=[{'label': '000', 'value': '000'}
                             ],
                    id='basecalls',
                    value='000',
                    style={'position': 'absolute', 'right': 0}
                ),
            ],
            style={'width': '100%', 'verticalAlign': 'middle', 'marginTop': '40px'}
        ),
        
        html.Datalist([], id='list-suggested-inputs'),
        create_search_modal(),
        dbc.Button("Search Sequence", id="open_search",
                   style={'position': 'absolute', 'right': 0, 'marginTop': '45px'}),
        html.Embed(src='/logo.svg',
                   style={'width': '100%', 'verticalAlign': 'middle', 'position': 'absolute', 'bottom': 0},
                   type='image/svg+xml'),
    
    ]


def create_search_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.Row([
                    dbc.Col(dbc.Input(id="search_input", placeholder="Search a Sequence", type="text"))
                    ,
                    dbc.Col(dbc.Button("Search", id="search", className="ml-auto"), width="auto")
                ]), tag='div', style={'width': '100%'}),
            dbc.ModalBody(
                DataTable(
                    id='search_results',
                    columns=[{"name": 'Seq', "id": 'seq'}, {"name": 'From', "id": 'from'}, {"name": 'To', "id": 'to'}],
                    data=[],
                    style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
                    style_table={'overflowY': 'scroll'},
                    fixed_rows={'headers': True, },
                    style_cell={
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                        'backgroundColor': 'grey',
                    },
                    row_selectable='single'
                ),
            
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close_search", className="ml-auto")
            ),
        ],
        id="search_modal",
        size="lg",
        backdrop='static',
        scrollable=True,
    )


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
    
    @app.callback(
        Output("search_modal", "is_open"),
        [Input("open_search", "n_clicks"), Input("close_search", "n_clicks")],
        [State("search_modal", "is_open")],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
    
    @app.callback(
        Output('search_results', 'data'),
        [Input("search", "n_clicks")],
        [State('search_input', 'value'), State('reads', 'active_cell'), State('basecalls', 'value'),
         State('hidden_path', 'value')],
    )
    def start_search(_, pattern, read_name_list, basecall_group, path):
        if path == '' or read_name_list is None:
            raise PreventUpdate
        read_name = read_name_list['row_id']
        fast5_file = Fast5(path)
        read = fast5_file[read_name]
        try:
            seq = read.get_seq(basecall_group)
            return list(search(pattern, seq))
        
        except:
            raise PreventUpdate
