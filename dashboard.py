import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# Your Google Sheets ID here
SHEET_ID = "1W58Fb7zDH0tyi6Sk8SAh5QEMQZtTvtgMAYtVIkHI13k"

# Map setup names to sheet tab names
SETUPS = {
    "Setup 1": "Sheet1",
    "Setup 2": "Sheet2"
}

# Function to load data from a given sheet tab
@st.cache_data(ttl=300)
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

# Function to read the crop type from cell G1
@st.cache_data(ttl=300)
def load_crop_type(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text), header=None)
    if df.shape[1] >= 7:
        return df.iloc[0, 6]  # Column G is index 6
    return "Unknown"

st.title("🌿 ESP32 Sensor Dashboard")

# 1) Select setup
setup_choice = st.selectbox("Select Setup", options=list(SETUPS.keys()))
sheet_name = SETUPS[setup_choice]

# Load data for selected setup
try:
    data = load_data(sheet_name)
    crop_type = load_crop_type(sheet_name)
except Exception as e:
    st.error(f"Error loading data for {setup_choice}: {e}")
    st.stop()

# Display crop type from cell G1
st.info(f"🌾 **Crop Type**: {crop_type}")

# 2) Select variable (all columns except Timestamp, dynamically)
variables = list(data.columns)
variables.remove('Timestamp')
variable_choice = st.selectbox("Select variable to display", options=variables)

# 3) Select date (filter by day)
min_date = data['Timestamp'].dt.date.min()
max_date = data['Timestamp'].dt.date.max()
selected_date = st.date_input("Select date", value=min_date, min_value=min_date, max_value=max_date)

# Filter data by selected date
filtered_data = data[data['Timestamp'].dt.date == selected_date]

if filtered_data.empty:
    st.warning("No data available for the selected date.")
else:
    st.subheader(f"{variable_choice} on {selected_date} for {setup_choice}")
    st.line_chart(filtered_data.set_index('Timestamp')[variable_choice])
    st.dataframe(filtered_data[['Timestamp', variable_choice]])

# Survey form
st.subheader("📝 Feedback Survey")

# Role selection
role = st.radio("Are you a:", ["Farmer", "Student"])

name = st.text_input("Your name or initials (optional)")

# Common rating question
rating = st.slider("How helpful is this dashboard?", 1, 5)

# Role-specific questions
if role == "Farmer":
    usage = st.text_area("How do you use this data to support your farming decisions?")
    suggestion = st.text_area("What features would help make this tool more useful on your farm?")
elif role == "Student":
    learning = st.text_area("What did you learn from using this dashboard?")
    idea = st.text_area("What could make this dashboard a better learning tool?")

# Submit
if st.button("Submit Feedback"):
    now = datetime.now().isoformat()
    comments = ""

    if role == "Farmer":
        comments = f"Usage: {usage.replace(',', ';')} | Suggestion: {suggestion.replace(',', ';')}"
    elif role == "Student":
        comments = f"Learning: {learning.replace(',', ';')} | Idea: {idea.replace(',', ';')}"

    with open("feedback.csv", "a") as f:
        f.write(f"{now},{name},{role},{setup_choice},{variable_choice},{selected_date},{rating},{comments}\n")

    st.success("Thank you for your feedback!")

st.markdown("🔒 This dashboard reads data from Google Sheets and stores feedback locally.")
