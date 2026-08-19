from app import create_app

app = create_app()
application = app  # WSGI alias for cloud web servers


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
