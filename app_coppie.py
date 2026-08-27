import json
import os
import random
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=5000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(
    page_title="Torneo Padel Live - Cyber Gaming Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STILE GRAFICO GLOBALE & ANIMAZIONI CYBERPUNK ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Orbitron:wght@600;800;900&family=Inter:wght@400;600;800&display=swap');

        @keyframes pulseGlow {
            0% {
                box-shadow: 0 0 15px rgba(255, 170, 0, 0.2), inset 0 0 10px rgba(255, 170, 0, 0.05);
                border-color: rgba(255, 170, 0, 0.6);
            }
            50% {
                box-shadow: 0 0 35px rgba(255, 170, 0, 0.7), inset 0 0 20px rgba(255, 170, 0, 0.2);
                border-color: #ffaa00;
            }
            100% {
                box-shadow: 0 0 15px rgba(255, 170, 0, 0.2), inset 0 0 10px rgba(255, 170, 0, 0.05);
                border-color: rgba(255, 170, 0, 0.6);
            }
        }

        @keyframes slideInQueue {
            from {
                opacity: 0;
                transform: translateY(15px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .match-live-card-animated {
            animation: pulseGlow 2s infinite ease-in-out;
            background: linear-gradient(135deg, rgba(30, 20, 10, 0.95) 0%, rgba(12, 8, 4, 0.98) 100%);
            border: 2px solid #ffaa00;
            border-radius: 16px;
            padding: 22px;
            text-align: center;
        }

        .queue-item-animated {
            animation: slideInQueue 0.4s ease-out forwards;
            background: linear-gradient(135deg, rgba(8, 36, 20, 0.9) 0%, rgba(2, 16, 8, 0.95) 100%);
            border: 2px solid #00ff66;
            padding: 14px;
            border-radius: 14px;
            margin-bottom: 12px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0,255,102,0.25);
        }

        div[data-baseweb="segmented-control"] {
            background-color: #0b1326 !important;
            border: 1.5px solid rgba(0, 242, 254, 0.5) !important;
            border-radius: 12px !important;
            padding: 3px !important;
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.15) !important;
        }
        div[data-baseweb="segmented-control"] button {
            color: #8b949e !important;
            font-family: 'Rajdhani', sans-serif !important;
            font-weight: 700 !important;
            border-radius: 9px !important;
            background-color: transparent !important;
            border: none !important;
            transition: all 0.2s ease-in-out !important;
        }
        div[data-baseweb="segmented-control"] button:hover {
            color: #00f2fe !important;
            background-color: rgba(0, 242, 254, 0.1) !important;
        }
        div[data-baseweb="segmented-control"] button[aria-selected="true"] {
            background: linear-gradient(180deg, #132238, #0a111c) !important;
            color: #00f2fe !important;
            border: 1px solid #00f2fe !important;
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.7), inset 0 0 8px rgba(0, 242, 254, 0.3) !important;
        }

        :root {
            color-scheme: dark !important;
        }

        .stApp {
            background-color: #05070f;
            background-image: 
                radial-gradient(circle at 50% 10%, rgba(0, 242, 254, 0.08) 0%, transparent 60%),
                radial-gradient(circle at 10% 90%, rgba(255, 0, 127, 0.06) 0%, transparent 50%),
                linear-gradient(to right, rgba(0, 242, 254, 0.03) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(0, 242, 254, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
            color: #f0f6fc;
            font-family: 'Inter', sans-serif;
            color-scheme: dark !important;
        }
        
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070a17, #020408);
            border-right: 2px solid rgba(0, 242, 254, 0.2);
            box-shadow: 8px 0 30px rgba(0, 242, 254, 0.08);
        }

        .neon-title-box {
            border: 2px solid #00f2fe;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.4), inset 0 0 15px rgba(0, 242, 254, 0.1);
            border-radius: 18px;
            padding: 24px;
            text-align: center;
            background: linear-gradient(135deg, rgba(16, 22, 36, 0.95) 0%, rgba(8, 12, 20, 0.98) 100%);
            margin-bottom: 20px;
        }
        .neon-title-text {
            color: #00ff66 !important;
            font-family: 'Rajdhani', sans-serif !important;
            font-size: 34px;
            font-weight: 900;
            text-shadow: 0 0 15px rgba(0,255,102,0.9), 0 0 30px rgba(0,255,102,0.5);
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .neon-subtitle {
            color: #8b949e;
            font-size: 14px;
            margin-top: 6px;
            font-weight: 600;
        }

        .neon-box-main {
            background: linear-gradient(135deg, rgba(16, 22, 36, 0.95) 0%, rgba(8, 12, 20, 0.98) 100%);
            border: 2px solid #00f2fe;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.25), inset 0 0 15px rgba(0, 242, 254, 0.08);
            position: relative;
        }

        .neon-gold { color: #ffaa00 !important; text-shadow: 0 0 12px rgba(255,170,0,0.8), 0 0 25px rgba(255,170,0,0.4); }
        .neon-blue { color: #00f2fe !important; text-shadow: 0 0 12px rgba(0,242,254,0.8), 0 0 25px rgba(0,242,254,0.4); }
        .neon-green { color: #00ff66 !important; text-shadow: 0 0 12px rgba(0,255,102,0.8), 0 0 25px rgba(0,255,102,0.4); }

        h1, h2, h3, h4 {
            font-family: 'Rajdhani', sans-serif !important;
            color: #ffffff !important;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 800;
            font-family: 'Rajdhani', sans-serif;
            font-size: 18px;
            height: 50px !important;
            letter-spacing: 1px;
            border: 1.5px solid rgba(0, 242, 254, 0.5);
            background: linear-gradient(180deg, #132238, #0a111c);
            color: #00f2fe;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div.stButton > button:hover {
            border-color: #00f2fe;
            background: linear-gradient(180deg, #1d3557, #0f2038);
            color: #ffffff;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.8), inset 0 0 12px rgba(0, 242, 254, 0.3);
            transform: translateY(-2px);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_FILE = "torneo_padel_data.json"


def carica_dati():
  coppie = [
      "DENNY LUIGI",
      "STANI GARDO",
      "HIGUAIN GIACOMO",
      "CARLO SAVIO",
      "ANGELO BEPPE",
      "FABIO PIERO",
      "MICHELE MA SOCIO",
      "GIANNI DIEGO",
      "LUCA AVVOCATO",
      "MAURA ANTONIO",
      "LONGO SOCIO",
      "ANNE RUBY",
      "DYLAN RAFFAELE",
      "DANIELE SOCIO",
      "EMILIO DAVIDE",
      "VITTORIO ALEXANDER",
      "FIORE CRISTOPHER",
      "BATTANI MAX",
      "MATTIA MARCO",
      "DANIELA ALFONSO",
      "CIRO CATO",
      "DONA CLAUDIO",
      "NELLO MIRKO",
      "MIKELE SOCIO",
      "ALEXANDRA LUCA",
      "MILANESI SOCIO",
      "ALAN ANDY",
      "GIANLUCA SOCIO",
      "DOMENICO SOCIO",
      "MARCO STEFANO",
      "ALESSIO MATTEO",
      "GIOVANNI PAOLO",
      "DAVIDE SIMONE",
      "ANDREA FEDERICO",
      "FRANCESCO ALESSANDRO",
      "GIUSEPPE SALVATORE",
      "NICOLA TOMMASO",
      "LORENZO FILIPPO",
      "EMANUELE PIETRO",
      "VINCENZO CHRISTIAN",
  ]

  gironi = {}
  num_gironi = 8
  for i in range(num_gironi):
    nome_girone = f"Girone {chr(65 + i)}"
    gironi[nome_girone] = coppie[i * 5 : (i + 1) * 5]

  dati_default = {
      "stato": "gironi",
      "coppie": coppie,
      "num_tavoli": 4,
      "num_gironi": 8,
      "admin_pin": "0000",
      "gironi": gironi,
      "punti_gironi": {},
      "calendario_gironi": {},
      "eliminazione_diretta": {
          "Ottavi": [
              {
                  "p1": coppie[0],
                  "prov1": "1° Classificato - Girone A",
                  "p2": coppie[1],
                  "prov2": "2° Classificato - Girone B",
                  "res": "",
              },
              {
                  "p1": coppie[2],
                  "prov1": "1° Classificato - Girone B",
                  "prov2": "2° Classificato - Girone A",
                  "p2": coppie[3],
                  "res": "",
              },
              {
                  "p1": coppie[4],
                  "prov1": "1° Classificato - Girone C",
                  "prov2": "2° Classificato - Girone D",
                  "p2": coppie[5],
                  "res": "",
              },
              {
                  "p1": coppie[6],
                  "prov1": "1° Classificato - Girone D",
                  "prov2": "2° Classificato - Girone C",
                  "p2": coppie[7],
                  "res": "",
              },
              {
                  "p1": coppie[8],
                  "prov1": "1° Classificato - Girone E",
                  "prov2": "2° Classificato - Girone F",
                  "p2": coppie[9],
                  "res": "",
              },
              {
                  "p1": coppie[10],
                  "prov1": "1° Classificato - Girone F",
                  "prov2": "2° Classificato - Girone E",
                  "p2": coppie[11],
                  "res": "",
              },
              {
                  "p1": coppie[12],
                  "prov1": "1° Classificato - Girone G",
                  "prov2": "2° Classificato - Girone H",
                  "p2": coppie[13],
                  "res": "",
              },
              {
                  "p1": coppie[14],
                  "prov1": "1° Classificato - Girone H",
                  "prov2": "2° Classificato - Girone G",
                  "p2": coppie[15],
                  "res": "",
              },
          ]
      },
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


def genera_pdf_coppie():
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 16)
  pdf.cell(0, 10, "Torneo Padel Live - Schema Gironi", 0, 1, "C")
  pdf.ln(5)

  for g_nome, coppie_lista in db["gironi"].items():
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"--- {g_nome} ---", 0, 1, "L")
    pdf.set_font("Arial", "", 11)
    for c in coppie_lista:
      pdf.cell(
          0,
          7,
          f"  - {c}".encode("latin-1", "ignore").decode("latin-1"),
          0,
          1,
          "L",
      )
    pdf.ln(2)
  return bytes(pdf.output())


# --- BARRA LATERALE ---
st.sidebar.header("⚙️ Pannello Controllo")
pdf_data = genera_pdf_coppie()
st.sidebar.download_button(
    label="📥 Scarica Elenco PDF",
    data=pdf_data,
    file_name="elenco_gironi_padel.pdf",
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
if is_sidebar_reset := st.sidebar.button(
    "🔄 Reset Totale Torneo", use_container_width=True
):
  if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
  for key in list(st.session_state.keys()):
    del st.session_state[key]
  st.success("Torneo ripristinato allo stato iniziale!")
  st.rerun()

# --- INTERFACCIA PRINCIPALE ---
st.markdown(
    """
    <div class="neon-title-box">
        <div class="neon-title-text">🏆 Torneo Padel - Gestione Live</div>
        <div class="neon-subtitle">Edizione Ufficiale 40 Coppie • Schedigironi & Knockout</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Selettore Coppia per la visualizzazione personalizzata
tutte_le_coppie = db["coppie"]
opzioni_selettore = ["-- Seleziona la tua coppia per accedere --"] + sorted(
    tutte_le_coppie
)

coppia_url = st.query_params.get(
    "coppia", "-- Seleziona la tua coppia per accedere --"
)
if coppia_url not in opzioni_selettore:
  coppia_url = "-- Seleziona la tua coppia per accedere --"

coppia_selezionata = st.selectbox(
    "📱 Seleziona la tua coppia:",
    options=opzioni_selettore,
    index=opzioni_selettore.index(coppia_url),
    key="widget_selezione_coppia",
)

if coppia_selezionata != coppia_url:
  st.query_params["coppia"] = coppia_selezionata
  st.rerun()

# Schede dell'applicazione (Tab)
tab1, tab2 = st.tabs(["📊 Gironi & Squadre", "⚔️ Tabellone Eliminazione Diretta"])

with tab1:
  st.header("Elenco Gironi e Coppie")
  girone_selezionato = st.selectbox(
      "Seleziona Girone", list(db["gironi"].keys())
  )

  coppie_girone = db["gironi"][girone_selezionato]
  st.write(f"Coppie iscritte in **{girone_selezionato}**:")
  for c in coppie_girone:
    # Evidenzia la coppia se è quella selezionata dall'utente
    if c == coppia_selezionata:
      st.markdown(
          f"- <span class='neon-green' style='font-size: 1.1em;'><b>⭐ {c} (La tua coppia)</b></span>",
          unsafe_allow_html=True,
      )
    else:
      st.markdown(f"- **{c}**")

with tab2:
  st.header("Tabellone Eliminazione Diretta")
  st.markdown("---")

  fase = "Ottavi"
  if fase in db["eliminazione_diretta"]:
    matchups = db["eliminazione_diretta"][fase]

    for idx, match in enumerate(matchups):
      col1, col2, col3 = st.columns([4, 2, 4])

      with col1:
        is_my_team_1 = coppia_selezionata == match["p1"]
        prefix_1 = "⭐ " if is_my_team_1 else ""
        st.markdown(f"### **{prefix_1}{match['p1']}**")
        st.caption(f"📍 Provenienza: {match['prov1']}")

      with col2:
        st.markdown(
            "<h3 style='text-align: center;'>VS</h3>", unsafe_allow_html=True
        )
        # Inserimento del risultato in tempo reale
        nuovo_res = st.text_input(
            f"Risultato {idx}",
            value=match["res"],
            key=f"res_{idx}",
            label_visibility="collapsed",
        )
        if nuovo_res != match["res"]:
          db["eliminazione_diretta"][fase][idx]["res"] = nuovo_res
          salva_dati(db)
          st.rerun()

      with col3:
        is_my_team_2 = coppia_selezionata == match["p2"]
        prefix_2 = "⭐ " if is_my_team_2 else ""
        st.markdown(f"### **{prefix_2}{match['p2']}**")
        st.caption(f"📍 Provenienza: {match['prov2']}")

      st.markdown("---")

# Pulsante manuale di sincronizzazione immediata
if st.button("🔄 Sincronizza Subito", use_container_width=True):
  st.rerun()
