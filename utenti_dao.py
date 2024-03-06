import sqlite3

def getUtenteByID(id):
    query = 'SELECT * FROM utenti WHERE id = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result 

def getIdUtenteByEmail(email):
    query = 'SELECT id FROM utenti WHERE email = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def getUtenteByEmail(email):
    query = 'SELECT * FROM utenti WHERE email = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result  

def inserisciUtente(user):
    success = False
    query = 'INSERT INTO utenti (nome, cognome, email, password, tipo, immagine_profilo) VALUES (?,?,?,?,?,?)'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    try:
        cursor.execute(query, (user.get('nome'), user.get('cognome'), user.get('email'), user.get('password'), user.get('tipo'), user.get('immagine_profilo')))
        connection.commit()
        success = True

    except Exception as e:
        print('Error: ' + str(e))
        connection.rollback()

    cursor.close
    connection.close

    return success