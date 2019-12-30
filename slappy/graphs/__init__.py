import dash_core_components as dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

from slappy.baseprobability import BaseProbertilites
from slappy.fast5 import Fast5
from dash.exceptions import PreventUpdate
import dash_html_components as html

from slappy.svg import get_nuc
import json
import itertools

colors = [
             ('rgba(0,255,0,0.5)', 'rgba(0,255,0,1)'),
             ('rgba(0,0,255,0.5)', 'rgba(0,0,255,1)'),
             ('rgba(255,255,0,0.5)', 'rgba(255,255,0,1)'),
             ('rgba(0,255,255,0.5)', 'rgba(0,255,255,1)'),
         ] * 2

basecolors = {
    'A': colors[0][0],
    'C': colors[1][0],
    'G': colors[2][0],
    'U': colors[3][0],
}
traceid = ['A', 'C', 'G', 'U'] * 2


def layout_graphs():
    return [
        dcc.Input(value='', type='hidden', id='load_info'),
        dcc.Tabs(id="tabs", value='tab-preview', children=[
            dcc.Tab(disabled=True),
            dcc.Tab(label='Preview', value='tab-preview', children=[
                dcc.Loading(
                    dcc.Graph(
                        id='graph_preview',
                    )
                )
            ], id='preview_head'),
            dcc.Tab(label='Raw based', value='tab-raw', children=[
                dcc.Loading(
                    dcc.Graph(
                        id='graph_raw',
                    )
                )
            ], id='raw_head'),
            dcc.Tab(label='Base based', value='tab-base', children=[
                dcc.Loading(
                    dcc.Graph(
                        id='graph_base',
                    )
                )
            ], id='base_head'),
            dcc.Tab(label='Base probability', value='tab-prob', children=[
                dcc.Loading(
                    [
                        dcc.Graph(
                            id='graph_prob',
                        ),
                    ]
                ),
                html.H2('Logo Options'),
                dcc.RadioItems(
                    options=[
                        {'label': 'Up next', 'value': 'up'},
                        {'label': 'At call', 'value': 'at'},
                        {'label': 'Around', 'value': 'ar'},
                    ],
                    value='up',
                    id="logo_options",
                    labelStyle={'display': 'inline-block', 'padding': 10}
                )
            ], id='prob_head'),
        
        ]),
        html.Div([
            html.H2('Graph Options'),
            dcc.Checklist(
                options=[
                    {'label': 'Stack Traces', 'value': 'trace_stack'},
                    {'label': 'Normalize to 1', 'value': 'normalize'},
                ],
                value=[],
                id="graph_options",
                labelStyle={'display': 'inline-block', 'padding': 10}
            )
        ],
            id='hide_options'
        ),
        html.Embed(src='/logo.svg',
                   style={'maxWidth': '20%', 'maxHeight': '60px', 'position': 'absolute', 'left': 0, 'top': 0},
                   type='image/svg+xml'),
    ]


def fetch_read(j_value):
    data = {'raw': None, 'base_positions': None, 'seq': None, 'traces': None, 'error': False, 'moves': None,
            'start': None, 'steps': None, 'rna': False}
    try:
        path, read_name, basecall_group = json.loads(j_value)
        fast5_file = Fast5(path)
        read = fast5_file[read_name]
        data['raw'] = read.get_raw_g0()[::-1]
        data['seq'] = read.get_rev_seq(basecall_group) + '-'
        if 'u' in data['seq'].lower():
            data['rna'] = True
        data['traces'] = read.get_traces(basecall_group)[::-1]
        data['moves'] = read.get_moves(basecall_group)[::-1]
        data['start'] = len(data['raw']) - read.get_start(basecall_group)
        data['steps'] = read.get_step(basecall_group)
        data['base_positions'] = [data['start'] % data['steps'],
                                  *[len(data['raw']) - x for x in reversed(read.get_basepositions(basecall_group))]]
    except KeyError:
        data['error'] = True
    
    return data


def graph_callbacks(app):
    @app.callback(
        [Output('load_info', 'value'), Output('tabs', 'value')],
        [Input('reads', 'active_cell'), Input('basecalls', 'value')],
        [State('hidden_path', 'value'), ]
    )
    def generate_load_info(read_name_list, basecall_group, path):
        if path == '' or read_name_list is None:
            raise PreventUpdate
        read_name = read_name_list['row_id']
        value = [path, read_name, basecall_group]
        j_value = json.dumps(value)
        # fetch_read(path, read_name, basecall_group)
        return j_value, 'tab-preview'
    
    @app.callback(
        Output('graph_preview', 'figure'),
        [Input('load_info', 'value')],
        []
    )
    def generate_preview_graph(j_value):
        if j_value == '':
            raise PreventUpdate
        data = fetch_read(j_value)
        raw = data['raw']
        
        fig = go.Figure()
        gernerate_base_legend(fig)
        
        fig.add_trace(generate_raw(raw, [*range(len(raw))]))
        if data['error']:
            fig.add_trace(create_error_trace(raw))
        else:
            max_raw = max(raw)
            shapes = generate_base_shapes(data['base_positions'], max_raw, data['seq'])
            fig.update_layout(shapes=shapes)
        fig["layout"]["yaxis"]["fixedrange"] = True
        return fig
    
    @app.callback(
        Output('graph_raw', 'figure'),
        [Input('load_info', 'value'), Input('graph_options', 'value')],
        []
    )
    def generate_raw_graph(j_value, options):
        if j_value == '':
            raise PreventUpdate
        data = fetch_read(j_value)
        raw = data['raw']
        
        number_of_base_values = 5
        trace_stack = False
        if 'trace_stack' in options:
            trace_stack = True
        normalize = False
        if 'normalize' in options:
            normalize = True
        
        fig = go.Figure()
        if data['error']:
            fig.add_trace(create_error_trace(raw))
        else:
            base_positions = data['base_positions']
            seq = data['seq']
            traces = data['traces']
            start = data['start']
            steps = data['steps']
            
            max_raw = max(raw)
            
            if normalize:
                base_y_values = [*[1 / x for x in range(1, number_of_base_values)], 0]
                raw = [raw_value / max_raw for raw_value in raw]
            else:
                base_y_values = [*[max_raw / x for x in range(1, number_of_base_values)], 0]
            
            gernerate_base_legend(fig)
            cor = start % steps
            x = [*range(cor, steps * len(traces) + cor + 1, steps)]
            for i in (0, 4, 1, 5, 2, 6, 3, 7):
                if normalize:
                    y = [*[float(y_value[i]) / 255 for y_value in traces], 0]
                else:
                    y = [*[float(y_value[i]) / 255 * max_raw for y_value in traces], 0]
                fig.add_trace(generate_traces(i, x, y, trace_stack))
            fig.add_trace(generate_raw(raw, [*range(len(raw))]))
            fig.add_trace(generate_base_legend())
            fig.add_traces(generate_bases(base_positions, base_y_values, seq, number_of_base_values))
            fig["layout"]["yaxis"]["fixedrange"] = True
        return fig
    
    @app.callback(
        Output('graph_base', 'figure'),
        [Input('load_info', 'value'), Input('graph_options', 'value'), ],
        []
    )
    def generate_base_graph(j_value, options):
        if j_value == '':
            raise PreventUpdate
        data = fetch_read(j_value)
        raw = data['raw']
        
        number_of_base_values = 5
        trace_stack = False
        if 'trace_stack' in options:
            trace_stack = True
        normalize = False
        if 'normalize' in options:
            normalize = True
        
        fig = go.Figure()
        if data['error']:
            fig.add_trace(create_error_trace(raw))
        else:
            base_positions = data['base_positions']
            seq = data['seq']
            traces = data['traces']
            steps = data['steps']
            
            max_raw = max(raw)
            
            if normalize:
                base_y_values = [*[1 / x for x in range(1, number_of_base_values)], 0]
                raw = [raw_value / max_raw for raw_value in raw]
            else:
                base_y_values = [*[max_raw / x for x in range(1, number_of_base_values)], 0]
            
            raw_x = generate_raw_x(base_positions, raw)
            trace_x = generate_trace_x(base_positions, steps)
            
            gernerate_base_legend(fig)
            for i in (0, 4, 1, 5, 2, 6, 3, 7):
                if normalize:
                    y = [*map(lambda y_value: float(y_value[i]) / 255, traces), 0]
                else:
                    y = [*map(lambda y_value: float(y_value[i]) / 255 * max_raw, traces), 0]
                fig.add_trace(generate_traces(i, trace_x, y, trace_stack))
            fig.add_trace(generate_raw(raw, raw_x))
            fig.add_trace(generate_base_legend())
            fig.add_traces(generate_bases([*range(len(base_positions))], base_y_values, seq, number_of_base_values))
            fig["layout"]["yaxis"]["fixedrange"] = True
        return fig
    
    @app.callback(
        Output('graph_prob', 'figure'),
        [Input('load_info', 'value'), Input('logo_options', 'value'), ],
        []
    )
    def generate_logo(j_value, option):
        if j_value == '':
            raise PreventUpdate
        data = fetch_read(j_value)
        
        fig = go.Figure()
        if data['error']:
            fig.add_trace(create_error_trace([0, 0, 0, 0, 0]))
        else:
            seq = data['seq']
            traces = data['traces']
            moves = [1, *data['moves'][:-1]]
            prop = BaseProbertilites(traces, moves)
            if option == 'up':
                prop.up_to_next_call()
            elif option == 'at':
                prop.at_call()
            elif option == 'ar':
                prop.around_call()
            else:
                raise KeyError()
            prop.make_logo()
            
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=[*range(len(seq))],
                    ticktext=[f'{x}<br>{i}' for i, x in enumerate(seq)],
                    showgrid=False,
                    tickangle=0,
                    zeroline=False,
                ),
                yaxis=dict(
                    gridcolor='grey',
                ),
                plot_bgcolor='white',
            )
            
            shapes = []
            for i, probabilities in enumerate(prop.order_by_probability()):
                prob_sum = 0
                for prob in probabilities:
                    shape = get_nuc(prob[0], i - 0.5, 1, prob_sum, prob[1], basecolors[prob[0]])
                    shapes.append(shape)
                    prob_sum += prob[1]
            fig.update_layout(shapes=shapes)
            
            fig.add_trace(go.Scatter(x=[0, len(prop)], y=[0, 2], mode='markers', showlegend=False))
            fig["layout"]["yaxis"]["fixedrange"] = True
        return fig
    
    @app.callback(
        Output('hide_options', 'style'),
        [Input('tabs', 'value'), ]
    )
    def hide_options(tab):
        if tab == 'tab-base' or tab == 'tab-raw':
            return {'display': 'block'}
        else:
            return {'display': 'none'}


def generate_raw_x(base_positions, raw):
    positions = [*base_positions, len(raw) + 1]
    return [*itertools.chain(
        *(
            itertools.islice(
                itertools.count(i - 1, 1 / (positions[i] - positions[i - 1])),
                positions[i] - positions[i - 1]
            )
            for i in range(1, len(positions)))
    )
            ]


def generate_trace_x(base_positions, steps):
    return [*itertools.chain(
        *(
            itertools.islice(
                itertools.count(i - 1, steps / (base_positions[i] - base_positions[i - 1])),
                (base_positions[i] - base_positions[i - 1]) // steps
            )
            for i in range(1, len(base_positions)))
    ),
            len(base_positions) - 1
            ]


def gernerate_base_legend(fig):
    for b in ['U', 'G', 'C', 'A']:
        fig.add_trace(go.Scatter(x=[0, 0], y=[0, 0], mode='lines', showlegend=True,
                                 line=dict(color=basecolors[b]), name=b, legendgroup=b
                                 ))


def generate_base_shapes(base_positions, max_raw, seq):
    shapes = []
    for i, x in enumerate(base_positions[:-1]):
        shape = go.layout.Shape(
            type="rect",
            x0=x,
            y0=0,
            x1=base_positions[i + 1],
            y1=max_raw,
            line=dict(
                width=0,
            ),
            fillcolor=basecolors[seq[i]],
        )
        shapes.append(shape)
    return shapes


def create_error_trace(raw):
    return go.Scatter(
        x=[0, len(raw) / 2, len(raw)],
        y=[0, 0, 0],
        mode="lines+text",
        name="Error",
        text=["", "Guppy data is needed", ""],
        textposition="top center",
        textfont=dict(
            family="sans serif",
            size=40,
            color="red"
        ),
        line=dict(width=0),
    
    )


def generate_raw(raw, raw_to_base):
    return go.Scatter(x=raw_to_base, y=raw, line=dict(color='black'), name='Raw')


def generate_base_legend():
    return go.Scatter(x=[0, 0], y=[0, 0], mode='lines', showlegend=True,
                      line=dict(color='red'), name='Moves/Bases',
                      legendgroup="bases"
                      )


def generate_bases(base_positions, base_y_values, seq, number_per_base):
    scatter_list = []
    for i in range(0, len(base_positions)):
        scatter_list.append(
            go.Scatter(x=[base_positions[i]] * (number_per_base + 1), y=base_y_values, mode='lines+text',
                       showlegend=False,
                       hovertext=[f'{seq[i]}<br>{i}'] * number_per_base, hoverinfo="text",
                       line=dict(color='red'),
                       legendgroup="bases",
                       text=[seq[i], *[''] * (number_per_base - 1)],
                       textposition="top center",
                       textfont={'color': 'red'},
                       )
        
        )
    return scatter_list


def generate_traces(i, trace_to_raw, y, trace_stack):
    if trace_stack:
        typ = {'mode': 'lines', 'stackgroup': 'traces'}
    else:
        typ = {'fill': 'tozeroy', 'fillcolor': colors[i][0]}
    return go.Scatter(
        x=trace_to_raw, y=y,
        **typ,
        line=dict(color=colors[i][1]), name=traceid[i], legendgroup=traceid[i],
        showlegend=False,
    )
