import dash_core_components as dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from slappy.fast5 import Fast5
from dash.exceptions import PreventUpdate


def layout_graphs():
    return [
                dcc.Tabs(id="tabs", value='tab-preview', children=[
                    dcc.Tab(label='Preview', value='tab-preview', children=[
                        dcc.Loading(
                            dcc.Graph(
                                id='graph_preview',
                            )
                        )
                    ]),
                    dcc.Tab(label='Raw based', value='tab-raw', children=[
                        dcc.Loading(
                            dcc.Graph(
                                id='graph_raw',
                            )
                        )
                    ]),
                    dcc.Tab(label='Base based', value='tab-base', children=[
                        dcc.Loading(
                            dcc.Graph(
                                id='graph_base',
                            )
                        )
                    ]),
                ])
            ]


def graph_callbacks(app):
    @app.callback(
        [Output('graph_preview', 'figure'), Output('tabs', 'value')],
        [Input('reads', 'active_cell'), Input('basecalls', 'value')],
        [State('hidden_path', 'value'), ]
    )
    def generate_preview_graph(read_name_list, basecall_group, path):
        if path == '' or read_name_list is None:
            raise PreventUpdate
        read_name = read_name_list['row_id']
        fast5_file = Fast5(path)
        read = fast5_file[read_name]
        raw = read.get_raw_g0()
        
        fig = go.Figure()
        gernerate_base_legend(fig)
        
        fig.add_trace(generate_raw(raw, list(range(len(raw)))))
        try:
            max_raw = max(raw)
            base_positions = read.get_basepositions(basecall_group)
            seq = read.get_seq(basecall_group)
            
            shapes = generate_base_shapes(base_positions, max_raw, len(raw), seq)
            fig.update_layout(shapes=shapes)
        except KeyError:
            fig.add_trace(create_error_trace(raw))
        
        return fig, 'tab-preview'
    
    @app.callback(
        [Output('graph_raw', 'figure'), Output('graph_base', 'figure')],
        [Input('graph_preview', 'figure'), Input('trace_stack', 'on'), ],
        [State('reads', 'active_cell'), State('basecalls', 'value'),
         State('hidden_path', 'value'), ]
    )
    def generate_other_graph(_, trace_stack, read_name_list, basecall_group, path):
        if path == '' or read_name_list is None:
            raise PreventUpdate
        read_name = read_name_list['row_id']
        fast5_file = Fast5(path)
        read = fast5_file[read_name]
        raw = read.get_raw_g0()
        number_of_base_values = 5
        
        figs = (go.Figure(), go.Figure())
        try:
            base_positions = read.get_basepositions(basecall_group)
            seq = read.get_seq(basecall_group)
            traces = read.get_traces(basecall_group)
            start = read.get_start(basecall_group)
            steps = read.get_step(basecall_group)
            max_raw = max(raw)
            base_y_values = [max_raw / x for x in range(1, number_of_base_values)] + [0]
            
            raw_x = generate_raw_x(base_positions, raw)
            trace_x = generate_trace_x(base_positions, raw, start, steps, traces)
            base_x = generate_base_x(base_positions, number_of_base_values)

            
            for graph in range(2):
                gernerate_base_legend(figs[graph])
                for i in (0, 4, 1, 5, 2, 6, 3, 7):
                    y = list(map(lambda y_value: float(y_value[i]) / 255 * max_raw, traces))
                    figs[graph].add_trace(generate_traces(i, trace_x[graph], y, trace_stack))
                figs[graph].add_trace(generate_raw(raw, raw_x[graph]))
                figs[graph].add_trace(generate_base_legend())
                for i in range(len(base_positions)):
                    figs[graph].add_trace(
                        generate_bases(i, base_y_values, seq, base_x[graph][i], number_of_base_values))
        except KeyError:
            for graph in range(2):
                figs[graph].add_trace(create_error_trace(raw))
        
        return figs


colors = [
             ('rgba(138,43,226,0.5)', 'rgba(138,43,226,1)'),
             ('rgba(0,128,0,0.5)', 'rgba(0,128,0,1)'),
             ('rgba(0,0,255,0.5)', 'rgba(0,0,255,1)'),
             ('rgba(255,192,203,0.5)', 'rgba(255,192,203,1)'),
         ] * 2

basecolors = {
    'A': colors[0][0],
    'C': colors[1][0],
    'G': colors[2][0],
    'U': colors[3][0],
}
traceid = ['A', 'C', 'G', 'U'] * 2


def generate_base_x(base_positions, number_of_base_values):
    return [[[x] * number_of_base_values for x in base_positions],
            [[i + 1] * number_of_base_values for i in range(len(base_positions))]
            ]


def generate_raw_x(base_positions, raw):
    last = 0
    raw_to_base = []
    raw_to_raw = []
    j = 0
    diff = base_positions[j]
    for i in range(len(raw)):
        if j < len(base_positions) and i == base_positions[j]:
            last = i
            j += 1
            if j < len(base_positions):
                diff = base_positions[j] - i
            else:
                diff = len(raw) - i
        
        val = (i - last) / diff + j
        raw_to_base.append(val)
        raw_to_raw.append(i)
    
    return raw_to_raw, raw_to_base


def generate_trace_x(base_positions, raw, start, steps, traces):
    trace_set = set(range(start, start + steps * len(traces), 10))
    last = 0
    trace_to_base = []
    trace_to_raw = []
    j = 0
    diff = base_positions[j]
    for i in range(len(raw)):
        if j < len(base_positions) and i == base_positions[j]:
            last = i
            j += 1
            if j < len(base_positions):
                diff = base_positions[j] - i
            else:
                diff = len(raw) - i
        
        val = (i - last) / diff + j
        if i in trace_set:
            trace_to_base.append(val)
            trace_to_raw.append(i)
    return trace_to_raw, trace_to_base


def generate_x_to_base_lists(base_positions, raw, start, steps, traces):
    trace_set = set(range(start, start + steps * len(traces), 10))
    last = 0
    raw_to_base = []
    trace_to_base = []
    j = 0
    diff = base_positions[j]
    for i in range(len(raw)):
        if j < len(base_positions) and i == base_positions[j]:
            last = i
            j += 1
            if j < len(base_positions):
                diff = base_positions[j] - i
            else:
                diff = len(raw) - i
        
        val = (i - last) / diff + j
        raw_to_base.append(val)
        if i in trace_set:
            trace_to_base.append(val)
    return raw_to_base, trace_to_base


def gernerate_base_legend(fig):
    for b in ['U', 'G', 'C', 'A']:
        fig.add_trace(go.Scatter(x=[0, 0], y=[0, 0], mode='lines', showlegend=True,
                                 line=dict(color=basecolors[b]), name=b, legendgroup=b
                                 ))


def generate_base_shapes(base_positions, max_raw, len_raw, seq):
    shapes = []
    for i, x in enumerate(base_positions):
        shape = go.layout.Shape(
            type="rect",
            x0=x,
            y0=0,
            x1=base_positions[i + 1] if i + 1 < len(base_positions) else len_raw,
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


def generate_bases(i, base_y_values, seq, x1, number_per_base):
    return go.Scatter(x=x1, y=base_y_values, mode='lines+text', showlegend=False,
                      hovertext=[seq[i] + '<br>' + str(i)] * number_per_base, hoverinfo="text", line=dict(color='red'),
                      legendgroup="bases",
                      text=[seq[i]] + [''] * (number_per_base - 1),
                      textposition="top center",
                      textfont=dict(
                          color='red'
                      ),
    
                      )


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