from app import app

if __name__ == "__main__":
    app.run(debug = app.config.get('DEBUG', False), host=app.config.get('BIND_ADDRESS', 'localhost'), port=app.config.get('PORT', '9191'))