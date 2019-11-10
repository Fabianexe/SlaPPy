"""Main function when running on DASHs build in webserver with debug."""
from slappy import generate_app


def main():
    """Running the app with build in websterver"""
    app = generate_app()
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
