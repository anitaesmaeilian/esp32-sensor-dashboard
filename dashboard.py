import streamlit as st
import pandas as pd
from datetime import datetime

# --- Load Google Sheet data as CSV ---
sheet_url = "https://docs.google.com/spreadsheets/d/1W58Fb7zDH0tyi6Sk8SAh5QEMQZtTvtgMAYtVIkHI13k/gviz/tq?tqx=out:csv&sheet=Sheet1"
df = pd.read_csv(sheet_url)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- Dashboard Title ---
st.title("🌿 ESP32 Sensor Dashboard")

# --- Latest Sensor Readings ---
latest = df.iloc[-1]
st.metric("🌡️ Temperature (°C)", f"{latest['temperature']:.1f}")
st.metric("💧 Humidity (%)", f"{latest['humidity']:.1f}")
st.metric("🪴 Soil Moisture", f"{latest['soil_moisture']}")

# --- Line Chart ---
st.subheader("📈 Temperature Over Time")
st.line_chart(df.set_index('timestamp')["temperature"])

# --- Feedback Survey ---
st.subheader("📝 Feedback Survey")
name = st.text_input("Your name or initials (optional)")
rating = st.slider("How helpful is this dashboard?", 1, 5)
comments = st.text_area("Any suggestions or feedback?")

if st.button("Submit Feedback"):
    with open("feedback.csv", "a") as f:
        now = datetime.now().isoformat()
        f.write(f"{now},{name},{rating},{comments}\n")
    st.success("Thank you for your feedback!")

# --- Footer ---
st.markdown("🔒 This dashboard reads data from Google Sheets and stores feedback locally.")
