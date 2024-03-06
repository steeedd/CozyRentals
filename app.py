# pip install flask
from flask import Flask, render_template, request, url_for, redirect, flash
# pip install flask_login
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# pip install werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
# pip install Pillow
from PIL import Image
from datetime import datetime, timedelta
import os
# os è un modulo in Python che fornisce un'interfaccia per interagire con il sistema operativo sottostante. 
# Esso offre funzioni che consentono di eseguire operazioni legate al sistema di file, manipolare percorsi, eseguire comandi del sistema operativo, gestire variabili di ambiente e altro.


from models import User
import utenti_dao, annunci_dao, prenotazioni_dao

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fkdwIO3KSoso2oi1393JDI2k2k1'

login_manager = LoginManager()
login_manager.init_app(app)

PROFILE_IMG_HEIGHT = 160
HOUSE_IMG_HEIGHT = 300


@app.route('/', methods = ['GET', 'POST'])
def home():
    ordinamento = request.form.get('ordinamento', 'prezzoDecrescente')
    if ordinamento == 'prezzoDecrescente':
        annunciDisponibili = annunci_dao.getAnnunciDisponibiliPrezzoDecrescente()

    elif ordinamento == 'localiCrescente':
        annunciDisponibili = annunci_dao.getAnnunciDisponibiliLocaliCrescente()

    else:
        return render_template('404.html', 404)

    lista_annunci = aggiungiFotoAgliAnnunci(annunciDisponibili)

    return render_template('home.html', annunci_disponibili = lista_annunci, ordinamento = ordinamento)

    

@app.route('/registrazione')
def iscriviti():
    return render_template('signup.html')

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    user_signup = request.form.to_dict()
    app.logger.debug(user_signup)
    if user_signup.get('nome') == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('iscriviti'))
    
    if user_signup.get('cognome') == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('iscriviti'))
    
    if user_signup.get('email') == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('iscriviti'))
    
    if user_signup.get('password') == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('iscriviti'))
    
    if len(user_signup.get('nome')) < 2:
        flash('Il nome inserito non è valido')
        return redirect(url_for('iscriviti'))
    
    if len(user_signup.get('cognome')) < 2:
        flash('Il cognome inserito non è valido')
        return redirect(url_for('iscriviti'))
    
    if '@' not in user_signup.get('email') or '.' not in user_signup.get('email'):
        flash('La mail inserita non esiste! La preghiamo di inserire un indirizzo mail valido', 'danger')
        return redirect(url_for('iscriviti'))
    
    if '1' not in user_signup.get('password') and '2' not in user_signup.get('password') and '3' not in user_signup.get('password') and '4' not in user_signup.get('password') and '5' not in user_signup.get('password') and '6' not in user_signup.get('password') and '7' not in user_signup.get('password') and '8' not in user_signup.get('password') and '9' not in user_signup.get('password') and '0' not in user_signup.get('password'):
        flash('La password deve contentere un numero!', 'danger')
        return redirect(url_for('iscriviti'))
    
    verifica_email = utenti_dao.getIdUtenteByEmail(user_signup.get('email'))
    if verifica_email:
        flash('Questa email risulta già registrata', 'warning')
        return redirect(url_for('iscriviti'))
    
    user_signup['password'] = generate_password_hash(user_signup.get('password'))

    if (user_signup.get('locatore') == 'on'):
        user_signup['tipo'] = 'locatore'
    else:
        user_signup['tipo'] = 'cliente'

    immagine = request.files.get('immagine_profilo')
    if immagine: 
        img = Image.open(immagine)

        width, height = img.size
        new_width = PROFILE_IMG_HEIGHT * width / height

        size = new_width, PROFILE_IMG_HEIGHT
        img.thumbnail(size, Image.Resampling.LANCZOS)

        left = (new_width/2 - PROFILE_IMG_HEIGHT/2)
        top = 0
        right = (new_width/2 + PROFILE_IMG_HEIGHT/2)
        bottom = PROFILE_IMG_HEIGHT

        img = img.crop((left, top, right, bottom))

        ext = immagine.filename.split('.')[-1]

        img.save('static/utenti/' + user_signup.get('email').lower() + '.' + ext)

        img_profilo = user_signup.get('email').lower() + '.' + ext
        user_signup['immagine_profilo'] = img_profilo

    else:
        user_signup['immagine_profilo'] = 'user.jpg'

    success = utenti_dao.inserisciUtente(user_signup)
    if success: 
        flash('Registrazione avvenuta con successo!', 'success')
        return redirect(url_for('home'))
    else:
        flash('Qualcosa è andato storto...', 'warning')
        return redirect(url_for('iscriviti'))


@app.route ('/accedi_form')
def login_page():
    return render_template('login.html')


@app.route('/login' , methods = ['POST', 'GET'])
def login():
    user_logged = request.form.to_dict()
    utente = utenti_dao.getUtenteByEmail(user_logged.get('email'))
    if utente and check_password_hash(utente['password'], user_logged.get('password')):
        new = User(id=utente['id'], nome = utente['nome'], cognome = utente['cognome'], email = utente['email'], password = utente['password'], tipo = utente['tipo'], immagine_profilo = utente['immagine_profilo'])
        login_user(new)
        return redirect(url_for('home'))

    else:
        flash('La mail e/o la password inserita non è corretta', 'danger')
        return redirect(url_for('login_page'))
    

@app.route('/profilo/<int:id_utente>', methods = ['POST', 'GET'])
@login_required
def area_personale(id_utente):

    if current_user.id != id_utente:
        return render_template('405.html')
    
    filtroRichieste = request.form.get('filtroRichieste', 'all')
    filtroEffettuate = request.form.get('filtroEffettuate', 'all')

    annunci_locatore = annunci_dao.getAnnunciLocatore(current_user.id)
    lista_annunci = aggiungiFotoAgliAnnunci(annunci_locatore)
    
    if filtroRichieste != 'all':
        prenotazioniRicevute = prenotazioni_dao.getRichiestePrenotazioniLocatoreFiltro(current_user.id, filtroRichieste)
    else:
        prenotazioniRicevute = prenotazioni_dao.getRichiestePrenotazioniLocatore(current_user.id)

    lista_prenotazioni_richieste = aggiungiFotoAllePrenotazioni(prenotazioniRicevute)

    if filtroEffettuate != 'all':
        prenotazioniEffettuate = prenotazioni_dao.getRichiestePrenotazioniClienteFiltro(id_utente, filtroEffettuate)
    else:
        prenotazioniEffettuate = prenotazioni_dao.getRichiestePrenotazioniCliente(id_utente)

    lista_prenotazioni_effettuate = aggiungiFotoAllePrenotazioni(prenotazioniEffettuate)

    return render_template('profilo.html', annunci_locatore = lista_annunci, lista_prenotazioni_richieste = lista_prenotazioni_richieste, lista_prenotazioni_effettuate = lista_prenotazioni_effettuate, filtroEffettuate = filtroEffettuate, filtroRichieste = filtroRichieste)


@app.route('/nuovo_annuncio', methods = ['POST'])
@login_required
def nuovo_annuncio():
    if current_user.tipo != 'locatore':
        return render_template('405.html'), 405
    
    oggi = datetime.now().strftime('%Y-%m-%d')
    annuncio = request.form.to_dict()
    titolo = annuncio.get('titolo')
    descrizione = annuncio.get('descrizione')
    indirizzo = annuncio.get('indirizzo')
    tipo_casa = annuncio.get('tipo_casa')
    numero_locali = annuncio.get('numero_locali')
    prezzo_mensile = int(annuncio.get('prezzo_mensile'))

    if annuncio.get('arredata') == 'on':
        arredata = 1
    else:
        arredata = 0
    
    if annuncio.get('disponibile') == 'on':
        disponibile = 1
    else:
        disponibile = 0

    if titolo == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if descrizione == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if indirizzo == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if tipo_casa == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if numero_locali == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if prezzo_mensile == '':
        flash('Devi compilare tutti i campi!', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if len(titolo) < 7 or len(titolo) > 40:
        flash ('Il titolo inserito non è valido', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if len(descrizione) < 100 or len(descrizione) > 600:
        flash('La descrizione inserita non è valida', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if len(indirizzo) < 5:
        flash('L\'indirizzo inserito non è valido', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if 'Via' not in indirizzo and 'Corso' not in indirizzo and 'Piazza' not in indirizzo and 'Borgo' not in indirizzo and 'Viale' not in indirizzo and 'Strada' not in indirizzo:
        flash('L\'indirizzo inserito non è valido', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if tipo_casa != 'Casa indipendente' and tipo_casa != 'Appartamento' and tipo_casa != 'Loft' and tipo_casa != 'Villa':
        flash('Devi selezionare una tipologia di abitazione tra quelle presenti!', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if numero_locali != '1' and numero_locali != '2' and numero_locali != '3' and numero_locali != '4' and numero_locali != '5':
        flash('Devi selezionare un numero di locali tra quelli presenti!', 'danger')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if prezzo_mensile < 0:
        flash('Non puoi inserire un prezzo mensile negativo per la casa', 'warning')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if ('.' or ',') in str(prezzo_mensile):
        flash('Puoi inserire solamente prezzi mensili interi!', 'warning')
        return redirect(url_for('pagina_annuncio', id = id)) 

    foto_abitazione = request.files.getlist('foto_abitazione[]')
    if not foto_abitazione:
        flash('Devi inserire almeno una foto dell\'abitazione!')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    if len(foto_abitazione) > 5:
        flash('Puoi allegare un massimo di 5 foto al tuo annuncio!')
        return redirect(url_for('area_personale', id_utente = current_user.id))

    nuovo_annuncio = {
        'titolo': titolo,
        'descrizione': descrizione,
        'indirizzo': indirizzo,
        'tipo_casa': tipo_casa,
        'numero_locali': int(numero_locali),
        'prezzo_mensile': prezzo_mensile,
        'data_annuncio': oggi,
        'arredata': arredata,
        'disponibile': disponibile,
        'id_locatore': current_user.id
    }

    success = annunci_dao.inserisciAnnuncio(nuovo_annuncio)
    secondi = datetime.now().timestamp()
    if success: 
        cnt = 0
        idAnnuncio = annunci_dao.getIdAnnuncio(nuovo_annuncio)['id']

        for foto in foto_abitazione:
            cnt += 1
            img = Image.open(foto)

            width, height = img.size
            new_width = HOUSE_IMG_HEIGHT * width / height

            size = new_width, HOUSE_IMG_HEIGHT
            img.thumbnail(size, Image.Resampling.LANCZOS)

            left = (new_width/2 - HOUSE_IMG_HEIGHT/2)
            top = 0
            right = (new_width/2 + HOUSE_IMG_HEIGHT/2)
            bottom = HOUSE_IMG_HEIGHT

            img = img.crop((left, top, right, bottom))

            ext = foto.filename.split('.')[-1]

            img.save('static/case/' + current_user.nome + '@House' + str(cnt) + '.' + str(idAnnuncio) + '.' + str(secondi) + '.' + ext)
            img_casa = current_user.nome + '@House' + str(cnt) + '.' + str(idAnnuncio) + '.' + str(secondi) + '.' + ext


            immagineDaInserire = {
                'url_immagine': img_casa,
                'id_annuncio': idAnnuncio
            }
            
            successFoto = annunci_dao.insertFotoAnnuncio(immagineDaInserire)
            if (successFoto):
                continue
            else:
                flash('Ci sono stati problemi con l\'inserimento delle immagini!', 'warning')
                return redirect(url_for('area_personale', id_utente = current_user.id))
            
        flash('L\'annuncio è stato inserito con successo!', 'success')
        return redirect(url_for('area_personale', id_utente = current_user.id))
    else:
        flash('Qualcosa è andato storto...', 'warning')
        return redirect(url_for('area_personale', id_utente = current_user.id))


@app.route('/annuncio/<int:id>', methods = ['POST', 'GET'])
def pagina_annuncio(id):
    # Uso timedelta per poter permettere agli utenti di effettuare una richiesta di visita presso un'abitazione
    # solamente nei sette giorni successivi al giorno in cui effettuano la richiesta
    domani = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    sette_giorni_dopo = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')

    annuncio = annunci_dao.getAnnuncioByID(id)
    annuncio_modificabile = dict(annuncio)
    foto_annuncio = annunci_dao.getFotoAnnunci(id)
    cnt = 1
    for foto in foto_annuncio:
        annuncio_modificabile['url_foto'+ str(cnt)] = foto['url_immagine']
        cnt+=1
    
    return render_template('annuncio.html', annuncio = annuncio_modificabile, domani=domani, sette_giorni_dopo=sette_giorni_dopo)


@app.route('/annuncio/<int:id>/modifica_annuncio', methods = ['POST', 'GET'])
@login_required
def modifica_annuncio(id):
    annuncio_attuale = annunci_dao.getAnnuncioByID(id)
    # Verifico che sia effettivamente il locatore che ha pubblicato l'annuncio colui che sta tentando di modificarlo.
    if current_user.tipo == 'locatore' and annuncio_attuale['id_locatore'] == current_user.id:
        annuncio = request.form.to_dict()
        titolo = request.form['titolo']
        descrizione = annuncio.get('descrizione')
        tipo_casa = annuncio.get('tipo_casa')
        numero_locali = annuncio.get('numero_locali')
        prezzo_mensile = int(annuncio.get('prezzo_mensile'))

        if annuncio.get('arredata') == 'on':
            arredata = 1
        else:
            arredata = 0
        
        if annuncio.get('disponibile') == 'on':
            disponibile = 1
        else:
            disponibile = 0

        if titolo == '':
            flash('Devi compilare tutti i campi!', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if descrizione == '':
            flash('Devi compilare tutti i campi!', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if tipo_casa == '':
            flash('Devi compilare tutti i campi!', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if numero_locali == '':
            flash('Devi compilare tutti i campi!', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if prezzo_mensile == '':
            flash('Devi compilare tutti i campi!', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if len(titolo) < 7 or len(titolo) > 40:
            flash ('Il titolo inserito non è valido', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if len(descrizione) < 100 or len(descrizione) > 600:
            flash('La descrizione inserita non è valida', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if tipo_casa != 'Casa indipendente' and tipo_casa != 'Appartamento' and tipo_casa != 'Loft' and tipo_casa != 'Villa':
            flash('Devi selezionare una tipologia di abitazione tra quelle presenti!', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if numero_locali != '1' and numero_locali != '2' and numero_locali != '3' and numero_locali != '4' and numero_locali != '5':
            flash('Devi selezionare un numero di locali tra quelli presenti!', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))   
        if prezzo_mensile < 0:
            flash('Non puoi inserire un prezzo mensile negativo per la casa', 'warning')
            return redirect(url_for('pagina_annuncio', id = id))  
        if ('.' or ',') in str(prezzo_mensile):
            flash('Puoi inserire solamente prezzi mensili interi!', 'warning')
            return redirect(url_for('pagina_annuncio', id = id))   
        if current_user.tipo != 'locatore':
            flash ('Prima di poter pubblicare un annuncio dovrai registrarti come locatore!', 'danger')
            return redirect(url_for('pagina_annuncio', id = id))  

        annuncio_modificato = {
            'titolo': titolo,
            'descrizione': descrizione,
            'tipo_casa': tipo_casa,
            'numero_locali': int(numero_locali),
            'prezzo_mensile': prezzo_mensile,
            'arredata': arredata,
            'disponibile': disponibile,
        }

        foto_abitazione = request.files.getlist('foto_abitazione[]')
        foto_attuali = annunci_dao.getFotoAnnunci(id)
        if len(foto_abitazione) > 1 or (len(foto_abitazione)==1 and foto_abitazione[0].filename!=''):
            # Verifico che, con l'aggiunta delle immagini, l'annuncio abbia un numero di foto massimo pari a 5.
            if (len(foto_abitazione) + len(foto_attuali)) > 5:
                flash ('Non puoi inserire più di cinque immagini per un signolo annuncio!', 'danger')
                return redirect(url_for('pagina_annuncio', id = id)) 

        secondi = datetime.now().timestamp()
        if len(foto_abitazione)>1 or (len(foto_abitazione)==1 and foto_abitazione[0].filename!=''):  
            cnt = 0
            for foto in foto_abitazione:
                    cnt += 1
                    img = Image.open(foto)

                    width, height = img.size
                    new_width = HOUSE_IMG_HEIGHT * width / height

                    size = new_width, HOUSE_IMG_HEIGHT
                    img.thumbnail(size, Image.Resampling.LANCZOS)

                    left = (new_width/2 - HOUSE_IMG_HEIGHT/2)
                    top = 0
                    right = (new_width/2 + HOUSE_IMG_HEIGHT/2)
                    bottom = HOUSE_IMG_HEIGHT

                    img = img.crop((left, top, right, bottom))

                    ext = foto.filename.split('.')[-1]

                    img.save('static/case/' + current_user.nome + '@House' + str(cnt) + '.' + str(id) + '.' + str(secondi) + '.' + ext)
                    img_casa = current_user.nome + '@House'+ str(cnt) + '.' + str(id) +  '.' + str(secondi) + '.' + ext


                    immagineDaInserire = {
                        'url_immagine': img_casa,
                        'id_annuncio': id
                    }

                    successFoto = annunci_dao.insertFotoAnnuncio(immagineDaInserire)
                    if (successFoto):
                        continue
                    else:
                        flash('Ci sono stati problemi con l\'inserimento delle immagini!', 'warning')
                        return redirect(url_for('area_personale'))
        

        success = annunci_dao.modificaAnnuncio(id, annuncio_modificato)
        if success:
            flash('Annuncio modificato con successo!', 'success')
            return redirect(url_for('pagina_annuncio', id = id))
        else:
            flash('Si sono verificati degli errori...', 'warning')
            return redirect(url_for('pagina_annuncio', id = id))
    else:
        flash('Non sei autorizzato/a a modificare questo annuncio!', 'warning')
        return render_template('405.html'), 405



@app.route('/annuncio/<int:id>/delete_image', methods = ['POST'])
@login_required
def elimina_immagine(id):
    url_foto = request.form['foto_da_eliminare']
    annuncio = annunci_dao.getAnnuncioByID(id)
    foto_attuali = annunci_dao.getFotoAnnunci(id)
    numero_foto_attuali = len(foto_attuali)
    # Verifico che colui che sta provando a eliminare l'immagine dell'annuncio sia EFFETTIVAMENTE il locatore che ha pubblicato l'annuncio.
    if current_user.tipo == 'locatore' and current_user.id == annuncio['id_locatore']:
        # Verifico che ci siano almeno due foto dell'abitazione all'interno dell'annuncio, infatti dato che ogni annuncio dovrà avere almeno un'immagine, non permetterò l'eliminazione
        # dell'immagine qualora l'annuncio avesse solamente un'immagine.
        if numero_foto_attuali > 1:
            if annunci_dao.eliminaFotoAnnuncio(id, url_foto):
                flash('L\'immagine è stata eliminata con successo!', 'success')
                os.remove('static/case/'+url_foto)
                # os.remove è un metodo del modulo os che mi permette di eliminare l'immagine non solo dal database tramite la query, ma anche dalla cartella static!
                return redirect(url_for('pagina_annuncio', id = id))
        
            else:
                flash('L\'eliminazione dell\'immagine non è andata a buon fine!', 'warning')
                return redirect(url_for('pagina_annuncio', id = id))
        else:
            flash('L\'annuncio deve contentere almeno un\'immagine!', 'warning')
            return redirect(url_for('pagina_annuncio', id = id))

    else:
        flash('Non sei autorizzato ad eliminare l\'immagine!', 'danger')
        return render_template('405.html', 405)


@app.route('/annuncio/<int:id>/verifica_disponibilità', methods = ['POST'])
@login_required
def verifica_disponibilità(id):
    annuncio = annunci_dao.getAnnuncioByID(id)  
    if annuncio['disponibile'] == 0:
        # Un locatore potrebbe anche rendere non disponibile un annuncio. Però un utente se ha effettuate delle visite in passato
        # alla sua proprietà potrebbe comunque raggiungere la sua pagina annuncio e richiedere una visita. Con questo controllo invece
        # non permetteremo ai clienti di poter effettuare prenotazioni per case rese non disponibili dai propri locatori.
        flash('L\'annuncio selezionato non è più disponibile, pertanto non puoi procedere con la prenotazione della visita!', 'warning')
        return redirect(url_for('home'))
    

    data = request.form['data']
    fasce_occupate = prenotazioni_dao.getFasceOrarieOccupate(data, id)
    # Faccio una query per ottenere una lista di tutte le fasce orarie OCCUPATE (quindi in cui è già stata ACCETTATA una visita da parte del locatore) in una certa data per un certo annuncio!
    
    fasce_disponibili = ['9-12', '12-14', '14-17', '17-20']
    fasce_disponibili_copy = fasce_disponibili.copy()
    for fascia in fasce_occupate:
        if fascia['fascia_oraria'] in fasce_disponibili_copy:
            fasce_disponibili.remove(fascia['fascia_oraria'])

    # se len(fasce_disponibili)==0 significa che quel giorno sono state occupate tutte le fasce orarie dalle prenotazioni di altri clienti!
    if len(fasce_disponibili)==0:
        flash('Ci dispiace, ma non risultano orari disponibili per la visita della casa nella data selezionata...', 'warning')
        return redirect(url_for('pagina_annuncio', id = id))

    return render_template('prenotazione.html', fasce_disponibili = fasce_disponibili, data_scelta = data, id_annuncio = id)


@app.route('/annuncio/<int:id>/prenotazione', methods = ['POST'])
@login_required
def nuova_prenotazione(id):
    prenotazione = request.form.to_dict()
    data = prenotazione['data']
    fascia_oraria = prenotazione['fascia_oraria']
    tipo_visita = prenotazione['tipo_visita']

    annuncio = annunci_dao.getAnnuncioByID(id)
    if annuncio['id_locatore'] == current_user.id:
        flash ('Non puoi prenotare una visita per la tua casa!')
        return redirect(url_for('pagina_annuncio', id = id))
    
    if fascia_oraria not in ['9-12', '12-14', '14-17', '17-20']:
        flash('La fascia oraria selezionata non è disponibile!', 'danger')
        return redirect(url_for('pagina_annuncio', id=id))

    prenotazione_esistente = prenotazioni_dao.getPrenotazione(current_user.id, id)
    # Verifico che l'utente non abbia delle richieste di prenotazione in stato 'accettata' o 'richiesta' per quell'annuncio.
    # Infatti il cliente potrà richiedere una visita solamente per le abitazioni per le quali non ha MAI fatto richiesta di visita, oppure l'ha fatto ma sono state rifiutate.
    if prenotazione_esistente:
        if prenotazione_esistente['stato_prenotazione'] == 'accettata':
            flash('Hai già effettuato una visita presso questa casa!', 'danger')
            return redirect(url_for('pagina_annuncio', id=id))
        
        elif prenotazione_esistente['stato_prenotazione'] == 'richiesta':
            flash('Hai già fatto una richiesta di prenotazione per questa casa. Devi attendere la risposta del locatore!', 'danger')
            return redirect(url_for('pagina_annuncio', id=id))
 
    else:
        prenotazione_inseribile = {
            'id_cliente': current_user.id,
            'id_annuncio': id,
            'tipo_visita': tipo_visita,
            'data_visita': data,
            'fascia_oraria': fascia_oraria
        }
        prenotazioni_dao.inserisciPrenotazione(prenotazione_inseribile)
        flash('La prenotazione è stata effettuata con successo! Ora dovrai attendere la conferma da parte del locatore.', 'success')
        return redirect(url_for('pagina_annuncio', id=id))


@app.route('/profilo/<int:id_utente>/modifica_stato_prenotazione/<int:id_prenotazione>', methods = ['POST'])
@login_required
def modifica_stato_prenotazione(id_prenotazione, id_utente):
    if id_utente != current_user.id:
        return render_template('405.html'), 405

    nuovo_stato_prenotazione = request.form['nuovo_stato']
    motivazione_rifiuto = None
    if (nuovo_stato_prenotazione=='rifiutata'):
        motivazione_rifiuto = request.form['motivazione_rifiuto']
        if len(motivazione_rifiuto)<5 or len(motivazione_rifiuto)>500:
            flash('La motivazione del rifiuto deve avere un minimo di 5 e un massimo di 500 caratteri!')
            return redirect(url_for('area_personale', id_utente = id_utente))

    if nuovo_stato_prenotazione == 'accettata':
        success = prenotazioni_dao.modificaStatoPrenotazioneAccettata(id_prenotazione)
    else:
        success = prenotazioni_dao.modificaStatoPrenotazioneRifiutata(id_prenotazione, motivazione_rifiuto)

    if success and nuovo_stato_prenotazione == 'accettata':
        flash ('Hai accettato correttamente la richiesta di prenotazione!', 'success')
        return redirect(url_for('area_personale', id_utente = id_utente))
    elif success and nuovo_stato_prenotazione == 'rifiutata':
        flash('Hai rifiutato correttamente la richiesta di prenotazione', 'success')
        return redirect(url_for('area_personale', id_utente = id_utente))
    else:
        flash('Si sono verificati degli errori...', 'warning')
        return redirect(url_for('area_personale', id_utente = id_utente))
    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(user_id):
    db_user = utenti_dao.getUtenteByID(user_id)
    if db_user is not None:
        user = User(id=db_user['id'], nome = db_user['nome'], cognome = db_user['cognome'], email = db_user['email'], password = db_user['password'], tipo = db_user['tipo'], immagine_profilo=db_user['immagine_profilo'])
    return user

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@login_manager.unauthorized_handler
@app.errorhandler(405)
def unauthorized(e):
    return render_template('405.html'), 405

# Funzione che utilizzo per, data una lista di annunci, ciclare sulla lista e, per ogni annuncio, fare un query al DB in cui
# le passo l'id dell'annuncio e mi restituisce in output le immagini dell'annuncio che andrò ad aggiungere a una nuova struttura dati, contenente
# tutte le informazioni dell'annuncio con, in più, le sue immagini.

def aggiungiFotoAgliAnnunci(lista_annunci):
    lista_annunci_con_foto = []
    for annuncio in lista_annunci:
        annuncio_da_modificare = dict(annuncio)
        foto_annuncio = annunci_dao.getFotoAnnunci(annuncio['id'])
        cnt = 1
        for foto in foto_annuncio:
            annuncio_da_modificare['url_foto'+ str(cnt)] = foto['url_immagine']
            cnt+=1
        lista_annunci_con_foto.append(annuncio_da_modificare)
    return lista_annunci_con_foto

# Uguale alla funziona sopra, ma in questo caso andrò ad aggiungere le immagini degli annunci non più agli annunci stessi, ma alle prenotazioni degli annunci.
def aggiungiFotoAllePrenotazioni(lista_prenotazioni):
    lista_prenotazioni_con_foto = []
    for prenotazione in lista_prenotazioni:
        annuncio_da_modificare = dict(prenotazione)
        foto_annuncio = annunci_dao.getFotoAnnunci(prenotazione['id_annuncio'])
        cnt = 1
        for foto in foto_annuncio:
            annuncio_da_modificare['url_foto'+ str(cnt)] = foto['url_immagine']
            cnt+=1
        lista_prenotazioni_con_foto.append(annuncio_da_modificare)
    return lista_prenotazioni_con_foto

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)