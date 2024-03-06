import sqlite3

def inserisciPrenotazione(prenotazione):
    success = False
    query = 'INSERT INTO prenotazioni (id_cliente, id_annuncio, tipo_visita, data_visita, fascia_oraria, stato_prenotazione) VALUES (?,?,?,?,?,?)'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    try:
        cursor.execute(query, (prenotazione.get('id_cliente'), prenotazione.get('id_annuncio'), prenotazione.get('tipo_visita'), prenotazione.get('data_visita'), prenotazione.get('fascia_oraria'), 'richiesta'))
        connection.commit()
        success = True

    except Exception as e:
        print('Error: ' + str(e))
        connection.rollback()

    cursor.close
    connection.close

    return success

def getPrenotazione(id_cliente, id_annuncio):
    query = 'SELECT * FROM prenotazioni WHERE id_cliente = ? and id_annuncio = ? and (stato_prenotazione = ? or stato_prenotazione = ?)'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id_cliente, id_annuncio, 'accettata', 'richiesta'))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def getFasceOrarieOccupate(data, id_annuncio):
    query = 'SELECT fascia_oraria FROM prenotazioni WHERE data_visita = ? and stato_prenotazione = ? and id_annuncio = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (data, 'accettata', id_annuncio))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def getRichiestePrenotazioniLocatore(id_locatore):
    query = 'SELECT * FROM prenotazioni, annunci, utenti WHERE annunci.id = prenotazioni.id_annuncio and prenotazioni.id_cliente = utenti.id and annunci.id_locatore = ? ORDER BY data_visita DESC'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id_locatore,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def getRichiestePrenotazioniLocatoreFiltro(id_locatore, stato_prenotazione):
    query = 'SELECT * FROM prenotazioni, annunci, utenti WHERE annunci.id = prenotazioni.id_annuncio and prenotazioni.id_cliente = utenti.id and annunci.id_locatore = ? and prenotazioni.stato_prenotazione = ? ORDER BY data_visita DESC'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id_locatore, stato_prenotazione))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def modificaStatoPrenotazioneAccettata(id_prenotazione):
    success = False
    query = 'UPDATE prenotazioni SET stato_prenotazione = ? WHERE id = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    try:
        cursor.execute(query, ('accettata',id_prenotazione))
        connection.commit()
        success = True

    except Exception as e:
        print('Error: ' + str(e))
        connection.rollback()

    cursor.close
    connection.close

    return success


def modificaStatoPrenotazioneRifiutata(id_prenotazione, motivazione_rifiuto):
    success = False
    query = 'UPDATE prenotazioni SET stato_prenotazione = ?, motivazione_rifiuto = ? WHERE id = ?'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    try:
        cursor.execute(query, ('rifiutata', motivazione_rifiuto, id_prenotazione))
        connection.commit()
        success = True

    except Exception as e:
        print('Error: ' + str(e))
        connection.rollback()

    cursor.close
    connection.close

    return success

def getRichiestePrenotazioniCliente(id_cliente):
    query = 'SELECT * FROM prenotazioni, annunci, utenti WHERE annunci.id = prenotazioni.id_annuncio and prenotazioni.id_cliente = utenti.id and prenotazioni.id_cliente = ? ORDER BY data_visita DESC'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id_cliente,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def getRichiestePrenotazioniClienteFiltro(id_cliente, stato_prenotazione):
    query = 'SELECT * FROM prenotazioni, annunci, utenti WHERE annunci.id = prenotazioni.id_annuncio and prenotazioni.id_cliente = utenti.id and prenotazioni.id_cliente = ? and prenotazioni.stato_prenotazione = ? ORDER BY data_visita DESC'
    connection = sqlite3.connect('db/cozy_rentals.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query, (id_cliente, stato_prenotazione))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result