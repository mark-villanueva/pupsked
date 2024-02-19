import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="Manage Schedules",
    page_icon="images/PUPLogo.png",
)


# Function to fetch programs from the database
def fetch_programs():
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT name FROM programs")
    rows = c.fetchall()
    conn.close()
    return ["All"] + [row[0] for row in rows]

# Function to fetch sections for a given program from the database
def fetch_sections(program_name):
    if program_name == "All":
        return ["All"]
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT sections FROM programs WHERE name=?", (program_name,))
    row = c.fetchone()
    conn.close()
    if row:
        return ["All"] + row[0].split(",")
    else:
        return []

# Function to retrieve subjects for a given program and section from the database
def fetch_subjects(program_name, section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    if program_name == "All" or section == "All":
        c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, program_name, section FROM subjects")
    else:
        c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, program_name, section FROM subjects WHERE program_name=? AND section=?", (program_name, section))
    rows = c.fetchall()
    conn.close()
    return rows



# Fetch programs from the database
programs = fetch_programs()

# Display dropdown to select program
selected_program = st.selectbox("Select Program", programs)

# Fetch sections based on the selected program
sections = fetch_sections(selected_program)

# Display dropdown to select section
selected_section = st.selectbox("Select Section", sections)

# Fetch subjects based on the selected program and section
subjects = fetch_subjects(selected_program, selected_section)

# Create a DataFrame for subjects
subjects_df = pd.DataFrame(subjects, columns=["Subject Code", "Subject Name", "Lecture", "Lab", "Unit", "Hours", "Room", "Program", "Section"])

# Add new columns "Faculty" and "Schedules" to the DataFrame
subjects_df["Faculty"] = ""
subjects_df["Schedules"] = ""

# Filter subjects by room
available_rooms = subjects_df["Room"].unique()
selected_room = st.selectbox("Filter by Room", ["All"] + list(available_rooms))
if selected_room != "All":
    subjects_df = subjects_df[subjects_df["Room"] == selected_room]

# Display the combined table
st.write("Schedules:")
# Set larger width for the table
st.write(subjects_df.style.set_table_styles([dict(selector='table', props=[('width', '100%')])]))








