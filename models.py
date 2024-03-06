from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, nome, cognome, email, password, tipo, immagine_profilo):
        self.id = id
        self.nome = nome
        self.cognome = cognome        
        self.email = email
        self.password = password
        self.tipo = tipo
        self.immagine_profilo = immagine_profilo