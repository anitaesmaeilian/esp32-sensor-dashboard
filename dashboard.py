import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime
import os

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

# ---------------------------------------
# Feedback Survey
# ---------------------------------------
st.subheader("📝 Feedback Survey")

st.markdown("""
We'd love your feedback to help improve this dashboard and the hands-on workshops associated with it.
Please rate the following statements on a scale from **1 (Strongly Disagree)** to **5 (Strongly Agree)**.
""")

# Role selection
role = st.radio("Are you a:", ["Farmer", "Student"])
name = st.text_input("Your name or initials (optional)")

# Overall rating
overall_rating = st.slider("Overall, how helpful is this dashboard?", 1, 5)

# Shared questions
shared_questions = [
    "The dashboard is useful for understanding plant/environmental health.",
    "The workshop helped me understand how this system works.",
    "I would recommend this system to others."
]

# Role-specific questions
farmer_questions = [
    "The dashboard helps me understand my farm's environmental conditions.",
    "The setup is easy to understand and use in a farming environment.",
    "I feel more confident making farming decisions using this data.",
    "The workshop helped me learn how to use this system on my farm.",
    "I would adopt this system on my own farm."
]

student_questions = [
    "I understand how environmental sensors work after using this dashboard.",
    "The dashboard helped me connect theory to real-world plant care.",
    "I feel confident explaining how the system collects and displays data.",
    "The workshop helped me learn how to build and use the setup.",
    "I would like to participate in more projects like this."
]

# Combine questions
questions = shared_questions + (farmer_questions if role == "Farmer" else student_questions)

# Collect ratings
responses = {}
for i, q in enumerate(questions, start=1):
    responses[f"Q{i}"] = st.slider(q, 1, 5, key=q)

# Optional comment
extra_comments = st.text_area("Anything else you'd like to share? (optional)")

# Submit feedback
if st.button("Submit Feedback"):
    now = datetime.now().isoformat()
    feedback_line = f"{now},{name},{role},{setup_choice},{variable_choice},{selected_date},{overall_rating}"
    for i in range(1, len(questions) + 1):
        feedback_line += f",{responses[f'Q{i}']}"
    feedback_line += f",\"{extra_comments.replace(',', ';')}\"\n"

    header = "Timestamp,Name,Role,Setup,Variable,Date,Overall Rating"
    for i in range(1, len(questions) + 1):
        header += f",Q{i}"
    header += ",Comments\n"

    file_exists = os.path.exists("feedback.csv")
    with open("feedback.csv", "a") as f:
        if not file_exists:
            f.write(header)
        f.write(feedback_line)

    st.success("Thank you for your feedback!")

st.markdown("🔒 This dashboard reads data from Google Sheets and stores feedback locally.")
