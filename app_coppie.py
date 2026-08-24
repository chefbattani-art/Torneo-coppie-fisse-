# --- CRUSCOTTO PERSONALE (VERSIONE NATIVA STREAMLIT) ---
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

# Mostriamo il cruscotto con i componenti nativi
with st.container():
  st.markdown(
      f"### 📊 Il Mio Andamento - {girone_mio if girone_mio else 'Girone'}"
  )

  col_p1, col_p2, col_p3 = st.columns(3)
  with col_p1:
    st.metric("Posizione", f"{pos_mia}° Posto" if pos_mia else "N.D.")
  with col_p2:
    st.metric(
        "Punti", f"{info_mie['punti']} pt" if info_mie else "0 pt"
    )
  with col_p3:
    dr_val = info_mie["dr"] if info_mie else 0
    dr_str = f"+{dr_val}" if dr_val >= 0 else str(dr_val)
    st.metric("Differenza Reti", dr_str)

  st.markdown("---")
  st.markdown("#### ⚽ Le tue partite nel girone")

  if partite_mie_in_corso:
    for m in partite_mie_in_corso:
      st.warning(
          f"🔥 **IN CORSO (Tavolo {m.get('tavolo', 'N/D')})**: {m['c1']} vs"
          f" {m['c2']}"
      )

  if partite_mie_in_coda:
    for m in partite_mie_in_coda:
      st.info(f"⏳ **IN CODA**: {m['c1']} vs {m['c2']}")

  if not partite_mie_in_corso and not partite_mie_in_coda:
    st.caption("Nessuna partita attiva o in coda adesso.")

  if partite_mie_fatte:
    st.markdown("**Partite già effettuate:**")
    for m in partite_mie_fatte:
      st.success(f"✅ {m['c1']} vs {m['c2']} ➔ **{m['gol1']} - {m['gol2']}**")
  else:
    st.caption("Nessuna partita disputata ancora.")

  st.markdown("---")
  st.markdown(f"#### 📋 Classifica Intera {girone_mio if girone_mio else ''}")

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

    data_cls = []
    for idx, (c_nome, stats) in enumerate(sorted_girone):
      dr_v = stats["dr"]
      dr_s = f"+{dr_v}" if dr_v >= 0 else str(dr_v)
      data_cls.append({
          "Pos": f"{idx+1}°",
          "Coppia": c_nome + (" ⭐" if c_nome == coppia_selezionata else ""),
          "PT": stats["punti"],
          "DR": dr_s,
      })

    df_c = pd.DataFrame(data_cls)
    st.dataframe(df_c, hide_index=True, use_container_width=True)

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
