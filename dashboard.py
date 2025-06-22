import streamlit as st
import pandas as pd
from datetime import datetime

# Your actual Google Sheets CSV URL here
sheet_url = "https://docs.google.com/spreadsheets/d/1W58Fb7zDH0tyi6Sk8SAh5QEMQZtTvtgMAYtVIkHI13k/gviz/tq?tqx=out:csv&sheet=<Sheet1>"

df = pd.read_csv(sheet_url)

# Use the exact column name 'Timestamp' (capital T)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

st.title("🌿 ESP32 Sensor Dashboard")

# Latest readings
latest = df.iloc[-1]
st.metric("🌡️ Temperature (°C)", f"{latest['Temperature']:.1f}")
st.metric("💧 Humidity (%)", f"{latest['Humidity']:.1f}")
st.metric("🪴 Soil Moisture", f"{latest['SoilMoisture']}")

# Temperature line chart over time (using exact 'Timestamp')
st.subheader("📈 Temperature Over Time")
st.line_chart(df.set_index('Timestamp')['Temperature'])

# Feedback survey
st.subheader("📝 Feedback Survey")
name = st.text_input("Your name or initials (optional)")
rating = st.slider("How helpful is this dashboard?", 1, 5)
comments = st.text_area("Any suggestions or feedback?")

if st.button("Submit Feedback"):
    with open("feedback.csv", "a") as f:
        now = datetime.now().isoformat()
        f.write(f"{now},{name},{rating},{comments}\n")
    st.success("Thank you for your feedback!")

st.markdown("🔒 This dashboard reads data from Google Sheets and stores feedback locally.")
