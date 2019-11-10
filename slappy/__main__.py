from slappy import generate_app


def main():
    app = generate_app()
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
