from slappy.graphs import *


def fetch_read(j_value):
    data = {'raw': None, 'base_positions': None, 'seq': None, 'traces': None, 'error': False, 'moves': None,
            'start': None, 'steps': None, 'rna': False}
    try:
        path, read_name, basecall_group = json.loads(j_value)
        fast5_file = Fast5(path)
        read = fast5_file[read_name]
        data['colors'] = [
            ('rgba(0,255,0,0.5)', 'rgba(0,255,0,1)'),
            ('rgba(0,0,255,0.5)', 'rgba(0,0,255,1)'),
            ('rgba(255,255,0,0.5)', 'rgba(255,255,0,1)'),
            ('rgba(0,255,255,0.5)', 'rgba(0,255,255,1)'),
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
    
    except KeyError:
        data['error'] = True
    
    return data


def generate_raw_graph(j_value, options):
    if j_value == '':
        raise PreventUpdate
    data = fetch_read(j_value)
    raw = data['raw']
    
    number_of_base_values = 2
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
        # traces = data['traces']
        # start = data['start']
        # steps = data['steps']
        
        max_raw = max(raw)
        
        if normalize:
            base_y_values = [*[1 / x for x in range(1, number_of_base_values)], 0]
            # raw = [raw_value / max_raw for raw_value in raw]
        else:
            base_y_values = [*[max_raw / x for x in range(1, number_of_base_values)], 0]
        
        # gernerate_base_legend(fig, data['bases'], data['basecolors'])
        # cor = start
        # if data['rna']:
        #     cor %= steps
        # x = [*range(cor, steps * len(traces) + cor + 1, steps)]
        # for i in data['traceorder']:
        #     if normalize:
        #         y = [*[float(y_value[i]) / 255 for y_value in traces], 0]
        #     else:
        #         y = [*[float(y_value[i]) / 255 * max_raw for y_value in traces], 0]
        #     # fig.add_trace(generate_traces(x, y, trace_stack, data['bases'][i % len(data['bases'])],
        #     #                               data['colors'][i % len(data['bases'])]))
        # fig.add_trace(generate_raw(raw, [*range(len(raw))]))
        # fig.add_trace(generate_base_legend())
        fig.add_traces(generate_bases(base_positions, base_y_values, seq, number_of_base_values))
        fig["layout"]["yaxis"]["fixedrange"] = True
    return fig

j = '["../test.fast5", "read_0088a112-22c0-4afc-8275-e1b8e078d754", "001"]'

generate_raw_graph(j, [])