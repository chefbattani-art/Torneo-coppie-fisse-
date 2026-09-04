import io
import json
import math
import os
import random
import re
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import streamlit as st
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURAZIONE PAGINA E AUTO REFRESH ---
st_autorefresh(interval=5000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(
    page_title="Torneo Coppie Fisse Live",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- STILE GLOBALE CYBER GAMER CHIARO E LUMINOSO ---
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #07111e 0%, #112233 45%, #0e7490 100%);
            color: #f1f5f9;
            font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #112233, #07111e);
            border-right: 2px solid #38bdf8;
            color: #ffffff;
        }
        section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stMarkdown {
            color: #ffe66d !important;
        }
        
        input, textarea, div[data-baseweb="input"] > div {
            background-color: #112233 !important;
            color: #38bdf8 !important;
            -webkit-text-fill-color: #38bdf8 !important;
            border-radius: 12px !important;
            border: 2px solid #38bdf8 !important;
            font-weight: 700 !important;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
        }
        textarea {
            padding: 10px !important;
            font-size: 16px !important;
        }
        input {
            font-size: 16px !important;
        }
        
        div[data-baseweb="input"], .stTextInput label, .stTextArea label, .stSelectbox label {
            color: #ffe66d !important;
            font-weight: 800 !important;
            text-shadow: 0 0 6px rgba(255, 230, 109, 0.4);
        }

        .cyber-card {
            background: rgba(17, 34, 51, 0.9);
            border: 2px solid #38bdf8;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 14px;
            box-shadow: 0 0 18px rgba(56, 189, 248, 0.25);
            color: #f1f5f9;
        }
        .cyber-card-gold {
            background: linear-gradient(135deg, rgba(17, 34, 51, 0.95) 0%, rgba(2, 132, 199, 0.4) 100%);
            border: 2.5px solid #ffe66d;
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 0 25px rgba(255, 230, 109, 0.4);
            text-align: center;
            color: #ffe66d;
        }
        .match-live-card {
            background: rgba(234, 179, 8, 0.15);
            border: 2.5px solid #eab308;
            border-radius: 16px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 0 20px rgba(234, 179, 8, 0.5);
            color: #ffffff;
            animation: pulse-yellow 2s infinite;
        }
        @keyframes pulse-yellow {
            0% { box-shadow: 0 0 10px rgba(234, 179, 8, 0.4); }
            50% { box-shadow: 0 0 25px rgba(234, 179, 8, 0.8); }
            100% { box-shadow: 0 0 10px rgba(234, 179, 8, 0.4); }
        }
        .match-next-neon {
            background: rgba(34, 197, 94, 0.15);
            border: 2.5px solid #22c55e;
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.6);
            color: #ffffff;
            animation: pulse-neon 2s infinite;
        }
        @keyframes pulse-neon {
            0% { box-shadow: 0 0 10px rgba(34, 197, 94, 0.4); }
            50% { box-shadow: 0 0 25px rgba(34, 197, 94, 0.8); }
            100% { box-shadow: 0 0 10px rgba(34, 197, 94, 0.4); }
        }
        h1, h2, h3, h4 {
            color: #ffe66d !important;
            letter-spacing: 1px;
            font-weight: 800;
            text-shadow: 0 0 10px rgba(255, 230, 109, 0.4);
        }
        h1 {
            text-shadow: 0 0 15px rgba(56, 189, 248, 0.7);
            color: #38bdf8 !important;
        }
        div.stButton > button {
            border-radius: 12px;
            font-weight: 700;
            border: 2px solid #0ea5e9;
            background: linear-gradient(180deg, #0ea5e9, #0284c7);
            color: #ffffff !important;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(14, 116, 144, 0.4);
            font-size: 16px !important;
        }
        div.stButton > button:hover {
            border-color: #22c55e;
            background: linear-gradient(180deg, #22c55e, #0e7490);
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.6);
            color: #07111e !important;
        }
        div[data-baseweb="select"] > div {
            background: rgba(17, 34, 51, 0.95) !important;
            border: 2.5px solid #38bdf8 !important;
            border-radius: 16px !important;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.25) !important;
            color: #38bdf8 !important;
            min-height: 60px !important;
            display: flex !important;
            align-items: center !important;
        }
        div[data-baseweb="select"] span {
            color: #ffe66d !important;
            font-size: 20px !important;
            font-weight: 800 !important;
        }
        div[data-baseweb="select"] svg {
            fill: #ffe66d !important;
            width: 28px !important;
            height: 28px !important;
        }

        .match-row-card {
            background: rgba(17,34,51,0.85);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            min-height: 50px;
        }
        .status-badge {
            font-size: 11px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 6px;
            white-space: nowrap;
            text-align: center;
            display: inline-block;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_FILE = "coppie_data_multi.json"

def carica_dati():
    dati_default = {
        "tornei": {},
        "admin_pin": "0000"
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                dati_salvati = json.load(f)
                if "tornei" not in dati_salvati:
                    return dati_default
                
                tornei_da_rimuovere = ["TORNEO GIOVEDÌ 3 MASSA LOMBARDA", "TORNEO GIOVEDÌ 3 MASSALOMBARDA", "Torneo Principale (PRO)", "Torneo Secondario (Amatoriale)"]
                for t_rem in tornei_da_rimuovere:
                    if t_rem in dati_salvati["tornei"]:
                        del dati_salvati["tornei"][t_rem]

                return dati_salvati
        except Exception:
            return dati_default
    return dati_default

def salva_dati(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Errore durante il salvataggio dei dati: {e}")

if "db" not in st.session_state:
    st.session_state.db = carica_dati()

db = st.session_state.db

def gestisci_spostamento_coppia(torneo_selezionato, coppia, girone_origine, girone_destinazione):
    t_data = db["tornei"][torneo_selezionato]
    if coppia in t_data["gironi"][girone_origine]:
        t_data["gironi"][girone_origine].remove(coppia)
        t_data["gironi"][girone_destinazione].append(coppia)
        
        for g_n in [girone_origine, girone_destinazione]:
            if g_n in t_data["calendario_gironi"]:
                for t_obj in t_data["calendario_gironi"][g_n]:
                    t_obj["partite"] = [
                        m for m in t_obj["partite"] 
                        if m["c1"] != coppia and m["c2"] != coppia
                    ]
        
        ricalcola_classifiche_gironi(torneo_selezionato)
        salva_dati(db)
        st.success(f"Coppia '{coppia}' spostata in {girone_destinazione}.")

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
                        if c1 in stats:
                            stats[c1]["punti"] += pt_s1
                            stats[c1]["gf"] += g1
                            stats[c1]["gs"] += g2
                        if c2 in stats:
                            stats[c2]["punti"] += pt_s2
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
    
    sorted_c = sorted(
        dati_girone.items(),
        key=lambda x: (x[1]["punti"], x[1]["scontri_diretti_pt"], x[1]["dr"], x[1]["gf"]),
        reverse=True
    )
    for idx, (coppia, info) in enumerate(sorted_c):
        gioc, tot = calcola_partite_giocate_coppia(torneo_selezionato, g_nome, coppia)
        is_fascia_a = idx < q_fascia_a
        border_color = "#22c55e" if is_fascia_a else "#38bdf8"
        bg_gradient = "linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(17, 34, 51, 0.95) 100%)" if is_fascia_a else "linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(17, 34, 51, 0.95) 100%)"
        shadow_color = "rgba(34, 197, 94, 0.2)" if is_fascia_a else "rgba(56, 189, 248, 0.2)"
        dot_color = "#22c55e" if is_fascia_a else "#38bdf8"

        st.markdown(
            f"""
            <div style="background: {bg_gradient}; border: 1.5px solid {border_color}; border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; box-shadow: 0 4px 12px {shadow_color}; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 10px; height: 10px; background-color: {dot_color}; border-radius: 50%; box-shadow: 0 0 8px {dot_color};"></div>
                    <span style="font-size: 16px; font-weight: 800; color: {dot_color}; min-width: 30px;">{idx+1}°</span>
                    <span style="font-size: 15px; font-weight: bold; color: #ffffff;">⚽ {coppia}</span>
                </div>
                <div style="display: flex; gap: 14px; text-align: right; font-size: 13px;">
                    <div>
                        <span style="font-size: 9px; color: #94a3b8; display: block;">PT</span>
                        <span style="font-weight: 800; color: #ffe66d; font-size: 15px;">{info['punti']}</span>
                    </div>
                    <div>
                        <span style="font-size: 9px; color: #94a3b8; display: block;">G</span>
                        <span style="color: #cbd5e1; font-weight: 600;">{gioc}/{tot}</span>
                    </div>
                    <div>
                        <span style="font-size: 9px; color: #94a3b8; display: block;">DR</span>
                        <span style="color: {"#22c55e" if info['dr'] >= 0 else "#38bdf8"}; font-weight: 600;">{info['dr']:+d}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- GENERAZIONE PDF AVANZATA CON REPORTLAB ---
def genera_pdf_coppie(torneo_selezionato):
    t_data = db["tornei"][torneo_selezionato]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15,
        leftMargin=15,
        topMargin=15,
        bottomMargin=15
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), alignment=1, spaceAfter=10)
    subtitle_style = ParagraphStyle('ReportSubtitle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#0EA5E9'), spaceBefore=8, spaceAfter=6)
    cell_style = ParagraphStyle('CellText', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#0F172A'))
    cell_header = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=8, textColor=colors.whitesmoke, fontName="Helvetica-Bold", alignment=1)

    story.append(Paragraph(f"TORNEO LIVE: {torneo_selezionato.upper()}", title_style))
    story.append(Spacer(1, 10))

    for g_nome, turni in t_data.get("calendario_gironi", {}).items():
        story.append(Paragraph(f"<b>{g_nome.upper()}</b>", subtitle_style))
        
        dati_g = t_data.get("punti_gironi", {}).get(g_nome, {})
        sorted_c = sorted(dati_g.items(), key=lambda x: (x[1]["punti"], x[1]["scontri_diretti_pt"], x[1]["dr"], x[1]["gf"]), reverse=True)
        
        table_data = [[
            Paragraph("Pos", cell_header),
            Paragraph("Coppia", cell_header),
            Paragraph("Punti", cell_header),
            Paragraph("GF", cell_header),
            Paragraph("GS", cell_header),
            Paragraph("DR", cell_header)
        ]]
        
        for idx, (coppia, stats) in enumerate(sorted_c, 1):
            table_data.append([
                Paragraph(f"<b>{idx}°</b>", cell_style),
                Paragraph(coppia, cell_style),
                Paragraph(str(stats['punti']), cell_style),
                Paragraph(str(stats['gf']), cell_style),
                Paragraph(str(stats['gs']), cell_style),
                Paragraph(f"{stats['dr']:+d}", cell_style)
            ])
            
        t_classifica = Table(table_data, colWidths=[30, 200, 40, 40, 40, 40])
        t_classifica.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_classifica)
        story.append(Spacer(1, 8))

        partite_rows = [[Paragraph("Turno", cell_header), Paragraph("Incontro", cell_header), Paragraph("Risultato / Stato", cell_header)]]
        for t_obj in turni:
            for m in t_obj["partite"]:
                ris = f"{m['gol1']} - {m['gol2']}" if m.get("giocata", False) else ("IN CORSO" if m.get("in_corso") else "DA GIOCARE")
                partite_rows.append([
                    Paragraph(f"Turno {t_obj['turno']}", cell_style),
                    Paragraph(f"{m['c1']} VS {m['c2']}", cell_style),
                    Paragraph(f"<b>{ris}</b>", cell_style)
                ])

        t_partite = Table(partite_rows, colWidths=[60, 230, 100])
        t_partite.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0ea5e9')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_partite)
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def ottieni_nome_turno_dinamico(num_partite_turno):
    tot_squadre = num_partite_turno * 2
    if num_partite_turno == 1:
        return "🏆 FINALE"
    elif num_partite_turno == 2:
        return "⚔️ SEMIFINALI"
    elif num_partite_turno == 4:
        return "🔥 QUARTI DI FINALE"
    elif num_partite_turno == 8:
        return "⭐ OTTAVI DI FINALE"
    elif num_partite_turno == 16:
        return "🌟 SEDICESIMI DI FINALE"
    else:
        return f"Eliminazione Diretta ({tot_squadre} Coppie)"

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

st.markdown(
    """
    <div style="text-align: left; margin-bottom: 8px;">
        <span style="color: #ffe66d; font-size: 13px; letter-spacing: 2px; font-weight: 800;">TOURNAMENT CIRCUIT SELECTION</span>
        <h1 style="font-size: 28px; margin: 4px 0 12px 0; color: #38bdf8; text-shadow: 0 0 10px rgba(56,189,248,0.6);">
            🏆 Torneo Coppie Fisse Live
        </h1>
    </div>
    """,
    unsafe_allow_html=True,
)

tornei_disponibili = [t for t in db["tornei"].keys() if t not in ["Torneo Principale (PRO)", "Torneo Secondario (Amatoriale)"]]

if not tornei_disponibili:
    st.info("Nessun torneo attivo al momento. Utilizza il pannello laterale admin per crearne uno nuovo.")

torneo_selezionato = st.selectbox(
    "🎯 Seleziona il Torneo a cui vuoi partecipare o consultare:",
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
                        "stato": "iscrizioni_aperte",
                        "coppie": [],
                        "coda": [],
                        "max_coppie": int(nc_max),
                        "num_tavoli": int(nc_tavoli),
                        "num_gironi": int(nc_gironi),
                        "qualificati_fascia_a": 4,
                        "gironi": {},
                        "calendario_gironi": {},
                        "punti_gironi": {},
                        "fasi_finali_configurate": False,
                        "tabellone_a": [],
                        "tabellone_b": [],
                        "terzo_quarto_a": [],
                        "terzo_quarto_b": []
                    }
                    salva_dati(db)
                    st.success("Torneo creato con successo!")
                    st.rerun()
    st.stop()

t_data = db["tornei"][torneo_selezionato]

if "coda" not in t_data:
    t_data["coda"] = []
if "max_coppie" not in t_data:
    t_data["max_coppie"] = 32
if "qualificati_fascia_a" not in t_data:
    t_data["qualificati_fascia_a"] = 4
salva_dati(db)

if is_admin:
    with st.sidebar.expander("➕ Crea Nuovo Torneo con Parametri"):
        nuovo_nome_torneo = st.text_input("Nome del Torneo / Categoria", key="input_new_torneo_sidebar")
        col_nc1, col_nc2 = st.columns(2)
        with col_nc1:
            nc_tavoli = st.number_input("N. Biliardini", min_value=1, max_value=10, value=6, key="tavoli_sidebar")
            nc_gironi = st.number_input("N. Gironi", min_value=1, max_value=8, value=4, key="gironi_sidebar")
        with col_nc2:
            nc_max = st.number_input("Max Coppie (Titolari)", min_value=2, max_value=128, value=32, key="max_sidebar")
            
        if st.button("Crea Torneo Avanzato", key="btn_create_sidebar", use_container_width=True):
            if nuovo_nome_torneo.strip() and nuovo_nome_torneo.strip().upper() not in db["tornei"]:
                db["tornei"][nuovo_nome_torneo.strip().upper()] = {
                    "stato": "iscrizioni_aperte",
                    "coppie": [],
                    "coda": [],
                    "max_coppie": int(nc_max),
                    "num_tavoli": int(nc_tavoli),
                    "num_gironi": int(nc_gironi),
                    "qualificati_fascia_a": 4,
                    "gironi": {},
                    "calendario_gironi": {},
                    "punti_gironi": {},
                    "fasi_finali_configurate": False,
                    "tabellone_a": [],
                    "tabellone_b": [],
                    "terzo_quarto_a": [],
                    "terzo_quarto_b": []
                }
                salva_dati(db)
                st.success("Torneo creato con successo!")
                st.rerun()

    if t_data.get("gironi"):
        with st.sidebar.expander("🔄 Gestione Coppie & Gironi Admin"):
            st.markdown("##### Sposta una Coppia tra i Gironi")
            lista_gironi = list(t_data["gironi"].keys())
            girone_da = st.selectbox("Da Girone", lista_gironi, key="admin_g_da")
            coppie_in_g = t_data["gironi"].get(girone_da, [])
            coppia_da_spostare = st.selectbox("Seleziona Coppia", coppie_in_g, key="admin_c_sposta") if coppie_in_g else None
            destinazioni = [g for g in lista_gironi if g != girone_da]
            girone_a = st.selectbox("A Girone", destinazioni, key="admin_g_a")
            
            if st.button("Sposta Coppia Ora", use_container_width=True) and coppia_da_spostare and girone_a:
                gestisci_spostamento_coppia(torneo_selezionato, coppia_da_spostare, girone_da, girone_a)
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🗑️ Elimina Torneo")
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
                st.sidebar.warning("⚠️ Spunta la casella di conferma.")

st.sidebar.markdown("⚙️ Pannello di Controllo")

if t_data["stato"] != "iscrizioni_aperte" and t_data["stato"] != "setup":
    pdf_data = genera_pdf_coppie(torneo_selezionato)
    st.sidebar.download_button(
        label="📥 Scarica Schema in PDF",
        data=pdf_data,
        file_name=f"schema_gironi_{torneo_selezionato.lower().replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.sidebar.markdown("---")

if is_admin and t_data["stato"] == "fasi_finali":
    if st.sidebar.button("🔙 Torna temporaneamente ai Gironi", use_container_width=True):
        t_data["stato"] = "gironi"
        salva_dati(db)
        st.rerun()
    st.sidebar.markdown("---")

st.sidebar.subheader("⚠️ Zona Pericolo")
if is_admin:
    conferma_reset = st.sidebar.checkbox("Spunta per confermare il reset", key="checkbox_reset_gara")
    if st.sidebar.button("🔄 Ricomincia torneo da zero", use_container_width=True):
        if conferma_reset:
            db["tornei"][torneo_selezionato] = {
                "stato": "iscrizioni_aperte",
                "coppie": [],
                "coda": [],
                "max_coppie": t_data.get("max_coppie", 32),
                "num_tavoli": t_data.get("num_tavoli", 6),
                "num_gironi": t_data.get("num_gironi", 4),
                "qualificati_fascia_a": t_data.get("qualificati_fascia_a", 4),
                "gironi": {},
                "calendario_gironi": {},
                "punti_gironi": {},
                "fasi_finali_configurate": False,
                "tabellone_a": [],
                "tabellone_b": [],
                "terzo_quarto_a": [],
                "terzo_quarto_b": []
            }
            salva_dati(db)
            st.success("Torneo azzerato con successo!")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Spunta la casella di conferma.")
else:
    st.sidebar.info("🔐 Accedi come admin per resettare.")

st.sidebar.markdown("---")

# --- GESTIONE ISCRIZIONI APERTE ---
if t_data["stato"] == "iscrizioni_aperte":
    st.markdown(f"### 📝 Registrazione Autonoma & Incolla WhatsApp - {torneo_selezionato}")
    st.info(f"Limite massimo coppie titolari: **{t_data['max_coppie']}**.")

    with st.form(f"form_iscrizione_{torneo_selezionato}"):
        c1_input = st.text_input("Nome Giocatore 1", key=f"c1_{torneo_selezionato}")
        c2_input = st.text_input("Nome Giocatore 2", key=f"c2_{torneo_selezionato}")
        st.markdown("---")
        whatsapp_paste = st.text_area("📋 Incolla qui la lista WhatsApp", key=f"wa_{torneo_selezionato}")
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
                    if not linea_pulita:
                        continue
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

    st.markdown("---")
    col_tit_vista, col_cod_vista = st.columns(2)
    
    with col_tit_vista:
        st.markdown(f"### 📋 Coppie Titolari ({len(t_data['coppie'])}/{t_data['max_coppie']})")
        if not t_data["coppie"]:
            st.info("Nessun titolare iscritto.")
        else:
            for idx, c in enumerate(t_data["coppie"], 1):
                col_ic1, col_ic2 = st.columns([0.80, 0.20])
                with col_ic1:
                    st.markdown(f"<div style='padding: 6px 10px; background: rgba(17,34,51,0.9); border: 1px solid #38bdf8; border-radius: 8px; margin-bottom: 5px; font-size: 14px; color: #ffffff;'><b>{idx}.</b> ⚽ {c}</div>", unsafe_allow_html=True)
                with col_ic2:
                    if st.button("🗑️", key=f"del_isc_{torneo_selezionato}_{idx}", use_container_width=True):
                        t_data["coppie"].remove(c)
                        if t_data["coda"]:
                            promossa = t_data["coda"].pop(0)
                            t_data["coppie"].append(promossa)
                        salva_dati(db)
                        st.rerun()

    with col_cod_vista:
        st.markdown(f"### ⏳ Coppie Lista d'Attesa ({len(t_data['coda'])})")
        if not t_data["coda"]:
            st.info("Nessuna coppia in coda.")
        else:
            for idx_c, c_coda in enumerate(t_data["coda"], 1):
                col_cc1, col_cc2 = st.columns([0.80, 0.20])
                with col_cc1:
                    st.markdown(f"<div style='padding: 6px 10px; background: rgba(14,116,144,0.2); border: 1px solid #0ea5e9; border-radius: 8px; margin-bottom: 5px; font-size: 14px; color: #ffe66d;'><b>{idx_c}.</b> ⏳ {c_coda}</div>", unsafe_allow_html=True)
                with col_cc2:
                    if st.button("🗑️", key=f"del_coda_{torneo_selezionato}_{idx_c}", use_container_width=True):
                        t_data["coda"].remove(c_coda)
                        salva_dati(db)
                        st.rerun()

    if is_admin:
        st.markdown("---")
        st.markdown("### ⚙️ Configurazione e Avvio Torneo")
        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1:
            t_data["num_tavoli"] = st.number_input("N. Biliardini", min_value=1, max_value=10, value=int(t_data.get("num_tavoli", 6)), key=f"tav_{torneo_selezionato}")
        with col_cfg2:
            t_data["num_gironi"] = st.number_input("N. Gironi", min_value=1, max_value=8, value=int(t_data.get("num_gironi", 4)), key=f"gir_{torneo_selezionato}")
        with col_cfg3:
            t_data["max_coppie"] = st.number_input("Max Titolari", min_value=2, max_value=128, value=int(t_data.get("max_coppie", 32)), key=f"maxc_{torneo_selezionato}")

        t_data["qualificati_fascia_a"] = st.number_input(
            "🏆 Passano in FASCIA A per girone:",
            min_value=1, max_value=16,
            value=int(t_data.get("qualificati_fascia_a", 4)),
            key=f"qfa_{torneo_selezionato}"
        )

        if st.button("🚀 Avvia Torneo (Crea Gironi Casuali)", use_container_width=True):
            num_g = int(t_data["num_gironi"])
            coppie = [str(c).upper() for c in t_data["coppie"]]
            if len(coppie) < (num_g * 2):
                st.error(f"Hai {len(coppie)} coppie titolari. Servono almeno {num_g * 2} coppie.")
            else:
                random.shuffle(coppie)
                nomi_gironi = [chr(65 + i) for i in range(num_g)]
                gironi_dict = {f"Girone {g}": [] for g in nomi_gironi}

                for idx, c in enumerate(coppie):
                    g_scelto = f"Girone {nomi_gironi[idx % num_g]}"
                    gironi_dict[g_scelto].append(c)

                t_data["gironi"] = gironi_dict
                t_data["punti_gironi"] = {
                    g: {c: {"punti": 0, "gf": 0, "gs": 0, "dr": 0, "scontri_diretti_pt": 0} for c in lst}
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

                t_data["calendario_gironi"] = calendario_totale
                t_data["stato"] = "gironi"
                t_data["fasi_finali_configurate"] = False
                salva_dati(db)
                st.success("Torneo avviato con successo!")
                st.rerun()

    st.stop()

# --- SELETTORE COPPIA ---
tutte_le_coppie = []
for g_lst in t_data["gironi"].values():
    tutte_le_coppie.extend(g_lst)
if not tutte_le_coppie and t_data.get("coppie"):
    tutte_le_coppie = t_data["coppie"]

opzioni_selettore = ["-- Seleziona la tua coppia per accedere --"] + sorted([str(c).upper() for c in tutte_le_coppie])
coppia_url = st.query_params.get("coppia", "-- Seleziona la tua coppia per accedere --").upper()
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
    st.success("🛡️ **Modalità Amministratore attiva:** Accesso completo sbloccato.")
elif coppia_selezionata == "-- Seleziona la tua coppia per accedere --":
    st.warning("⚠️ **Attenzione:** Seleziona la tua coppia dal menu a tendina per accedere.")
    st.stop()
else:
    st.success(f"✅ Accesso effettuato come: **{coppia_selezionata}**")

if coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
    with st.expander(f"👁️ Segui la tua coppia: {coppia_selezionata}", expanded=True):
        girone_mio, pos_mia, info_mie = None, None, None
        for g_nome, lista_c in t_data["gironi"].items():
            if coppia_selezionata in lista_c:
                girone_mio = g_nome
                ricalcola_classifiche_gironi(torneo_selezionato)
                if g_nome in t_data["punti_gironi"]:
                    dati_g = t_data["punti_gironi"][g_nome]
                    sorted_c = sorted(
                        dati_g.items(),
                        key=lambda x: (x[1]["punti"], x[1]["scontri_diretti_pt"], x[1]["dr"], x[1]["gf"]),
                        reverse=True,
                    )
                    for idx, (c_nome, stats) in enumerate(sorted_c):
                        if c_nome == coppia_selezionata:
                            pos_mia = idx + 1
                            info_mie = stats
                break

        st.markdown(
            f"""
            <div class="cyber-card" style="border-color: #38bdf8; text-align: left; padding: 20px;">
                <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #ffe66d; font-weight: bold; margin-bottom: 2px;">LA TUA COPPIA</div>
                <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-bottom: 14px;">🤝 {coppia_selezionata}</div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <div style="background: rgba(17, 34, 51, 0.9); border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; flex: 1; min-width: 100px; text-align: center;">
                        <div style="font-size: 10px; color: #94a3b8; font-weight: bold;">POSIZIONE</div>
                        <div style="font-size: 16px; font-weight: 700; color: #22c55e; margin-top: 2px;">{str(pos_mia) + '° POSTO' if pos_mia else 'N.D.'}</div>
                    </div>
                    <div style="background: rgba(17, 34, 51, 0.9); border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; flex: 1; min-width: 100px; text-align: center;">
                        <div style="font-size: 10px; color: #94a3b8; font-weight: bold;">GIRONE</div>
                        <div style="font-size: 16px; font-weight: 700; color: #0ea5e9; margin-top: 2px;">{girone_mio if girone_mio else 'N.D.'}</div>
                    </div>
                    <div style="background: rgba(17, 34, 51, 0.9); border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; flex: 1; min-width: 100px; text-align: center;">
                        <div style="font-size: 10px; color: #94a3b8; font-weight: bold;">PUNTI / DR</div>
                        <div style="font-size: 16px; font-weight: 700; color: #ffe66d; margin-top: 2px;">{info_mie['punti'] if info_mie else 0} PT <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">(DR: {info_mie['dr'] if info_mie else 0})</span></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        match_in_corso_mio = None
        match_in_coda_mio = None

        if t_data.get("stato") == "gironi":
            for g_n, turni in t_data.get("calendario_gironi", {}).items():
                for t_obj in turni:
                    for m in t_obj["partite"]:
                        if not m.get("giocata", False):
                            if m.get("in_corso", False) and (m["c1"] == coppia_selezionata or m["c2"] == coppia_selezionata):
                                match_in_corso_mio = m
                                break

            if not match_in_corso_mio:
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

                partite_miste = []
                max_len = max([len(v) for v in partite_per_girone_dict.values()]) if partite_per_girone_dict else 0
                for idx_misto in range(max_len):
                    for g_chiave in sorted(partite_per_girone_dict.keys()):
                        if idx_misto < len(partite_per_girone_dict[g_chiave]):
                            partite_miste.append(partite_per_girone_dict[g_chiave][idx_misto])

                partite_da_giocare = [m for m in partite_miste if not m.get("giocata", False) and not m.get("in_corso", False)]
                prossime_in_coda = partite_da_giocare[:num_tavoli]

                for idx, m in enumerate(prossime_in_coda):
                    if m["c1"] == coppia_selezionata or m["c2"] == coppia_selezionata:
                        match_in_coda_mio = (m, idx + 1)
                        break

        if match_in_corso_mio:
            tav_num = match_in_corso_mio.get("tavolo", "N.D.")
            match_id_mio = match_in_corso_mio["id"]
            st.markdown(
                f"""
                <div class="match-live-card" style="margin-top: 10px;">
                    <div style="font-size: 13px; color: #eab308; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px;">
                        🔥 SEI IN CAMPO ORA!
                    </div>
                    <b style="font-size: 14px; color: #ffe66d;">🏟️ Biliardino {tav_num} • {match_in_corso_mio['girone']}</b>
                    <div style="font-size: 16px; font-weight: 800; color: #ffffff; margin-top: 6px;">
                        🤝 {match_in_corso_mio['c1']} <span style="color: #eab308;">VS</span> 🤝 {match_in_corso_mio['c2']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("📝 Inserisci Risultato della Partita", expanded=True):
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    gol_c1 = st.selectbox(f"Gol {match_in_corso_mio['c1']}", options=[0, 1, 2, 3, 4, 5, 6, 7], index=int(match_in_corso_mio.get("gol1", 0)), key=f"user_g1_{match_id_mio}")
                with col_m2:
                    gol_c2 = st.selectbox(f"Gol {match_in_corso_mio['c2']}", options=[0, 1, 2, 3, 4, 5, 6, 7], index=int(match_in_corso_mio.get("gol2", 0)), key=f"user_g2_{match_id_mio}")
                
                if st.button("✅ Salva e Invia Risultato", key=f"user_save_{match_id_mio}", use_container_width=True):
                    match_in_corso_mio["gol1"] = int(gol_c1)
                    match_in_corso_mio["gol2"] = int(gol_c2)
                    match_in_corso_mio["giocata"] = True
                    match_in_corso_mio["in_corso"] = False
                    match_in_corso_mio["tavolo"] = None
                    ricalcola_classifiche_gironi(torneo_selezionato)
                    salva_dati(db)
                    st.success("Risultato salvato correttamente!")
                    st.rerun()

        elif match_in_coda_mio:
            m_coda, pos_coda = match_in_coda_mio
            st.markdown(
                f"""
                <div class="match-next-neon" style="margin-top: 10px;">
                    <div style="font-size: 13px; color: #22c55e; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px;">
                        ⚡ PROSSIMA PARTITA IN ARRIVO - PREPARATI!
                    </div>
                    <b style="font-size: 13px; color: #ffe66d;">⏳ {pos_coda}° in Coda • {m_coda['girone']}</b>
                    <div style="font-size: 16px; font-weight: 800; color: #ffffff; margin-top: 6px;">
                        🤝 {m_coda['c1']} <span style="color: #22c55e;">VS</span> 🤝 {m_coda['c2']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# 2. FASE A GIRONI LIVE
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

    st.subheader(f"⚡ Stato Biliardini e Incontri - {torneo_selezionato}")
    col_ic, col_coda = st.columns(2)

    with col_ic:
        st.markdown("#### 🔥 Partite in Corso ai Tavoli")
        if not partite_in_corso:
            st.info("Nessuna partita in corso.")
        else:
            for m in partite_in_corso:
                tavolo_str = f"<b>🏟️ Biliardino {m.get('tavolo')} - {m['girone']}</b>" if m.get("tavolo") else f"<b>🏟️ In campo - {m['girone']}</b>"
                match_id = m["id"]
                fa_al_caso_nostro = is_admin or coppia_selezionata == m["c1"] or coppia_selezionata == m["c2"]

                st.markdown(
                    f"""
                    <div class="match-live-card" style="margin-bottom: 12px;">
                        <div style="font-size: 14px; color: #ffe66d; font-weight: bold; margin-bottom: 8px;">{tavolo_str}</div>
                        <div style="font-size: 16px; font-weight: bold; color: #ffffff;">🤝 {m['c1']}</div>
                        <div style="margin: 4px 0; font-size: 12px; font-weight: bold; color: #ffe66d;">VS</div>
                        <div style="font-size: 16px; font-weight: bold; color: #ffffff;">🤝 {m['c2']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if is_admin:
                    if st.button("🔄 Posticipa di 2 partite", key=f"post_{torneo_selezionato}_{match_id}", use_container_width=True):
                        if posticipa_partita_coda(torneo_selezionato, match_id):
                            st.success("Partita posticipata!")
                            st.rerun()

                if fa_al_caso_nostro:
                    with st.expander(f"📝 Inserisci Risultato Tavolo {m.get('tavolo', '')}"):
                        gol_p1 = st.selectbox(f"Gol {m['c1']}", options=[0, 1, 2, 3, 4, 5, 6, 7], index=int(m.get("gol1", 0)), key=f"g1_{torneo_selezionato}_{match_id}")
                        gol_p2 = st.selectbox(f"Gol {m['c2']}", options=[0, 1, 2, 3, 4, 5, 6, 7], index=int(m.get("gol2", 0)), key=f"g2_{torneo_selezionato}_{match_id}")
                        if st.button("✅ Conferma Risultato", key=f"save_{torneo_selezionato}_{match_id}", use_container_width=True):
                            m["gol1"] = int(gol_p1) if gol_p1 is not None else 0
                            m["gol2"] = int(gol_p2) if gol_p2 is not None else 0
                            m["giocata"] = True
                            m["in_corso"] = False
                            m["tavolo"] = None
                            ricalcola_classifiche_gironi(torneo_selezionato)
                            salva_dati(db)
                            st.success("Risultato registrato!")
                            st.rerun()

    with col_coda:
        partite_in_coda_correnti = partite_da_giocare[:num_tavoli]
        st.markdown("#### ⏳ In Coda (Prossimi Incontri)")
        if not partite_in_coda_correnti:
            st.info("Coda vuota.")
        else:
            for idx, m in enumerate(partite_in_coda_correnti):
                is_mia_partita = (
                    coppia_selezionata != "-- Seleziona la tua coppia per accedere --" 
                    and (coppia_selezionata == m['c1'] or coppia_selezionata == m['c2'])
                )
                
                st.markdown(
                    f"""
                    <div class="match-next-neon" style="margin-bottom: 12px;">
                        <div style="font-size: 13px; color: #22c55e; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px;">
                            {'⚡ LA TUA PROSSIMA PARTITA - PREPARATI!' if is_mia_partita else '⏳ IN CODA'}
                        </div>
                        <b style="font-size: 13px; color: #ffe66d;">⏳ {idx+1}° In Coda • {m['girone']}</b><br>
                        <div style="font-size: 16px; font-weight: 800; color: #ffffff; margin-top: 6px;">
                            🤝 {m['c1']} <span style="color: #22c55e;">VS</span> 🤝 {m['c2']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    if is_admin:
        st.subheader("👥 Composizione dei Gironi (Riservato Admin)")
        nomi_gironi_chiavi = list(t_data["gironi"].keys())

        for i in range(0, len(nomi_gironi_chiavi), 2):
            col_gironi_comp = st.columns(2)
            for j in range(2):
                if i + j < len(nomi_gironi_chiavi):
                    g_nome = nomi_gironi_chiavi[i + j]
                    coppie_g = sorted(t_data["gironi"][g_nome])
                    with col_gironi_comp[j]:
                        st.markdown(f"<h4 style='margin:0 0 8px 0; color: #ffe66d;'>📁 {g_nome}</h4>", unsafe_allow_html=True)
                        html_coppie = "<div class='cyber-card' style='padding: 10px 14px; margin-bottom: 15px;'>"
                        for c_idx, c_nome in enumerate(coppie_g, 1):
                            html_coppie += f"<div style='padding: 4px 0; border-bottom: 1px solid rgba(56,189,248,0.2); color: #ffffff; font-size: 13px;'><b>{c_idx}.</b> ⚽ {c_nome}</div>"
                        html_coppie += "</div>"
                        st.markdown(html_coppie, unsafe_allow_html=True)

        st.markdown("---")
    else:
        nomi_gironi_chiavi = list(t_data["gironi"].keys())

    st.subheader("📊 Classifiche dei Gironi")
    prossime_in_coda_ids = [m["id"] for m in partite_in_coda_correnti]

    for i in range(0, len(nomi_gironi_chiavi), 2):
        col_gironi = st.columns(2)
        for j in range(2):
            if i + j < len(nomi_gironi_chiavi):
                g_nome = nomi_gironi_chiavi[i + j]
                with col_gironi[j]:
                    st.markdown(f"<h3 style='margin:0 0 10px 0; color: #38bdf8;'>📁 {g_nome}</h3>", unsafe_allow_html=True)
                    renderizza_classifica_stile_card(torneo_selezionato, g_nome)

    # --- PARTITE DIVISE PER GIRONE ---
    st.markdown("---")
    st.subheader("📅 Partite divise per Girone")

    for g_nome in nomi_gironi_chiavi:
        st.markdown(f"### 📁 {g_nome}")
        turni_del_girone = t_data.get("calendario_gironi", {}).get(g_nome, [])
        
        for t_obj in turni_del_girone:
            st.markdown(f"**Turno {t_obj['turno']}**")
            for m in t_obj["partite"]:
                match_id = m["id"]
                if m.get("giocata", False):
                    color_border = "#ef4444"
                    stato_badge = f"<span class='status-badge' style='border: 1px solid #ef4444; color: #f87171; background: rgba(239, 68, 68, 0.1);'>COMPLETATA ({m['gol1']} - {m['gol2']})</span>"
                elif m.get("in_corso", False):
                    color_border = "#eab308"
                    stato_badge = f"<span class='status-badge' style='border: 1px solid #eab308; color: #ffe66d; background: rgba(234, 179, 8, 0.1);'>IN CORSO (Tavolo {m.get('tavolo', '')})</span>"
                elif match_id in prossime_in_coda_ids:
                    color_border = "#22c55e"
                    stato_badge = "<span class='status-badge' style='border: 1px solid #22c55e; color: #4ade80; background: rgba(34, 197, 94, 0.1);'>IN CODA</span>"
                else:
                    color_border = "#0ea5e9"
                    stato_badge = "<span class='status-badge' style='border: 1px solid #0ea5e9; color: #38bdf8; background: rgba(14, 165, 233, 0.1);'>DA GIOCARE</span>"

                st.markdown(
                    f"""
                    <div class="match-row-card" style="border: 1.5px solid {color_border};">
                        <div>
                            <span style="font-size: 14px; font-weight: bold; color: #ffffff;">{m['c1']}</span>
                            <span style="font-size: 12px; color: #ffe66d; font-weight: bold; margin: 0 6px;">VS</span>
                            <span style="font-size: 14px; font-weight: bold; color: #ffffff;">{m['c2']}</span>
                        </div>
                        <div>
                            {stato_badge}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if is_admin:
                    with st.expander(f"⚙️ Modifica / Inserisci Risultato ({m['c1']} vs {m['c2']})"):
                        col_adm1, col_adm2 = st.columns(2)
                        with col_adm1:
                            gol_adm_1 = st.selectbox(f"Gol {m['c1']}", options=[0, 1, 2, 3, 4, 5, 6, 7], index=int(m.get("gol1", 0)), key=f"adm_g1_{torneo_selezionato}_{match_id}")
                        with col_adm2:
                            gol_adm_2 = st.selectbox(f"Gol {m['c2']}", options=[0, 1, 2, 3, 4, 5, 6, 7], index=int(m.get("gol2", 0)), key=f"adm_g2_{torneo_selezionato}_{match_id}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("💾 Salva Risultato", key=f"adm_save_{torneo_selezionato}_{match_id}", use_container_width=True):
                                m["gol1"] = int(gol_adm_1)
                                m["gol2"] = int(gol_adm_2)
                                m["giocata"] = True
                                m["in_corso"] = False
                                m["tavolo"] = None
                                ricalcola_classifiche_gironi(torneo_selezionato)
                                salva_dati(db)
                                st.success("Risultato salvato/modificato!")
                                st.rerun()
                        with col_btn2:
                            if m.get("giocata", False):
                                if st.button("🔄 Annulla Risultato", key=f"adm_reset_{torneo_selezionato}_{match_id}", use_container_width=True):
                                    m["gol1"] = 0
                                    m["gol2"] = 0
                                    m["giocata"] = False
                                    m["in_corso"] = False
                                    m["tavolo"] = None
                                    ricalcola_classifiche_gironi(torneo_selezionato)
                                    salva_dati(db)
                                    st.success("Risultato azzerato!")
                                    st.rerun()

    if is_admin:
        st.markdown("---")
        q_a = int(t_data.get("qualificati_fascia_a", 4))
        if st.button(f"🏆 Genera Fasi Finali (Prime {q_a} in Fascia A)", use_container_width=True):
            classificate_a, classificate_b_raw = {}, {}
            for g_nome in t_data["gironi"]:
                dati_girone = t_data["punti_gironi"][g_nome]
                sorted_c = sorted(dati_girone.items(), key=lambda x: (x[1]["punti"], x[1]["scontri_diretti_pt"], x[1]["dr"], x[1]["gf"]), reverse=True)
                squadre_girone = [(str(c[0]).upper(), idx + 1) for idx, c in enumerate(sorted_c)]
                classificate_a[g_nome] = squadre_girone[:q_a]
                classificate_b_raw[g_nome] = [sq[0] for sq in squadre_girone]

            tutte_sq_a = []
            for g_n in classificate_a:
                for sq_info in classificate_a[g_n]:
                    tutte_sq_a.append((sq_info[0], g_n, sq_info[1]))
            random.shuffle(tutte_sq_a)
            abbinamenti_a = []
            for i in range(0, len(tutte_sq_a), 2):
                if i + 1 < len(tutte_sq_a):
                    abbinamenti_a.append((tutte_sq_a[i], tutte_sq_a[i + 1]))
                else:
                    abbinamenti_a.append((tutte_sq_a[i], ("RIPOSO", "", 0)))

            abbinamenti_b = crea_abbinamenti_fascia_b(classificate_b_raw, q_a)

            turno_a_iniziale = [{"id": f"fa_t1_m{i}", "s1": str(s1[0]).upper(), "g1": s1[1], "p1": s1[2], "s2": str(s2[0]).upper(), "g2": s2[1], "p2": s2[2], "giocata": False, "vincente": None} for i, (s1, s2) in enumerate(abbinamenti_a)]
            turno_b_iniziale = [{"id": f"fb_t1_m{i}", "s1": str(s1[0]).upper(), "g1": s1[1], "p1": s1[2], "s2": str(s2[0]).upper(), "g2": s2[1], "p2": s2[2], "giocata": False, "vincente": None} for i, (s1, s2) in enumerate(abbinamenti_b)]

            t_data["tabellone_a"] = [{"turno": 1, "partite": turno_a_iniziale}]
            t_data["tabellone_b"] = [{"turno": 1, "partite": turno_b_iniziale}]
            t_data["terzo_quarto_a"] = []
            t_data["terzo_quarto_b"] = []
            t_data["stato"] = "fasi_finali"
            t_data["fasi_finali_configurate"] = True
            salva_dati(db)
            st.success("Fasi finali generate correttamente!")
            st.rerun()

# 3. FASI FINALI
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

        campione, secondo_posto, terzo_posto, quarto_posto = None, None, None, None
        tot_partite_turno_1 = len(turni_tab[0]["partite"])
        num_totale_squadre_tab = tot_partite_turno_1 * 2

        num_turni_totali = math.ceil(math.log2(num_totale_squadre_tab)) if num_totale_squadre_tab > 1 else 1

        modificato_tabellone = False
        while len(turni_tab) < num_turni_totali:
            prossimo_t_num = len(turni_tab) + 1
            num_match_prossimo = max(1, len(turni_tab[-1]["partite"]) // 2)
            partite_nuovo_turno = [{"id": f"{chiave_tabellone}_t{prossimo_t_num}_m{m_idx}", "s1": "In attesa...", "g1": "", "p1": "", "s2": "In attesa...", "g2": "", "p2": "", "giocata": False, "vincente": None} for m_idx in range(num_match_prossimo)]
            turni_tab.append({"turno": prossimo_t_num, "partite": partite_nuovo_turno})
            modificato_tabellone = True
            
        if modificato_tabellone:
            salva_dati(db)

        for t_idx, turno_obj in enumerate(turni_tab):
            t_num = turno_obj["turno"]
            partite_turno = turno_obj["partite"]
            nome_etichetta = ottieni_nome_turno_dinamico(len(partite_turno))

            st.markdown(f"""<div style="background: linear-gradient(90deg, #38bdf8 0%, #0284c7 100%); padding: 10px; border-radius: 8px; margin: 15px 0; text-align: center; color: #ffffff; font-weight: bold;"><b>{nome_etichetta}</b></div>""", unsafe_allow_html=True)

            if t_idx + 1 < len(turni_tab):
                turno_successivo = turni_tab[t_idx + 1]
                for m_i, match_corrente in enumerate(partite_turno):
                    if match_corrente["giocata"] and match_corrente.get("vincente"):
                        vincitore_corrente = str(match_corrente["vincente"]).upper()
                        g_v, p_v = mappa_girone_pos.get(vincitore_corrente, ("", ""))
                        target_match_idx = m_i // 2
                        slot_squadra = "s1" if (m_i % 2 == 0) else "s2"
                        slot_g = "g1" if (m_i % 2 == 0) else "g2"
                        slot_p = "p1" if (m_i % 2 == 0) else "p2"

                        if target_match_idx < len(turno_successivo["partite"]):
                            dest_match = turno_successivo["partite"][target_match_idx]
                            if dest_match[slot_squadra] in ["In attesa...", ""]:
                                dest_match[slot_squadra] = vincitore_corrente
                                dest_match[slot_g] = g_v
                                dest_match[slot_p] = p_v
                                salva_dati(db)

            perdenti_turno = []
            for idx, m in enumerate(partite_turno):
                match_id = m["id"]
                s1_nome, s2_nome = str(m["s1"]).upper(), str(m["s2"]).upper()
                
                g1_info = f" ({m['g1']} - {m['p1']}°)" if m.get("g1") and m.get("p1") else ""
                g2_info = f" ({m['g2']} - {m['p2']}°)" if m.get("g2") and m.get("p2") else ""
                
                if s1_nome in ["In attesa...", ""] or s2_nome in ["In attesa...", ""]:
                    st.markdown(f"""<div class="cyber-card" style="text-align: center;"><b>{s1_nome}{g1_info} vs {s2_nome}{g2_info}</b><br><span style="color: #94a3b8;">In attesa di squadre</span></div>""", unsafe_allow_html=True)
                    continue

                if m["giocata"]:
                    perdente_match = s2_nome if str(m["vincente"]).upper() == s1_nome else s1_nome
                    perdenti_turno.append(perdente_match)
                    centro_testo = f"<b style='color: #22c55e;'>Vince: {str(m['vincente']).upper()}</b>"
                else:
                    centro_testo = "<b style='color: #ffe66d;'>VS</b>"

                st.markdown(
                    f"""<div class="cyber-card" style="text-align: center;">
                        <span style="font-size: 15px;"><b>{s1_nome}</b><span style="color: #38bdf8; font-size: 12px; font-weight: bold;">{g1_info}</span></span>
                        <br>{centro_testo}<br>
                        <span style="font-size: 15px;"><b>{s2_nome}</b><span style="color: #38bdf8; font-size: 12px; font-weight: bold;">{g2_info}</span></span>
                    </div>""",
                    unsafe_allow_html=True
                )

                if is_admin:
                    with st.expander(f"⚙️ Imposta Vincitore ({s1_nome} vs {s2_nome})"):
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
                quarto_posto = str(tq_match["s2"]).upper() if terzo_posto == str(tq_match["s1"]).upper() else str(tq_match["s1"]).upper()
            
            info_tq1 = f" ({tq_match['g1']} - {tq_match['p1']}°)" if tq_match.get("g1") and tq_match.get("p1") else ""
            info_tq2 = f" ({tq_match['g2']} - {tq_match['p2']}°)" if tq_match.get("g2") and tq_match.get("p2") else ""
            
            st.markdown(f"<div class='cyber-card' style='text-align: center;'><b>{str(tq_match['s1']).upper()}{info_tq1} vs {str(tq_match['s2']).upper()}{info_tq2}</b><br>Vincitore 3° posto: {str(tq_match.get('vincente', 'Da assegnare')).upper()}</div>", unsafe_allow_html=True)
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
            st.markdown(
                f"""
                <div class="cyber-card-gold" style="padding: 20px; margin-top: 15px;">
                    <h2>🏆 PODIO - {titolo_tab} 🏆</h2>
                    <p style="font-size: 18px; color: #ffe66d;">🥇 1° POSTO: <b>{campione}</b></p>
                    <p style="font-size: 16px; color: #cbd5e1;">🥈 2° POSTO: {secondo_posto}</p>
                    <p style="font-size: 16px; color: #22c55e;">🥉 3° POSTO: {terzo_posto if terzo_posto else 'N.D.'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_a_view:
        gestisci_tabellone("tabellone_a", "terzo_quarto_a", "Fascia A")
    with tab_b_view:
        gestisci_tabellone("tabellone_b", "terzo_quarto_b", "Fascia B")
