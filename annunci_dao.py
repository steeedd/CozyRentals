import sqlite3

def inserisciAnnuncio(annuncio):
    success = False
    query = 'INSERT INTO annunci (titolo, indirizzo, tipo_casa, numero_locali, prezzo_mensile, descrizione, data_annuncio, arredata, disponibile, id_locatore) VALUES (?,?,?,?,?,?,?,?,?,?)'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    try:
        cursor.execute(query, (annuncio.get('titolo'), annuncio.get('indirizzo'), annuncio.get('tipo_casa'), annuncio.get('numero_locali'), annuncio.get('prezzo_mensile'), annuncio.get('descrizione'), annuncio.get('data_annuncio'), annuncio.get('arredata'), annuncio.get('disponibile'), annuncio.get('id_locatore')))
        connection.commit()
        success = True

    except Exception as e:
        print('Error: ' + str(e))
        connection.rollback()

    cursor.close
    connection.close

    return success

def getIdAnnuncio(annuncio):
    query = 'SELECT id FROM annunci WHERE titolo = ? and descrizione = ? and id_locatore = ? and data_annuncio = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (annuncio.get('titolo'),annuncio.get('descrizione'), annuncio.get('id_locatore'), annuncio.get('data_annuncio')))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result


def insertFotoAnnuncio(foto_annuncio):
    success = False
    query = 'INSERT INTO immagini_annuncio VALUES (?,?)'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    try:
        cursor.execute(query, (foto_annuncio.get('url_immagine'), foto_annuncio.get('id_annuncio')))
        connection.commit()
        success = True

    except Exception as e:
        print('Error: ' + str(e))
        connection.rollback()

    cursor.close
    connection.close

    return success

def getAnnunciLocatore(id_locatore):
    query = 'SELECT * FROM annunci WHERE id_locatore = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id_locatore,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def getAnnunciDisponibiliPrezzoDecrescente():
    query = 'SELECT * FROM annunci WHERE disponibile = ? ORDER BY prezzo_mensile DESC'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (1,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def getAnnunciDisponibiliLocaliCrescente():
    query = 'SELECT * FROM annunci WHERE disponibile = ? ORDER BY numero_locali ASC'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (1,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def getFotoAnnunci(id_annuncio):
    query = 'SELECT url_immagine FROM immagini_annuncio WHERE id_annuncio = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id_annuncio,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def getAnnuncioByID(id_annuncio):
    query = 'SELECT * FROM annunci, utenti WHERE annunci.id = ? and utenti.id = annunci.id_locatore'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id_annuncio,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def modificaAnnuncio(id_annuncio, annuncio_modificato):
    success = False
    query = 'UPDATE annunci SET titolo = ?, tipo_casa = ?, numero_locali = ?, prezzo_mensile = ?, descrizione = ?, arredata = ?, disponibile = ? WHERE annunci.id = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    try:
        cursor.execute(query, (annuncio_modificato.get('titolo'), annuncio_modificato.get('tipo_casa'), annuncio_modificato.get('numero_locali'), annuncio_modificato.get('prezzo_mensile'), annuncio_modificato.get('descrizione'), annuncio_modificato.get('arredata'), annuncio_modificato.get('disponibile'), id_annuncio))
        connection.commit()
        success = True

    except Exception as e:
        print('Error: ' + str(e))
        connection.rollback()

    cursor.close
    connection.close

    return success


def eliminaFotoAnnuncio(id_annuncio, url_foto):
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    success = False
    sql = 'DELETE FROM immagini_annuncio WHERE url_immagine = ? AND id_annuncio = ?'

    try:
        cursor.execute(
            sql, (url_foto, id_annuncio))
        connection.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        connection.rollback()

    cursor.close()
    connection.close()

    return success