import dash_html_components as html

search_popovers = [
    {'content': 'Show/Hide Search Help',
     'target': 'help_search',
     'position': 'left'
     },
    {'content': ['The searched subsqeuence in ', html.A('one Letter IUPAC nucleotide code', target="_blank",
                                                        href='https://www.bioinformatics.org/sms/iupac.html')],
     'target': 'search_input',
     'position': 'bottom'
     },
    {'content': 'Start search',
     'target': 'search',
     'position': 'right'
     },
    {'content': 'The results of the search. Mark a line at the beginning.',
     'target': 'search_body',
     'position': 'left'
     },
    {'content': 'Close the search without applying the result (close help first)',
     'target': 'close_search',
     'position': 'bottom'
     },
    {'content': 'Close the search and apply the result (close help first)',
     'target': 'run_search',
     'position': 'bottom'
     },
]

popovers = [
    {'content': ['Show/Hide', html.Br(), 'Help'],
     'target': 'help',
     'position': 'bottom'
     },
    {'content': ['Show a preview of the Raw', html.Br(), 'data with annotated Bases'],
     'target': 'preview_head',
     'position': 'bottom'
     },
    {'content': ['Show annotated Bases with', html.Br(), 'respect to raw data'],
     'target': 'raw_head',
     'position': 'bottom'
     },
    {'content': ['Show annotated Bases with', html.Br(), 'respect to the sequence'],
     'target': 'base_head',
     'position': 'bottom'
     },
    {'content': ['Show Sequence logo based on', html.Br(), 'the guppy traces'],
     'target': 'prob_head',
     'position': 'bottom'
     },
    {'content': ['Open the fast5 file'],
     'target': 'open',
     'position': 'right'
     },
    {'content': ['Select the read of the fast5 file'],
     'target': 'read_col',
     'position': 'right'
     },
    {'content': ['Select the basecall group', html.Br(), '(only guppy is supported)'],
     'target': 'basecalls',
     'position': 'right'
     },
    {'content': ['Search for a subsequence', html.Br(), 'in the given read'],
     'target': 'open_search',
     'position': 'bottom'
     },
]