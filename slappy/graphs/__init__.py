import dash_core_components as dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html

from dash_bio import SequenceViewer
import dash_bootstrap_components as dbc

from flask_caching import Cache

from slappy.baseprobability import BaseProbertilites
from slappy.fast5 import Fast5
from slappy.svg import get_nuc
from slappy.search import search
from slappy.modification import read_modifcations, create_modification_layout, insert_mods, \
    generate_modification_callbacks

import json
import itertools

use_scatter = go.Scatter


# use_scatter = go.Scattergl


def layout_graphs():
    return [
        dcc.Input(value='', type='hidden', id='load_info'),
        dcc.Input(value='', type='hidden', id='start_info'),
        dcc.Tabs(id="tabs", value='tab-preview', children=[
            dcc.Tab(disabled=True),
            dcc.Tab(label='Preview', value='tab-preview', children=[
                dcc.Loading(
                    dcc.Graph(
                        id='graph_preview',
                    )
                )
            ], id='preview_head'),
            dcc.Tab(label='Signal scale', value='tab-raw', children=[
                dcc.Loading(
                    dcc.Graph(
                        id='graph_raw',
                    )
                )
            ], id='raw_head'),
            dcc.Tab(label='Base scale', value='tab-base', children=[
                dcc.Loading(
                    dcc.Graph(
                        id='graph_base',
                    )
                )
            ], id='base_head'),
            dcc.Tab(label='Base probability', value='tab-prob', children=[
                html.P('A logo with more then 200 Bases is unreadeable. '
                       'Use the slider or search to determine the shown range.'),
                dcc.RangeSlider(
                    min=0,
                    max=200,
                    value=[0],
                    updatemode='drag',
                    id='logo_range'
                ),
                dcc.Input(id='range_from', value='0', disabled=True),
                ' to ',
                dcc.Input(id='range_to', value='200', disabled=True),
                dcc.Input(value='[0,200]', type='hidden', id='hidden_range'),
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
                        # {'label': 'Around', 'value': 'ar'},
                    ],
                    value='up',
                    id="logo_options",
                    labelStyle={'display': 'inline-block', 'padding': 10}
                )
            ], id='prob_head'),
            dcc.Tab(label='Sequence', value='tab-seq', children=[
                SequenceViewer(
                    id='mod_viewer',
                    charsPerLine=80,
                    badge=False,
                ),
            ], id='mod_head'),
        
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
        *create_modification_layout(),
        html.Embed(src='/logo.svg',
                   style={'maxWidth': '20%', 'maxHeight': '60px', 'position': 'absolute', 'left': 0, 'top': 0},
                   type='image/svg+xml'),
    ]


def graph_callbacks(app):
    cache = Cache()
    cache.init_app(app.server, config={"CACHE_TYPE": "simple"})
    
    @cache.memoize()
    def fetch_read(j_value):
        data = {'raw': None, 'base_positions': None, 'seq': None, 'traces': None, 'error': False, 'moves': None,
                'start': None, 'steps': None, 'rna': False, 'mod': False, }
        try:
            path, read_name, basecall_group = json.loads(j_value)
            fast5_file = Fast5(path)
            read = fast5_file[read_name]
            data['colors'] = [
                ('rgba(0,255,0,0.5)', 'rgba(0,255,0,1)'),
                ('rgba(0,0,255,0.5)', 'rgba(0,0,255,1)'),
                ('rgba(255,255,0,0.5)', 'rgba(255,255,0,1)'),
                ('rgba(0,255,255,0.5)', 'rgba(0,255,255,1)'),
                ('rgba(255,0,0,0.5)', 'rgba(255,0,0,1)'),
                ('rgba(255,0,255,0.5)', 'rgba(255,0,255,1)'),
            ]
            
            if 'u' in read.get_seq(basecall_group).lower():
                data['rna'] = True
                data['seq'] = read.get_rev_seq(basecall_group) + '-'
                data['raw'] = read.get_raw_g0()[::-1]
                data['bases'] = ['A', 'C', 'G', 'U']
                data['basecolors'] = {data['bases'][0]: data['colors'][0][0],
                                      data['bases'][1]: data['colors'][1][0],
                                      data['bases'][2]: data['colors'][2][0],
                                      data['bases'][3]: data['colors'][3][0],
                                      }
                data['traceorder'] = [
                    *itertools.chain(*[(j, j + len(data['bases'])) for j in range(len(data['bases']))])
                ]
                data['start'] = len(data['raw']) - read.get_start(basecall_group)
                data['steps'] = read.get_step(basecall_group)
                data['base_positions'] = [data['start'] % data['steps'],
                                          *[len(data['raw']) - x for x in
                                            reversed(read.get_basepositions(basecall_group))]]
                data['traces'] = read.get_traces(basecall_group)[::-1]
                data['moves'] = read.get_moves(basecall_group)[::-1]
                data['moves'] = [1, *data['moves'][:-1]]
            else:
                data['raw'] = read.get_raw_g0()
                data['seq'] = read.get_rev_seq(basecall_group)
                data['rna'] = False
                data['bases'] = ['A', 'C', 'G', 'T']
                data['basecolors'] = {data['bases'][0]: data['colors'][0][0],
                                      data['bases'][1]: data['colors'][1][0],
                                      data['bases'][2]: data['colors'][2][0],
                                      data['bases'][3]: data['colors'][3][0],
                                      }
                data['traceorder'] = [
                    *itertools.chain(*[(j, j + len(data['bases'])) for j in range(len(data['bases']))])
                ]
                data['start'] = read.get_start(basecall_group)
                data['steps'] = read.get_step(basecall_group)
                data['base_positions'] = read.get_basepositions(basecall_group)
                data['traces'] = read.get_traces(basecall_group)
                data['moves'] = read.get_moves(basecall_group)
            read_modifcations(data, read, basecall_group)
            data['mod'] = read.has_modification(basecall_group)
            if data['mod']:
                data['mod_names'] = read.get_modification_names(basecall_group)
                data['mod_data'] = read.get_modification(basecall_group)
        
        except KeyError:
            data['error'] = True
        
        return data
    
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
        fetch_read(j_value)
        return j_value, 'tab-preview'
    
    @app.callback(
        Output('start_info', 'value'),
        [Input('load_info', 'value')],
        []
    )
    def start_graphs(value):
        return value
    
    @app.callback(
        Output('graph_preview', 'figure'),
        [Input('start_info', 'value'), Input('mod_values', 'value'), ],
        []
    )
    def generate_preview_graph(j_value, mods):
        if j_value == '':
            raise PreventUpdate
        data = fetch_read(j_value)
        raw = data['raw']
        
        insert_mods(data, mods)
        
        fig = go.Figure()
        
        fig.add_trace(generate_raw(raw, [*range(len(raw))]))
        if data['error']:
            fig.add_trace(create_error_trace(raw))
        else:
            max_raw = max(raw)
            traces = generate_base_shapes(data['base_positions'], max_raw, data['seq'], data['basecolors'])
            fig.add_traces(traces)
        fig["layout"]["yaxis"]["fixedrange"] = True
        return fig
    
    @app.callback(
        Output('graph_raw', 'figure'),
        [Input('start_info', 'value'), Input('graph_options', 'value')],
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
            steps = data['steps']

            start = data['start']
            max_raw = max(raw)
            
            fig.update_layout({
                'yaxis': {'range': [0, 1 if normalize else max_raw], },
                'xaxis': {'range': [0, len(raw)], },
                'xaxis2': {
                    'tickvals': base_positions,
                    'ticktext': list(seq),
                    'range': [0, len(raw)],
                    "overlaying": 'x',
                    "matches": 'x',
                    "side": 'top',
                    'tickangle': 0,
                },
            })
            
            if normalize:
                base_y_values = [*[1 / x for x in range(1, number_of_base_values)], 0]
                raw = [raw_value / max_raw for raw_value in raw]
            else:
                base_y_values = [*[max_raw / x for x in range(1, number_of_base_values)], 0]
            
            gernerate_base_legend(fig, data['bases'], data['basecolors'])
            cor = start
            if data['rna']:
                cor %= steps
            x = [*range(cor, steps * len(traces) + cor + 1, steps)]
            for i in data['traceorder']:
                if normalize:
                    y = [*[float(y_value[i]) / 255 for y_value in traces], 0]
                else:
                    y = [*[float(y_value[i]) / 255 * max_raw for y_value in traces], 0]
                fig.add_trace(generate_traces(x, y, trace_stack, data['bases'][i % len(data['bases'])],
                                              data['colors'][i % len(data['bases'])]))
            fig.add_trace(generate_raw(raw, [*range(len(raw))]))
            generate_bases(fig, base_positions, base_y_values, seq, number_of_base_values)
            
            fig["layout"]["yaxis"]["fixedrange"] = True
        return fig
    
    @app.callback(
        Output('graph_base', 'figure'),
        [Input('start_info', 'value'), Input('graph_options', 'value'), ],
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
            
            fig.update_layout({
                'yaxis': {'range': [0, 1 if normalize else max_raw], },
                'xaxis': {'range': [-1, len(base_positions)], },
                'xaxis2': {
                    'tickvals': [*range(len(base_positions))],
                    'ticktext': list(seq),
                    'range': [-1, len(base_positions)],
                    "overlaying": 'x',
                    "matches": 'x',
                    "side": 'top',
                    'tickangle': 0,
                },
            })
            
            if normalize:
                base_y_values = [*[1 / x for x in range(1, number_of_base_values)], 0]
                raw = [raw_value / max_raw for raw_value in raw]
            else:
                base_y_values = [*[max_raw / x for x in range(1, number_of_base_values)], 0]
            
            if data['rna']:
                raw_x = generate_raw_x(base_positions, raw)
                trace_x = generate_trace_x(base_positions, steps)
            else:
                raw_x = generate_raw_x_dna(base_positions, raw)
                trace_x = generate_trace_x_dna(base_positions, steps, raw)
            
            gernerate_base_legend(fig, data['bases'], data['basecolors'])
            for i in data['traceorder']:
                if normalize:
                    y = [*map(lambda y_value: float(y_value[i]) / 255, traces), 0]
                else:
                    y = [*map(lambda y_value: float(y_value[i]) / 255 * max_raw, traces), 0]
                fig.add_trace(generate_traces(trace_x, y, trace_stack, data['bases'][i % len(data['bases'])],
                                              data['colors'][i % len(data['bases'])]))
            fig.add_trace(generate_raw(raw, raw_x))
            generate_bases(fig, [*range(len(base_positions))], base_y_values, seq, number_of_base_values)
            fig["layout"]["yaxis"]["fixedrange"] = True
        return fig
    
    @app.callback(
        Output('logo_range', 'max'),
        [Input('start_info', 'value')],
        []
    )
    def generate_logo_range(j_value):
        if j_value == '':
            raise PreventUpdate
        data = fetch_read(j_value)
        if data['base_positions']:
            return len(data['base_positions'])
        return 200
    
    @app.callback(
        Output('graph_prob', 'figure'),
        [Input('start_info', 'value'), Input('logo_options', 'value'),
         Input('range_from', 'value'), Input('range_to', 'value'), ],
        []
    )
    def generate_logo(j_value, option, f, t):
        if j_value == '':
            raise PreventUpdate
        data = fetch_read(j_value)
        
        fig = go.Figure()
        if data['error']:
            fig.add_trace(create_error_trace([0, 0, 0, 0, 0]))
        else:
            seq = data['seq']
            traces = data['traces']
            moves = data['moves']
            basecolors = data['basecolors']
            prop = BaseProbertilites(traces, moves, data['bases'])
            if option == 'up':
                prop.up_to_next_call(f)
            elif option == 'at':
                prop.at_call(f)
            elif option == 'ar':
                prop.around_call(f)
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
                    shape = get_nuc(prob[0], f + i - 0.5, 1, prob_sum, prob[1], basecolors[prob[0]])
                    shapes.append(shape)
                    prob_sum += prob[1]
            fig.update_layout(shapes=shapes)
            
            fig.add_trace(use_scatter(x=[f, t], y=[0, 2], mode='markers', showlegend=False))
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
    
    @app.callback(
        Output('search_results', 'data'),
        [Input("search", "n_clicks")],
        [State('search_input', 'value'), State('load_info', 'value')],
    )
    def start_search(_, pattern, j_value):
        if j_value == '':
            raise PreventUpdate
        data = fetch_read(j_value)
        try:
            seq = data['seq']
            return list(search(pattern, seq, data['rna']))
        
        except KeyError:
            raise PreventUpdate
    
    @app.callback(
        [Output('javascript', 'value'), Output("open_search", "n_clicks")],
        [Input("run_search", "n_clicks")],
        [State('search_results', 'data'), State('search_results', 'selected_rows'), State('load_info', 'value'),
         State('tabs', 'value')],
    )
    def apply_search(_, search_data, ids, j_value, tab):
        if j_value == '' or ids is None:
            raise PreventUpdate
        select = search_data[ids[0]]
        data = fetch_read(j_value)
        return create_javascipt(tab, select, data['base_positions']), 0
    
    @app.callback(
        [Output('mod_viewer', 'sequence'), Output('mod_viewer', 'coverage'), Output('mod_viewer', 'legend'), ],
        [Input('start_info', 'value'), Input('mod_values', 'value'), ],
        [],
    )
    def generate_sequence(j_value, mods):
        if j_value == '':
            raise PreventUpdate
        
        data = fetch_read(j_value)
        
        insert_mods(data, mods)
        
        current_cov = []
        for i, c in enumerate(data['seq']):
            if c == '-':
                continue
            current_cov.append(
                {'start': i,
                 'end': i + 1,
                 'bgcolor': data['basecolors'][c],
                 }
            )
        
        legend = [{'name': c, 'color': data['basecolors'][c]} for c in data['basecolors'].keys()]
        
        return [data['seq'], current_cov, legend]
    
    app.clientside_callback(
        """
        function (value) {
            eval(value)
            return '';
        }
        """,
        Output('javascript_out', 'value'),
        [Input('javascript', 'value')]
    )
    
    app.clientside_callback(
        """
        function (value, max) {
            return [value[0], Math.min(value[0]+200, max)];
        }
        """,
        [Output('range_from', 'value'), Output('range_to', 'value')],
        [Input('logo_range', 'value')],
        [State('logo_range', 'max')]
    )
    
    generate_modification_callbacks(app, fetch_read)


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


def generate_raw_x_dna(base_positions, raw):
    positions = [0, *base_positions, len(raw) + 1]
    return [*itertools.chain(
        *(
            itertools.islice(
                itertools.count(i - 2, 1 / (positions[i] - positions[i - 1])),
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


def generate_trace_x_dna(base_positions, steps, raw):
    positions = [*base_positions, len(raw) + 1]
    return [*itertools.chain(
        *(
            itertools.islice(
                itertools.count(i - 1, steps / (positions[i] - positions[i - 1])),
                (positions[i] - positions[i - 1]) // steps
            )
            for i in range(1, len(positions)))
    ),
            ]


def gernerate_base_legend(fig, bases, basecolors):
    for b in bases:
        fig.add_trace(use_scatter(x=[0, 0], y=[0, 0], mode='lines', showlegend=True,
                                  line=dict(color=basecolors[b]), name=b, legendgroup=b
                                  ))


def generate_base_shapes(base_positions, max_raw, seq, basecolors):
    baselines = {}
    baselines_y = {}
    for i, x in enumerate(base_positions):
        c = seq[i]
        if c == '-':
            continue
        if c not in baselines:
            baselines[c] = []
            baselines_y[c] = []
        if i == 0 or seq[i - 1] != c:
            baselines[c].append(x)
            baselines_y[c].append(0)
            baselines[c].append(x)
            baselines_y[c].append(max_raw)
        if i < len(base_positions) - 1 and seq[i + 1] != c:
            baselines[c].append(base_positions[i + 1])
            baselines_y[c].append(max_raw)
            baselines[c].append(base_positions[i + 1])
            baselines_y[c].append(0)
    
    ret = []
    for x in baselines:
        scat = use_scatter(
            x=baselines[x], y=baselines_y[x], mode='lines',
            fill='tozeroy',
            showlegend=True,
            name=x,
            line=dict(color='rgba(0,0,0,0)'),
            fillcolor=basecolors[x],
            xaxis='x1',
            # stackgroup='bases'
        )
        ret.append(scat)
    
    return ret


def create_error_trace(raw):
    return use_scatter(
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
    return use_scatter(x=raw_to_base, y=raw, line=dict(color='black'), name='Raw')


def generate_bases(fig, base_positions, base_y_values, seq, number_per_base):
    x = ([*[base_positions[i]] * number_per_base, None] for i in range(0, len(base_positions)))
    x = [*itertools.chain(*x)]
    y = ([*base_y_values, None] for _ in range(0, len(base_positions)))
    y = [*itertools.chain(*y)]
    hover = ([*[f'{seq[i]}<br>{i}'] * number_per_base, None] for i in range(0, len(base_positions)))
    hover = [*itertools.chain(*hover)]
    fig.add_trace(
        use_scatter(
            x=x, y=y, mode='lines',
            showlegend=True,
            name='Moves/Bases',
            hovertext=hover, hoverinfo="text",
            line=dict(color='red'),
            xaxis='x2',
        
        )
    )


def generate_traces(trace_to_raw, y, trace_stack, traceid, color):
    if trace_stack:
        typ = {'mode': 'lines', 'stackgroup': 'traces'}
    else:
        typ = {'fill': 'tozeroy', 'fillcolor': color[0]}
    return use_scatter(
        x=trace_to_raw, y=y,
        **typ,
        line=dict(color=color[1]), name=traceid, legendgroup=traceid,
        showlegend=False,
    )


def create_javascipt(tab, select, base_positions):
    if tab == 'tab-raw' or tab == 'tab-preview':
        f = base_positions[int(select['from']) - 1]
        t = base_positions[int(select['to']) - 1]
        return f'Plotly.relayout(document.getElementsByClassName("js-plotly-plot")[0], {{"xaxis.range": [{f}, {t}]}})'
    elif tab == 'tab-base':
        f = select['from'] - 1
        t = select['to'] - 1
        return f'Plotly.relayout(document.getElementsByClassName("js-plotly-plot")[0], {{"xaxis.range": [{f}, {t}]}})'
    elif tab == 'tab-prob':
        f = select['from'] - 1.5
        t = select['to'] - 1.5
        return f'Plotly.relayout(document.getElementsByClassName("js-plotly-plot")[0], {{"xaxis.range": [{f}, {t}]}})'
    return ''
