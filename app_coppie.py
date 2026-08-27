import json
import os
import random
import re
from fpdf import FPDF
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=5000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(
    page_title="Torneo Coppie Fisse Live - Cyber Gaming Edition",
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
        .neon-purple { color: #d946ef !important; text-shadow: 0 0 12px rgba(217,70,239,0.8), 0 0 25px rgba(217,70,239,0.4); }
        .neon-green { color: #00ff66 !important; text-shadow: 0 0 12px rgba(0,255,102,0.8), 0 0 25px rgba(0,255,102,0.4); }
        .neon-silver { color: #e2e8f0 !important; text-shadow: 0 0 12px rgba(226,232,240,0.7), 0 0 25px rgba(226,232,240,0.3); }

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

DB_FILE = "coppie_data.json"


def carica_dati():
  dati_default = {
      "stato": "setup",
      "coppie": [],
      "num_tavoli": 6,
      "num_gironi": 8,
      "admin_pin": "0000",
      "gironi": {},
      "calendario_gironi": {},
      "punti_gironi": {},
      "fasi_finali_configurate": False,
      "num_qualificate_knockout": 4,
      "tabellone_principale": [],
      "terzo_quarto": [],
      "tabellone_secondario": [],
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


def ricalcola_classifiche_gironi():
  for g_nome, coppie_lista in db["gironi"].items():
    stats = {
        c: {
            "punti": 0,
            "partite_giocate": 0,
            "vinte": 0,
            "perse": 0,
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

            stats[c1]["partite_giocate"] += 1
            stats[c2]["partite_giocate"] += 1

            if g1 > g2:
              pt_s1, pt_s2 = (3, 0) if diff >= 2 else (2, 1)
              stats[c1]["vinte"] += 1
              stats[c2]["perse"] += 1
            elif g2 > g1:
              pt_s1, pt_s2 = (0, 3) if diff >= 2 else (1, 2)
              stats[c2]["vinte"] += 1
              stats[c1]["perse"] += 1
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
  if num_partite_turno == 1:
    return "🏆 FINALE SUPREMA"
  elif num_partite_turno == 2:
    return "⚔️ SEMIFINALI EPICHE"
  elif num_partite_turno == 4:
    return "🔥 QUARTI DI FINALE"
  elif num_partite_turno == 8:
    return "⚡ OTTAVI DI FINALE"
  else:
    return f"Fase a Eliminazione ({num_partite_turno * 2} Coppie)"


# --- BARRA LATERALE CYBER ---
st.sidebar.header("⚙️ Pannello Controllo")

if db["stato"] != "setup":
  pdf_data = genera_pdf_coppie()
  st.sidebar.download_button(
      label="📥 Scarica Schema PDF",
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
      "⚙️ Mostra / Nascondi Setup Iniziale", use_container_width=True
  ):
    st.session_state["mostra_setup"] = not st.session_state.get(
        "mostra_setup", False
    )

if is_admin and db["stato"] == "fasi_finali":
  if st.sidebar.button(
      "🔙 Torna temporaneamente ai Gironi", use_container_width=True
  ):
    db["stato"] = "gironi"
    salva_dati(db)
    st.rerun()
  st.sidebar.markdown("---")

st.sidebar.subheader("⚠️ Zona Pericolo")
if is_admin:
  conferma_reset = st.sidebar.checkbox(
      "Spunta per confermare il reset totale", key="checkbox_reset_gara"
  )
  if st.sidebar.button(
      "🔄 Ricomincia la gara da zero", use_container_width=True
  ):
    if conferma_reset:
      if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
      for key in list(st.session_state.keys()):
        del st.session_state[key]
      st.success("Torneo azzerato con successo! Ricarico...")
      st.rerun()
    else:
      st.sidebar.warning(
          "⚠️ Spunta la casella di conferma sopra per procedere."
      )
else:
  st.sidebar.info("🔐 Accedi come admin per resettare la gara.")

st.sidebar.markdown("---")

# --- INTERFACCIA PRINCIPALE ---
st.markdown(
    """
    <div class="neon-title-box">
        <div class="neon-title-text">⚡ TORNEO COPPIE FISSE LIVE</div>
        <div class="neon-subtitle">Regolamento 3 Tocchi Uisp • Cyber Gaming & Esports Edition</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("ℹ️ Come funziona il torneo"):
  st.markdown(
      """
        L'app gestisce la prima fase a gironi (8 gironi da 5 squadre) e il tabellone finale a eliminazione diretta a 32 squadre (dagli ottavi in poi) con incroci mirati per proteggere le squadre dello stesso girone.
        """,
      unsafe_allow_html=True,
  )

st.markdown(
    """
    <div style="padding: 16px 20px; background: linear-gradient(135deg, rgba(48, 16, 26, 0.95) 0%, rgba(24, 6, 12, 0.98) 100%); border: 2px solid #ff3366; border-radius: 16px; font-size: 14px; color: #ff3366; margin-bottom: 20px; font-weight: bold; line-height: 1.5; box-shadow: 0 0 30px rgba(255,51,102,0.35);">
        🚨 Chi vince è pregato di inserire il risultato esatto tramite i selettori e chi è in coda di tenersi pronto a salire al primo calcetto libero.
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

if is_admin:
  st.markdown(
      """
      <div style="padding: 12px 18px; background: linear-gradient(135deg, rgba(10, 36, 20, 0.95) 0%, rgba(4, 16, 8, 0.98) 100%); border: 2px solid #00ff66; border-radius: 14px; font-size: 14px; color: #00ff66; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 25px rgba(0,255,102,0.3);">
          🛡️ Modalità Amministratore attiva: Accesso completo sbloccato.
      </div>
      """,
      unsafe_allow_html=True,
  )
elif coppia_selezionata == "-- Seleziona la tua coppia per accedere --":
  st.markdown(
      """
      <div style="padding: 14px 18px; background: linear-gradient(135deg, rgba(40, 32, 10, 0.95) 0%, rgba(16, 12, 4, 0.98) 100%); border: 2px solid #ffaa00; border-radius: 14px; font-size: 14px; color: #ffaa00; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 25px rgba(255,170,0,0.3);">
          ⚠️ Seleziona la tua coppia dal menu a tendina per inserire i risultati e seguire il tuo percorso.
      </div>
      """,
      unsafe_allow_html=True,
  )
  st.stop()
else:
  st.markdown(
      f"""
      <div style="padding: 12px 18px; background: linear-gradient(135deg, rgba(10, 36, 20, 0.95) 0%, rgba(4, 16, 8, 0.98) 100%); border: 2px solid #00ff66; border-radius: 14px; font-size: 14px; color: #00ff66; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 25px rgba(0,255,102,0.3);">
          ✅ Accesso effettuato come: <b>{coppia_selezionata}</b>
      </div>
      """,
      unsafe_allow_html=True,
  )

# --- DETTAGLIO SQUADRA UTENTE E STATO PARTITE ---
if not is_admin or coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
  if coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
    with st.expander(
        f"👁️ Segui la tua coppia: {coppia_selezionata}", expanded=True
    ):
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

      match_in_corso_coppia = None
      pos_in_coda = None

      if db["stato"] == "gironi":
        num_tavoli = db.get("num_tavoli", 6)
        max_turni = (
            max([len(turni) for turni in db["calendario_gironi"].values()])
            if db["calendario_gironi"]
            else 0
        )
        for t_num in range(1, max_turni + 1):
          for g_n, turni_girone in db["calendario_gironi"].items():
            for t_obj in turni_girone:
              if t_obj["turno"] == t_num:
                for m in t_obj["partite"]:
                  if not m.get("giocata", False):
                    if (
                        m["c1"] == coppia_selezionata
                        or m["c2"] == coppia_selezionata
                    ):
                      if m.get("in_corso", False):
                        match_in_corso_coppia = m

        all_da_giocare = []
        for t_num in range(1, max_turni + 1):
          for g_n in sorted(db["calendario_gironi"].keys()):
            for t_obj in db["calendario_gironi"][g_n]:
              if t_obj["turno"] == t_num:
                for m in t_obj["partite"]:
                  if not m.get("giocata", False) and not m.get(
                      "in_corso", False
                  ):
                    all_da_giocare.append(m)

        for idx_coda, m_coda in enumerate(all_da_giocare[:num_tavoli]):
          if (
              m_coda["c1"] == coppia_selezionata
              or m_coda["c2"] == coppia_selezionata
          ):
            pos_in_coda = idx_coda + 1

      st.markdown(
          f"""
          <div class="neon-box-main">
              <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #d946ef; font-weight: bold; margin-bottom: 6px;">Riepilogo Squadra</div>
              <div style="font-size: 24px; font-weight: 800; color: #ffffff; margin-bottom: 16px; text-shadow: 0 0 15px rgba(0,242,254,0.6);">🤝 {coppia_selezionata}</div>
              <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                  <div style="background: rgba(8, 12, 20, 0.85); border: 1.5px solid rgba(0, 242, 254, 0.5); border-radius: 12px; padding: 14px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 15px rgba(0,242,254,0.2);">
                      <div style="font-size: 11px; color: #8b949e; font-weight: bold;">GIRONE</div>
                      <div class="neon-blue" style="font-size: 20px; font-weight: 700; margin-top: 4px;">{girone_mio if girone_mio else 'N.D.'}</div>
                  </div>
                  <div style="background: rgba(8, 12, 20, 0.85); border: 1.5px solid rgba(0, 255, 102, 0.5); border-radius: 12px; padding: 14px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 15px rgba(0,255,102,0.2);">
                      <div style="font-size: 11px; color: #8b949e; font-weight: bold;">POSIZIONE</div>
                      <div class="neon-green" style="font-size: 20px; font-weight: 700; margin-top: 4px;">{str(pos_mia) + '° posto' if pos_mia else 'N.D.'}</div>
                  </div>
                  <div style="background: rgba(8, 12, 20, 0.85); border: 1.5px solid rgba(255, 170, 0, 0.5); border-radius: 12px; padding: 14px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 15px rgba(255,170,0,0.2);">
                      <div style="font-size: 11px; color: #8b949e; font-weight: bold;">PUNTI / DR</div>
                      <div class="neon-gold" style="font-size: 20px; font-weight: 700; margin-top: 4px;">{info_mie['punti'] if info_mie else 0} pt <span style="font-size: 12px; font-weight: normal; color: #8b949e;">(DR: {info_mie['dr'] if info_mie else 0})</span></div>
                  </div>
              </div>
          </div>
          """,
          unsafe_allow_html=True,
      )

      if match_in_corso_coppia:
        avversario = (
            match_in_corso_coppia["c2"]
            if match_in_corso_coppia["c1"] == coppia_selezionata
            else match_in_corso_coppia["c1"]
        )
        tavolo_num = match_in_corso_coppia.get("tavolo", "N.D.")
        match_id = match_in_corso_coppia["id"]

        st.markdown(
            f"""
            <div class="match-live-card-animated" style="margin-bottom: 20px;">
                <div class="neon-gold" style="font-size: 15px; font-weight: bold; margin-bottom: 6px;">🔴 PARTITA IN CORSO AL BILIARDINO {tavolo_num}!</div>
                <div style="font-size: 16px; color: #ffffff;">Stai giocando contro: <b>{avversario}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(
            f"⚙️ Inserisci Gol Biliardino {tavolo_num}", expanded=True
        ):
          st.markdown(f"**🤝 {match_in_corso_coppia['c1']}**")
          gol_p1 = st.segmented_control(
              "Gol Coppia 1",
              options=list(range(8)),
              default=int(match_in_corso_coppia.get("gol1", 0)),
              key=f"riep_g1_{match_id}",
              label_visibility="collapsed",
          )

          st.markdown(f"**🤝 {match_in_corso_coppia['c2']}**")
          gol_p2 = st.segmented_control(
              "Gol Coppia 2",
              options=list(range(8)),
              default=int(match_in_corso_coppia.get("gol2", 0)),
              key=f"riep_g2_{match_id}",
              label_visibility="collapsed",
          )

          if st.button(
              "💾 Salva Risultato Finale",
              key=f"riepilogo_save_{match_id}",
              use_container_width=True,
          ):
            match_in_corso_coppia["gol1"] = (
                int(gol_p1) if gol_p1 is not None else 0
            )
            match_in_corso_coppia["gol2"] = (
                int(gol_p2) if gol_p2 is not None else 0
            )
            match_in_corso_coppia["giocata"] = True
            match_in_corso_coppia["in_corso"] = False
            match_in_corso_coppia["tavolo"] = None
            ricalcola_classifiche_gironi()
            salva_dati(db)
            st.success("Risultato salvato con successo!")
            st.rerun()

      elif pos_in_coda is not None:
        st.markdown(
            f"""
            <div class="queue-item-animated" style="margin-bottom: 20px;">
                <div class="neon-green" style="font-size: 14px; font-weight: bold;">⏳ PARTITE IN CODA</div>
                <div style="font-size: 14px; color: #ffffff; margin-top: 4px;">La tua coppia è in posizione <b>#{pos_in_coda}</b> nella coda d'attesa. Teniti pronto!</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# 1. SETUP INIZIALE
if db["stato"] == "setup" or st.session_state.get("mostra_setup", False):
  st.subheader("1. Configurazione Iniziale Torneo a Coppie (8 Gironi da 5)")

  if not is_admin:
    st.markdown(
        """
        <div style="padding: 12px 18px; background: linear-gradient(135deg, rgba(40, 32, 10, 0.95) 0%, rgba(16, 12, 4, 0.98) 100%); border: 2px solid #ffaa00; border-radius: 14px; font-size: 14px; color: #ffaa00; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 25px rgba(255,170,0,0.3);">
            ⚠️ Configurazione bloccata. Accedi come amministratore dalla barra laterale con il PIN.
        </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    whatsapp_text = st.text_area(
        "Incolla qui la lista delle coppie da WhatsApp:", height=150
    )

    col1, col2, col3 = st.columns(3)
    with col1:
      db["num_tavoli"] = st.number_input(
          "Numero di biliardini",
          min_value=1,
          max_value=10,
          value=int(db["num_tavoli"]),
      )
    with col2:
      db["num_gironi"] = st.number_input(
          "Numero di gironi",
          min_value=1,
          max_value=8,
          value=int(db["num_gironi"]),
      )
    with col3:
      db["num_qualificate_knockout"] = st.number_input(
          "Coppie che passano per girone (Zona Verde)",
          min_value=1,
          max_value=5,
          value=4,
      )

    db["admin_pin"] = st.text_input("Cambia PIN Admin", value=db["admin_pin"])

    if st.button("🚀 Crea Gironi e Sorteggia Coppie", use_container_width=True):
      coppie = []
      for line in whatsapp_text.split("\n"):
        nome_c = pulisci_nome(line)
        if nome_c:
          coppie.append(nome_c)

      num_g = int(db["num_gironi"])

      if len(coppie) < (num_g * 2):
        st.error(
            f"Hai inserito {len(coppie)} coppie. Con {num_g} gironi servono"
            f" almeno {num_g * 2} coppie."
        )
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
                    "partite_giocate": 0,
                    "vinte": 0,
                    "perse": 0,
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
        db["tabellone_principale"] = []
        db["terzo_quarto"] = []
        salva_dati(db)
        st.success(f"Creati con successo {num_g} gironi!")
        st.session_state["mostra_setup"] = False
        st.rerun()
  st.markdown("---")

# 2. FASE A GIRONI
if db["stato"] == "gironi":
  ricalcola_classifiche_gironi()
  num_tavoli = db.get("num_tavoli", 6)

  if db.get("fasi_finali_configurate", False) and is_admin:
    if st.button(
        "⬅️ Torna alla schermata delle Fasi Finali", use_container_width=True
    ):
      db["stato"] = "fasi_finali"
      salva_dati(db)
      st.rerun()
    st.markdown("---")

  soglia_passaggio = db.get("num_qualificate_knockout", 4)

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

  partite_in_corso, partite_da_giocare = [], []

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

  st.subheader("⚡ Stato dei Biliardini e Coda Incontri")

  col_ic, col_coda = st.columns(2)

  with col_ic:
    st.markdown("#### 🔥 Partite in Corso ai Tavoli (Live)")
    if not partite_in_corso:
      st.markdown(
          """
          <div style="background: rgba(16, 22, 36, 0.7); border: 1.5px solid rgba(0, 242, 254, 0.3); padding: 14px; border-radius: 12px; text-align: center; color: #8b949e; font-size: 13px;">
              Nessuna partita in corso al momento.
          </div>
          """,
          unsafe_allow_html=True,
      )
    else:
      for m in partite_in_corso:
        tavolo_str = (
            f"<b>🏟️ BILIARDINO {m.get('tavolo')}</b>"
            if m.get("tavolo")
            else "<b>🏟️ IN CAMPO</b>"
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
                        <div class="match-live-card-animated" style="margin-bottom: 14px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <span class="neon-gold" style="font-size: 14px; font-weight: bold;">{tavolo_str}</span>
                                <span style="font-size: 12px; color: #8b949e; font-weight: bold;">{m['girone']}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="font-size: 16px; font-weight: bold; color: #ffffff; text-align: left; flex: 1;">🤝 {m['c1']}</div>
                                <div style="color: #ff3366; font-weight: 900; font-size: 16px; padding: 0 10px;">VS</div>
                                <div style="font-size: 16px; font-weight: bold; color: #ffffff; text-align: right; flex: 1;">🤝 {m['c2']}</div>
                            </div>
                        </div>
                        """,
              unsafe_allow_html=True,
          )

          if fa_al_caso_nostro:
            with st.expander(
                f"⚙️ Inserisci Gol Biliardino {m.get('tavolo', '')} (Admin)"
            ):
              st.markdown(f"**🤝 {m['c1']}**")
              gol_p1 = st.segmented_control(
                  "Gol Coppia 1",
                  options=list(range(8)),
                  default=int(m.get("gol1", 0)),
                  key=f"live_g1_{match_id}",
                  label_visibility="collapsed",
              )

              st.markdown(f"**🤝 {m['c2']}**")
              gol_p2 = st.segmented_control(
                  "Gol Coppia 2",
                  options=list(range(8)),
                  default=int(m.get("gol2", 0)),
                  key=f"live_g2_{match_id}",
                  label_visibility="collapsed",
              )

              if st.button(
                  "💾 Salva Risultato Finale",
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
                st.success("Risultato registrato con successo!")
                st.rerun()

          if is_admin:
            with st.expander(f"⚙️ Opzioni Admin Tavolo {m.get('tavolo', '')}"):
              if st.button(
                  "🛑 Libera tavolo senza salvare",
                  key=f"admin_libera_{match_id}",
                  use_container_width=True,
              ):
                m["in_corso"] = False
                m["tavolo"] = None
                salva_dati(db)
                st.success("Tavolo liberato con successo!")
                st.rerun()

  with col_coda:
    partite_in_coda_correnti = partite_da_giocare[:num_tavoli]
    st.markdown("#### ⏳ In Coda (Prossimi Incontri)")
    if not partite_in_coda_correnti:
      st.markdown(
          """
          <div style="background: rgba(16, 22, 36, 0.7); border: 1.5px solid rgba(0, 242, 254, 0.3); padding: 14px; border-radius: 12px; text-align: center; color: #8b949e; font-size: 13px;">
              La coda è vuota.
          </div>
          """,
          unsafe_allow_html=True,
      )
    else:
      for idx, m in enumerate(partite_in_coda_correnti):
        st.markdown(
            f"""
                    <div class="queue-item-animated">
                        <b class="neon-green" style="font-size: 13px;">⏳ POSIZIONE #{idx+1} IN CODA • {m['girone']}</b><br>
                        <div style="font-weight: bold; font-size: 15px; margin-top: 6px; color: #ffffff;">{m['c1']} vs {m['c2']}</div>
                    </div>
                    """,
            unsafe_allow_html=True,
        )

  st.markdown("---")
  st.subheader("📊 Classifiche Ufficiali dei Gironi")

  nomi_gironi_chiavi = list(db["gironi"].keys())
  for g_nome in nomi_gironi_chiavi:
    with st.container():
      st.markdown(
          f"""
                <div style="background: linear-gradient(135deg, rgba(16, 22, 36, 0.95) 0%, rgba(8, 12, 20, 0.98) 100%); border: 2px solid #00f2fe; border-radius: 14px; padding: 14px; margin-bottom: 18px; box-shadow: 0 0 20px rgba(0,242,254,0.2);">
                    <div style="font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 900; color: #00f2fe; margin-bottom: 10px; text-transform: uppercase;">📁 {g_nome}</div>
                """,
          unsafe_allow_html=True,
      )

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

      for idx, (coppia, info) in enumerate(sorted_c):
        posizione = idx + 1
        in_zona_verde = posizione <= soglia_passaggio

        colore_bordo = (
            "rgba(0, 255, 102, 0.6)"
            if in_zona_verde
            else "rgba(255, 51, 102, 0.4)"
        )
        colore_sfondo = (
            "linear-gradient(135deg, rgba(0, 255, 102, 0.12) 0%, rgba(8, 12, 20, 0.9) 100%)"
            if in_zona_verde
            else "linear-gradient(135deg, rgba(255, 51, 102, 0.08) 0%, rgba(8, 12, 20, 0.9) 100%)"
        )
        simbolo_stato = "🟢" if in_zona_verde else "🔴"
        testo_colore_pos = "#00ff66" if in_zona_verde else "#ff3366"

        st.markdown(
            f"""
                <div style="background: {colore_sfondo}; border: 1.5px solid {colore_bordo}; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 15px; font-weight: 900; color: {testo_colore_pos}; min-width: 28px;">{posizione}° {simbolo_stato}</span>
                        <span style="font-size: 15px; font-weight: 700; color: #ffffff;">{coppia}</span>
                    </div>
                    <div style="display: flex; gap: 10px; font-size: 13px; text-align: right;">
                        <div><span style="color: #8b949e; font-size: 10px; display: block;">PT</span><b style="color: #ffaa00; font-size: 15px;">{info['punti']}</b></div>
                        <div><span style="color: #8b949e; font-size: 10px; display: block;">G</span>{info['partite_giocate']}</div>
                        <div><span style="color: #8b949e; font-size: 10px; display: block;">V/P</span>{info['vinte']}/{info['perse']}</div>
                        <div><span style="color: #8b949e; font-size: 10px; display: block;">DR</span><span style="color: {'#00ff66' if info['dr']>=0 else '#ff3366'};">{info['dr']:+d}</span></div>
                    </div>
                </div>
                """,
            unsafe_allow_html=True,
        )

      st.markdown("</div>", unsafe_allow_html=True)

  if is_admin:
    st.markdown("---")
    btn_text = (
        "🔄 Ricrea Tabellone a Eliminazione Diretta"
        if db.get("fasi_finali_configurate", False)
        else "🏆 Genera Tabellone Ottavi a 32 Squadre"
    )
    if st.button(btn_text, use_container_width=True):
      # Raccogliamo le classifiche ordinate per ciascun girone (da A a H)
      classifiche_gironi = {}
      for g_nome in sorted(db["gironi"].keys()):
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
        classifiche_gironi[g_nome] = [c[0] for c in sorted_c]

      # Assicuriamoci di avere i gironi chiave da A a H
      nomi_g = sorted(list(classifiche_gironi.keys()))
      if len(nomi_g) >= 8:
        gA, gB, gC, gD, gE, gF, gG, gH = (
            nomi_g[0],
            nomi_g[1],
            nomi_g[2],
            nomi_g[3],
            nomi_g[4],
            nomi_g[5],
            nomi_g[6],
            nomi_g[7],
        )

        def get_sq(girone_nome, pos):
          lst = classifiche_gironi.get(girone_nome, [])
          return lst[pos - 1] if len(lst) >= pos else "RIPOSO"

        # Griglia esatta richiesta dagli ottavi di finale (32 squadre)
        ottavi_partite = [
            # Lato Alto
            {
                "id": "ottavi_1",
                "s1": get_sq(gA, 1),
                "s2": get_sq(gE, 4),
                "giocata": False,
                "vincente": None,
            },
            {
                "id": "ottavi_2",
                "s1": get_sq(gC, 2),
                "s2": get_sq(gG, 3),
                "giocata": False,
                "vincente": None,
            },
            {
                "id": "ottavi_3",
                "s1": get_sq(gB, 1),
                "s2": get_sq(gF, 4),
                "giocata": False,
                "vincente": None,
            },
            {
                "id": "ottavi_4",
                "s1": get_sq(gD, 2),
                "s2": get_sq(gH, 3),
                "giocata": False,
                "vincente": None,
            },
            # Lato Basso
            {
                "id": "ottavi_5",
                "s1": get_sq(gC, 1),
                "s2": get_sq(gG, 4),
                "giocata": False,
                "vincente": None,
            },
            {
                "id": "ottavi_6",
                "s1": get_sq(gA, 2),
                "s2": get_sq(gE, 3),
                "giocata": False,
                "vincente": None,
            },
            {
                "id": "ottavi_7",
                "s1": get_sq(gD, 1),
                "s2": get_sq(gH, 4),
                "giocata": False,
                "vincente": None,
            },
            {
                "id": "ottavi_8",
                "s1": get_sq(gB, 2),
                "s2": get_sq(gF, 3),
                "giocata": False,
                "vincente": None,
            },
        ]

        db["tabellone_principale"] = [{"turno": 1, "partite": ottavi_partite}]
        db["terzo_quarto"] = []
        db["stato"] = "fasi_finali"
        db["fasi_finali_configurate"] = True
        salva_dati(db)
        st.success(
            "Tabellone a 32 squadre generato con successo rispettando gli"
            " incroci!"
        )
        st.rerun()
      else:
        st.error("Servono almeno 8 gironi configurati per questa griglia.")

# 3. FASI FINALI (ELIMINAZIONE DIRETTA)
elif db["stato"] == "fasi_finali":
  st.subheader("🏆 Tabellone a Eliminazione Diretta (32 Coppie)")

  turni_tab = db["tabellone_principale"]
  campione, secondo_posto, terzo_posto, quarto_posto = None, None, None, None

  for t_idx, turno_obj in enumerate(turni_tab):
    t_num = turno_obj["turno"]
    partite_turno = turno_obj["partite"]

    nome_etichetta = ottieni_nome_turno_dinamico(len(partite_turno))

    st.markdown(
        f"""
            <div style="background: linear-gradient(90deg, #00f2fe 0%, #d946ef 100%); padding: 14px 20px; border-radius: 12px; margin: 24px 0 16px 0; color: white; text-align: center; box-shadow: 0 0 25px rgba(0,242,254,0.4);">
                <h3 style="margin: 0; font-size: 19px; font-weight: bold; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">⚡ {nome_etichetta}</h3>
            </div>
            """,
        unsafe_allow_html=True,
    )

    tutti_giocati = True
    vincitori_turno, perdenti_turno = [], []

    for idx, m in enumerate(partite_turno):
      match_id = m["id"]
      s1_nome, s2_nome = m["s1"], m["s2"]

      if s2_nome == "RIPOSO":
        m["giocata"] = True
        m["vincente"] = s1_nome
        vincitori_turno.append(s1_nome)
        continue
      elif s1_nome == "RIPOSO":
        m["giocata"] = True
        m["vincente"] = s2_nome
        vincitori_turno.append(s2_nome)
        continue

      if m["giocata"]:
        vincitori_turno.append(m["vincente"])
        perdente = s2_nome if m["vincente"] == s1_nome else s1_nome
        perdenti_turno.append(perdente)
        centro_testo = f"<b class='neon-green'>Vince: {m['vincente']}</b>"
      else:
        tutti_giocati = False
        centro_testo = "<span style='color: #8b949e;'>VS</span>"

      st.markdown(
          f"""
                <div style="background: linear-gradient(135deg, rgba(16, 22, 36, 0.9) 0%, rgba(8, 12, 20, 0.95) 100%); border: 1.5px solid rgba(0, 242, 254, 0.3); border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.4);">
                    <b>{s1_nome}</b> vs <b>{s2_nome}</b><br>{centro_testo}
                </div>
                """,
          unsafe_allow_html=True,
      )

      if is_admin:
        with st.expander(f"⚙️ Assegna Vincitore: {s1_nome} vs {s2_nome}"):
          col_v1, col_v2 = st.columns(2)
          with col_v1:
            if st.button(
                f"🏆 {s1_nome}",
                key=f"win_s1_{match_id}",
                use_container_width=True,
            ):
              m["giocata"] = True
              m["vincente"] = s1_nome
              salva_dati(db)
              st.rerun()
          with col_v2:
            if st.button(
                f"🏆 {s2_nome}",
                key=f"win_s2_{match_id}",
                use_container_width=True,
            ):
              m["giocata"] = True
              m["vincente"] = s2_nome
              salva_dati(db)
              st.rerun()

    if "FINALE" in nome_etichetta and tutti_giocati and len(partite_turno) == 1:
      fin_m = partite_turno[0]
      if fin_m["giocata"] and fin_m.get("vincente"):
        campione = fin_m["vincente"]
        secondo_posto = fin_m["s2"] if campione == fin_m["s1"] else fin_m["s1"]

    # Generazione automatica turni successivi (Quarti, Semifinali, Finale)
    if tutti_giocati and len(vincitori_turno) > 1 and is_admin:
      prossimo_turno_num = t_num + 1
      turno_esistente = next(
          (t for t in turni_tab if t["turno"] == prossimo_turno_num), None
      )
      if not turno_esistente:
        nuove_partite = []
        for i in range(0, len(vincitori_turno), 2):
          if i + 1 < len(vincitori_turno):
            nuove_partite.append({
                "id": f"turno_{prossimo_turno_num}_m{i//2}",
                "s1": vincitori_turno[i],
                "s2": vincitori_turno[i + 1],
                "giocata": False,
                "vincente": None,
            })
        if nuove_partite:
          turni_tab.append({"turno": prossimo_turno_num, "partite": nuove_partite})
          salva_dati(db)
          st.rerun()

  if campione:
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, rgba(16, 22, 36, 0.95) 0%, rgba(8, 12, 20, 0.98) 100%); border: 2px solid #ffaa00; border-radius: 18px; padding: 24px; text-align: center; margin-top: 24px; box-shadow: 0 0 35px rgba(255,170,0,0.35);">
            <h2 class="neon-gold">🏆 PODIO FINALE</h2>
            <p style="font-size: 18px; margin: 10px 0;"><b>🥇 1° Posto:</b> <span class="neon-gold">{campione}</span></p>
            <p style="font-size: 17px; margin: 8px 0;"><b>🥈 2° Posto:</b> <span class="neon-silver">{secondo_posto}</span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
