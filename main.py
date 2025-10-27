import flet as ft  # Importa la libreria Flet per costruire interfacce GUI
import automobile  # Modulo contenente la classe Automobile usata dall'app (preso dal lab03)
from alert import AlertManager  # Importa un gestore di alert personalizzato per mostrare finestre di errore/avviso
from autonoleggio import Autonoleggio  # Importa la classe Autonoleggio (logica dell'app)

FILE_AUTO = "automobili.csv"  # Nome del file CSV usato per caricare/salvare le automobili

# Funzione principale che Flet esegue per costruire la pagina
def main(page: ft.Page):
    page.title = "Lab05"  # Titolo della finestra
    page.horizontal_alignment = "center"  # Centra orizzontalmente i contenuti nella pagina
    page.theme_mode = ft.ThemeMode.DARK  # Imposta tema scuro di default

    # --- ALERT ---
    alert = AlertManager(page)  # Crea un'istanza del gestore di alert collegata alla pagina

    # --- LA LOGICA DELL'APPLICAZIONE E' PRESA DALL'AUTONOLEGGIO DEL LAB03 ---
    autonoleggio = Autonoleggio("Polito Rent", "Alessandro Visconti")
    try:
        autonoleggio.carica_file_automobili(FILE_AUTO)  # Prova a caricare il file CSV delle automobili
    except Exception as e:
        alert.show_alert(f"❌ {e}")  # Mostra un alert con l'errore se il caricamento fallisce

    # --- UI ELEMENTI ---
    # Text per mostrare il nome e il responsabile dell'autonoleggio
    txt_titolo = ft.Text(value=autonoleggio.nome, size=38, weight=ft.FontWeight.BOLD)
    txt_responsabile = ft.Text(
        value=f"Responsabile: {autonoleggio.responsabile}",
        size=16,
        weight=ft.FontWeight.BOLD
    )

    # TextField per modificare il responsabile
    input_responsabile = ft.TextField(value=autonoleggio.responsabile, label="Responsabile")

    # ListView per mostrare la lista di auto aggiornata (sarà popolata dinamicamente)
    lista_auto = ft.ListView(expand=True, spacing=5, padding=10, auto_scroll=True)

    # Campi per l'inserimento di una nuova automobile
    input_marca = ft.TextField(value="", label="Marca")
    input_modello = ft.TextField(value="", label="Modello")
    input_anno = ft.TextField(value="", label="Anno")
    input_posti = ft.IconButton()  # Non usato direttamente: placeholder per eventuale controllo visivo

    # --- FUNZIONI APP ---
    def aggiorna_lista_auto():
        """Rimuove tutti i controlli dalla ListView e la ricostruisce a partire
        dalla lista di automobili ordinata per marca fornita dall'istanza Autonoleggio."""
        lista_auto.controls.clear()
        for auto in autonoleggio.automobili_ordinate_per_marca():
            stato = "✅" if auto.disponibile else "⛔"  # Indica se l'auto è disponibile o noleggiata
            lista_auto.controls.append(ft.Text(f"{stato} {auto}"))
        page.update()  # Applica l'aggiornamento alla pagina

    # --- HANDLERS APP ---
    def cambia_tema(e):
        # Alterna tra tema scuro e chiaro quando viene cambiato lo switch
        page.theme_mode = ft.ThemeMode.DARK if toggle_cambia_tema.value else ft.ThemeMode.LIGHT
        toggle_cambia_tema.label = "Tema scuro" if toggle_cambia_tema.value else "Tema chiaro"
        page.update()

    def conferma_responsabile(e):
        # Aggiorna il responsabile nell'oggetto Autonoleggio e nel Text visualizzato
        autonoleggio.responsabile = input_responsabile.value
        txt_responsabile.value = f"Responsabile: {autonoleggio.responsabile}"
        page.update()

    # Handlers per la gestione dei bottoni utili all'inserimento di una nuova auto
    def handleAdd(e):
        # Incrementa il valore del campo txtOut (numero di posti visualizzato)
        currentVal = txtOut.value
        txtOut.value = currentVal + 1
        txtOut.update()

    def handleRemove(e):
        # Decrementa il valore del campo txtOut (numero di posti visualizzato)
        currentVal = txtOut.value
        if (currentVal > 0):
            txtOut.value = currentVal - 1
            txtOut.update()

    def conferma_automobili(e):
        # Raccoglie i dati dai campi, valida i valori e aggiunge una nuova automobile
        automobile.marca = input_marca.value
        automobile.modello = input_modello.value
        automobile.anno = input_anno.value
        automobile.posti = txtOut.value

        # Validazioni base: marca e modello non vuoti
        if input_marca.value != "" and input_modello.value != "":
            # Validazione anno: fra 1886 e anno corrente (qui hardcoded 2025 nel codice originale)
            if int(input_anno.value) >1885 and int(input_anno.value) < 2025:
                # Aggiunge l'automobile tramite l'istanza Autonoleggio e ottiene l'oggetto creato
                auto=autonoleggio.aggiungi_automobile(input_marca.value, input_modello.value, input_anno.value, txtOut.value)
                codice=auto.codice
                if auto.disponibile == True:
                    libera="Disponibile"
                else:
                    libera="Noleggiata"
                # Aggiunge una riga descrittiva alla ListView
                lista_auto.controls.append(ft.Text(f"✅{codice} | {input_marca.value} {input_modello.value} ({input_anno.value}) | {txtOut.value} posti | {libera}"))
            else:
                # Messaggio d'errore nella ListView per anno non valido
                lista_auto.controls.append(
                    ft.Text("⛔ Inserire un anno compreso tra il 1886 e l'anno corrente perchè è in questo periodo che esistono le auto."))
        else:
            # Messaggio d'errore nella ListView per marca o modello mancanti
            lista_auto.controls.append(ft.Text("⛔ Inserire una marca e un modello, non è possibile inserire un'automobile senza questi dati"))
        page.update()

    # --- EVENTI ---
    toggle_cambia_tema = ft.Switch(label="Tema scuro", value=True, on_change=cambia_tema)  # Switch per cambiare tema
    pulsante_conferma_responsabile = ft.ElevatedButton("Conferma", on_click=conferma_responsabile)  # Bottone per salvare il responsabile

    # Bottoni per la gestione dell'inserimento di una nuova auto
    btnMinus = ft.IconButton(icon=ft.Icons.REMOVE,
                             icon_color="red",
                             icon_size=24, on_click=handleRemove)
    btnAdd = ft.IconButton(icon=ft.Icons.ADD,
                           icon_color="green",
                           icon_size=24, on_click=handleAdd)
    txtOut = ft.TextField(width=100, disabled=True,
                          value=0, border_color="green",
                          text_align=ft.TextAlign.CENTER)  # Campo che mostra il numero di posti selezionati

    pulsante_conferma_automobile = ft.ElevatedButton("Conferma", on_click=conferma_automobili)

    # --- LAYOUT ---
    # Costruzione dell'interfaccia: aggiunge i controlli alla pagina in ordine
    page.add(
        toggle_cambia_tema,

        # Sezione 1: titolo e responsabile
        txt_titolo,
        txt_responsabile,
        ft.Divider(),

        # Sezione 2: modifica informazioni responsabile
        ft.Text("Modifica Informazioni", size=20),
        ft.Row(spacing=200,
               controls=[input_responsabile, pulsante_conferma_responsabile],
               alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(),

        # Sezione 3: aggiungi nuova automobile (marca, modello, anno, posti)
        ft.Text("Aggiungi nuova automobile", size=20),
        ft.Row(spacing=20,
               controls=[input_marca, input_modello, input_anno, btnMinus, txtOut, btnAdd],
               alignment=ft.MainAxisAlignment.CENTER),
        ft.Row(spacing=0,
               controls=[pulsante_conferma_automobile],
               alignment=ft.MainAxisAlignment.CENTER),

        # Sezione 4: lista delle automobili
        ft.Divider(),
        ft.Text("Automobili", size=20),
        lista_auto,
    )
    aggiorna_lista_auto()  # Popola la lista all'avvio

# Avvia l'applicazione Flet specificando la funzione main come target
ft.app(target=main)
