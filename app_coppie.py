import json
import os
import random
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=4000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(page_title="Torneo Coppie Fisse Live", page_icon="🏆", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@700&display=swap');
:root{--cyan:#00F0FF;--magenta:#FF00E5;--acid:#00FF88;--gold:#FFC700;--bg:#050510}
.stApp{background:radial-gradient(120% 80% at 50% 0%,#1a1440 0%,#0a0a1e 45%,#050510 100%);color:#EAF0FF;font-family:'Space Grotesk',sans-serif}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0e0e26,#050510);border-right:1px solid rgba(0,240,255,0.15)}
h1{letter-spacing:3px!important;text-transform:uppercase!important;text-shadow:0 0 15px #00F0FF!important}
.cyber-card{background:rgba(14,14,30,0.88);border:1px solid rgba(0,240,255,0.25);border-left:3px solid var(--cyan);border-radius:4px 16px 4px 16px;backdrop-filter:blur(12px);box-shadow:0 0 20px rgba(0,240,255,0.12);padding:16px;margin-bottom:10px}
.cyber-card-gold{background:linear-gradient(135deg,rgba(30,25,10,0.9),rgba(20,15,5,0.9));border:1.5px solid var(--gold);border-radius:8px 20px;padding:20px;box-shadow:0 0 30px rgba(255,199,0,0.25);text-align:center}
.match-live-card{background:linear-gradient(135deg,rgba(20,20,45,0.98),rgba(10,10,25,0.98));border:1.5px solid var(--cyan);border-radius:6px 18px;padding:16px;text-align:center;box-shadow:0 0 30px rgba(0,240,255,0.25);margin-bottom:12px;position:relative;overflow:hidden}
.match-live-card:before{content:"";position:absolute;top:0;left:-100%;right:0;height:2px;background:linear-gradient(90deg,transparent,#00F0FF,#FF00E5,transparent);animation:scan 2s linear infinite}
.rank-row{display:flex;justify-content:space-between;align-items:center;background:rgba(15,15,35,0.65);border-left:3px solid transparent;border-bottom:1px solid rgba(255,255,255,0.06);padding:12px 14px;margin-bottom:2px}
.rank-row.top4{border-left-color:var(--acid);background:rgba(0,255,136,0.08)}
div.stButton>button{background:linear-gradient(180deg,#16162E,#0E0E22)!important;border:1.2px solid #00F0FF!important;color:#00F0FF!important;border-radius:6px 14px!important;font-family:'JetBrains Mono'!important;height:54px!important}
div.stButton>button:hover{background:#00F0FF!important;color:#000!important;box-shadow:0 0 25px #00F0FF!important}
div[data-baseweb="select"]>div{background:rgba(10,10,25,0.95)!important;border:1.5px solid #00F0FF!important;border-radius:8px 16px!important;box-shadow:0 0 20px rgba(0,240,255,0.18)!important;min-height:56px!important}
@keyframes scan{0%{transform:translateX(0)}100%{transform:translateX(200%)}}
</style>
""", unsafe_allow_html=True)

DB_FILE = "coppie_data_multi.json"

def carica_dati():
    dati_default = {"tornei": {}, "admin_pin": "0000"}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                dati_salvati = json.load(f)
                if "tornei" not in dati_salvati:
                    return dati_default
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

def ricalcola_classifiche_gironi(torneo_selezionato):
    t_data = db["tornei"][torneo_selezionato]
    for g_nome, coppie_lista in t_data["gironi"].items():
        stats = {c: {"punti": 0, "gf": 0, "gs": 0, "dr": 0, "scontri_diretti_pt": 0} for c in coppie_lista}
        if g_nome in t_data["calendario_gironi"]:
            for turno_obj in t_data["calendario_gironi"][g_nome]:
                for m in turno_obj["partite"]:
                    if m.get("giocata", False):
                        c1, c2 = m["c1"], m["c2"]
                        g1, g2 = m["gol1"], m["gol2"]
                        diff = abs(g1 - g2)
                        if g1 > g2:
                            pt_s1, pt_s2 = (3, 0) if diff >= 2 else (2, 1)
                        elif g2 > g1:
                            pt_s1, pt_s2 = (0, 3) if diff >= 2 else (1, 2)
                        else:
                            pt_s1, pt_s2 = 2, 2
                        stats[c1]["punti"] += pt_s1
                        stats[c2]["punti"] += pt_s2
                        stats[c1]["gf"] += g1
                        stats[c1]["gs"] += g2
                        stats[c2]["gf"] += g2
                        stats[c2]["gs"] += g1
            for c in coppie_lista:
                stats[c]["dr"] = stats[c]["gf"] - stats[c]["gs"]
        t_data["punti_gironi"][g_nome] = stats

def calcola_partite_giocate_coppia(torneo_selezionato, g_nome, coppia):
    t_data = db["tornei"][torneo_selezionato]
    giocate, totali = 0, 0
    if g_nome in t_data["calendario_gironi"]:
        for turno_obj in t_data["calendario_gironi"][g_nome]:
            for m in turno_obj["partite"]:
                if m["c1"] == coppia or m["c2"] == coppia:
                    totali += 1
                    if m.get("giocata", False):
                        giocate += 1
    return giocate, totali

def renderizza_classifica_stile_card(torneo_selezionato, g_nome):
    t_data = db["tornei"][torneo_selezionato]
    dati_girone = t_data["punti_gironi"][g_nome]
    sorted_c = sorted(dati_girone.items(), key=lambda x: (x[1]["punti"], x[1]["dr"], x[1]["gf"]), reverse=True)
    for idx, (coppia, info) in enumerate(sorted_c):
        gioc, tot = calcola_partite_giocate_coppia(torneo_selezionato, g_nome, coppia)
        is_top = idx < 4
        dot = "#00FF88" if is_top else "#7A7FB5"
        st.markdown(f'<div class="rank-row {"top4" if is_top else ""}"><div style="display:flex;gap:10px;align-items:center;"><span style="font-family:JetBrains Mono;font-size:11px;color:{dot};">{idx+1:02d}</span><span style="font-weight:700;color:#fff;">{coppia}</span><span style="font-size:10px;color:#7A7FB5;">{gioc}/{tot}</span></div><div style="display:flex;gap:12px;font-family:JetBrains Mono;font-size:12px;"><span style="color:#FFC700;font-weight:800;">{info["punti"]} PT</span><span style="color:{"#00FF88" if info["dr"]>=0 else "#FF4D6D"};">{info["dr"]:+d}</span></div></div>', unsafe_allow_html=True)

def genera_pdf_coppie(torneo_selezionato):
    t_data = db["tornei"][torneo_selezionato]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Torneo: {torneo_selezionato} - Schema Gironi", 0, 1, "C")
    pdf.ln(5)
    for g_nome, turni in t_data["calendario_gironi"].items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"--- {g_nome} ---", 0, 1, "L")
        for turno_obj in turni:
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Turno {turno_obj['turno']}", 0, 1, "L")
            pdf.set_font("Arial", "", 10)
            for idx, m in enumerate(turno_obj["partite"]):
                risultato = f"{m['gol1']} - {m['gol2']}" if m.get("giocata", False) else "Da giocare"
                riga = f"  {m['c1']} VS {m['c2']} -> {risultato}"
                pdf.cell(0, 6, riga.encode("latin-1", "ignore").decode("latin-1"), 0, 1, "L")
            pdf.ln(2)
    return bytes(pdf.output())

def ottieni_nome_turno_dinamico(num_partite_turno):
    if num_partite_turno == 1:
        return "FINALE"
    elif num_partite_turno == 2:
        return "SEMIFINALI"
    elif num_partite_turno == 4:
        return "QUARTI DI FINALE"
    elif num_partite_turno == 8:
        return "OTTAVI DI FINALE"
    else:
        return f"Eliminazione Diretta ({num_partite_turno*2} Coppie)"

def crea_abbinamenti_fascia_a_perfetti(classificate_per_girone):
    nomi_g = list(classificate_per_girone.keys())
    if len(nomi_g) < 4:
        return crea_abbinamenti_rigorosi_generico(classificate_per_girone)
    g0, g1, g2, g3 = nomi_g[0], nomi_g[1], nomi_g[2], nomi_g[3]
    squadre_g = {g: classificate_per_girone[g] for g in nomi_g}
    def get_sq(g_nome, pos_idx):
        lst = squadre_g.get(g_nome, [])
        if pos_idx < len(lst):
            return (lst[pos_idx], g_nome, pos_idx + 1)
        return ("RIPOSO", g_nome, pos_idx + 1)
    abbinamenti = [
        (get_sq(g0, 0), get_sq(g1, 3)),
        (get_sq(g2, 2), get_sq(g3, 1)),
        (get_sq(g2, 1), get_sq(g3, 2)),
        (get_sq(g1, 0), get_sq(g0, 3)),
        (get_sq(g0, 1), get_sq(g1, 2)),
        (get_sq(g2, 3), get_sq(g3, 0)),
        (get_sq(g2, 0), get_sq(g3, 3)),
        (get_sq(g1, 1), get_sq(g0, 2)),
    ]
    return abbinamenti

def crea_abbinamenti_rigorosi_generico(classificate_per_girone):
    nomi_gironi = list(classificate_per_girone.keys())
    prime, seconde, terze, quarte = [], [], [], []
    for g_n in nomi_gironi:
        lst = classificate_per_girone[g_n]
        if len(lst) > 0: prime.append((lst[0], g_n, 1))
        if len(lst) > 1: seconde.append((lst[1], g_n, 2))
        if len(lst) > 2: terze.append((lst[2], g_n, 3))
        if len(lst) > 3: quarte.append((lst[3], g_n, 4))
    abbinamenti = []
    for i in range(len(prime)):
        p = prime[i]
        q = quarte[(i + 1) % len(quarte)] if len(quarte) > 0 else ("RIPOSO", "", 4)
        abbinamenti.append((p, q))
    for i in range(len(seconde)):
        s = seconde[i]
        t = terze[(i + 1) % len(terze)] if len(terze) > 0 else ("RIPOSO", "", 3)
        abbinamenti.append((s, t))
    return abbinamenti

def crea_abbinamenti_fascia_b(classificate_per_girone):
    tutte_b = []
    for g_n, lista in classificate_per_girone.items():
        for idx in range(4, len(lista)):
            tutte_b.append((lista[idx], g_n, idx + 1))
    random.shuffle(tutte_b)
    abbinamenti = []
    for i in range(0, len(tutte_b), 2):
        if i + 1 < len(tutte_b):
            abbinamenti.append((tutte_b[i], tutte_b[i + 1]))
        else:
            abbinamenti.append((tutte_b[i], ("RIPOSO", "", 0)))
    return abbinamenti

def posticipa_partita_coda(torneo_selezionato, match_id_da_spostare):
    t_data = db["tornei"][torneo_selezionato]
    for g_nome, turni in t_data["calendario_gironi"].items():
        tutte_partite_girone = []
        for turno_obj in turni:
            tutte_partite_girone.extend(turno_obj["partite"])
        idx_trovato = -1
        for i, m in enumerate(tutte_partite_girone):
            if m["id"] == match_id_da_spostare:
                idx_trovato = i
                break
        if idx_trovato != -1:
            if idx_trovato + 2 < len(tutte_partite_girone):
                partita = tutte_partite_girone.pop(idx_trovato)
                tutte_partite_girone.insert(idx_trovato + 2, partita)
                it = iter(tutte_partite_girone)
                for turno_obj in turni:
                    turno_obj["partite"] = [next(it) for _ in range(len(turno_obj["partite"]))]
                for t_obj in turni:
                    for m in t_obj["partite"]:
                        if m["id"] == match_id_da_spostare:
                            m["in_corso"] = False
                            m["tavolo"] = None
                salva_dati(db)
                return True
    return False

# --- ADMIN SIDEBAR ---
admin_param = st.query_params.get("admin", "false")
is_admin_autenticato = admin_param == "true"
modalita_admin = st.sidebar.checkbox("Modalita Amministratore (PIN)", value=is_admin_autenticato)
is_admin = False
if modalita_admin:
    if is_admin_autenticato:
        is_admin = True
        st.sidebar.success("Accesso Admin Attivo")
        if st.sidebar.button("Logout Admin", use_container_width=True):
            st.query_params["admin"] = "false"
            st.rerun()
    else:
        pin_inserito = st.sidebar.text_input("Inserisci PIN Admin", type="password")
        if pin_inserito == db["admin_pin"]:
            st.query_params["admin"] = "true"
            st.rerun()
        elif pin_inserito:
            st.sidebar.error("PIN errato.")
else:
    if is_admin_autenticato:
        st.query_params["admin"] = "false"
        st.rerun()
st.sidebar.markdown("---")
st.markdown('<div style="text-align:left;margin-bottom:8px;"><span style="color:#00F0FF;font-size:13px;letter-spacing:2px;font-weight:bold;">TOURNAMENT CIRCUIT</span><h1 style="font-size:28px;margin:4px 0 12px 0;">Torneo Coppie Fisse Live</h1></div>', unsafe_allow_html=True)
tornei_disponibili = [t for t in db["tornei"].keys() if t not in ["Torneo Principale (PRO)", "Torneo Secondario (Amatoriale)"]]
if not tornei_disponibili:
    st.info("Nessun torneo attivo. Usa pannello admin per crearne uno.")
torneo_selezionato = st.selectbox("Seleziona il Torneo:", options=tornei_disponibili if tornei_disponibili else ["Nessun Torneo Disponibile"], key="selettore_torneo_principale")
if not tornei_disponibili:
    if is_admin:
        with st.sidebar.expander("Crea Nuovo Torneo", expanded=True):
            nuovo_nome_torneo = st.text_input("Nome Torneo")
            col_nc1, col_nc2 = st.columns(2)
            with col_nc1:
                nc_tavoli = st.number_input("N. Biliardini", min_value=1, max_value=10, value=6)
                nc_gironi = st.number_input("N. Gironi", min_value=1, max_value=8, value=4)
            with col_nc2:
                nc_max = st.number_input("Max Coppie", min_value=2, max_value=128, value=32)
            if st.button("Crea Torneo Avanzato", use_container_width=True):
                if nuovo_nome_torneo.strip() and nuovo_nome_torneo.strip().upper() not in db["tornei"]:
                    db["tornei"][nuovo_nome_torneo.strip().upper()] = {"stato": "iscrizioni_aperte","coppie": [],"coda": [],"max_coppie": int(nc_max),"num_tavoli": int(nc_tavoli),"num_gironi": int(nc_gironi),"gironi": {},"calendario_gironi": {},"punti_gironi": {},"pagamenti": {},"fasi_finali_configurate": False,"tabellone_a": [],"tabellone_b": [],"terzo_quarto_a": [],"terzo_quarto_b": []}
                    salva_dati(db)
                    st.success("Torneo creato!")
                    st.rerun()
    st.stop()
t_data = db["tornei"][torneo_selezionato]
if "coda" not in t_data: t_data["coda"] = []
if "max_coppie" not in t_data: t_data["max_coppie"] = 32
if "pagamenti" not in t_data: t_data["pagamenti"] = {}
salva_dati(db)
if is_admin:
    with st.sidebar.expander("Crea Nuovo Torneo"):
        nuovo_nome_torneo = st.text_input("Nome Torneo / Categoria")
        col_nc1, col_nc2 = st.columns(2)
        with col_nc1:
            nc_tavoli = st.number_input("N. Biliardini", min_value=1, max_value=10, value=6, key="tav_new")
            nc_gironi = st.number_input("N. Gironi", min_value=1, max_value=8, value=4, key="gir_new")
        with col_nc2:
            nc_max = st.number_input("Max Coppie", min_value=2, max_value=128, value=32, key="max_new")
        if st.button("Crea Torneo Avanzato", use_container_width=True):
            if nuovo_nome_torneo.strip() and nuovo_nome_torneo.strip().upper() not in db["tornei"]:
                db["tornei"][nuovo_nome_torneo.strip().upper()] = {"stato": "iscrizioni_aperte","coppie": [],"coda": [],"max_coppie": int(nc_max),"num_tavoli": int(nc_tavoli),"num_gironi": int(nc_gironi),"gironi": {},"calendario_gironi": {},"punti_gironi": {},"pagamenti": {},"fasi_finali_configurate": False,"tabellone_a": [],"tabellone_b": [],"terzo_quarto_a": [],"terzo_quarto_b": []}
                salva_dati(db)
                st.success("Torneo creato!")
                st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.subheader("Elimina Torneo")
    tornei_eliminabili = list(db["tornei"].keys())
    if tornei_eliminabili:
        torneo_da_eliminare = st.sidebar.selectbox("Seleziona torneo da rimuovere", options=tornei_eliminabili, key="sel_del_torneo")
        conferma_canc_torneo = st.sidebar.checkbox("Conferma eliminazione definitiva", key="chk_del_torneo")
        if st.sidebar.button("Elimina Torneo Selezionato", use_container_width=True):
            if conferma_canc_torneo:
                if torneo_da_eliminare in db["tornei"]:
                    del db["tornei"][torneo_da_eliminare]
                    salva_dati(db)
                    st.success(f"Torneo '{torneo_da_eliminare}' eliminato!")
                    st.rerun()
            else:
                st.sidebar.warning("Spunta la casella di conferma.")
st.sidebar.markdown("Pannello di Controllo")
if t_data["stato"] != "iscrizioni_aperte" and t_data["stato"] != "setup":
    pdf_data = genera_pdf_coppie(torneo_selezionato)
    st.sidebar.download_button(label="Scarica Schema PDF", data=pdf_data, file_name=f"schema_{torneo_selezionato.lower()}.pdf", mime="application/pdf", use_container_width=True)
    st.sidebar.markdown("---")
if is_admin and t_data["stato"] == "fasi_finali":
    if st.sidebar.button("Torna ai Gironi", use_container_width=True):
        t_data["stato"] = "gironi"
        salva_dati(db)
        st.rerun()
    st.sidebar.markdown("---")
st.sidebar.subheader("Zona Pericolo")
if is_admin:
    conferma_reset = st.sidebar.checkbox("Conferma reset torneo", key="checkbox_reset_gara")
    if st.sidebar.button("Ricomincia da zero", use_container_width=True):
        if conferma_reset:
            db["tornei"][torneo_selezionato] = {"stato": "iscrizioni_aperte","coppie": [],"coda": [],"max_coppie": t_data.get("max_coppie", 32),"num_tavoli": t_data.get("num_tavoli", 6),"num_gironi": t_data.get("num_gironi", 4),"gironi": {},"calendario_gironi": {},"punti_gironi": {},"pagamenti": {},"fasi_finali_configurate": False,"tabellone_a": [],"tabellone_b": [],"terzo_quarto_a": [],"terzo_quarto_b": []}
            salva_dati(db)
            st.success("Torneo azzerato!")
            st.rerun()
else:
    st.sidebar.info("Accedi come admin per resettare.")

if t_data["stato"] == "iscrizioni_aperte":
    if is_admin:
        st.markdown("### Gestione Pagamenti")
        tutte_le_coppie_iscritte = sorted(list(set(t_data.get("coppie", []) + t_data.get("coda", []))))
        if tutte_le_coppie_iscritte:
            opzioni_ricerca = ["-- Mostra Tutte --"] + tutte_le_coppie_iscritte
            coppia_cercata = st.selectbox("Cerca coppia:", options=opzioni_ricerca, key=f"ricerca_{torneo_selezionato}")
            coppie_da_mostrare = [coppia_cercata] if coppia_cercata != "-- Mostra Tutte --" else tutte_le_coppie_iscritte
            for coppia in coppie_da_mostrare:
                idx = tutte_le_coppie_iscritte.index(coppia)
                parti = [p.strip() for p in coppia.split("/")]
                g1_nome = parti[0] if len(parti) > 0 else "G1"
                g2_nome = parti[1] if len(parti) > 1 else "G2"
                if coppia not in t_data["pagamenti"] or not isinstance(t_data["pagamenti"][coppia], dict):
                    t_data["pagamenti"][coppia] = {g1_nome: False, g2_nome: False}
                pagato_g1 = t_data["pagamenti"][coppia].get(g1_nome, False)
                pagato_g2 = t_data["pagamenti"][coppia].get(g2_nome, False)
                cols = st.columns([0.15, 0.70, 0.15])
                with cols[0]:
                    if st.button("EUR", key=f"pay_l_{torneo_selezionato}_{idx}", use_container_width=True):
                        t_data["pagamenti"][coppia][g1_nome] = not pagato_g1
                        salva_dati(db)
                        st.rerun()
                with cols[1]:
                    st.markdown(f'<div style="text-align:center;padding:8px;border:1px solid {"#00FF88" if pagato_g1 else "#FF4D6D"};border-radius:8px;margin-bottom:4px;">{g1_nome} - {"PAID" if pagato_g1 else "DA PAGARE"}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="text-align:center;padding:8px;border:1px solid {"#00FF88" if pagato_g2 else "#FF4D6D"};border-radius:8px;">{g2_nome} - {"PAID" if pagato_g2 else "DA PAGARE"}</div>', unsafe_allow_html=True)
                with cols[2]:
                    if st.button("EUR", key=f"pay_r_{torneo_selezionato}_{idx}", use_container_width=True):
                        t_data["pagamenti"][coppia][g2_nome] = not pagato_g2
                        salva_dati(db)
                        st.rerun()
        st.markdown("---")
    st.markdown(f"### Registrazione - {torneo_selezionato}")
    with st.form(f"form_iscrizione_{torneo_selezionato}"):
        c1_input = st.text_input("Nome Giocatore 1")
        c2_input = st.text_input("Nome Giocatore 2")
        whatsapp_paste = st.text_area("Incolla lista WhatsApp")
        submit_isc = st.form_submit_button("Registra / Importa Coppie", use_container_width=True)
        if submit_isc:
            nuove_inserite = []
            if c1_input.strip() and c2_input.strip():
                nuove_inserite.append(f"{c1_input.strip().upper()} / {c2_input.strip().upper()}")
            if whatsapp_paste.strip():
                linee = whatsapp_paste.split("\n")
                for linea in linee:
                    linea_pulita = re.sub(r'^\s*(\d+[\.\)]\s*|-\s*)', '', linea).strip()
                    if not linea_pulita: continue
                    for sep in ["/", "-", " E ", " CON "]:
                        if sep.lower() in linea_pulita.lower():
                            parti = re.split(sep, linea_pulita, flags=re.IGNORECASE)
                            if len(parti) >= 2:
                                p1 = parti[0].strip().upper(); p2 = parti[1].strip().upper()
                                if p1 and p2:
                                    nuove_inserite.append(f"{p1} / {p2}")
                                    break
            aggiunte_titolari = aggiunte_coda = 0
            for nc in nuove_inserite:
                nc_upper = nc.upper()
                if nc_upper not in t_data["coppie"] and nc_upper not in t_data["coda"]:
                    if len(t_data["coppie"]) < int(t_data["max_coppie"]):
                        t_data["coppie"].append(nc_upper); aggiunte_titolari+=1
                    else:
                        t_data["coda"].append(nc_upper); aggiunte_coda+=1
            if aggiunte_titolari>0 or aggiunte_coda>0:
                salva_dati(db); st.success(f"Aggiunte: {aggiunte_titolari} titolari e {aggiunte_coda} in coda"); st.rerun()
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### Titolari ({len(t_data['coppie'])}/{t_data['max_coppie']})")
        for idx,c in enumerate(t_data["coppie"],1):
            c1,c2=st.columns([0.8,0.2])
            with c1: st.markdown(f"<div class='cyber-card'><b>{idx}.</b> {c}</div>",unsafe_allow_html=True)
            with c2:
                if st.button("X", key=f"del_isc_{torneo_selezionato}_{idx}", use_container_width=True):
                    t_data["coppie"].remove(c)
                    if t_data["coda"]:
                        promossa=t_data["coda"].pop(0); t_data["coppie"].append(promossa)
                    salva_dati(db); st.rerun()
    with col2:
        st.markdown(f"### Coda ({len(t_data['coda'])})")
        for idx_c,c_coda in enumerate(t_data["coda"],1):
            c1,c2=st.columns([0.8,0.2])
            with c1: st.markdown(f"<div class='cyber-card' style='border-left-color:#FF8A00;'>{idx_c}. {c_coda}</div>",unsafe_allow_html=True)
            with c2:
                if st.button("X", key=f"del_coda_{torneo_selezionato}_{idx_c}", use_container_width=True):
                    t_data["coda"].remove(c_coda); salva_dati(db); st.rerun()
    if is_admin:
        st.markdown("---")
        st.markdown("### Pannello Admin: Avvio")
        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1: t_data["num_tavoli"] = st.number_input("N. Biliardini", min_value=1, max_value=10, value=int(t_data.get("num_tavoli", 6)), key=f"tav_{torneo_selezionato}")
        with col_cfg2: t_data["num_gironi"] = st.number_input("N. Gironi", min_value=1, max_value=8, value=int(t_data.get("num_gironi", 4)), key=f"gir_{torneo_selezionato}")
        with col_cfg3: t_data["max_coppie"] = st.number_input("Max Titolari", min_value=2, max_value=128, value=int(t_data.get("max_coppie", 32)), key=f"maxc_{torneo_selezionato}")
        if st.button("Avvia Torneo (Crea Gironi Casuali)", use_container_width=True):
            num_g = int(t_data["num_gironi"])
            coppie = [str(c).upper() for c in t_data["coppie"]]
            if len(coppie) < (num_g * 2):
                st.error(f"Servono almeno {num_g*2} coppie")
            else:
                random.shuffle(coppie)
                nomi_gironi = [chr(65 + i) for i in range(num_g)]
                gironi_dict = {f"Girone {g}": [] for g in nomi_gironi}
                for idx, c in enumerate(coppie):
                    g_scelto = f"Girone {nomi_gironi[idx % num_g]}"
                    gironi_dict[g_scelto].append(c)
                t_data["gironi"] = gironi_dict
                t_data["punti_gironi"] = {g: {c: {"punti": 0, "gf": 0, "gs": 0, "dr": 0, "scontri_diretti_pt": 0} for c in lst} for g, lst in gironi_dict.items()}
                # FIX APPLICATO QUI
                calendario_totale = {}
                for g_nome, lista_c in gironi_dict.items():
                    squadre = lista_c.copy()
                    if len(squadre) % 2 != 0: squadre.append("RIPOSO")
                    n = len(squadre)
                    turni_girone = []
                    for t in range(n - 1):
                        partite_turno = []
                        for i in range(n // 2):
                            s1 = squadre[i]; s2 = squadre[n - 1 - i]
                            if s1 != "RIPOSO" and s2 != "RIPOSO":
                                match_id = f"{g_nome}_t{t+1}_m{i}"
                                partite_turno.append({"id": match_id,"girone": g_nome,"c1": s1,"c2": s2,"giocata": False,"in_corso": False,"tavolo": None,"gol1": 0,"gol2": 0})
                        turni_girone.append({"turno": t + 1, "partite": partite_turno})
                        squadre = [squadre[0]] + [squadre[-1]] + squadre[1:-1]
                    calendario_totale[g_nome] = turni_girone
                t_data["calendario_gironi"] = calendario_totale
                t_data["stato"] = "gironi"
                t_data["fasi_finali_configurate"] = False
                salva_dati(db)
                st.success("Torneo avviato!")
                st.rerun()
    st.stop()
