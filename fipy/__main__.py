import dash

from fipy.menu import layout_menu, menu_callbacks
from fipy.graphs import layout_graphs, graph_callbacks
from fipy import devide_page


def main():
    app = dash.Dash(__name__)
    app.layout = devide_page(layout_menu(), layout_graphs())
    menu_callbacks(app)
    graph_callbacks(app)
    app.run_server(debug=False)


if __name__ == '__main__':
    main()
