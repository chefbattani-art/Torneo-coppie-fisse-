import json
import os
import random
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Refresh automatico ogni 5 secondi
st_autorefresh(interval=5000, debounce=False, key="auto_refresh_coppie")

st.set_page_config(
    page_title="Torneo Coppie Fisse Live - Gaming Edition",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STILE GRAFICO GAMING NEON (CYBERPUNK / HIGH-CONTRAST) ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

        /* Sfondo principale e font globale */
        .stApp {
            background: radial-gradient(circle at 50% -20%, #150a21 0%, #080511 40%, #020105 100%);
            color: #e6f1ff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 17px;
        }

        /* Sidebar in stile Console / Scuro con bordo Neon Blu */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0612 0%, #030207 100%);
            border-right: 2px solid #0066ff;
            box-shadow: 4px 0 20px rgba(0, 102, 255, 0.2);
        }

        /* Intestazioni e Titoli */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Orbitron', sans-serif !important;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        /* Neon Text Colors */
        .neon-text-cyan { color: #00f3ff !important; text-shadow: 0 0 10px rgba(0, 243, 255, 0.6); }
        .neon-text-gold { color: #ffd700 !important; text-shadow: 0 0 10px rgba(255, 215, 0, 0.6); }
        .neon-text-purple { color: #b967ff !important; text-shadow: 0 0 10px rgba(185, 103, 255, 0.6); }
        .neon-text-green { color: #00ff66 !important; text-shadow: 0 0 10px rgba(0, 255, 102, 0.6); }
        .neon-text-red { color: #ff0055 !important; text-shadow: 0 0 10px rgba(255, 0, 85, 0.6); }

        /* Card Generica con Bordo Neon Azzurro */
        .custom-card {
            background: linear-gradient(135deg, rgba(16, 23, 42, 0.8) 0%, rgba(8, 12, 24, 0.9) 100%);
            border: 1px solid #00f3ff;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
        }

        /* Pulsanti Personalizzati Gaming */
        div.stButton > button {
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            font-weight: 700;
            border-radius: 8px;
            border: 1px solid #00f3ff;
            background: linear-gradient(135deg, #091a2e 0%, #030a14 100%);
            color: #00f3ff;
            transition: all 0.3s ease-in-out;
            box-shadow: 0 0 8px rgba(0, 243, 255, 0.3);
            text-transform: uppercase;
        }
        div.stButton > button:hover {
            border-color: #b967ff;
            color: #ffffff;
            background: linear-gradient(135deg, #2a085c 0%, #120329 100%);
            box-shadow: 0 0 20px rgba(185, 103, 255, 0.8);
            transform: translateY(-2px);
        }

        /* Tab Stile Neon Gaming */
        button[data-baseweb="tab"] {
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            color: #8b949e !important;
            border-bottom: 2px solid transparent !important;
        }
        button[aria-selected="true"] {
            color: #00f3ff !important;
            border-bottom: 3px solid #00f3ff !important;
            text-shadow: 0 0 10px rgba(0, 243, 255, 0.8);
        }

        /* Dataframe / Tabelle */
        div[data-testid="stDataFrame"] {
            border: 1px solid #b967ff;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(185, 103, 255, 0.2);
        }

        /* Inputs e Selectbox */
        div[data-baseweb="select"] > div, input {
            background-color: #0d081a !important;
            border: 1px solid #00f3ff !important;
            color: #ffffff !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_FILE = "coppie_data.json"


def carica_dati():
    dati_default = {
        "stato": "setup",
        "coppie": [],
        "num_tavoli": 6,
        "num_gironi": 4,
        "admin_pin": "0000",
        "gironi": {},
        "calendario_gironi": {},
        "punti_gironi": {},
        "fasi_finali_configurate": False,
        "tabellone_a": [],
        "tabellone_b": [],
        "terzo_quarto_a": [],
        "terzo_quarto_b": [],
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
    testo = re.sub(r"^\d+[\.\-\)]?\s*", "", testo)
    return testo.strip()


def evidenzia_nome_coppia(testo_match, mia_coppia):
    return testo_match.replace(
        mia_coppia,
        f"<span style='color: #ff0055; font-weight: 900; text-shadow: 0 0 10px rgba(255,0,85,0.8);'>{mia_coppia}</span>",
    )


def ricalcola_classifiche_gironi():
    for g_nome, coppie_lista in db["gironi"].items():
        stats = {
            c: {
                "punti": 0,
                "gf": 0,
                "gs": 0,
                "dr": 0,
                "scontri_diretti_pt": {},
            }
            for c in coppie_lista
        }

        if g_nome in db["calendario_gironi"]:
            for turno_obj in db["calendario_gironi"][g_nome]:
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

            punti_gruppo = {}
            for c in coppie_lista:
                p = stats[c]["punti"]
                if p not in punti_gruppo:
                    punti_gruppo[p] = []
                punti_gruppo[p].append(c)

            for p, gruppo in punti_gruppo.items():
                if len(gruppo) > 1:
                    mini_punti = {c: 0 for c in gruppo}
                    for turno_obj in db["calendario_gironi"][g_nome]:
                        for m in turno_obj["partite"]:
                            if m.get("giocata", False):
                                c1, c2 = m["c1"], m["c2"]
                                if c1 in gruppo and c2 in gruppo:
                                    g1, g2 = m["gol1"], m["gol2"]
                                    if g1 > g2:
                                        mini_punti[c1] += 3
                                    elif g2 > g1:
                                        mini_punti[c2] += 3
                                    else:
                                        mini_punti[c1] += 1
                                        mini_punti[c2] += 1
                    for c in gruppo:
                        stats[c]["scontri_diretti_pt"] = mini_punti[c]
                else:
                    for c in gruppo:
                        stats[c]["scontri_diretti_pt"] = 0

        db["punti_gironi"][g_nome] = stats


def calcola_partite_giocate_coppia(g_nome, coppia):
    giocate = 0
    totali = 0
    if g_nome in db["calendario_gironi"]:
        for turno_obj in db["calendario_gironi"][g_nome]:
            for m in turno_obj["partite"]:
                if m["c1"] == coppia or m["c2"] == coppia:
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
                risultato = (
                    f"{m['gol1']} - {m['gol2']}"
                    if m.get("giocata", False)
                    else "Da giocare"
                )
                riga = f"  {m['c1']} VS {m['c2']} -> {risultato}"
                pdf.cell(
                    0,
                    6,
                    riga.encode("latin-1", "ignore").decode("latin-1"),
                    0,
                    1,
                    "L",
                )
            pdf.ln(2)
    return bytes(pdf.output())


def ottieni_nome_turno_dinamico(num_partite_turno):
    tot_squadre = num_partite_turno * 2
    if num_partite_turno == 1:
        return "🏆 FINALE ASSOLUTA"
    elif num_partite_turno == 2:
        return "⚔️ SEMIFINALI"
    elif num_partite_turno == 4:
        return "🔥 QUARTI DI FINALE"
    elif num_partite_turno == 8:
        return "⭐ OTTAVI DI FINALE"
    else:
        return f"Eliminazione Diretta ({tot_squadre} Coppie)"


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
        (get_sq(g0, 0), get_sq(g3, 3)),
        (get_sq(g1, 1), get_sq(g2, 2)),
        (get_sq(g1, 0), get_sq(g2, 3)),
        (get_sq(g0, 1), get_sq(g3, 2)),
        (get_sq(g2, 0), get_sq(g0, 3)),
        (get_sq(g3, 1), get_sq(g1, 2)),
        (get_sq(g2, 1), get_sq(g0, 2)),
        (get_sq(g3, 0), get_sq(g1, 3)),
    ]
    return abbinamenti


def crea_abbinamenti_rigorosi_generico(classificate_per_girone):
    nomi_gironi = list(classificate_per_girone.keys())
    prime, seconde, terze, quarte = [], [], [], []
    for g_n in nomi_gironi:
        lst = classificate_per_girone[g_n]
        if len(lst) > 0:
            prime.append((lst[0], g_n, 1))
        if len(lst) > 1:
            seconde.append((lst[1], g_n, 2))
        if len(lst) > 2:
            terze.append((lst[2], g_n, 3))
        if len(lst) > 3:
            quarte.append((lst[3], g_n, 4))

    abbinamenti = []
    for i in range(len(prime)):
        p = prime[i]
        q = (
            quarte[(i + 1) % len(quarte)]
            if len(quarte) > 0
            else ("RIPOSO", "", 4)
        )
        abbinamenti.append((p, q))
    for i in range(len(seconde)):
        s = seconde[i]
        t = (
            terze[(i + 1) % len(terze)] if len(terze) > 0 else ("RIPOSO", "", 3)
        )
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


def verifica_conflitto_stesso_girone(s1_nome, s2_nome, mappa_girone_pos):
    g1, p1 = mappa_girone_pos.get(s1_nome, ("", 0))
    g2, p2 = mappa_girone_pos.get(s2_nome, ("", 0))
    if g1 and g2 and g1 == g2:
        if {p1, p2} == {1, 2}:
            return True
    return False


# --- BARRA LATERALE (GAMING CONTROL CENTER) ---
st.sidebar.markdown(
    "<h2 class='neon-text-cyan' style='font-size: 20px; text-align: center;'>⚙️ CONTROL PANEL</h2>",
    unsafe_allow_html=True,
)

if db["stato"] != "setup":
    pdf_data = genera_pdf_coppie()
    st.sidebar.download_button(
        label="📥 Scarica Schema (PDF)",
        data=pdf_data,
        file_name="schema_gironi_torneo.pdf",
        mime="application/pdf",
        use_container_width=True,
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
    if st.sidebar.button(
        "⚙️ Setup Iniziale", use_container_width=True
    ):
        st.session_state["mostra_setup"] = not st.session_state.get(
            "mostra_setup", False
        )

if is_admin and db["stato"] == "fasi_finali":
    if st.sidebar.button(
        "🔙 Torna ai Gironi", use_container_width=True
    ):
        db["stato"] = "gironi"
        salva_dati(db)
        st.rerun()
    st.sidebar.markdown("---")

st.sidebar.markdown("<h4 class='neon-text-red'>⚠️ Danger Zone</h4>", unsafe_allow_html=True)
if is_admin:
    conferma_reset = st.sidebar.checkbox(
        "Conferma Reset Totale", key="checkbox_reset_gara"
    )
    if st.sidebar.button("🔄 Reset Torneo", use_container_width=True):
        if conferma_reset:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Torneo azzerato!")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Spunta la casella per confermare.")
else:
    st.sidebar.info("🔐 Accedi come Admin per i comandi avanzati.")

# --- INTERFACCIA PRINCIPALE ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 25px; padding: 20px; background: linear-gradient(135deg, rgba(9, 26, 46, 0.8) 0%, rgba(18, 3, 41, 0.9) 100%); border-radius: 16px; border: 2px solid #00f3ff; box-shadow: 0 0 25px rgba(0, 243, 255, 0.3);">
        <h1 style="font-size: 34px; margin: 0; color: #ffffff; text-shadow: 0 0 15px #00f3ff, 0 0 25px #b967ff;">
            🏆 TORNEO COPPIE FISSE LIVE
        </h1>
        <p style="font-size: 16px; color: #ffd700; margin: 8px 0 0 0; font-weight: 700; letter-spacing: 2px; text-shadow: 0 0 8px rgba(255, 215, 0, 0.5);">
            ⚡ REGOLAMENTO 3 TOCCHI UISP • GAMING NEON EDITION ⚡
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("ℹ️ Regolamento e Info Torneo"):
    st.markdown(
        """
        L'app gestisce autonomamente l'avanzamento delle partite e delle fasi a eliminazione.
        - **Inserimento Risultati:** Chi vince la partita deve registrare il punteggio esatto.
        - **Coda Biliardini:** Si prega di farsi trovare pronti a salire al tavolo appena si libera!
        """,
        unsafe_allow_html=True,
    )

# Banner Avviso Neon Rosso
st.markdown(
    """
    <div style="padding: 14px; background: linear-gradient(135deg, rgba(64, 0, 21, 0.8) 0%, rgba(20, 0, 7, 0.9) 100%); border: 2px solid #ff0055; border-radius: 10px; font-size: 15px; color: #ffffff; margin-bottom: 15px; font-weight: bold; text-align: center; box-shadow: 0 0 15px rgba(255, 0, 85, 0.4);">
        🚨 CHI VINCE INSERISCE IL RISULTATO. CONSULTA LA CODA TAVOLI E TIENITI PRONTO A GIOCARE!
    </div>
    """,
    unsafe_allow_html=True,
)

# Banner Aggiornamento Neon Azzurro
st.markdown(
    """
    <div style="padding: 10px; background: rgba(9, 26, 46, 0.6); border: 1px solid #00f3ff; border-radius: 8px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);">
        🔄 <a href="javascript:window.location.reload(true)" style="text-decoration: none; color: #00f3ff; font-weight: bold; font-size: 15px; text-shadow: 0 0 8px rgba(0,243,255,0.6);">
            Clicca qui per aggiornare manualmente la diretta
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- SELETTORE COPPIA ---
tutte_le_coppie = []
for g_lst in db["gironi"].values():
    tutte_le_coppie.extend(g_lst)

if not tutte_le_coppie and db.get("coppie"):
    tutte_le_coppie = db["coppie"]

opzioni_selettore = ["-- Seleziona la tua coppia per accedere --"] + sorted(tutte_le_coppie)

coppia_url = st.query_params.get("coppia", "-- Seleziona la tua coppia per accedere --")
if coppia_url not in opzioni_selettore:
    coppia_url = "-- Seleziona la tua coppia per accedere --"

coppia_selezionata = st.selectbox(
    "📱 SELEZIONA LA TUA COPPIA:",
    options=opzioni_selettore,
    index=opzioni_selettore.index(coppia_url),
    key="widget_selezione_coppia",
)

if coppia_selezionata != coppia_url:
    st.query_params["coppia"] = coppia_selezionata
    st.rerun()

if is_admin:
    st.success("🛡️ Modalità Admin Attiva: Navigazione Libera")
elif coppia_selezionata == "-- Seleziona la tua coppia per accedere --":
    st.warning("⚠️ Per accedere al torneo, inserire i risultati e vedere i tavoli, seleziona la tua coppia in alto.")
    st.stop()
else:
    st.markdown(f"<h3 class='neon-text-green'>✅ LOGIN EFFETTUATO: {coppia_selezionata}</h3>", unsafe_allow_html=True)

# DASHBOARD INDIVIDUALE COPPIA
if not is_admin or coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
    if coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
        with st.expander(f"👁️ DASHBOARD SQUADRA: {coppia_selezionata}", expanded=True):
            girone_mio = None
            pos_mia = None
            info_mie = None
            for g_nome, lista_c in db["gironi"].items():
                if coppia_selezionata in lista_c:
                    girone_mio = g_nome
                    ricalcola_classifiche_gironi()
                    if g_nome in db["punti_gironi"]:
                        dati_g = db["punti_gironi"][g_nome]
                        sorted_c = sorted(
                            dati_g.items(),
                            key=lambda x: (
                                x[1]["punti"],
                                x[1]["scontri_diretti_pt"],
                                x[1]["dr"],
                                x[1]["gf"],
                            ),
                            reverse=True,
                        )
                        for idx, (c_nome, stats) in enumerate(sorted_c):
                            if c_nome == coppia_selezionata:
                                pos_mia = idx + 1
                                info_mie = stats
                    break

            # Card personalizzata con indicatori neon
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, rgba(19, 9, 36, 0.9) 0%, rgba(9, 26, 46, 0.9) 100%); border: 2px solid #b967ff; border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 0 20px rgba(185, 103, 255, 0.3);">
                    <div style="font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #00f3ff; font-weight: bold; margin-bottom: 4px;">STATISTICHE CORRENTI</div>
                    <div style="font-size: 24px; font-weight: 900; color: #ffffff; margin-bottom: 16px; text-shadow: 0 0 10px #00f3ff;">🤝 {coppia_selezionata}</div>
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        <div style="background: rgba(3, 10, 20, 0.8); border: 1px solid #00f3ff; border-radius: 10px; padding: 12px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 10px rgba(0,243,255,0.15);">
                            <div style="font-size: 12px; color: #8b949e; font-weight: bold;">GIRONE</div>
                            <div style="font-size: 20px; font-weight: 700; color: #00f3ff; margin-top: 2px;">{girone_mio if girone_mio else 'N.D.'}</div>
                        </div>
                        <div style="background: rgba(3, 10, 20, 0.8); border: 1px solid #00ff66; border-radius: 10px; padding: 12px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 10px rgba(0,255,102,0.15);">
                            <div style="font-size: 12px; color: #8b949e; font-weight: bold;">POSIZIONE</div>
                            <div style="font-size: 20px; font-weight: 700; color: #00ff66; margin-top: 2px;">{str(pos_mia) + '° Pos' if pos_mia else 'N.D.'}</div>
                        </div>
                        <div style="background: rgba(3, 10, 20, 0.8); border: 1px solid #ffd700; border-radius: 10px; padding: 12px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 10px rgba(255,215,0,0.15);">
                            <div style="font-size: 12px; color: #8b949e; font-weight: bold;">PUNTI / DR</div>
                            <div style="font-size: 20px; font-weight: 700; color: #ffd700; margin-top: 2px;">{info_mie['punti'] if info_mie else 0} pt <span style="font-size: 13px; font-weight: normal; color: #8b949e;">(DR: {info_mie['dr'] if info_mie else 0})</span></div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<h4 class='neon-text-cyan'>🔍 LE TUE PARTITE NEL GIRONE</h4>", unsafe_allow_html=True)

            partite_mie_in_corso = []
            partite_mie_in_coda = []
            partite_mie_da_giocare_dopo = []
            partite_mie_fatte = []

            if girone_mio and girone_mio in db["calendario_gironi"]:
                max_t = (
                    max([len(t) for t in db["calendario_gironi"].values()])
                    if db["calendario_gironi"]
                    else 0
                )
                tutte_p_girone = []
                for t_num in range(1, max_t + 1):
                    for g_n, turni in db["calendario_gironi"].items():
                        for t_obj in turni:
                            if t_obj["turno"] == t_num:
                                tutte_p_girone.extend(t_obj["partite"])

                da_giocare_tot = [
                    p for p in tutte_p_girone if not p.get("giocata", False)
                ]
                num_tavoli_conf = db.get("num_tavoli", 6)
                coda_globale = da_giocare_tot[:num_tavoli_conf]

                for turno_obj in db["calendario_gironi"][girone_mio]:
                    for m in turno_obj["partite"]:
                        if m["c1"] == coppia_selezionata or m["c2"] == coppia_selezionata:
                            if m.get("giocata", False):
                                partite_mie_fatte.append(m)
                            elif m.get("in_corso", False):
                                partite_mie_in_corso.append(m)
                            elif m in coda_globale:
                                partite_mie_in_coda.append(m)
                            else:
                                partite_mie_da_giocare_dopo.append(m)

            col_m1, col_m2 = st.columns(2)

            with col_m1:
                st.markdown("**🔥 IN CORSO / IN CODA:**")
                if not partite_mie_in_corso and not partite_mie_in_coda:
                    st.info("Nessuna partita attiva o in coda adesso per te.")
                else:
                    for m in partite_mie_in_corso:
                        testo_scontro = f"{m['c1']} vs {m['c2']}"
                        testo_evidenziato = evidenzia_nome_coppia(
                            testo_scontro, coppia_selezionata
                        )
                        match_id_mio = m["id"]
                        st.markdown(
                            f"""
                            <div style="background: linear-gradient(135deg, rgba(51, 41, 0, 0.9) 0%, rgba(20, 16, 0, 0.9) 100%); border: 2px solid #ffd700; padding: 14px; border-radius: 10px; margin-bottom: 8px; text-align: center; box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);">
                                <span style="color: #ffd700; font-weight: bold; font-size: 13px; text-shadow: 0 0 8px rgba(255,215,0,0.6);">🏟️ IN CORSO (BILIARDINO {m.get('tavolo', 'N/D')})</span><br>
                                <b style="color: #ffffff; font-size: 16px; display: block; margin-top: 4px;">{testo_evidenziato}</b>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        with st.expander(
                            f"📝 Inserisci Risultato (Tav. {m.get('tavolo', '')})"
                        ):
                            gol_p1_mio = st.pills(
                                f"Gol {m['c1']}",
                                options=[0, 1, 2, 3, 4, 5, 6, 7],
                                default=int(m.get("gol1", 0)),
                                key=f"user_pers_g1_{match_id_mio}",
                            )
                            gol_p2_mio = st.pills(
                                f"Gol {m['c2']}",
                                options=[0, 1, 2, 3, 4, 5, 6, 7],
                                default=int(m.get("gol2", 0)),
                                key=f"user_pers_g2_{match_id_mio}",
                            )
                            if st.button(
                                "✅ Salva Risultato",
                                key=f"btn_save_pers_{match_id_mio}",
                                use_container_width=True,
                            ):
                                m["gol1"] = int(gol_p1_mio) if gol_p1_mio is not None else 0
                                m["gol2"] = int(gol_p2_mio) if gol_p2_mio is not None else 0
                                m["giocata"] = True
                                m["in_corso"] = False
                                m["tavolo"] = None
                                ricalcola_classifiche_gironi()
                                salva_dati(db)
                                st.success("Risultato salvato! Tavolo liberato.")
                                st.rerun()

                    for m in partite_mie_in_coda:
                        testo_scontro = f"{m['c1']} vs {m['c2']}"
                        testo_evidenziato = evidenzia_nome_coppia(
                            testo_scontro, coppia_selezionata
                        )
                        st.markdown(
                            f"""
                            <div style="background: linear-gradient(135deg, rgba(0, 51, 20, 0.9) 0%, rgba(0, 20, 8, 0.9) 100%); border: 1.5px solid #00ff66; padding: 12px; border-radius: 10px; margin-bottom: 8px; text-align: center; color: #00ff66; box-shadow: 0 0 10px rgba(0,255,102,0.3);">
                                <b style="font-size: 13px; text-shadow: 0 0 8px rgba(0,255,102,0.6);">⏳ IN CODA (PROSSIMO TURNO)</b><br>
                                <b style="color: #ffffff; font-size: 15px; display: block; margin-top: 4px;">{testo_evidenziato}</b>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                st.markdown("---")
                st.markdown("**📅 INCONTRI PROGRAMMATI:**")
                if not partite_mie_da_giocare_dopo:
                    st.info("Nessuna altra partita prevista nei turni successivi.")
                else:
                    for m in partite_mie_da_giocare_dopo:
                        testo_scontro = f"{m['c1']} vs {m['c2']}"
                        testo_evidenziato = evidenzia_nome_coppia(
                            testo_scontro, coppia_selezionata
                        )
                        st.markdown(
                            f"""
                            <div style="background: rgba(13, 8, 26, 0.8); border: 1px solid #00f3ff; padding: 10px; border-radius: 8px; margin-bottom: 6px; text-align: center;">
                                <span style="font-size: 14px; color: #ffffff;"><b>{testo_evidenziato}</b></span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            with col_m2:
                st.markdown("**✅ PARTITE GIOCATE:**")
                if not partite_mie_fatte:
                    st.info("Nessuna partita ancora conclusa.")
                else:
                    for m in partite_mie_fatte:
                        testo_scontro = f"{m['c1']} vs {m['c2']}"
                        testo_evidenziato = evidenzia_nome_coppia(
                            testo_scontro, coppia_selezionata
                        )
                        st.markdown(
                            f"""
                            <div style="background: rgba(9, 26, 46, 0.8); border: 1px solid #b967ff; padding: 10px; border-radius: 8px; margin-bottom: 6px; text-align: center;">
                                <span style="font-size: 13px; color: #8b949e;">{testo_evidenziato}</span><br>
                                <b style="color: #00ff66; font-size: 16px; text-shadow: 0 0 8px rgba(0,255,102,0.5);">Risultato: {m['gol1']} - {m['gol2']}</b>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            if girone_mio:
                st.markdown("---")
                st.markdown(
                    f"#### 📊 Classifica {girone_mio} (Azzurro: Fascia A | Viola: Fascia B)"
                )
                dati_girone = db["punti_gironi"][girone_mio]
                sorted_c = sorted(
                    dati_girone.items(),
                    key=lambda x: (
                        x[1]["punti"],
                        x[1]["scontri_diretti_pt"],
                        x[1]["dr"],
                        x[1]["gf"],
                    ),
                    reverse=True,
                )

                data_g = []
                for idx, (coppia, info) in enumerate(sorted_c):
                    gioc, tot = calcola_partite_giocate_coppia(girone_mio, coppia)
                    fascia_assegnata = "⭐ A" if idx < 4 else "🔻 B"
                    data_g.append({
                        "Pos": f"{idx+1}°",
                        "Coppia": coppia,
                        "Pt": info["punti"],
                        "DR": info["dr"],
                        "GF": info["gf"],
                        "Gioc": f"{gioc}/{tot}",
                        "Fascia": fascia_assegnata,
                    })

                df_g = pd.DataFrame(data_g)

                def colora_fasce_mio_girone(val):
                    try:
                        pos = int(str(val).replace("°", ""))
                        if pos <= 4:
                            return "background-color: rgba(0, 243, 255, 0.2); color: #00f3ff; font-weight: bold;"
                        else:
                            return "background-color: rgba(185, 103, 255, 0.2); color: #b967ff; font-weight: bold;"
                    except:
                        return ""

                if not df_g.empty:
                    df_styled = df_g.style.map(colora_fasce_mio_girone, subset=["Pos"])
                    st.dataframe(df_styled, hide_index=True, use_container_width=True)
                else:
                    st.dataframe(df_g, hide_index=True, use_container_width=True)

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# 1. SETUP INIZIALE
if db["stato"] == "setup" or st.session_state.get("mostra_setup", False):
    st.markdown("<h2 class='neon-text-cyan'>1. CONFIGURAZIONE TORNEO</h2>", unsafe_allow_html=True)

    if not is_admin:
        st.warning("⚠️ Accesso Setup bloccato. Effettua il login Admin dalla barra laterale.")
    else:
        whatsapp_text = st.text_area(
            "Incolla Lista Coppie (da WhatsApp):",
            height=150,
        )

        col1, col2 = st.columns(2)
        with col1:
            db["num_tavoli"] = st.number_input(
                "Numero Biliardini Disponibili",
                min_value=1,
                max_value=10,
                value=int(db["num_tavoli"]),
            )
        with col2:
            db["num_gironi"] = st.number_input(
                "Numero Gironi da Creare",
                min_value=1,
                max_value=8,
                value=int(db["num_gironi"]),
            )

        db["admin_pin"] = st.text_input("PIN Admin", value=db["admin_pin"])

        if st.button("🚀 GENERA GIRONI E MATCH", use_container_width=True):
            coppie = []
            for line in whatsapp_text.split("\n"):
                nome_c = pulisci_nome(line)
                if nome_c:
                    coppie.append(nome_c)

            num_g = int(db["num_gironi"])

            if len(coppie) < (num_g * 2):
                st.error(f"Coppie insufficienti! Servono almeno {num_g * 2} coppie per {num_g} gironi.")
            else:
                db["coppie"] = coppie
                random.shuffle(coppie)

                nomi_gironi = [chr(65 + i) for i in range(num_g)]
                gironi_dict = {f"Girone {g}": [] for g in nomi_gironi}

                for idx, c in enumerate(coppie):
                    g_scelto = f"Girone {nomi_gironi[idx % num_g]}"
                    gironi_dict[g_scelto].append(c)

                db["gironi"] = gironi_dict
                db["punti_gironi"] = {
                    g: {
                        c: {
                            "punti": 0,
                            "gf": 0,
                            "gs": 0,
                            "dr": 0,
                            "scontri_diretti_pt": 0,
                        }
                        for c in lst
                    }
                    for g, lst in gironi_dict.items()
                }

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
                                    "c1": s1,
                                    "c2": s2,
                                    "giocata": False,
                                    "in_corso": False,
                                    "tavolo": None,
                                    "gol1": 0,
                                    "gol2": 0,
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
                st.success(f"Gironi creati con successo!")
                st.session_state["mostra_setup"] = False
                st.rerun()
    st.markdown("---")

# 2. FASE A GIRONI LIVE
if db["stato"] == "gironi":
    ricalcola_classifiche_gironi()
    num_tavoli = db.get("num_tavoli", 6)

    if db.get("fasi_finali_configurate", False) and is_admin:
        if st.button("⬅️ Torna alle Fasi Finali", use_container_width=True):
            db["stato"] = "fasi_finali"
            salva_dati(db)
            st.rerun()
        st.markdown("---")

    max_turni = (
        max([len(turni) for turni in db["calendario_gironi"].values()])
        if db["calendario_gironi"]
        else 0
    )

    partite_per_girone_dict = {}
    for t_num in range(1, max_turni + 1):
        for g_nome, turni_girone in db["calendario_gironi"].items():
            for t_obj in turni_girone:
                if t_obj["turno"] == t_num:
                    if g_nome not in partite_per_girone_dict:
                        partite_per_girone_dict[g_nome] = []
                    partite_per_girone_dict[g_nome].extend(t_obj["partite"])

    partite_miste_totali = []
    max_len_partite = (
        max([len(v) for v in partite_per_girone_dict.values()])
        if partite_per_girone_dict
        else 0
    )
    for idx_misto in range(max_len_partite):
        for g_chiave in sorted(partite_per_girone_dict.keys()):
            lista_p = partite_per_girone_dict[g_chiave]
            if idx_misto < len(lista_p):
                partite_miste_totali.append(lista_p[idx_misto])

    partite_in_corso = []
    partite_da_giocare = []

    for m in partite_miste_totali:
        if not m.get("giocata", False):
            if m.get("in_corso", False):
                partite_in_corso.append(m)
            else:
                partite_da_giocare.append(m)

    tavoli_occupati_ids = [
        p.get("tavolo") for p in partite_in_corso if p.get("tavolo") is not None
    ]
    tavoli_liberi_disponibili = [
        t for t in range(1, num_tavoli + 1) if t not in tavoli_occupati_ids
    ]

    if tavoli_liberi_disponibili and partite_da_giocare:
        cambiato = False
        for tavolo_libero in tavoli_liberi_disponibili:
            if partite_da_giocare:
                prossima_partita = partite_da_giocare.pop(0)
                prossima_partita["in_corso"] = True
                prossima_partita["tavolo"] = tavolo_libero
                partite_in_corso.append(prossima_partita)
                cambiato = True
        if cambiato:
            salva_dati(db)

    partite_in_corso = sorted(
        partite_in_corso,
        key=lambda x: x.get("tavolo") if x.get("tavolo") is not None else 999,
    )

    st.markdown("<h3 class='neon-text-gold'>⚡ STATO BILIARDINI E CODA LIVE</h3>", unsafe_allow_html=True)

    col_ic, col_coda = st.columns(2)

    with col_ic:
        st.markdown("<h4 class='neon-text-gold'>🔥 PARTITE IN CORSO</h4>", unsafe_allow_html=True)
        if not partite_in_corso:
            st.info("Nessun tavolo attualmente occupato.")
        else:
            for m in partite_in_corso:
                tavolo_str = (
                    f"<b>🏟️ BILIARDINO {m.get('tavolo')} — {m['girone']}</b>"
                    if m.get("tavolo")
                    else f"<b>🏟️ IN CAMPO — {m['girone']}</b>"
                )
                match_id = m["id"]

                fa_al_caso_nostro = (
                    is_admin
                    or coppia_selezionata == m["c1"]
                    or coppia_selezionata == m["c2"]
                )

                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: linear-gradient(135deg, rgba(51, 41, 0, 0.9) 0%, rgba(18, 14, 0, 0.9) 100%); border: 2px solid #ffd700; padding: 18px; border-radius: 14px; margin-bottom: 12px; text-align: center; box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);">
                            <div style="font-size: 15px; color: #ffd700; font-weight: bold; margin-bottom: 8px; text-shadow: 0 0 8px rgba(255,215,0,0.6);">{tavolo_str}</div>
                            <div style="font-size: 18px; font-weight: bold; color: #ffffff; line-height: 1.4;">🤝 {m['c1']}</div>
                            <div style="margin: 4px 0; font-size: 13px; font-weight: bold; color: #ffd700;">VS</div>
                            <div style="font-size: 18px; font-weight: bold; color: #ffffff; line-height: 1.4;">🤝 {m['c2']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if fa_al_caso_nostro:
                        with st.expander(
                            f"📝 Inserisci Risultato Tavolo {m.get('tavolo', '')}"
                        ):
                            st.markdown(f"**⚽ {m['c1']}**")
                            gol_p1 = st.pills(
                                f"Gol {m['c1']}",
                                options=[0, 1, 2, 3, 4, 5, 6, 7],
                                default=int(m.get("gol1", 0)),
                                key=f"user_g1_{match_id}",
                                label_visibility="collapsed",
                            )

                            st.markdown(f"**⚽ {m['c2']}**")
                            gol_p2 = st.pills(
                                f"Gol {m['c2']}",
                                options=[0, 1, 2, 3, 4, 5, 6, 7],
                                default=int(m.get("gol2", 0)),
                                key=f"user_g2_{match_id}",
                                label_visibility="collapsed",
                            )

                            if st.button(
                                "✅ Salva e Libera Tavolo",
                                key=f"user_save_{match_id}",
                                use_container_width=True,
                            ):
                                m["gol1"] = int(gol_p1) if gol_p1 is not None else 0
                                m["gol2"] = int(gol_p2) if gol_p2 is not None else 0
                                m["giocata"] = True
                                m["in_corso"] = False
                                m["tavolo"] = None
                                ricalcola_classifiche_gironi()
                                salva_dati(db)
                                st.success("Risultato Registrato!")
                                st.rerun()

                    if is_admin:
                        with st.expander(f"⚙️ Opzioni Admin Tavolo {m.get('tavolo', '')}"):
                            if st.button(
                                "🛑 Sgombera Tavolo (Annulla Match)",
                                key=f"admin_libera_{match_id}",
                                use_container_width=True,
                            ):
                                m["in_corso"] = False
                                m["tavolo"] = None
                                salva_dati(db)
                                st.success("Tavolo Liberato.")
                                st.rerun()

    with col_coda:
        partite_in_coda_correnti = partite_da_giocare[:num_tavoli]

        st.markdown("<h4 class='neon-text-green'>⏳ IN CODA PROSSIMI MATCH</h4>", unsafe_allow_html=True)
        if not partite_in_coda_correnti:
            st.info("Nessun match presente in coda.")
        else:
            for idx, m in enumerate(partite_in_coda_correnti):
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, rgba(0, 51, 20, 0.9) 0%, rgba(0, 20, 8, 0.9) 100%); border: 1.5px solid #00ff66; padding: 14px; border-radius: 10px; margin-bottom: 10px; text-align: center; box-shadow: 0 0 12px rgba(0, 255, 102, 0.25);">
                        <b style="font-size: 13px; color: #00ff66; text-shadow: 0 0 8px rgba(0,255,102,0.6);">⏳ CODA #{idx+1} — {m['girone']}</b><br>
                        <div style="font-weight: bold; font-size: 15px; margin-top: 4px; color: #ffffff;">{m['c1']}</div>
                        <div style="font-size: 12px; color: #00ff66; font-weight: bold;">VS</div>
                        <div style="font-weight: bold; font-size: 15px; color: #ffffff;">{m['c2']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    st.markdown("<h3 class='neon-text-cyan'>📊 CLASSIFICHE GIRONI</h3>", unsafe_allow_html=True)
    nomi_gironi_chiavi = list(db["gironi"].keys())
    for i in range(0, len(nomi_gironi_chiavi), 2):
        col_gironi = st.columns(2)
        for j in range(2):
            if i + j < len(nomi_gironi_chiavi):
                g_nome = nomi_gironi_chiavi[i + j]
                with col_gironi[j]:
                    st.markdown(f"<h4 class='neon-text-purple'>📁 {g_nome}</h4>", unsafe_allow_html=True)

                    dati_girone = db["punti_gironi"][g_nome]
                    sorted_c = sorted(
                        dati_girone.items(),
                        key=lambda x: (
                            x[1]["punti"],
                            x[1]["scontri_diretti_pt"],
                            x[1]["dr"],
                            x[1]["gf"],
                        ),
                        reverse=True,
                    )

                    data_g = []
                    for idx, (coppia, info) in enumerate(sorted_c):
                        gioc, tot = calcola_partite_giocate_coppia(g_nome, coppia)
                        fascia_assegnata = "⭐ A" if idx < 4 else "🔻 B"
                        data_g.append({
                            "Pos": f"{idx+1}°",
                            "Coppia": coppia,
                            "Pt": info["punti"],
                            "DR": info["dr"],
                            "GF": info["gf"],
                            "Gioc": f"{gioc}/{tot}",
                            "Fascia": fascia_assegnata,
                        })

                    df_g = pd.DataFrame(data_g)

                    def colora_fasce(val):
                        try:
                            pos = int(str(val).replace("°", ""))
                            if pos <= 4:
                                return "background-color: rgba(0, 243, 255, 0.2); color: #00f3ff; font-weight: bold;"
                            else:
                                return "background-color: rgba(185, 103, 255, 0.2); color: #b967ff; font-weight: bold;"
                        except:
                            return ""

                    if not df_g.empty:
                        df_styled = df_g.style.map(colora_fasce, subset=["Pos"])
                        st.dataframe(
                            df_styled, hide_index=True, use_container_width=True
                        )
                    else:
                        st.dataframe(df_g, hide_index=True, use_container_width=True)

    st.markdown("---")

    st.markdown("<h3 class='neon-text-cyan'>📅 INCONTRI PER GIRONE</h3>", unsafe_allow_html=True)
    nomi_gironi_lista = list(db["calendario_gironi"].keys())
    if nomi_gironi_lista:
        tabs_gironi = st.tabs(nomi_gironi_lista)

        for idx_tab, g_nome in enumerate(nomi_gironi_lista):
            with tabs_gironi[idx_tab]:
                turni_girone = db["calendario_gironi"][g_nome]

                for turno_obj in turni_girone:
                    t_num = turno_obj["turno"]
                    st.markdown(f"**Turno {t_num}**")

                    for m in turno_obj["partite"]:
                        match_id = m["id"]

                        if m["giocata"]:
                            bg_color = "linear-gradient(135deg, rgba(0, 51, 20, 0.9) 0%, rgba(0, 20, 8, 0.9) 100%)"
                            border_color = "#00ff66"
                            stato_testo = f"<b style='color: #00ff66; text-shadow: 0 0 8px rgba(0,255,102,0.6);'>{m['gol1']} - {m['gol2']}</b>"
                        elif m.get("in_corso", False):
                            bg_color = "linear-gradient(135deg, rgba(51, 41, 0, 0.9) 0%, rgba(20, 16, 0, 0.9) 100%)"
                            border_color = "#ffd700"
                            stato_testo = (
                                f"<b style='color: #ffd700; text-shadow: 0 0 8px rgba(255,215,0,0.6);'>🔥 In Corso (Tav. {m.get('tavolo', 'N/D')})</b>"
                            )
                        else:
                            bg_color = "rgba(13, 8, 26, 0.8)"
                            border_color = "#00f3ff"
                            stato_testo = "<span style='color: #8b949e;'>VS</span>"

                        st.markdown(
                            f"""
                            <div style="background: {bg_color}; border: 1.5px solid {border_color}; padding: 14px 16px; border-radius: 10px; margin-bottom: 10px; text-align: center;">
                                <div style="font-weight: bold; color: #ffffff; font-size: 15px; line-height: 1.4;">
                                    🤝 {m['c1']}
                                </div>
                                <div style="margin: 3px 0; font-size: 12px; color: #8b949e; font-weight: bold;">
                                    VS
                                </div>
                                <div style="font-weight: bold; color: #ffffff; font-size: 15px; line-height: 1.4;">
                                    {m['c2']} 🤝
                                </div>
                                <div style="margin-top: 8px; font-weight: bold; font-size: 15px;">
                                    {stato_testo}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if is_admin:
                            with st.expander(
                                f"⚙️ Gestisci Risultato: {m['c1']} vs {m['c2']}"
                            ):
                                st.markdown(f"**⚽ {m['c1']}**")
                                rg1 = st.pills(
                                    f"Gol S1 {match_id}",
                                    options=[0, 1, 2, 3, 4, 5, 6, 7],
                                    default=int(m.get("gol1", 0)),
                                    key=f"admin_g1_{match_id}",
                                    label_visibility="collapsed",
                                )

                                st.markdown(f"**⚽ {m['c2']}**")
                                rg2 = st.pills(
                                    f"Gol S2 {match_id}",
                                    options=[0, 1, 2, 3, 4, 5, 6, 7],
                                    default=int(m.get("gol2", 0)),
                                    key=f"admin_g2_{match_id}",
                                    label_visibility="collapsed",
                                )

                                if st.button(
                                    "💾 Salva Risultato (Admin)",
                                    key=f"save_{match_id}",
                                    use_container_width=True,
                                ):
                                    m["gol1"] = int(rg1) if rg1 is not None else 0
                                    m["gol2"] = int(rg2) if rg2 is not None else 0
                                    m["giocata"] = True
                                    m["in_corso"] = False
                                    m["tavolo"] = None
                                    ricalcola_classifiche_gironi()
                                    salva_dati(db)
                                    st.success("Risultato salvato!")
                                    st.rerun()

    if is_admin:
        st.markdown("---")
        btn_testo = (
            "🔄 Rigenera Fasi Finali"
            if db.get("fasi_finali_configurate", False)
            else "🏆 Genera Fasi Finali (Fascia A & Fascia B)"
        )
        if st.button(btn_testo, use_container_width=True):
            classificate_a = {}
            classificate_b_raw = {}
            for g_nome in db["gironi"]:
                dati_girone = db["punti_gironi"][g_nome]
                sorted_c = sorted(
                    dati_girone.items(),
                    key=lambda x: (
                        x[1]["punti"],
                        x[1]["scontri_diretti_pt"],
                        x[1]["dr"],
                        x[1]["gf"],
                    ),
                    reverse=True,
                )
                squadre_girone = [c[0] for c in sorted_c]
                classificate_a[g_nome] = squadre_girone[:4]
                classificate_b_raw[g_nome] = squadre_girone

            abbinamenti_a = crea_abbinamenti_fascia_a_perfetti(classificate_a)
            abbinamenti_b = crea_abbinamenti_fascia_b(classificate_b_raw)

            turno_a_iniziale = []
            for i, (s1_info, s2_info) in enumerate(abbinamenti_a):
                turno_a_iniziale.append({
                    "id": f"fa_t1_m{i}",
                    "s1": s1_info[0],
                    "g1": s1_info[1],
                    "p1": s1_info[2],
                    "s2": s2_info[0],
                    "g2": s2_info[1],
                    "p2": s2_info[2],
                    "giocata": False,
                    "vincente": None,
                })

            turno_b_iniziale = []
            for i, (s1_info, s2_info) in enumerate(abbinamenti_b):
                turno_b_iniziale.append({
                    "id": f"fb_t1_m{i}",
                    "s1": s1_info[0],
                    "g1": s1_info[1],
                    "p1": s1_info[2],
                    "s2": s2_info[0],
                    "g2": s2_info[1],
                    "p2": s2_info[2],
                    "giocata": False,
                    "vincente": None,
                })

            db["tabellone_a"] = [{"turno": 1, "partite": turno_a_iniziale}]
            db["tabellone_b"] = [{"turno": 1, "partite": turno_b_iniziale}]
            db["terzo_quarto_a"] = []
            db["terzo_quarto_b"] = []

            db["stato"] = "fasi_finali"
            db["fasi_finali_configurate"] = True
            salva_dati(db)
            st.success("Fasi Finali create con successo!")
            st.rerun()

# 3. FASI FINALI (TABELLONI PLAYOFF NEON)
elif db["stato"] == "fasi_finali":
    st.markdown("<h2 class='neon-text-gold' style='text-align: center;'>🏆 PLAYOFF & FASI FINALI</h2>", unsafe_allow_html=True)

    tab_a_view, tab_b_view = st.tabs(
        ["⭐ FASCIA A (TORNEO PRINCIPALE)", "🔻 FASCIA B (TORNEO SECONDARIO)"]
    )

    def gestisci_tabellone(chiave_tabellone, chiave_34, titolo_tab):
        st.markdown(f"<h3 class='neon-text-cyan'>📋 {titolo_tab}</h3>", unsafe_allow_html=True)
        turni_tab = db[chiave_tabellone]

        mappa_girone_pos = {}
        for g_nome, lista_sq in db["gironi"].items():
            dati_girone = db["punti_gironi"][g_nome]
            sorted_c = sorted(
                dati_girone.items(),
                key=lambda x: (
                    x[1]["punti"],
                    x[1]["scontri_diretti_pt"],
                    x[1]["dr"],
                    x[1]["gf"],
                ),
                reverse=True,
            )
            for idx, (sq, info) in enumerate(sorted_c):
                mappa_girone_pos[sq] = (g_nome, idx + 1)

        campione = None
        secondo_posto = None
        terzo_posto = None
        quarto_posto = None

        for t_idx, turno_obj in enumerate(turni_tab):
            t_num = turno_obj["turno"]
            partite_turno = turno_obj["partite"]
            num_part = len(partite_turno)

            nome_etichetta = ottieni_nome_turno_dinamico(num_part)

            st.markdown(
                f"""
                <div style="background: linear-gradient(90deg, #0066ff 0%, #00f3ff 100%); padding: 10px 18px; border-radius: 8px; margin: 22px 0 14px 0; color: white; text-align: center; box-shadow: 0 0 15px rgba(0,243,255,0.4);">
                    <h3 style="margin: 0; font-size: 18px; font-weight: bold; color: #ffffff;">⚡ {nome_etichetta}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            tutti_giocati = True
            vincitori_turno = []
            perdenti_turno = []

            for idx, m in enumerate(partite_turno):
                match_id = m["id"]
                s1_nome = m["s1"]
                s2_nome = m["s2"]

                g1_val, p1_val = mappa_girone_pos.get(s1_nome, ("", ""))
                g2_val, p2_val = mappa_girone_pos.get(s2_nome, ("", ""))

                s1_sottotitolo = f"{p1_val}° del {g1_val}" if g1_val and p1_val else ""
                s2_sottotitolo = f"{p2_val}° del {g2_val}" if g2_val and p2_val else ""

                if s2_nome == "RIPOSO":
                    m["giocata"] = True
                    m["vincente"] = s1_nome
                    vincitori_turno.append(s1_nome)
                    st.success(f"🟢 **{s1_nome}** avanza al turno successivo (Bye).")
                    continue
                elif s1_nome == "RIPOSO":
                    m["giocata"] = True
                    m["vincente"] = s2_nome
                    vincitori_turno.append(s2_nome)
                    st.success(f"🟢 **{s2_nome}** avanza al turno successivo (Bye).")
                    continue

                if m["giocata"]:
                    box_bg = "linear-gradient(135deg, rgba(0, 51, 20, 0.9) 0%, rgba(0, 20, 8, 0.9) 100%)"
                    border_c = "#00ff66"
                    centro_testo = f"<span style='font-size: 14px; font-weight: bold; background-color: #00ff66; color: #000000; padding: 6px 14px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,255,102,0.6);'>Vincitore: {m['vincente']}</span>"
                    vincitori_turno.append(m["vincente"])
                    perdente_match = s2_nome if m["vincente"] == s1_nome else s1_nome
                    perdenti_turno.append(perdente_match)
                else:
                    tutti_giocati = False
                    box_bg = "rgba(13, 8, 26, 0.8)"
                    border_c = "#00f3ff"
                    centro_testo = "<span style='font-size: 14px; font-weight: bold; background-color: rgba(0,243,255,0.2); color: #00f3ff; padding: 6px 12px; border-radius: 8px;'>VS</span>"

                st.markdown(
                    f"""
                    <div style="background: {box_bg}; border: 2px solid {border_c}; padding: 18px 22px; border-radius: 14px; margin-bottom: 12px; text-align: center; box-shadow: 0 0 15px rgba(0,243,255,0.2);">
                        <div style="font-size: 18px; font-weight: bold; color: #ffffff; line-height: 1.4;">
                            🤝 {s1_nome} <span style="font-size: 12px; color: #8b949e; font-weight: normal; display: block;">({s1_sottotitolo})</span>
                        </div>
                        <div style="margin: 6px 0; font-size: 13px; font-weight: bold; color: #8b949e;">
                            VS
                        </div>
                        <div style="font-size: 18px; font-weight: bold; color: #ffffff; line-height: 1.4;">
                            🤝 {s2_nome} <span style="font-size: 12px; color: #8b949e; font-weight: normal; display: block;">({s2_sottotitolo})</span>
                        </div>
                        <div style="margin-top: 12px;">
                            {centro_testo}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if is_admin:
                    with st.expander(
                        f"⚙️ Assegna Vittoria: {s1_nome} vs {s2_nome}"
                    ):
                        col_v1, col_v2 = st.columns(2)
                        with col_v1:
                            if st.button(
                                f"🏆 Vince: {s1_nome}",
                                key=f"win_s1_{match_id}",
                                use_container_width=True,
                            ):
                                m["giocata"] = True
                                m["vincente"] = s1_nome
                                salva_dati(db)
                                st.success(f"Vincitore: {s1_nome}")
                                st.rerun()
                        with col_v2:
                            if st.button(
                                f"🏆 Vince: {s2_nome}",
                                key=f"win_s2_{match_id}",
                                use_container_width=True,
                            ):
                                m["giocata"] = True
                                m["vincente"] = s2_nome
                                salva_dati(db)
                                st.success(f"Vincitore: {s2_nome}")
                                st.rerun()

            if (
                nome_etichetta == "🏆 FINALE ASSOLUTA"
                and tutti_giocati
                and len(partite_turno) == 1
            ):
                fin_m = partite_turno[0]
                if fin_m["giocata"] and fin_m.get("vincente"):
                    campione = fin_m["vincente"]
                    secondo_posto = (
                        fin_m["s2"] if campione == fin_m["s1"] else fin_m["s1"]
                    )

            if (
                tutti_giocati
                and nome_etichetta == "⚔️ SEMIFINALI"
                and len(perdenti_turno) == 2
                and not db[chiave_34]
            ):
                if is_admin:
                    p1, p2 = perdenti_turno[0], perdenti_turno[1]
                    if p1 != p2:
                        g_p1, pos_p1 = mappa_girone_pos.get(p1, ("", ""))
                        g_p2, pos_p2 = mappa_girone_pos.get(p2, ("", ""))
                        db[chiave_34] = [{
                            "id": f"{chiave_tabellone}_terzo_quarto",
                            "s1": p1,
                            "g1": g_p1,
                            "p1": pos_p1,
                            "s2": p2,
                            "g2": g_p2,
                            "p2": pos_p2,
                            "giocata": False,
                            "vincente": None,
                        }]
                        salva_dati(db)

            if tutti_giocati and len(partite_turno) > 1:
                prossimo_turno_num = t_num + 1
                vincitori_dettagli = []
                for v in vincitori_turno:
                    g_v, p_v = mappa_girone_pos.get(v, ("", ""))
                    vincitori_dettagli.append((v, g_v, p_v))

                if len(vincitori_dettagli) == 4 and chiave_tabellone == "tabellone_a":
                    sq1, sq2, sq3, sq4 = vincitori_dettagli
                    if verifica_conflitto_stesso_girone(sq1[0], sq2[0], mappa_girone_pos):
                        vincitori_dettagli = [sq1, sq3, sq2, sq4]

                nuove_partite = []
                for i in range(0, len(vincitori_dettagli), 2):
                    if i + 1 < len(vincitori_dettagli):
                        s1_info = vincitori_dettagli[i]
                        s2_info = vincitori_dettagli[i + 1]
                        nuove_partite.append({
                            "id": f"{chiave_tabellone}_t{prossimo_turno_num}_m{i//2}",
                            "s1": s1_info[0],
                            "g1": s1_info[1],
                            "p1": s1_info[2],
                            "s2": s2_info[0],
                            "g2": s2_info[1],
                            "p2": s2_info[2],
                            "giocata": False,
                            "vincente": None,
                        })

                turno_esistente = next(
                    (t for t in turni_tab if t["turno"] == prossimo_turno_num), None
                )
                if not turno_esistente and is_admin and nuove_partite:
                    turni_tab.append(
                        {"turno": prossimo_turno_num, "partite": nuove_partite}
                    )
                    salva_dati(db)
                    st.success("🎉 Generazione Turno Successivo Completata!")
                    st.rerun()

        if db[chiave_34]:
            st.markdown(
                """
                <div style="background: linear-gradient(90deg, #b967ff 0%, #00f3ff 100%); padding: 10px 18px; border-radius: 8px; margin: 25px 0 14px 0; color: white; text-align: center; box-shadow: 0 0 15px rgba(185,103,255,0.4);">
                    <h3 style="margin: 0; font-size: 18px; font-weight: bold; color: #ffffff;">🥉 FINALE 3° / 4° POSTO</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            tq_match = db[chiave_34][0]
            tq_id = tq_match["id"]

            tq_g1, tq_p1 = mappa_girone_pos.get(tq_match["s1"], ("", ""))
            tq_g2, tq_p2 = mappa_girone_pos.get(tq_match["s2"], ("", ""))

            tq_s1_sub = f"{tq_p1}° del {tq_g1}" if tq_g1 and tq_p1 else ""
            tq_s2_sub = f"{tq_p2}° del {tq_g2}" if tq_g2 and tq_p2 else ""

            if tq_match["giocata"]:
                tq_bg = "linear-gradient(135deg, rgba(51, 41, 0, 0.9) 0%, rgba(18, 14, 0, 0.9) 100%)"
                tq_border = "#ffd700"
                tq_centro = f"<span style='font-size: 14px; font-weight: bold; background-color: #ffd700; color: #000000; padding: 6px 14px; border-radius: 8px;'>3° Posto: {tq_match['vincente']}</span>"
                terzo_posto = tq_match["vincente"]
                quarto_posto = (
                    tq_match["s2"]
                    if terzo_posto == tq_match["s1"]
                    else tq_match["s1"]
                )
            else:
                tq_bg = "rgba(13, 8, 26, 0.8)"
                tq_border = "#b967ff"
                tq_centro = "<span style='font-size: 14px; font-weight: bold; background-color: rgba(185,103,255,0.2); color: #b967ff; padding: 6px 12px; border-radius: 8px;'>VS</span>"

            st.markdown(
                f"""
                <div style="background: {tq_bg}; border: 2px solid {tq_border}; padding: 18px 22px; border-radius: 14px; margin-bottom: 12px; text-align: center; box-shadow: 0 0 15px rgba(185,103,255,0.3);">
                    <div style="font-size: 18px; font-weight: bold; color: #ffffff; line-height: 1.4;">
                        🤝 {tq_match['s1']} <span style="font-size: 12px; color: #8b949e; font-weight: normal; display: block;">({tq_s1_sub})</span>
                    </div>
                    <div style="margin: 6px 0; font-size: 13px; font-weight: bold; color: #8b949e;">
                        VS
                    </div>
                    <div style="font-size: 18px; font-weight: bold; color: #ffffff; line-height: 1.4;">
                        🤝 {tq_match['s2']} <span style="font-size: 12px; color: #8b949e; font-weight: normal; display: block;">({tq_s2_sub})</span>
                    </div>
                    <div style="margin-top: 12px;">
                        {tq_centro}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if is_admin:
                with st.expander("⚙️ Assegna Vincitore 3°/4° Posto"):
                    col_tq1, col_tq2 = st.columns(2)
                    with col_tq1:
                        if st.button(
                            f"🥉 3° Posto: {tq_match['s1']}",
                            key=f"tq_win_s1_{tq_id}",
                            use_container_width=True,
                        ):
                            tq_match["giocata"] = True
                            tq_match["vincente"] = tq_match["s1"]
                            salva_dati(db)
                            st.success(f"3° Posto Assegnato a {tq_match['s1']}")
                            st.rerun()
                    with col_tq2:
                        if st.button(
                            f"🥉 3° Posto: {tq_match['s2']}",
                            key=f"tq_win_s2_{tq_id}",
                            use_container_width=True,
                        ):
                            tq_match["giocata"] = True
                            tq_match["vincente"] = tq_match["s2"]
                            salva_dati(db)
                            st.success(f"3° Posto Assegnato a {tq_match['s2']}")
                            st.rerun()

        # CERIMONIA DI PREMIAZIONE / PODIO NEON
        if campione:
            st.markdown("---")
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, rgba(51, 41, 0, 0.95) 0%, rgba(19, 9, 36, 0.95) 100%); border: 3px solid #ffd700; padding: 30px; border-radius: 18px; text-align: center; color: #ffffff; margin-top: 25px; box-shadow: 0 0 35px rgba(255, 215, 0, 0.5);">
                    <h2 style="margin: 0 0 15px 0; color: #ffd700; font-size: 28px; text-shadow: 0 0 15px rgba(255,215,0,0.8);">👑 PODIO FINALE — {titolo_tab} 👑</h2>
                    <p style="font-size: 24px; margin: 12px 0; font-weight: bold; color: #ffd700; text-shadow: 0 0 10px rgba(255,215,0,0.6);">🥇 1° POSTO (CAMPIONI): {campione}</p>
                    <p style="font-size: 20px; margin: 10px 0; font-weight: 600; color: #00f3ff; text-shadow: 0 0 10px rgba(0,243,255,0.6);">🥈 2° POSTO: {secondo_posto if secondo_posto else 'N.D.'}</p>
                    <p style="font-size: 20px; margin: 10px 0; font-weight: 600; color: #b967ff; text-shadow: 0 0 10px rgba(185,103,255,0.6);">🥉 3° POSTO: {terzo_posto if terzo_posto else 'N.D.'}</p>
                    <p style="font-size: 16px; margin: 12px 0; color: #8b949e;">4° Posto: {quarto_posto if quarto_posto else 'N.D.'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_a_view:
        gestisci_tabellone(
            "tabellone_a",
            "terzo_quarto_a",
            "TABELLONE FASCIA A (TORNEO PRINCIPALE)",
        )

    with tab_b_view:
        gestisci_tabellone(
            "tabellone_b",
            "terzo_quarto_b",
            "TABELLONE FASCIA B (TORNEO SECONDARIO)",
        )
