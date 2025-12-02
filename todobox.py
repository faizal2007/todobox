from app import app

if __name__ == "__main__":
    app.run(debug = app.config.get('DEBUG', False), host=app.config.get('BIND_ADDRESS', '127.0.0.1'), port=app.config.get('PORT', '9191'))