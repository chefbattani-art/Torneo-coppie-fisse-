import json
import os
import random
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=3000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(
    page_title="Torneo Coppie Fisse Live",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- STILE GLOBALE PROFESSIONALE - ALTA VISIBILITA' PER TUTTE LE ETA' ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&display=swap');

       .stApp {
            background: #F1F5F9;
            color: #0F172A;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        /* SIDEBAR - Blu notte professionale */
        section[data-testid="stSidebar"] {
            background: #0F172A!important;
            border-right: 4px solid #2563EB;
        }
        section[data-testid="stSidebar"].stMarkdown,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #FFFFFF!important;
            font-weight: 600!important;
            font-size: 15px!important;
        }
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #60A5FA!important;
        }

        /* INPUT - Altissimo contrasto */
        input, textarea, div[data-baseweb="input"] > div {
            background-color: #FFFFFF!important;
            color: #0F172A!important;
            -webkit-text-fill-color: #0F172A!important;
            border-radius: 12px!important;
            border: 2px solid #CBD5E1!important;
            font-weight: 700!important;
            font-size: 18px!important;
        }
        input:focus, textarea:focus, div[data-baseweb="input"] > div:focus-within {
            border-color: #2563EB!important;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15)!important;
        }
       .stTextInput label,.stTextArea label,.stSelectbox label {
            color: #0F172A!important;
            font-weight: 800!important;
            font-size: 14px!important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        h1, h2, h3 {
            color: #0F172A!important;
            font-weight: 800!important;
        }

        /* BOTTONI - Grandi e visibili */
        div.stButton > button {
            border-radius: 12px!important;
            font-weight: 800!important;
            border: none!important;
            background: #2563EB!important;
            color: #FFFFFF!important;
            font-size: 17px!important;
            padding: 12px 20px!important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
        div.stButton > button:hover {
            background: #1D4ED8!important;
            color: #FFFFFF!important;
        }

        /* SELECTBOX TORNEO */
        div[data-baseweb="select"] > div {
            background: #FFFFFF!important;
            border: 2.5px solid #0F172A!important;
            border-radius: 14px!important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08)!important;
            min-height: 64px!important;
        }
        div[data-baseweb="select"] span {
            color: #0F172A!important;
            font-size: 19px!important;
            font-weight: 800!important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_FILE = "coppie_data_multi.json"

def carica_dati():
  dati_default = {"tornei": {}, "admin_pin": "0000"}
  if os.path.exists(DB_FILE):
    try:
      with open(DB_FILE, "r") as f:
        dati_salvati = json.load(f)
        if "tornei" not in dati_salvati:
          return dati_default
        tornei_da_rimuovere = ["TORNEO GIOVEDÌ 3 MASSA LOMBARDA", "TORNEO GIOVEDÌ 3 MASSALOMBARDA", "Torneo Principale (PRO)", "Torneo Secondario (Amatoriale)"]
        for t_rem in tornei_da_rimuovere:
          if t_rem in dati_salvati["tornei"]:
            del dati_salvati["tornei"][t_rem]
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
    stats = {c: {"punti": 0, "gf": 0, "gs": 0, "dr": 0, "scontri_diretti_pt": {}} for c in coppie_lista}
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
      punti_gruppo = {}
      for c in coppie_lista:
        p = stats[c]["punti"]
        if p not in punti_gruppo:
          punti_gruppo[p] = []
        punti_gruppo[p].append(c)
      for p, gruppo in punti_gruppo.items():
        if len(gruppo) > 1:
          mini_punti = {c: 0 for c in gruppo}
          for turno_obj in t_data["calendario_gironi"][g_nome]:
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
  q_fascia_a = int(t_data.get("qualificati_fascia_a", 4))
  sorted_c = sorted(dati_girone.items(), key=lambda x: (x[1]["punti"], x[1]["scontri_diretti_pt"], x[1]["dr"], x[1]["gf"]), reverse=True)
  for idx, (coppia, info) in enumerate(sorted_c):
    gioc, tot = calcola_partite_giocate_coppia(torneo_selezionato, g_nome, coppia)
    is_fascia_a = idx < q_fascia_a
    border_left = "#2563EB" if is_fascia_a else "#94A3B8"
    badge_bg = "#DBEAFE" if is_fascia_a else "#F1F5F9"
    badge_color = "#1E40AF" if is_fascia_a else "#475569"
    fascia_label = "FASCIA A" if is_fascia_a else "FASCIA B"

    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 6px solid {border_left}; border-radius: 14px; padding: 14px 16px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="background: {badge_bg}; color: {badge_color}; font-weight: 800; font-size: 13px; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">{idx+1}°</div>
                <div>
                    <div style="font-size: 15px; font-weight: 800; color: #0F172A;">{coppia}</div>
                    <div style="font-size: 11px; font-weight: 700; color: {badge_color}; letter-spacing: 0.5px;">{fascia_label}</div>
                </div>
            </div>
            <div style="display: flex; gap: 8px; text-align: center;">
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 6px 10px; min-width: 46px;">
                    <div style="font-size: 9px; color: #92400E; font-weight: 800;">PUNTI</div>
                    <div style="font-weight: 800; color: #0F172A; font-size: 16px;">{info['punti']}</div>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px 10px; min-width: 46px;">
                    <div style="font-size: 9px; color: #64748B; font-weight: 800;">GIOCATE</div>
                    <div style="font-weight: 700; color: #0F172A;">{gioc}/{tot}</div>
                </div>
                <div style="background: {'#DCFCE7' if info['dr'] >=0 else '#FEE2E2'}; border-radius: 8px; padding: 6px 10px; min-width: 46px;">
                    <div style="font-size: 9px; color: #334155; font-weight: 800;">DIFF</div>
                    <div style="font-weight: 800; color: {'#166534' if info['dr'] >=0 else '#991B1B'};">{info['dr']:+d}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def genera_pdf_coppie(torneo_selezionato):
  t_data = db["tornei"][torneo_selezionato]
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Helvetica", "B", 16)
  titolo_pdf = f"Torneo: {torneo_selezionato} - Schema Gironi"
  pdf.cell(0, 10, titolo_pdf.encode("latin-1", "ignore").decode("latin-1"), 0, 1, "C")
  pdf.ln(5)
  for g_nome, turni in t_data["calendario_gironi"].items():
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"--- {g_nome} ---".encode("latin-1", "ignore").decode("latin-1"), 0, 1, "L")
    for turno_obj in turni:
      pdf.set_font("Helvetica", "B", 11)
      pdf.cell(0, 7, f"Turno {turno_obj['turno']}", 0, 1, "L")
      pdf.set_font("Helvetica", "", 10)
      for idx, m in enumerate(turno_obj["partite"]):
        risultato = f"{m['gol1']} - {m['gol2']}" if m.get("giocata", False) else "Da giocare"
        riga = f" {m['c1']} VS {m['c2']} -> {risultato}"
        pdf.cell(0, 6, riga.encode("latin-1", "ignore").decode("latin-1"), 0, 1, "L")
      pdf.ln(2)
  return bytes(pdf.output())

def ottieni_nome_turno_dinamico(num_partite_turno):
  tot_squadre = num_partite_turno * 2
  if num_partite_turno == 1: return "🏆 FINALE"
  elif num_partite_turno == 2: return "⚔️ SEMIFINALI"
  elif num_partite_turno == 4: return "🔥 QUARTI DI FINALE"
  elif num_partite_turno == 8: return "⭐ OTTAVI DI FINALE"
  elif num_partite_turno == 16: return "🌟 SEDICESIMI DI FINALE"
  else: return f"Eliminazione Diretta ({tot_squadre} Coppie)"

def crea_abbinamenti_fascia_a_generico(classificate_per_girone):
  nomi_g = list(classificate_per_girone.keys())
  tutte_a = []
  for g_n in nomi_g:
    for sq in classificate_per_girone[g_n]:
      tutte_a.append((sq, g_n))
  abbinamenti = []
  n = len(tutte_a)
  for i in range(n // 2):
    abbinamenti.append((tutte_a[i], tutte_a[n - 1 - i] if (n - 1 - i) >= 0 else ("RIPOSO", "")))
  return abbinamenti

def crea_abbinamenti_fascia_b(classificate_per_girone, q_fascia_a):
  tutte_b = []
  for g_n, lista in classificate_per_girone.items():
    for idx in range(q_fascia_a, len(lista)):
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
    if idx_trovato!= -1:
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

# --- GESTIONE ADMIN DALLA SIDEBAR ---
admin_param = st.query_params.get("admin", "false")
is_admin_autenticato = admin_param == "true"
modalita_admin = st.sidebar.checkbox("Modalità Amministratore (PIN)", value=is_admin_autenticato)
is_admin = False
if modalita_admin:
  if is_admin_autenticato:
    is_admin = True
    st.sidebar.success("Accesso Admin Attivo ✅")
    if st.sidebar.button("🔒 Logout Admin", use_container_width=True):
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

# --- SELETTORE TORNEO IN EVIDENZA ---
st.markdown(
    """
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 18px 22px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <div style="color: #2563EB; font-size: 12px; letter-spacing: 2px; font-weight: 800;">CIRCUITO UFFICIALE</div>
        <div style="font-size: 28px; font-weight: 800; color: #0F172A; margin: 4px 0;">🏆 Torneo Coppie Fisse Live</div>
        <div style="font-size: 14px; color: #64748B; font-weight: 600;">Gestione professionale, risultati in tempo reale</div>
    </div>
    """,
    unsafe_allow_html=True,
)

tornei_disponibili = [t for t in db["tornei"].keys() if t not in ["Torneo Principale (PRO)", "Torneo Secondario (Amatoriale)"]]
if not tornei_disponibili:
  st.info("Nessun torneo attivo al momento. Utilizza il pannello laterale admin per crearne uno nuovo.")
torneo_selezionato = st.selectbox(
    "🎯 SELEZIONA TORNEO",
    options=tornei_disponibili if tornei_disponibili else ["Nessun Torneo Disponibile"],
    key="selettore_torneo_principale"
)
if not tornei_disponibili:
  if is_admin:
    with st.sidebar.expander("➕ Crea Nuovo Torneo con Parametri", expanded=True):
      nuovo_nome_torneo = st.text_input("Nome del Torneo / Categoria")
      col_nc1, col_nc2 = st.columns(2)
      with col_nc1:
        nc_tavoli = st.number_input("N. Biliardini", min_value=1, max_value=10, value=6)
        nc_gironi = st.number_input("N. Gironi", min_value=1, max_value=8, value=4)
      with col_nc2:
        nc_max = st.number_input("Max Coppie (Titolari)", min_value=2, max_value=128, value=32)
      if st.button("Crea Torneo Avanzato", use_container_width=True):
        if nuovo_nome_torneo.strip() and nuovo_nome_torneo.strip().upper() not in db["tornei"]:
          db["tornei"][nuovo_nome_torneo.strip().upper()] = {
              "stato": "iscrizioni_aperte", "coppie": [], "coda": [], "max_coppie": int(nc_max),
              "num_tavoli": int(nc_tavoli), "num_gironi": int(nc_gironi), "qualificati_fascia_a": 4,
              "gironi": {}, "calendario_gironi": {}, "punti_gironi": {}, "fasi_finali_configurate": False,
              "tabellone_a": [], "tabellone_b": [], "terzo_quarto_a": [], "terzo_quarto_b": []
          }
          salva_dati(db)
          st.success("Torneo creato!")
          st.rerun()
  st.stop()

t_data = db["tornei"][torneo_selezionato]
if "coda" not in t_data: t_data["coda"] = []
if "max_coppie" not in t_data: t_data["max_coppie"] = 32
if "qualificati_fascia_a" not in t_data: t_data["qualificati_fascia_a"] = 4
salva_dati(db)

if is_admin:
  with st.sidebar.expander("➕ Crea Nuovo Torneo"):
    nuovo_nome_torneo = st.text_input("Nome del Torneo")
    col_nc1, col_nc2 = st.columns(2)
    with col_nc1:
      nc_tavoli = st.number_input("N. Biliardini", min_value=1, max_value=10, value=6)
      nc_gironi = st.number_input("N. Gironi", min_value=1, max_value=8, value=4)
    with col_nc2:
      nc_max = st.number_input("Max Coppie", min_value=2, max_value=128, value=32)
    if st.button("Crea Torneo", use_container_width=True):
      if nuovo_nome_torneo.strip() and nuovo_nome_torneo.strip().upper() not in db["tornei"]:
        db["tornei"][nuovo_nome_torneo.strip().upper()] = {
            "stato": "iscrizioni_aperte", "coppie": [], "coda": [], "max_coppie": int(nc_max),
            "num_tavoli": int(nc_tavoli), "num_gironi": int(nc_gironi), "qualificati_fascia_a": 4,
            "gironi": {}, "calendario_gironi": {}, "punti_gironi": {}, "fasi_finali_configurate": False,
            "tabellone_a": [], "tabellone_b": [], "terzo_quarto_a": [], "terzo_quarto_b": []
        }
        salva_dati(db)
        st.success("Torneo creato!")
        st.rerun()
  st.sidebar.markdown("---")
  st.sidebar.subheader("🗑️ Elimina Torneo")
  tornei_eliminabili = list(db["tornei"].keys())
  if tornei_eliminabili:
    torneo_da_eliminare = st.sidebar.selectbox("Seleziona torneo", options=tornei_eliminabili, key="sel_del_torneo")
    conferma_canc_torneo = st.sidebar.checkbox("Conferma eliminazione", key="chk_del_torneo")
    if st.sidebar.button("Elimina Torneo", use_container_width=True):
      if conferma_canc_torneo:
        del db["tornei"][torneo_da_eliminare]
        salva_dati(db)
        st.rerun()

st.sidebar.markdown("⚙️ Pannello di Controllo")
if t_data["stato"]!= "iscrizioni_aperte" and t_data["stato"]!= "setup":
  pdf_data = genera_pdf_coppie(torneo_selezionato)
  st.sidebar.download_button(label="📥 Scarica Schema in PDF", data=pdf_data, file_name=f"schema_{torneo_selezionato.lower().replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
  st.sidebar.markdown("---")
if is_admin and t_data["stato"] == "fasi_finali":
  if st.sidebar.button("🔙 Torna ai Gironi", use_container_width=True):
    t_data["stato"] = "gironi"
    salva_dati(db)
    st.rerun()
  st.sidebar.markdown("---")
st.sidebar.subheader("⚠️ Zona Pericolo")
if is_admin:
  conferma_reset = st.sidebar.checkbox("Conferma reset torneo", key="checkbox_reset_gara")
  if st.sidebar.button("🔄 Ricomincia da zero", use_container_width=True):
    if conferma_reset:
      db["tornei"][torneo_selezionato] = {
          "stato": "iscrizioni_aperte", "coppie": [], "coda": [], "max_coppie": t_data.get("max_coppie", 32),
          "num_tavoli": t_data.get("num_tavoli", 6), "num_gironi": t_data.get("num_gironi", 4),
          "qualificati_fascia_a": t_data.get("qualificati_fascia_a", 4), "gironi": {}, "calendario_gironi": {},
          "punti_gironi": {}, "fasi_finali_configurate": False, "tabellone_a": [], "tabellone_b": [],
          "terzo_quarto_a": [], "terzo_quarto_b": []
      }
      salva_dati(db)
      st.rerun()
else:
  st.sidebar.info("🔐 Accedi come admin per resettare.")
st.sidebar.markdown("---")
with st.expander("ℹ️ Come funziona"):
  st.markdown("L'app consente l'iscrizione autonoma o l'incolla rapido da WhatsApp. Superato il limite, i partecipanti vanno in **Lista d'Attesa**.")

# --- ISCRIZIONI APERTE ---
if t_data["stato"] == "iscrizioni_aperte":
  st.markdown(f"### 📝 Iscrizioni - {torneo_selezionato}")
  st.info(f"Limite titolari: **{t_data['max_coppie']}**.")
  with st.form(f"form_iscrizione_{torneo_selezionato}"):
    c1_input = st.text_input("Nome Giocatore 1")
    c2_input = st.text_input("Nome Giocatore 2")
    st.markdown("---")
    whatsapp_paste = st.text_area("📋 Incolla lista WhatsApp (es. 1. Mario/Luigi)")
    submit_isc = st.form_submit_button("Registra / Importa Coppie 🚀", use_container_width=True)
    if submit_isc:
      nuove_inserite = []
      if c1_input.strip() and c2_input.strip():
        nuova_c = f"{c1_input.strip().upper()} / {c2_input.strip().upper()}"
        nuove_inserite.append(nuova_c)
      if whatsapp_paste.strip():
        linee = whatsapp_paste.split("\n")
        for linea in linee:
          linea_pulita = re.sub(r'^\s*(\d+[\.\)]\s*|-\s*)', '', linea).strip()
          if not linea_pulita: continue
          separatori = ["/", "-", " E ", " CON "]
          coppia_formattata = None
          for sep in separatori:
            if sep.lower() in linea_pulita.lower():
              parti = re.split(sep, linea_pulita, flags=re.IGNORECASE)
              if len(parti) >= 2:
                p1 = parti[0].strip().upper()
                p2 = parti[1].strip().upper()
                if p1 and p2:
                  coppia_formattata = f"{p1} / {p2}"
                  break
          if not coppia_formattata:
            parole = linea_pulita.split()
            if len(parole) >= 2:
              meta = len(parole) // 2
              p1 = " ".join(parole[:meta]).upper()
              p2 = " ".join(parole[meta:]).upper()
              if p1 and p2:
                coppia_formattata = f"{p1} / {p2}"
          if coppia_formattata:
            nuove_inserite.append(coppia_formattata)
      aggiunte_titolari = 0
      aggiunte_coda = 0
      for nc in nuove_inserite:
        nc_upper = nc.upper()
        if nc_upper not in t_data["coppie"] and nc_upper not in t_data["coda"]:
          if len(t_data["coppie"]) < int(t_data["max_coppie"]):
            t_data["coppie"].append(nc_upper)
            aggiunte_titolari += 1
          else:
            t_data["coda"].append(nc_upper)
            aggiunte_coda += 1
      if aggiunte_titolari > 0 or aggiunte_coda > 0:
        salva_dati(db)
        st.success(f"Aggiunte: {aggiunte_titolari} Titolari e {aggiunte_coda} in Coda.")
        st.rerun()
      else:
        st.warning("Nessuna nuova coppia valida.")
  st.markdown("---")
  col_tit_vista, col_cod_vista = st.columns(2)
  with col_tit_vista:
    st.markdown(f"### 📋 Titolari ({len(t_data['coppie'])}/{t_data['max_coppie']})")
    if not t_data["coppie"]:
      st.info("Nessun titolare iscritto.")
    else:
      for idx, c in enumerate(t_data["coppie"], 1):
        col_ic1, col_ic2 = st.columns([0.80, 0.20])
        with col_ic1:
          st.markdown(f"<div style='padding: 10px 12px; background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB; border-radius: 10px; margin-bottom: 6px; font-weight: 700; color: #0F172A;'>{idx}. {c}</div>", unsafe_allow_html=True)
        with col_ic2:
          if st.button("🗑️", key=f"del_isc_{torneo_selezionato}_{idx}", use_container_width=True):
            t_data["coppie"].remove(c)
            if t_data["coda"]:
              promossa = t_data["coda"].pop(0)
              t_data["coppie"].append(promossa)
            salva_dati(db)
            st.rerun()
  with col_cod_vista:
    st.markdown(f"### ⏳ Lista d'Attesa ({len(t_data['coda'])})")
    if not t_data["coda"]:
      st.info("Nessuna coppia in coda.")
    else:
      for idx_c, c_coda in enumerate(t_data["coda"], 1):
        col_cc1, col_cc2 = st.columns([0.80, 0.20])
        with col_cc1:
          st.markdown(f"<div style='padding: 10px 12px; background: #FFF7ED; border: 1px solid #FDBA74; border-radius: 10px; margin-bottom: 6px; font-weight: 700; color: #7C2D12;'>{idx_c}. {c_coda}</div>", unsafe_allow_html=True)
        with col_cc2:
          if st.button("🗑️", key=f"del_coda_{torneo_selezionato}_{idx_c}", use_container_width=True):
            t_data["coda"].remove(c_coda)
            salva_dati(db)
            st.rerun()
  if is_admin:
    st.markdown("---")
    st.markdown("### ⚙️ Configurazione e Avvio")
    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
      t_data["num_tavoli"] = st.number_input("N. Biliardini", min_value=1, max_value=10, value=int(t_data.get("num_tavoli", 6)), key=f"tav_{torneo_selezionato}")
    with col_cfg2:
      t_data["num_gironi"] = st.number_input("N. Gironi", min_value=1, max_value=8, value=int(t_data.get("num_gironi", 4)), key=f"gir_{torneo_selezionato}")
    with col_cfg3:
      t_data["max_coppie"] = st.number_input("Max Titolari", min_value=2, max_value=128, value=int(t_data.get("max_coppie", 32)), key=f"maxc_{torneo_selezionato}")
    t_data["qualificati_fascia_a"] = st.number_input("Quante coppie in FASCIA A per girone?", min_value=1, max_value=16, value=int(t_data.get("qualificati_fascia_a", 4)))
    if st.button("🚀 Avvia Torneo (Crea Gironi)", use_container_width=True):
      num_g = int(t_data["num_gironi"])
      coppie = [str(c).upper() for c in t_data["coppie"]]
      if len(coppie) < (num_g * 2):
        st.error(f"Servono almeno {num_g * 2} coppie per {num_g} gironi.")
      else:
        random.shuffle(coppie)
        nomi_gironi = [chr(65 + i) for i in range(num_g)]
        gironi_dict = {f"Girone {g}": [] for g in nomi_gironi}
        for idx, c in enumerate(coppie):
          g_scelto = f"Girone {nomi_gironi[idx % num_g]}"
          gironi_dict[g_scelto].append(c)
        t_data["gironi"] = gironi_dict
        t_data["punti_gironi"] = {g: {c: {"punti": 0, "gf": 0, "gs": 0, "dr": 0, "scontri_diretti_pt": 0} for c in lst} for g, lst in gironi_dict.items()}
        calendario_totale = {}
        for g_nome, lista_c in gironi_dict.items():
          squadre = lista_c.copy()
          if len(squadre) % 2!= 0: squadre.append("RIPOSO")
          n = len(squadre)
          turni_girone = []
          for t in range(n - 1):
            partite_turno = []
            for i in range(n // 2):
              s1 = squadre[i]
              s2 = squadre[n - 1 - i]
              if s1!= "RIPOSO" and s2!= "RIPOSO":
                match_id = f"{g_nome}_t{t+1}_m{i}"
                partite_turno.append({"id": match_id, "girone": g_nome, "c1": s1, "c2": s2, "giocata": False, "in_corso": False, "tavolo": None, "gol1": 0, "gol2": 0})
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

# --- SELETTORE COPPIA ---
tutte_le_coppie = []
for g_lst in t_data["gironi"].values():
  tutte_le_coppie.extend(g_lst)
if not tutte_le_coppie and t_data.get("coppie"):
  tutte_le_coppie = t_data["coppie"]
opzioni_selettore = ["-- Seleziona la tua coppia --"] + sorted([str(c).upper() for c in tutte_le_coppie])
coppia_url = st.query_params.get("coppia", "-- Seleziona la tua coppia --").upper()
if coppia_url not in opzioni_selettore:
  coppia_url = "-- Seleziona la tua coppia --"
coppia_selezionata = st.selectbox("📱 LA TUA COPPIA:", options=opzioni_selettore, index=opzioni_selettore.index(coppia_url), key="widget_selezione_coppia")
if coppia_selezionata!= coppia_url:
  st.query_params["coppia"] = coppia_selezionata
  st.rerun()
if is_admin:
  st.success("🛡️ **Modalità Amministratore attiva**")
elif coppia_selezionata == "-- Seleziona la tua coppia --":
  st.warning("⚠️ Seleziona la tua coppia per vedere le tue partite e inserire i risultati.")
  st.stop()
else:
  st.success(f"✅ Accesso come: **{coppia_selezionata}**")

if coppia_selezionata!= "-- Seleziona la tua coppia --":
  with st.expander(f"👁️ La tua coppia: {coppia_selezionata}", expanded=True):
    girone_mio, pos_mia, info_mie = None, None, None
    for g_nome, lista_c in t_data["gironi"].items():
      if coppia_selezionata in lista_c:
        girone_mio = g_nome
        ricalcola_classifiche_gironi(torneo_selezionato)
        if g_nome in t_data["punti_gironi"]:
          dati_g = t_data["punti_gironi"][g_nome]
          sorted_c = sorted(dati_g.items(), key=lambda x: (x[1]["punti"], x[1]["scontri_diretti_pt"], x[1]["dr"], x[1]["gf"]), reverse=True)
          for idx, (c_nome, stats) in enumerate(sorted_c):
            if c_nome == coppia_selezionata:
              pos_mia = idx + 1
              info_mie = stats
        break
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 2px solid #0F172A; border-radius: 16px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
            <div style="font-size: 11px; font-weight: 800; letter-spacing: 1px; color: #2563EB; margin-bottom: 4px;">LA TUA COPPIA</div>
            <div style="font-size: 22px; font-weight: 800; color: #0F172A; margin-bottom: 14px;">🤝 {coppia_selezionata}</div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px; flex: 1; text-align: center;"><div style="font-size: 10px; font-weight: 800; color: #64748B;">POSIZIONE</div><div style="font-size: 16px; font-weight: 800; color: #0F172A;">{str(pos_mia) + '°' if pos_mia else 'N.D.'}</div></div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px; flex: 1; text-align: center;"><div style="font-size: 10px; font-weight: 800; color: #64748B;">GIRONE</div><div style="font-size: 16px; font-weight: 800; color: #2563EB;">{girone_mio if girone_mio else 'N.D.'}</div></div>
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 10px; flex: 1; text-align: center;"><div style="font-size: 10px; font-weight: 800; color: #92400E;">PUNTI / DR</div><div style="font-size: 16px; font-weight: 800; color: #0F172A;">{info_mie['punti'] if info_mie else 0} <span style="font-weight:600; color:#64748B;">({info_mie['dr'] if info_mie else 0})</span></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True,
    )

# FASE A GIRONI
if t_data["stato"] == "gironi":
  ricalcola_classifiche_gironi(torneo_selezionato)
  num_tavoli = t_data.get("num_tavoli", 6)
  max_turni = max([len(turni) for turni in t_data["calendario_gironi"].values()]) if t_data["calendario_gironi"] else 0
  partite_per_girone_dict = {}
  for t_num in range(1, max_turni + 1):
    for g_nome, turni_girone in t_data["calendario_gironi"].items():
      for t_obj in turni_girone:
        if t_obj["turno"] == t_num:
          if g_nome not in partite_per_girone_dict:
            partite_per_girone_dict[g_nome] = []
          partite_per_girone_dict[g_nome].extend(t_obj["partite"])
  partite_miste_totali = []
  max_len_partite = max([len(v) for v in partite_per_girone_dict.values()]) if partite_per_girone_dict else 0
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
  tavoli_occupati_ids = [p.get("tavolo") for p in partite_in_corso if p.get("tavolo") is not None]
  tavoli_liberi_disponibili = [t for t in range(1, num_tavoli + 1) if t not in tavoli_occupati_ids]
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
  partite_in_corso = sorted(partite_in_corso, key=lambda x: x.get("tavolo") if x.get("tavolo") is not None else 999)

  st.subheader(f"⚡ Biliardini - {torneo_selezionato}")
  col_ic, col_coda = st.columns(2)
  with col_ic:
    st.markdown("#### 🔥 In Corso")
    if not partite_in_corso:
      st.info("Nessuna partita in corso.")
    else:
      for m in partite_in_corso:
        match_id = m["id"]
        fa_al_caso_nostro = is_admin or coppia_selezionata == m["c1"] or coppia_selezionata == m["c2"]
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 2.5px solid #0F172A; border-radius: 16px; padding: 16px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                <div style="font-size: 11px; font-weight: 800; color: #2563EB; letter-spacing: 1px; margin-bottom: 6px;">🏟️ BILIARDINO {m.get('tavolo','')} • {m['girone']}</div>
                <div style="font-size: 16px; font-weight: 800; color: #0F172A;">{m['c1']}</div>
                <div style="margin: 6px 0;"><span style="background: #0F172A; color: #FFF; font-weight: 800; padding: 2px 14px; border-radius: 20px; font-size: 12px;">VS</span></div>
                <div style="font-size: 16px; font-weight: 800; color: #0F172A;">{m['c2']}</div>
            </div>
            """, unsafe_allow_html=True,
        )
        if st.button("🔄 Posticipa di 2", key=f"post_{torneo_selezionato}_{match_id}", use_container_width=True):
          if posticipa_partita_coda(torneo_selezionato, match_id):
            st.success("Posticipata!")
            st.rerun()
        if fa_al_caso_nostro:
          with st.expander(f"📝 Risultato Tavolo {m.get('tavolo', '')}"):
            gol_p1 = st.selectbox(f"Gol {m['c1']}", options=[0, 1, 2, 3, 4, 5, 6, 7], index=int(m.get("gol1", 0)), key=f"g1_{torneo_selezionato}_{match_id}")
            gol_p2 = st.selectbox(f"Gol {m['c2']}", options=[0, 1, 2, 3, 4, 5, 6, 7], index=int(m.get("gol2", 0)), key=f"g2_{torneo_selezionato}_{match_id}")
            if st.button("✅ Conferma Risultato", key=f"save_{torneo_selezionato}_{match_id}", use_container_width=True):
              m["gol1"] = int(gol_p1)
              m["gol2"] = int(gol_p2)
              m["giocata"] = True
              m["in_corso"] = False
              m["tavolo"] = None
              ricalcola_classifiche_gironi(torneo_selezionato)
              salva_dati(db)
              st.rerun()
  with col_coda:
    partite_in_coda_correnti = partite_da_giocare[:num_tavoli]
    st.markdown("#### ⏳ Prossime")
    if not partite_in_coda_correnti:
      st.info("Coda vuota.")
    else:
      for idx, m in enumerate(partite_in_coda_correnti):
        st.markdown(f"""<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #F59E0B; padding: 12px; border-radius: 10px; margin-bottom: 8px; text-align: center;"><b style="font-size: 12px; color: #D97706;">{idx+1}. {m['girone']}</b><br><b style="color: #0F172A;">{m['c1']} vs {m['c2']}</b></div>""", unsafe_allow_html=True)

  st.markdown("---")
  st.subheader("📊 Classifiche")
  nomi_gironi_chiavi = list(t_data["gironi"].keys())
  for i in range(0, len(nomi_gironi_chiavi), 2):
    col_gironi = st.columns(2)
    for j in range(2):
      if i + j < len(nomi_gironi_chiavi):
        g_nome = nomi_gironi_chiavi[i + j]
        with col_gironi[j]:
          st.markdown(f"<h3 style='text-align: center;'>📁 {g_nome}</h3>", unsafe_allow_html=True)
          renderizza_classifica_stile_card(torneo_selezionato, g_nome)

  if is_admin:
    st.markdown("---")
    q_a = int(t_data.get("qualificati_fascia_a", 4))
    if st.button(f"🏆 Genera Fasi Finali (Prime {q_a} in A)", use_container_width=True):
      classificate_a, classificate_b_raw = {}, {}
      for g_nome in t_data["gironi"]:
        dati_girone = t_data["punti_gironi"][g_nome]
        sorted_c = sorted(dati_girone.items(), key=lambda x: (x[1]["punti"], x[1]["scontri_diretti_pt"], x[1]["dr"], x[1]["gf"]), reverse=True)
        squadre_girone = [str(c[0]).upper() for c in sorted_c]
        classificate_a[g_nome] = squadre_girone[:q_a]
        classificate_b_raw[g_nome] = squadre_girone
      tutte_sq_a = []
      for g_n in classificate_a:
        for sq in classificate_a[g_n]:
          tutte_sq_a.append((sq, g_n))
      random.shuffle(tutte_sq_a)
      abbinamenti_a = []
      for i in range(0, len(tutte_sq_a), 2):
        if i + 1 < len(tutte_sq_a):
          abbinamenti_a.append((tutte_sq_a[i], tutte_sq_a[i + 1]))
        else:
          abbinamenti_a.append((tutte_sq_a[i], ("RIPOSO", "")))
      abbinamenti_b = crea_abbinamenti_fascia_b(classificate_b_raw, q_a)
      turno_a_iniziale = [{"id": f"fa_t1_m{i}", "s1": str(s1[0]).upper(), "g1": s1[1], "p1": "", "s2": str(s2[0]).upper(), "g2": s2[1], "p2": "", "giocata": False, "vincente": None} for i, (s1, s2) in enumerate(abbinamenti_a)]
      turno_b_iniziale = [{"id": f"fb_t1_m{i}", "s1": str(s1[0]).upper(), "g1": s1[1], "p1": s1[2], "s2": str(s2[0]).upper(), "g2": s2[1], "p2": s2[2], "giocata": False, "vincente": None} for i, (s1, s2) in enumerate(abbinamenti_b)]
      t_data["tabellone_a"] = [{"turno": 1, "partite": turno_a_iniziale}]
      t_data["tabellone_b"] = [{"turno": 1, "partite": turno_b_iniziale}]
      t_data["terzo_quarto_a"] = []
      t_data["terzo_quarto_b"] = []
      t_data["stato"] = "fasi_finali"
      t_data["fasi_finali_configurate"] = True
      salva_dati(db)
      st.rerun()

# FASI FINALI
elif t_data["stato"] == "fasi_finali":
  st.subheader(f"🏆 Fasi Finali - {torneo_selezionato}")
  tab_a_view, tab_b_view = st.tabs(["⭐ Fascia A", "🔻 Fascia B"])

  def gestisci_tabellone(chiave_tabellone, chiave_34, titolo_tab):
    st.markdown(f"### 📋 {titolo_tab}")
    turni_tab = t_data[chiave_tabellone]
    mappa_girone_pos = {}
    for g_nome, lista_sq in t_data["gironi"].items():
      dati_girone = t_data["punti_gironi"][g_nome]
      sorted_c = sorted(dati_girone.items(), key=lambda x: (x[1]["punti"], x[1]["scontri_diretti_pt"], x[1]["dr"], x[1]["gf"]), reverse=True)
      for idx, (sq, info) in enumerate(sorted_c):
        mappa_girone_pos[str(sq).upper()] = (g_nome, idx + 1)
    campione, secondo_posto, terzo_posto = None, None, None
    tot_partite_turno_1 = len(turni_tab[0]["partite"])
    num_totale_squadre_tab = tot_partite_turno_1 * 2
    import math
    num_turni_totali = math.ceil(math.log2(num_totale_squadre_tab)) if num_totale_squadre_tab > 1 else 1
    while len(turni_tab) < num_turni_totali:
      prossimo_t_num = len(turni_tab) + 1
      num_match_prossimo = max(1, len(turni_tab[-1]["partite"]) // 2)
      partite_nuovo_turno = [{"id": f"{chiave_tabellone}_t{prossimo_t_num}_m{m_idx}", "s1": "In attesa...", "g1": "", "p1": "", "s2": "In attesa...", "g2": "", "p2": "", "giocata": False, "vincente": None} for m_idx in range(num_match_prossimo)]
      turni_tab.append({"turno": prossimo_t_num, "partite": partite_nuovo_turno})
    salva_dati(db)

    for t_idx, turno_obj in enumerate(turni_tab):
      t_num = turno_obj["turno"]
      partite_turno = turno_obj["partite"]
      nome_etichetta = ottieni_nome_turno_dinamico(len(partite_turno))
      st.markdown(f"""<div style="background: #0F172A; padding: 10px; border-radius: 10px; margin: 16px 0; text-align: center; color: #FFFFFF; font-weight: 800; letter-spacing: 1px;">{nome_etichetta}</div>""", unsafe_allow_html=True)
      if t_idx + 1 < len(turni_tab):
        turno_successivo = turni_tab[t_idx + 1]
        for m_i, match_corrente in enumerate(partite_turno):
          if match_corrente["giocata"] and match_corrente.get("vincente"):
            vincitore_corrente = str(match_corrente["vincente"]).upper()
            g_v, p_v = mappa_girone_pos.get(vincitore_corrente, ("", ""))
            target_match_idx = m_i // 2
            slot_squadra = "s1" if (m_i % 2 == 0) else "s2"
            slot_g = "g1" if (m_i % 2 == 0) else "g2"
            if target_match_idx < len(turno_successivo["partite"]):
              dest_match = turno_successivo["partite"][target_match_idx]
              if dest_match[slot_squadra] in ["In attesa...", ""]:
                dest_match[slot_squadra] = vincitore_corrente
                dest_match[slot_g] = g_v
                salva_dati(db)
      perdenti_turno = []
      for idx, m in enumerate(partite_turno):
        match_id = m["id"]
        s1_nome, s2_nome = str(m["s1"]).upper(), str(m["s2"]).upper()
        if s1_nome in ["In attesa...", ""] or s2_nome in ["In attesa...", ""]:
          st.markdown(f"""<div style="background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 14px; text-align: center; margin-bottom: 8px; color: #64748B;"><b>{s1_nome} vs {s2_nome}</b><br>In attesa</div>""", unsafe_allow_html=True)
          continue
        if m["giocata"]:
          perdente_match = s2_nome if str(m["vincente"]).upper() == s1_nome else s1_nome
          perdenti_turno.append(perdente_match)
          centro_testo = f"<span style='background: #2563EB; color: #FFF; padding: 3px 12px; border-radius: 20px; font-size: 12px; font-weight: 800;'>VINCE {str(m['vincente']).upper()}</span>"
        else:
          centro_testo = "<span style='background: #F1F5F9; color: #0F172A; padding: 3px 12px; border-radius: 20px; font-size: 12px; font-weight: 800;'>VS</span>"
        st.markdown(f"""<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px; text-align: center; margin-bottom: 8px;"><b style="color: #0F172A;">{s1_nome}</b> vs <b style="color: #0F172A;">{s2_nome}</b><br><div style="margin-top: 6px;">{centro_testo}</div></div>""", unsafe_allow_html=True)
        if is_admin:
          with st.expander(f"⚙️ Vincitore ({s1_nome} vs {s2_nome})"):
            col_wv1, col_wv2 = st.columns(2)
            with col_wv1:
              if st.button(f"🏆 {s1_nome}", key=f"win1_{match_id}"):
                m["giocata"] = True
                m["vincente"] = s1_nome
                salva_dati(db)
                st.rerun()
            with col_wv2:
              if st.button(f"🏆 {s2_nome}", key=f"win2_{match_id}"):
                m["giocata"] = True
                m["vincente"] = s2_nome
                salva_dati(db)
                st.rerun()
      if nome_etichetta == "🏆 FINALE" and len(partite_turno) == 1 and partite_turno[0]["giocata"]:
        campione = str(partite_turno[0]["vincente"]).upper()
        secondo_posto = str(partite_turno[0]["s2"]).upper() if campione == str(partite_turno[0]["s1"]).upper() else str(partite_turno[0]["s1"]).upper()
      if nome_etichetta == "⚔️ SEMIFINALI" and len(perdenti_turno) == 2 and not t_data[chiave_34]:
        if is_admin:
          p1, p2 = perdenti_turno[0], perdenti_turno[1]
          g_p1, pos_p1 = mappa_girone_pos.get(p1, ("", ""))
          g_p2, pos_p2 = mappa_girone_pos.get(p2, ("", ""))
          t_data[chiave_34] = [{"id": f"{chiave_tabellone}_tq", "s1": p1, "g1": g_p1, "p1": pos_p1, "s2": p2, "g2": g_p2, "p2": pos_p2, "giocata": False, "vincente": None}]
          salva_dati(db)
    if t_data[chiave_34]:
      st.markdown("### 🥉 Finale 3° / 4° Posto")
      tq_match = t_data[chiave_34][0]
      if tq_match["giocata"]:
        terzo_posto = str(tq_match["vincente"]).upper()
      st.markdown(f"<div style='background: #FFFFFF; border: 2px solid #F59E0B; border-radius: 12px; padding: 14px; text-align: center;'><b>{str(tq_match['s1']).upper()} vs {str(tq_match['s2']).upper()}</b><br>Vincitore 3°: {str(tq_match.get('vincente', 'Da assegnare')).upper()}</div>", unsafe_allow_html=True)
      if is_admin:
        col_tq1, col_tq2 = st.columns(2)
        with col_tq1:
          if st.button(f"🥉 Vince {str(tq_match['s1']).upper()}", key=f"tq1_{chiave_tabellone}"):
            tq_match["giocata"] = True
            tq_match["vincente"] = str(tq_match['s1']).upper()
            salva_dati(db)
            st.rerun()
        with col_tq2:
          if st.button(f"🥉 Vince {str(tq_match['s2']).upper()}", key=f"tq2_{chiave_tabellone}"):
            tq_match["giocata"] = True
            tq_match["vincente"] = str(tq_match['s2']).upper()
            salva_dati(db)
            st.rerun()
    if campione:
      st.markdown(f"""<div style="background: #FFFFFF; border: 3px solid #F59E0B; border-radius: 20px; padding: 24px; margin-top: 16px; text-align: center; box-shadow: 0 8px 24px rgba(245,158,11,0.2);"><h2 style="color: #0F172A!important;">🏆 PODIO - {titolo_tab}</h2><p style="font-size: 20px; font-weight: 800; color: #D97706;">🥇 1° {campione}</p><p style="font-size: 16px; font-weight: 700; color: #334155;">🥈 2° {secondo_posto}</p><p style="font-size: 16px; font-weight: 700; color: #2563EB;">🥉 3° {terzo_posto if terzo_posto else 'N.D.'}</p></div>""", unsafe_allow_html=True)

  with tab_a_view:
    gestisci_tabellone("tabellone_a", "terzo_quarto_a", "Fascia A")
  with tab_b_view:
    gestisci_tabellone("tabellone_b", "terzo_quarto_b", "Fascia B")
