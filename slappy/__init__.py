"""The starting point to create the app. """

__version__ = '0.4'
"""The version of the package"""


def devide_page(menu_layout, content_layout, menu_size=20):
    """Generates the base layout of the app with left a menu and right the content.
    
    :param menu_layout: The layout of the menu.
    :type menu_layout: dash.development.base_component.Component.
    :param content_layout: The layout of the content.
    :type menu_layout: dash.development.base_component.Component.
    :param menu_size: The percentage of the page that is taken by the menu, defaults to  20.
    :type menu_size: int, optional.
    :return: The finished app layout.
    :rtype: menu_layout: class:'dash.development.base_component.Component'.
    """
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
                    'backgroundColor': 'grey'
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
    """Generates the ready to run app from sub components.
    
    :return: The app ready to start.
    :rtype: dash.Dash
    """
    import dash
    
    from slappy.menu import layout_menu, menu_callbacks
    from slappy.graphs import layout_graphs, graph_callbacks
    from slappy import devide_page
    from slappy.statics import setRouts
    import dash_bootstrap_components as dbc
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "/custom.css",
                                                    'https://use.fontawesome.com/releases/v5.12.0/css/all.css'])

    app.title = 'Slappy'
    setRouts(app)
    app.layout = devide_page(layout_menu(), layout_graphs())
    menu_callbacks(app)
    graph_callbacks(app)
    return app
