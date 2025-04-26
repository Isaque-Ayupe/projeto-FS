from flask import Flask 
import models

app = Flask(__name__)
#CONFIGURA A ROTA DE ONDE O DB ESTA
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dados.db"
models.init_app(app)

from views import *

#APP FUNCIONA
if __name__ == "__main__":
    with app.app_context():
        models.create_all()
    app.run(debug=True)

