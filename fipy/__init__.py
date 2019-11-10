
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

