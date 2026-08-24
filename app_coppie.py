import streamlit as st

# Blocco Dashboard Torneo per Streamlit
st.markdown("""
<div style="font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); border-radius: 16px; padding: 20px; max-width: 480px; margin: 0 auto; box-shadow: 0 8px 20px rgba(0,0,0,0.08); color: #2d3748;">
  
  <!-- INTESTAZIONE GIRONE E POSIZIONE -->
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 18px; color: white; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(102,126,234,0.3);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;">Girone B</span>
      <span style="background: #48bb78; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold;">1° Posto</span>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 14px; font-weight: 500;">
      <span>Punti: <strong>6 pt</strong></span>
      <span>DR: <strong style="color: #9ae6b4;">+14</strong></span>
    </div>
  </div>

  <!-- PULSANTE SPECIALE: ANDAMENTO PERSONALE -->
  <div style="margin-bottom: 24px; text-align: center;">
    <a href="#andamento" onclick="alert('Caricamento andamento personale della coppia!'); return false;" style="display: block; background: linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%); color: white; text-decoration: none; padding: 16px 20px; border-radius: 12px; font-weight: bold; font-size: 16px; box-shadow: 0 6px 15px rgba(255,126,95,0.4);">
      🔥 Il Mio Andamento Gara
    </a>
    <p style="margin: 8px 0 0 0; font-size: 12px; color: #718096;">
      Clicca per visualizzare lo storico, i grafici e l'andamento della tua coppia.
    </p>
  </div>

  <!-- LE TUE PARTITE -->
  <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <h4 style="margin: 0 0 12px 0; font-size: 15px; color: #1a202c; border-bottom: 2px solid #edf2f7; padding-bottom: 8px;">⚽ Le tue partite nel girone</h4>
    
    <div style="margin-bottom: 14px;">
      <span style="font-size: 13px; font-weight: bold; color: #dd6b20; display: block; margin-bottom: 6px;">⏳ Partite che mancano:</span>
      <div style="background: #fffaf0; border: 1px dashed #ed8936; border-radius: 8px; padding: 10px; font-size: 13px; color: #c05621; text-align: center;">
        <strong>Balzo Lisa vs Marco & Luca</strong>
      </div>
    </div>

    <div>
      <span style="font-size: 13px; font-weight: bold; color: #38a169; display: block; margin-bottom: 6px;">✅ Partite già effettuate:</span>
      <div style="background: #f0fff4; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 13px; display: flex; justify-content: space-between; align-items: center;">
        <span>Balzo Lisa vs Clara Maicol</span>
        <strong style="color: #276749; background: #c6f6d5; padding: 2px 8px; border-radius: 6px;">7 - 0</strong>
      </div>
      <div style="background: #f0fff4; border-radius: 8px; padding: 8px 12px; font-size: 13px; display: flex; justify-content: space-between; align-items: center;">
        <span>Balzo Lisa vs Titto Turbo</span>
        <strong style="color: #276749; background: #c6f6d5; padding: 2px 8px; border-radius: 6px;">7 - 0</strong>
      </div>
    </div>
  </div>

  <!-- INTERA CLASSIFICA DEL GIRONE -->
  <div style="background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <h4 style="margin: 0 0 12px 0; font-size: 15px; color: #1a202c; border-bottom: 2px solid #edf2f7; padding-bottom: 8px;">📊 Classifica Intera Girone B</h4>
    
    <table style="width: 100%; border-collapse: collapse; font-size: 13px; text-align: left;">
      <thead>
        <tr style="color: #a0aec0; border-bottom: 1px solid #edf2f7;">
          <th style="padding-bottom: 6px;">Pos</th>
          <th style="padding-bottom: 6px;">Coppia</th>
          <th style="padding-bottom: 6px; text-align: center;">PT</th>
          <th style="padding-bottom: 6px; text-align: right;">DR</th>
        </tr>
      </thead>
      <tbody>
        <tr style="background: #ebf8ff; font-weight: bold; color: #2b6cb0; border-bottom: 1px solid #edf2f7;">
          <td style="padding: 8px 4px;">1°</td>
          <td style="padding: 8px 4px;">Balzo Lisa ⭐</td>
          <td style="padding: 8px 4px; text-align: center;">6</td>
          <td style="padding: 8px 4px; text-align: right;">+14</td>
        </tr>
        <tr style="border-bottom: 1px solid #edf2f7;">
          <td style="padding: 8px 4px;">2°</td>
          <td style="padding: 8px 4px;">Clara Maicol</td>
          <td style="padding: 8px 4px; text-align: center;">3</td>
          <td style="padding: 8px 4px; text-align: right;">-2</td>
        </tr>
        <tr style="border-bottom: 1px solid #edf2f7;">
          <td style="padding: 8px 4px;">3°</td>
          <td style="padding: 8px 4px;">Titto Turbo</td>
          <td style="padding: 8px 4px; text-align: center;">3</td>
          <td style="padding: 8px 4px; text-align: right;">-4</td>
        </tr>
        <tr>
          <td style="padding: 8px 4px;">4°</td>
          <td style="padding: 8px 4px;">Marco & Luca</td>
          <td style="padding: 8px 4px; text-align: center;">0</td>
          <td style="padding: 8px 4px; text-align: right;">-8</td>
        </tr>
      </tbody>
    </table>
  </div>

</div>
""", unsafe_allow_html=True)
