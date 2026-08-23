import streamlit as st
import pandas as pd
import json
import os
import re
import random
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF

st_autorefresh(interval=5000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(page_title="Torneo Coppie Fisse Live", layout="wide")

DB_FILE = "coppie_data.json"

def carica_dati():
    dati_default = {
        "stato": "setup",
        "coppie": [],
        "num_tavoli": 6,
        "num_gironi": 2,
        "admin_pin": "0000",
        "gironi": {}, 
        "calendario_gironi": {}, 
        "punti_gironi": {}, 
        "fasi_finali_configurate": False,
        "tabellone_a": [], 
        "tabellone_b": [],
        "terzo_quarto_a": [],
        "terzo_quarto_b": []
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                dati_salvati = json.load(f)
                for k, v in dati_default.items():
                    if k not in dati_salvati:
                        dati_salvati[k] = v
                return dati_salvati
        except:
            pass
    return dati_default

def salva_dati(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = carica_dati()

db = st.session_state.db

def pulisci_nome(testo):
    testo = testo.replace("🤝", "").replace("⚽", "").replace("🏆", "")
    testo = re.sub(r'^\d+[\.\-\)]?\s*', '', testo)
    return testo.strip()

def ricalcola_classifiche_gironi():
    for g_nome, coppie_lista in db["gironi"].items():
        punti = {c: 0 for c in coppie_lista}
        if g_nome in db["calendario_gironi"]:
            for turno_obj in db["calendario_gironi"][g_nome]:
                for m in turno_obj["partite"]:
                    if m.get("giocata", False):
                        g1 = m["gol1"]
                        g2 = m["gol2"]
                        diff = abs(g1 - g2)
                        
                        if g1 > g2:
                            pt_s1, pt_s2 = (3, 0) if diff >= 2 else (2, 1)
                        elif g2 > g1:
                            pt_s1, pt_s2 = (0, 3) if diff >= 2 else (1, 2)
                        else:
                            pt_s1, pt_s2 = 2, 2
                        
                        punti[m['c1']] = punti.get(m['c1'], 0) + pt_s1
                        punti[m['c2']] = punti.get(m['c2'], 0) + pt_s2
        db["punti_gironi"][g_nome] = punti

def calcola_partite_giocate_coppia(g_nome, coppia):
    giocate = 0
    totali = 0
    if g_nome in db["calendario_gironi"]:
        for turno_obj in db["calendario_gironi"][g_nome]:
            for m in turno_obj["partite"]:
                if m['c1'] == coppia or m['c2'] == coppia:
                    totali += 1
                    if m.get("giocata", False):
                        giocate += 1
    return giocate, totali

def genera_pdf_coppie():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Torneo a Coppie Fisse - Schema Gironi", 0, 1, "C")
    pdf.ln(5)
    
    for g_nome, turni in db["calendario_gironi"].items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"--- {g_nome} ---", 0, 1, "L")
        for turno_obj in turni:
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Turno {turno_obj['turno']}", 0, 1, "L")
            pdf.set_font("Arial", "", 10)
            for idx, m in enumerate(turno_obj["partite"]):
                risultato = f"{m['gol1']} - {m['gol2']}" if m.get("giocata", False) else "Da giocare"
                riga = f"  {m['c1']} VS {m['c2']} -> {risultato}"
                riga_pulita = riga.encode('latin-1', 'ignore').decode('latin-1')
                pdf.cell(0, 6, riga_pulita, 0, 1, "L")
            pdf.ln(2)
    return bytes(pdf.output())

def crea_abbinamenti_protetti(lista_squadre_ordinate_per_girone):
    gironi = list(lista_squadre_ordinate_per_girone.keys())
    max_profondita = max([len(v) for v in lista_squadre_ordinate_per_girone.values()])
    
    pool_squadre = []
    for livello in range(max_profondita):
        for g in gironi:
            lst = lista_squadre_ordinate_per_girone[g]
            if livello < len(lst):
                pool_squadre.append((lst[livello], g))
                
    accoppiamenti = []
    rimanenti = pool_squadre.copy()
    
    while len(rimanenti) >= 2:
        s1, g1 = rimanenti.pop(0)
        trovato = False
        for idx, (s2, g2) in enumerate(rimanenti):
            if g1 != g2:
                accoppiamenti.append(((s1, g1), (s2, g2)))
                rimanenti.pop(idx)
                trovato = True
                break
        if not trovato:
            s2, g2 = rimanenti.pop(0)
            accoppiamenti.append(((s1, g1), (s2, g2)))
            
    if rimanenti:
        s1, g1 = rimanenti.pop(0)
        accoppiamenti.append(((s1, g1), ("RIPOSO", "NESSUNO")))
        
    return accoppiamenti

def ottieni_nome_turno(num_turno, totale_turni):
    diff = totale_turni - num_turno
    if diff == 0:
        return "🏆 FINALE"
    elif diff == 1:
        return "⚔️ SEMIFINALI"
    elif diff == 2:
        return "🔥 QUARTI DI FINALE"
    else:
        return f"Turno {num_turno}"

# --- BARRA LATERALE ---
st.sidebar.header("⚙️ Pannello di Controllo")

if db["stato"] != "setup":
    pdf_data = genera_pdf_coppie()
    st.sidebar.download_button(
        label="📥 Scarica Schema in PDF",
        data=pdf_data,
        file_name="schema_gironi_torneo.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.sidebar.markdown("---")

modalita_admin = st.sidebar.checkbox("Modalità Amministratore (PIN)")
is_admin = False
if modalita_admin:
    pin_inserito = st.sidebar.text_input("Inserisci PIN Admin", type="password")
    if pin_inserito == db["admin_pin"]:
        is_admin = True
        st.sidebar.success("Accesso Admin Autorizzato ✅")
    else:
        st.sidebar.error("PIN errato.")

st.sidebar.markdown("---")

if is_admin:
    if st.sidebar.button("⚙️ Mostra / Nascondi Setup Iniziale", use_container_width=True):
        st.session_state["mostra_setup"] = not st.session_state.get("mostra_setup", False)

if is_admin and db["stato"] == "fasi_finali":
    if st.sidebar.button("🔙 Torna temporaneamente ai Gironi", use_container_width=True):
        db["stato"] = "gironi"
        salva_dati(db)
        st.rerun()
    st.sidebar.markdown("---")

st.sidebar.subheader("⚠️ Zona Pericolo")
if is_admin:
    conferma_reset = st.sidebar.checkbox("Spunta per confermare il reset totale", key="checkbox_reset_gara")
    if st.sidebar.button("🔄 Ricomincia la gara da zero", use_container_width=True):
        if conferma_reset:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Torneo azzerato con successo! Ricarico...")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Spunta la casella di conferma sopra per procedere.")
else:
    st.sidebar.info("🔐 Accedi come admin per resettare la gara.")

st.sidebar.markdown("---")
st.sidebar.info("📱 **Link WhatsApp:** Copia l'indirizzo della pagina dal browser e incollalo nel gruppo.")

# --- INTERFACCIA PRINCIPALE ---
st.title("🏆 Torneo Coppie Fisse Live")

st.markdown(
    """
    <div style="padding: 10px; background-color: #f0f2f6; border-radius: 8px; text-align: center; margin-bottom: 20px;">
        🔄 <a href="javascript:window.location.reload(true)" style="text-decoration: none; color: #262730; font-weight: bold; font-size: 15px;">
            Quando vuoi vedere l’andamento della gara e quando vuoi giocare ricarica la pagina del browser
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# 1. SETUP
if db["stato"] == "setup" or st.session_state.get("mostra_setup", False):
    st.subheader("1. Configurazione Iniziale Torneo a Coppie")
    
    if not is_admin:
        st.warning("⚠️ Configurazione bloccata. Accedi come amministratore dalla barra laterale con il PIN.")
    else:
        whatsapp_text = st.text_area("Incolla qui la lista delle coppie da WhatsApp (es. 🤝 Mario / Luigi):")
        
        col1, col2 = st.columns(2)
        with col1:
            db["num_tavoli"] = st.number_input("Numero di biliardini disponibili", min_value=1, max_value=10, value=db["num_tavoli"])
        with col2:
            db["num_gironi"] = st.number_input("Numero di gironi da creare", min_value=1, max_value=6, value=db["num_gironi"])
            
        db["admin_pin"] = st.text_input("Cambia PIN Admin", value=db["admin_pin"])

        if st.button("🚀 Crea Gironi e Sorteggia Coppie"):
            coppie = []
            for line in whatsapp_text.split("\n"):
                nome_c = pulisci_nome(line)
                if nome_c:
                    coppie.append(nome_c)
            
            num_g = int(db["num_gironi"])
            
            if len(coppie) < (num_g * 2):
                st.error(f"Hai inserito {len(coppie)} coppie. Con {num_g} gironi servono almeno {num_g * 2} coppie.")
            else:
                db["coppie"] = coppie
                random.shuffle(coppie)
                
                nomi_gironi = [chr(65 + i) for i in range(num_g)]
                gironi_dict = {f"Girone {g}": [] for g in nomi_gironi}
                
                for idx, c in enumerate(coppie):
                    g_scelto = f"Girone {nomi_gironi[idx % num_g]}"
                    gironi_dict[g_scelto].append(c)
                
                db["gironi"] = gironi_dict
                db["punti_gironi"] = {g: {c: 0 for c in lst} for g, lst in gironi_dict.items()}
                
                calendario_totale = {}
                for g_nome, lista_c in gironi_dict.items():
                    squadre = lista_c.copy()
                    if len(squadre) % 2 != 0:
                        squadre.append("RIPOSO")
                    
                    n = len(squadre)
                    turni_girone = []
                    
                    for t in range(n - 1):
                        partite_turno = []
                        for i in range(n // 2):
                            s1 = squadre[i]
                            s2 = squadre[n - 1 - i]
                            if s1 != "RIPOSO" and s2 != "RIPOSO":
                                match_id = f"{g_nome}_t{t+1}_m{i}"
                                partite_turno.append({
                                    "id": match_id,
                                    "girone": g_nome,
                                    "c1": s1, "c2": s2,
                                    "giocata": False, "in_corso": False,
                                    "gol1": 0, "gol2": 0
                                })
                        turni_girone.append({"turno": t + 1, "partite": partite_turno})
                        squadre = [squadre[0]] + [squadre[-1]] + squadre[1:-1]
                    
                    calendario_totale[g_nome] = turni_girone
                
                db["calendario_gironi"] = calendario_totale
                db["stato"] = "gironi"
                db["fasi_finali_configurate"] = False
                db["tabellone_a"] = []
                db["tabellone_b"] = []
                db["terzo_quarto_a"] = []
                db["terzo_quarto_b"] = []
                salva_dati(db)
                st.success(f"Creati con successo {num_g} gironi!")
                st.session_state["mostra_setup"] = False
                st.rerun()
    st.markdown("---")

# 2. FASE A GIRONI
if db["stato"] == "gironi":
    st.subheader("📊 Classifiche dei Gironi")
    ricalcola_classifiche_gironi()
    num_tavoli = db.get("num_tavoli", 6)

    if db.get("fasi_finali_configurate", False):
        if st.button("⬅️ Torna alla schermata delle Fasi Finali", use_container_width=True):
            db["stato"] = "fasi_finali"
            salva_dati(db)
            st.rerun()
        st.markdown("---")

    nomi_gironi_chiavi = list(db["gironi"].keys())
    for i in range(0, len(nomi_gironi_chiavi), 2):
        col_gironi = st.columns(2)
        for j in range(2):
            if i + j < len(nomi_gironi_chiavi):
                g_nome = nomi_gironi_chiavi[i + j]
                coppie_lista = db["gironi"][g_nome]
                with col_gironi[j]:
                    st.markdown(f"**📁 {g_nome}**")
                    sorted_c = sorted(db["punti_gironi"][g_nome].items(), key=lambda x: x[1], reverse=True)
                    
                    data_g = []
                    for idx, (coppia, pt) in enumerate(sorted_c):
                        gioc, tot = calcola_partite_giocate_coppia(g_nome, coppia)
                        fascia_assegnata = "⭐ A" if idx < 4 else "🔻 B"
                        data_g.append({
                            "Pos": f"{idx+1}°",
                            "Coppia": coppia,
                            "Pt": pt,
                            "Gioc": f"{gioc}/{tot}",
                            "Fascia": fascia_assegnata
                        })
                        
                    df_g = pd.DataFrame(data_g)
                    
                    def colora_fasce(val):
                        try:
                            pos = int(str(val).replace("°", ""))
                            if pos <= 4:
                                return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                            else:
                                return 'background-color: #f8d7da; color: #721c24;'
                        except:
                            return ''

                    if not df_g.empty:
                        df_styled = df_g.style.map(colora_fasce, subset=["Pos"])
                        st.dataframe(df_styled, hide_index=True, use_container_width=True)
                    else:
                        st.dataframe(df_g, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("⚡ Stato dei Biliardini e Coda Incontri")

    partite_in_corso = []
    partite_da_giocare = []

    for g_nome, turni in db["calendario_gironi"].items():
        for t_obj in turni:
            for m in t_obj["partite"]:
                if not m.get("giocata", False):
                    if m.get("in_corso", False):
                        partite_in_corso.append(m)
                    else:
                        partite_da_giocare.append(m)

    col_ic, col_coda = st.columns(2)

    with col_ic:
        st.markdown("#### 🔥 Partite in Corso ai Tavoli")
        if not partite_in_corso:
            st.info("Nessuna partita in corso al momento.")
        else:
            for m in partite_in_corso:
                st.warning(f"🏟️ **{m['girone']}**: {m['c1']} vs {m['c2']}")

        st.markdown("#### 📣 Chiamata / Preparazione")
        if partite_in_corso:
            primo_match = partite_in_corso[0]
            st.success(f"In arrivo al tavolo... **{primo_match['c1']}** e **{primo_match['c2']}** ({primo_match['girone']}) - **Preparatevi!**")
        elif partite_da_giocare:
            prossimo = partite_da_giocare[0]
            st.success(f"📣 Prossimi a scendere: **{prossimo['c1']}** e **{prossimo['c2']}** ({prossimo['girone']})")
        else:
            st.info("Nessuna altra partita in programma.")

    with col_coda:
        st.markdown("#### ⏳ In Coda (Prossimi Incontri)")
        if not partite_da_giocare:
            st.info("La coda è vuota.")
        else:
            for idx, m in enumerate(partite_da_giocare[:5]):
                st.write(f"{idx+1}. **{m['girone']}**: {m['c1']} vs {m['c2']}")

    st.markdown("---")
    st.subheader("📅 Tutte le Partite dei Gironi (Mischia Unica per Turno)")
    st.info(f"📌 **Organizzazione Biliardini:** Hai impostato **{num_tavoli} biliardini**. Le partite di tutti i gironi sono unite e mischiate per turno.")

    max_turni = max([len(turni) for turni in db["calendario_gironi"].values()])

    for t_num in range(1, max_turni + 1):
        st.markdown(f"### 🚩 Turno {t_num}")
        
        partite_questo_turno = []
        for g_nome, turni_girone in db["calendario_gironi"].items():
            for t_obj in turni_girone:
                if t_obj["turno"] == t_num:
                    partite_questo_turno.extend(t_obj["partite"])
        
        for m in partite_questo_turno:
            match_id = m['id']
            girone_m = m['girone']

            with st.container(border=True):
                st.caption(f"📁 **{girone_m}**")
                col_s1, col_mid, col_s2 = st.columns([4, 2.5, 4], gap="small")
                with col_s1:
                    st.info(f"🤝 **{m['c1']}**")
                with col_mid:
                    if m["giocata"]:
                        st.error(f"🛑 **{m['gol1']} - {m['gol2']}**")
                    elif m.get("in_corso", False):
                        st.warning("🔥 **In Corso al Tavolo**")
                    else:
                        st.write("**VS**")
                        if is_admin:
                            if st.button("▶️ Metti al Tavolo", key=f"btn_avvia_{match_id}", use_container_width=True):
                                m["in_corso"] = True
                                salva_dati(db)
                                st.rerun()
                with col_s2:
                    st.info(f"🤝 **{m['c2']}**")

                if is_admin:
                    with st.expander(f"⚙️ Gestisci Risultato: {m['c1']} vs {m['c2']}"):
                        rg1 = st.radio("Gol S1", list(range(8)), index=int(m.get('gol1', 0)), horizontal=True, key=f"rg1_{match_id}")
                        rg2 = st.radio("Gol S2", list(range(8)), index=int(m.get('gol2', 0)), horizontal=True, key=f"rg2_{match_id}")
                        if st.button("💾 Salva Risultato", key=f"save_{match_id}", use_container_width=True):
                            m['gol1'] = rg1
                            m['gol2'] = rg2
                            m['giocata'] = True
                            m['in_corso'] = False
                            ricalcola_classifiche_gironi()
                            salva_dati(db)
                            st.success("Salvato e aggiornato!")
                            st.rerun()

    if is_admin:
        st.markdown("---")
        btn_testo = "🔄 Aggiorna Tabelloni Fasi Finali con Classifiche Ricalcolate" if db.get("fasi_finali_configurate", False) else "🏆 Genera Fasi Finali (Fascia A e Fascia B)"
        if st.button(btn_testo, use_container_width=True):
            classificate_a = {}
            classificate_b = {}
            for g_nome in db["gironi"]:
                sorted_c = sorted(db["punti_gironi"][g_nome].items(), key=lambda x: x[1], reverse=True)
                squadre_girone = [c[0] for c in sorted_c]
                classificate_a[g_nome] = squadre_girone[:4]
                classificate_b[g_nome] = squadre_girone[4:]
            
            abbinamenti_a = crea_abbinamenti_protetti(classificate_a)
            abbinamenti_b = crea_abbinamenti_protetti(classificate_b)
            
            turno_a_iniziale = []
            for i, (s1_info, s2_info) in enumerate(abbinamenti_a):
                turno_a_iniziale.append({
                    "id": f"fa_t1_m{i}",
                    "s1": s1_info[0], "g1": s1_info[1],
                    "s2": s2_info[0], "g2": s2_info[1],
                    "giocata": False, "gol1": 0, "gol2": 0, "vincente": None
                })
                
            turno_b_iniziale = []
            for i, (s1_info, s2_info) in enumerate(abbinamenti_b):
                turno_b_iniziale.append({
                    "id": f"fb_t1_m{i}",
                    "s1": s1_info[0], "g1": s1_info[1],
                    "s2": s2_info[0], "g2": s2_info[1],
                    "giocata": False, "gol1": 0, "gol2": 0, "vincente": None
                })
                
            if not db.get("fasi_finali_configurate", False):
                db["tabellone_a"] = [ {"turno": 1, "partite": turno_a_iniziale} ]
                db["tabellone_b"] = [ {"turno": 1, "partite": turno_b_iniziale} ]
                db["terzo_quarto_a"] = []
                db["terzo_quarto_b"] = []
            else:
                if db["tabellone_a"]:
                    db["tabellone_a"][0]["partite"] = turno_a_iniziale
                else:
                    db["tabellone_a"] = [ {"turno": 1, "partite": turno_a_iniziale} ]
                if db["tabellone_b"]:
                    db["tabellone_b"][0]["partite"] = turno_b_iniziale
                else:
                    db["tabellone_b"] = [ {"turno": 1, "partite": turno_b_iniziale} ]

            db["stato"] = "fasi_finali"
            db["fasi_finali_configurate"] = True
            salva_dati(db)
            st.success("Operazione completata con successo! Ritorno alle Fasi Finali...")
            st.rerun()

# 3. FASI FINALI
elif db["stato"] == "fasi_finali":
    st.subheader("🏆 Fasi Finali: Tabelloni a Eliminazione Diretta")
    st.info("💡 Gestione completa turni finali con possibilità di modifica risultati.")
    
    tab_a_view, tab_b_view = st.tabs(["⭐ Fascia A (Torneo Principale)", "🔻 Fascia B (Torneo Secondario)"])
    
    def gestisci_tabellone(chiave_tabellone, chiave_34, titolo_tab):
        st.markdown(f"### 📋 {titolo_tab}")
        turni_tab = db[chiave_tabellone]
        totale_turni = len(turni_tab)
        
        mappa_girone = {}
        for g, lista_sq in db["gironi"].items():
            for sq in lista_sq:
                mappa_girone[sq] = g

        for turno_obj in turni_tab:
            t_num = turno_obj["turno"]
            nome_etichetta = ottieni_nome_turno(t_num, totale_turni)
            st.markdown(f"#### 🚩 {nome_etichetta}")
            
            partite_turno = turno_obj["partite"]
            tutti_giocati = True
            vincitori_turno = []
            perdenti_turno = []
            
            for idx, m in enumerate(partite_turno):
                match_id = m['id']
                s1_nome = m['s1']
                s2_nome = m['s2']
                
                if s2_nome == "RIPOSO":
                    m['giocata'] = True
                    m['vincente'] = s1_nome
                    vincitori_turno.append(s1_nome)
                    st.success(f"🟢 **{s1_nome}** passa il turno automaticamente (Bye).")
                    continue
                elif s1_nome == "RIPOSO":
                    m['giocata'] = True
                    m['vincente'] = s2_nome
                    vincitori_turno.append(s2_nome)
                    st.success(f"🟢 **{s2_nome}** passa il turno automaticamente (Bye).")
                    continue
                
                with st.container(border=True):
                    col_s1, col_mid, col_s2 = st.columns([4, 2.5, 4], gap="small")
                    with col_s1:
                        st.info(f"🤝 **{s1_nome}** ({m.get('g1', '')})")
                    with col_mid:
                        if m["giocata"]:
                            st.error(f"🛑 **{m['gol1']} - {m['gol2']}**\nVince: **{m['vincente']}**")
                            vincente_match = m['vincente']
                            vincitori_turno.append(vincente_match)
                            perdente_match = s2_nome if vincente_match == s1_nome else s1_nome
                            perdenti_turno.append(perdente_match)
                        else:
                            tutti_giocati = False
                            st.write("**VS**")
                    with col_s2:
                        st.info(f"🤝 **{s2_nome}** ({m.get('g2', '')})")
                    
                    if is_admin:
                        with st.expander(f"⚙️ Inserisci / Modifica Risultato: {s1_nome} vs {s2_nome}"):
                            rg1 = st.radio("Gol S1", list(range(8)), index=int(m.get('gol1', 0)), horizontal=True, key=f"rg1_{match_id}")
                            rg2 = st.radio("Gol S2", list(range(8)), index=int(m.get('gol2', 0)), horizontal=True, key=f"rg2_{match_id}")
                            if st.button("💾 Salva / Aggiorna Risultato", key=f"save_{match_id}", use_container_width=True):
                                m['gol1'] = rg1
                                m['gol2'] = rg2
                                m['giocata'] = True
                                if rg1 > rg2:
                                    m['vincente'] = s1_nome
                                elif rg2 > rg1:
                                    m['vincente'] = s2_nome
                                else:
                                    m['vincente'] = s1_nome
                                salva_dati(db)
                                st.success("Risultato aggiornato con successo!")
                                st.rerun()
                
            if tutti_giocati and nome_etichetta == "⚔️ SEMIFINALI" and len(perdenti_turno) >= 2 and not db[chiave_34]:
                if is_admin:
                    p1, p2 = perdenti_turno[0], perdenti_turno[1]
                    if p1 != p2:
                        db[chiave_34] = [{
                            "id": f"{chiave_tabellone}_terzo_quarto",
                            "s1": p1, "g1": mappa_girone.get(p1, ""),
                            "s2": p2, "g2": mappa_girone.get(p2, ""),
                            "giocata": False, "gol1": 0, "gol2": 0, "vincente": None
                        }]
                        salva_dati(db)

            if tutti_giocati and len(partite_turno) > 1:
                prossimo_turno_num = t_num + 1
                vincitori_con_girone = [(v, mappa_girone.get(v, "Sconosciuto")) for v in vincitori_turno]
                nuove_partite = []
                for i in range(0, len(vincitori_con_girone), 2):
                    if i + 1 < len(vincitori_con_girone):
                        s1_info = vincitori_con_girone[i]
                        s2_info = vincitori_con_girone[i+1]
                        nuove_partite.append({
                            "id": f"{chiave_tabellone}_t{prossimo_turno_num}_m{i//2}",
                            "s1": s1_info[0], "g1": s1_info[1],
                            "s2": s2_info[0], "g2": s2_info[1],
                            "giocata": False, "gol1": 0, "gol2": 0, "vincente": None
                        })
                
                turno_esistente = next((t for t in turni_tab if t['turno'] == prossimo_turno_num), None)
                if turno_esistente and is_admin:
                    for idx_p, p_nuova in enumerate(nuove_partite):
                        if idx_p < len(turno_esistente["partite"]):
                            turno_esistente["partite"][idx_p]["s1"] = p_nuova["s1"]
                            turno_esistente["partite"][idx_p]["g1"] = p_nuova["g1"]
                            turno_esistente["partite"][idx_p]["s2"] = p_nuova["s2"]
                            turno_esistente["partite"][idx_p]["g2"] = p_nuova["g2"]
                    salva_dati(db)
                elif not turno_esistente and is_admin and nuove_partite:
                    turni_tab.append({"turno": prossimo_turno_num, "partite": nuove_partite})
                    salva_dati(db)
                    st.success(f"🎉 Turno successivo generato con successo!")
                    st.rerun()

        if db[chiave_34]:
            st.markdown("#### 🥉 FINALE 3° / 4° POSTO")
            tq_match = db[chiave_34][0]
            tq_id = tq_match['id']
            
            with st.container(border=True):
                col_s1, col_mid, col_s2 = st.columns([4, 2.5, 4], gap="small")
                with col_s1:
                    st.info(f"🤝 **{tq_match['s1']}** ({tq_match.get('g1', '')})")
                with col_mid:
                    if tq_match["giocata"]:
                        st.error(f"🛑 **{tq_match['gol1']} - {tq_match['gol2']}**\nVince 3° Posto: **{tq_match['vincente']}**")
                    else:
                        st.write("**VS**")
                with col_s2:
                    st.info(f"🤝 **{tq_match['s2']}** ({tq_match.get('g2', '')})")
                    
                if is_admin:
                    with st.expander(f"⚙️ Inserisci / Modifica 3°/4° Posto"):
                        rg1 = st.radio("Gol S1", list(range(8)), index=int(tq_match.get('gol1', 0)), horizontal=True, key=f"tq_rg1_{tq_id}")
                        rg2 = st.radio("Gol S2", list(range(8)), index=int(tq_match.get('gol2', 0)), horizontal=True, key=f"tq_rg2_{tq_id}")
                        if st.button("💾 Salva 3°/4° Posto", key=f"tq_save_{tq_id}", use_container_width=True):
                            tq_match['gol1'] = rg1
                            tq_match['gol2'] = rg2
                            tq_match['giocata'] = True
                            if rg1 > rg2:
                                tq_match['vincente'] = tq_match['s1']
                            elif rg2 > rg1:
                                tq_match['vincente'] = tq_match['s2']
                            else:
                                tq_match['vincente'] = tq_match['s1']
                            salva_dati(db)
                            st.success("Risultato 3°/4° posto salvato!")
                            st.rerun()

    with tab_a_view:
        gestisci_tabellone("tabellone_a", "terzo_quarto_a", "Tabellone Eliminazione Diretta - Fascia A")
        
    with tab_b_view:
        gestisci_tabellone("tabellone_b", "terzo_quarto_b", "Tabellone Eliminazione Diretta - Fascia B")
