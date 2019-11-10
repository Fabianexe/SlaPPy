__version__ = '0.1'


def devide_page(menu_layout, content_layout, menu_size=20):
    import dash_html_components as html
    return html.Div(
        [
            html.Div(
                menu_layout,
                style={
                    'height': '100%',
                    'width': str(menu_size) + '%',
                    'position': 'fixed',
                    'top': 0,
                    'left': 0,
                    'background-color': 'grey'
                }
            ),
            html.Div(
                content_layout,
                style={
                    'height': '100%',
                    'width': str(100-menu_size) + '%',
                    'position': 'fixed',
                    'top': 0,
                    'right': 0,
                }
            ),
        ])


def generate_app():
    import dash
    
    from slappy.menu import layout_menu, menu_callbacks
    from slappy.graphs import layout_graphs, graph_callbacks
    from slappy import devide_page
    app = dash.Dash(__name__)
    app.title = 'Slappy'
    app.layout = devide_page(layout_menu(), layout_graphs())
    menu_callbacks(app)
    graph_callbacks(app)
    return app
