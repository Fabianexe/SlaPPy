import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from slappy.fast5 import Fast5
from slappy.config import search_popovers, popovers
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
                    ), id='read_col',
                )
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Select(
                        options=[{'label': '000', 'value': '000'}
                                 ],
                        id='basecalls',
                        value='000',
                    
                    )
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(html.I(className='fas fa-question-circle',
                               style={'color': 'green', 'fontSize': 'x-large'},
                               id="help"), width="auto", align='end'),
                dbc.Col(
                    dbc.Button("Search Sequence", id="open_search", ),
                    width='auto', align='end'
                )
            ],
            justify='between',
        ),
    ]),
        dcc.Input(value='', type='hidden', id='javascript'),
        dcc.Input(value='', type='hidden', id='javascript_out'),
        html.Datalist([], id='list-suggested-inputs'),
        create_search_modal(),
        *[create_popover(**d) for d in popovers]
    
    ]


def create_search_modal():
    return dbc.Modal(
        [
            
            dbc.ModalHeader(
                dbc.Row([
                    dbc.Col(html.I(className='fas fa-question-circle',
                                   style={'color': 'green', 'fontSize': 'large'},
                                   id="help_search"), width="auto", align='start'),
                    dbc.Col(dbc.Input(id="search_input", placeholder="Search a Sequence", type="text")),
                    dbc.Col(dbc.Button("Search", id="search", className="ml-auto"), width="auto")
                ], no_gutters=True), tag='div', style={'width': '100%'}),
            
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
                id='search_body'
            ),
            dbc.ModalFooter(
                dbc.Row([
                    dbc.Col(dbc.Button("Close", id="close_search", className="ml-auto"), xs=2),
                    
                    dbc.Col(dbc.Button("Apply", id="run_search", className="ml-auto"), xs=2),
                ], justify="between", style={'width': '100%'})
            ),
            *[create_popover(**d) for d in search_popovers]
        
        ],
        id="search_modal",
        size="lg",
        backdrop='static',
        scrollable=True,
    )


def create_popover(content, target, position):
    return dbc.Popover(
        dbc.PopoverBody(content),
        id=f"{target}_popover", target=target, placement=position
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
        return False
    
    @app.callback(
        [Output(f"{d['target']}_popover", "is_open") for d in search_popovers] +
        [Output('close_search', 'disabled'), Output('run_search', 'disabled'), ],
        [Input("help_search", "n_clicks")],
        [State("help_search_popover", "is_open")],
    )
    def toggle_search_popover(n, is_open):
        value = False
        if n:
            value = not is_open
        
        return [value] * (len(search_popovers) + 2)

    @app.callback(
        [Output(f"{d['target']}_popover", "is_open") for d in popovers],
        [Input("help", "n_clicks")],
        [State("help_popover", "is_open")],
    )
    def toggle_search_popover(n, is_open):
        value = False
        if n:
            value = not is_open
        
        return [value] * len(popovers)
