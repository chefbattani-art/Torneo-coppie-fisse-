import streamlit as st

# Esempio per la partita: Lorenzo Casanova vs Carlo Pensionato
st.markdown("### Inserisci Risultato Tavolo")

# Invece di st.number_input o st.slider, usiamo st.radio in orizzontale o st.pills (disponibile nelle versioni recenti di Streamlit)
# oppure dei bottoni grandi stilizzati con i numeri da 0 a 7.

col1, col2 = st.columns(2)

with col1:
  st.markdown(
      "<p"
      ' style="font-weight: bold; font-size: 16px;">Gol Lorenzo'
      " Casanova</p>",
      unsafe_allow_html=True,
  )
  # Usiamo st.radio in modalità orizzontale (orizzontale nativo o tramite CSS personalizzato per farlo sembrare più grande)
  gol_p1 = st.radio(
      "Seleziona gol Lorenzo",
      options=list(range(8)),  # Da 0 a 7
      format_func=lambda x: f" {x} ",
      key="gol_lorenzo",
      horizontal=True,
  )

with col2:
  st.markdown(
      "<p"
      ' style="font-weight: bold; font-size: 16px;">Gol Carlo Pensionato</p>',
      unsafe_allow_html=True,
  )
  gol_p2 = st.radio(
      "Seleziona gol Carlo",
      options=list(range(8)),  # Da 0 a 7
      format_func=lambda x: f" {x} ",
      key="gol_carlo",
      horizontal=True,
  )

# CSS personalizzato per ingrandire i numeri e renderli simili a pulsanti grandi da admin
st.markdown(
    """
<style>
    /* Ingrandisce i testi dei radio button e li trasforma in pulsanti/pillole grandi */
    div[row-widget="stRadio"] div {{
        gap: 8px;
    }}
    div[row-widget="stRadio"] label {{
        background-color: #f0f2f6;
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px solid #d6d6d6;
        font-size: 18px !important;
        font-weight: bold !important;
        text-align: center;
    }}
    div[row-widget="stRadio"] input[type="radio"]:checked + div {{
        background-color: #ff4b4b;
        color: white;
    }}
</style>
""",
    unsafe_allow_html=True,
)

if st.button("✅ Conferma e Registra Risultato", use_container_width=True):
  st.success(f"Risultato registrato: {gol_p1} - {gol_p2}")
