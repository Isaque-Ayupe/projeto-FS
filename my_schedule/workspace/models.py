from flask_sqlalchemy import SQLALchemy
db = SQLALchemy
#CONFIGURA A ROTA DE ONDE O DB ESTA

db.init_app

class usuario(db.Models):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer,primary_key = True)
    nome = db.Column(db.Sring(40), nullable = False,unique = True)

