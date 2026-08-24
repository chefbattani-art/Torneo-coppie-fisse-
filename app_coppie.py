# --- CRUSCOTTO PERSONALE (VERSIONE INTEGRATA E COLORATA) ---

if "db" in locals() and "coppia_selezionata" in locals() and coppia_selezionata:
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

  # Raccogliamo le partite della coppia
  partite_mie_in_corso = []
  partite_mie_in_coda = []
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

    da_giocare_tot = [p for p in tutte_p_girone if not p.get("giocata", False)]
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

  punti_str = f"{info_mie['punti']} pt" if info_mie else "0 pt"
  dr_val = info_mie["dr"] if info_mie else 0
  dr_str = f"+{dr_val}" if dr_val >= 0 else str(dr_val)
  pos_str = f"{pos_mia}° Posto" if pos_mia else "N.D."

  # Generazione righe partite fatte HTML
  html_partite_fatte = ""
  if not partite_mie_fatte:
    html_partite_fatte = (
        '<div style="font-size: 12px; color: #718096; text-align:'
        ' center;">Nessuna partita disputata ancora.</div>'
    )
  else:
    for m in partite_mie_fatte:
      html_partite_fatte += f"""
      <div style="background: #f0fff4; border-radius: 6px; padding: 6px 10px; font-size: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span>{m['c1']} vs {m['c2']}</span>
        <strong style="color: #276749;">{m['gol1']} - {m['gol2']}</strong>
      </div>
      """

  # Generazione righe partite da giocare HTML
  html_partite_mancanti = ""
  if not partite_mie_in_corso and not partite_mie_in_coda:
    html_partite_mancanti = (
        '<div style="font-size: 12px; color: #718096; text-align:'
        ' center;">Nessuna partita attiva o in coda adesso.</div>'
    )
  else:
    for m in partite_mie_in_corso:
      html_partite_mancanti += f"""
      <div style="background: #fff9db; border: 1px solid #fcc419; border-radius: 6px; padding: 8px; font-size: 12px; text-align: center; margin-bottom: 4px; color: #f08c00;">
        🔥 <b>IN CORSO (Tavolo {m.get('tavolo', 'N/D')})</b>: {m['c1']} vs {m['c2']}
      </div>
      """
    for m in partite_mie_in_coda:
      html_partite_mancanti += f"""
      <div style="background: #fffaf0; border: 1px dashed #ed8936; border-radius: 6px; padding: 8px; font-size: 12px; color: #c05621; text-align: center; margin-bottom: 4px;">
        ⏳ <b>IN CODA</b>: {m['c1']} vs {m['c2']}
      </div>
      """

  # Generazione classifica intera del girone HTML
  html_righe_classifica = ""
  if girone_mio and girone_mio in db["punti_gironi"]:
    dati_girone = db["punti_gironi"][girone_mio]
    sorted_girone = sorted(
        dati_girone.items(),
        key=lambda x: (
            x[1]["punti"],
            x[1]["scontri_diretti_pt"],
            x[1]["dr"],
            x[1]["gf"],
        ),
        reverse=True,
    )
    for idx, (c_nome, stats) in enumerate(sorted_girone):
      is_tuo = c_nome == coppia_selezionata
      bg_riga = "#ebf8ff" if is_tuo else "transparent"
      font_w = "bold" if is_tuo else "normal"
      colore_testo = "#2b6cb0" if is_tuo else "#2d3748"
      stella = " ⭐" if is_tuo else ""
      dr_v = stats["dr"]
      dr_s = f"+{dr_v}" if dr_v >= 0 else str(dr_v)

      html_righe_classifica += f"""
      <tr style="background: {bg_riga}; font-weight: {font_w}; color: {colore_testo}; border-bottom: 1px solid #edf2f7;">
        <td style="padding: 6px 2px;">{idx+1}°</td>
        <td>{c_nome}{stella}</td>
        <td style="text-align: center;">{stats['punti']}</td>
        <td style="text-align: right;">{dr_s}</td>
      </tr>
      """

  # Widget completo unificato
  st.markdown(
      f"""
  <div style="font-family: 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; border-radius: 16px; padding: 20px; max-width: 480px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); color: #2d3748; margin-bottom: 25px;">
    
    <!-- Intestazione Girone -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 16px; color: white; margin-bottom: 16px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 14px; font-weight: 600;">📁 {girone_mio if girone_mio else 'Girone'}</span>
        <span style="background: #48bb78; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;">🏆 {pos_str}</span>
      </div>
      <div style="display: flex; justify-content: space-between; font-size: 14px; margin-top: 10px;">
        <span>Punti: <strong>{punti_str}</strong></span>
        <span>DR: <strong style="color: #9ae6b4;">{dr_str}</strong></span>
      </div>
    </div>

    <!-- Pulsante Andamento -->
    <div style="margin-bottom: 20px; text-align: center;">
      <div style="background: linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%); color: white; padding: 14px; border-radius: 10px; font-weight: bold; font-size: 15px; box-shadow: 0 4px 10px rgba(255,126,95,0.3);">
        🔥 Il Mio Andamento Gara & Storico
      </div>
    </div>

    <!-- Partite della Coppia -->
    <div style="background: white; border-radius: 10px; padding: 14px; margin-bottom: 16px; border: 1px solid #e2e8f0;">
      <div style="font-size: 14px; font-weight: bold; color: #1a202c; margin-bottom: 10px; border-bottom: 1px solid #edf2f7; padding-bottom: 6px;">⚽ Le tue partite nel girone</div>
      
      <div style="font-size: 12px; font-weight: bold; color: #dd6b20; margin-bottom: 4px;">⏳ Partite in coda o attive:</div>
      <div style="margin-bottom: 10px;">
        {html_partite_mancanti}
      </div>

      <div style="font-size: 12px; font-weight: bold; color: #38a169; margin-bottom: 4px;">✅ Partite già effettuate:</div>
      <div>
        {html_partite_fatte}
      </div>
    </div>

    <!-- Intera Classifica del Girone -->
    <div style="background: white; border-radius: 10px; padding: 14px; border: 1px solid #e2e8f0;">
      <div style="font-size: 14px; font-weight: bold; color: #1a202c; margin-bottom: 10px; border-bottom: 1px solid #edf2f7; padding-bottom: 6px;">📊 Classifica Intera {girone_mio if girone_mio else 'Girone'}</div>
      <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
        <tr style="color: #a0aec0; border-bottom: 1px solid #edf2f7;">
          <th style="padding-bottom: 4px;">Pos</th>
          <th style="padding-bottom: 4px;">Coppia</th>
          <th style="padding-bottom: 4px; text-align: center;">PT</th>
          <th style="padding-bottom: 4px; text-align: right;">DR</th>
        </tr>
        {html_righe_classifica}
      </table>
    </div>

  </div>
  """,
      unsafe_allow_html=True,
  )

  st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
else:
  st.info("👈 Seleziona una coppia dal menu per visualizzare il cruscotto.")
