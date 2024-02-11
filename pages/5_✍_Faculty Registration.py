import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Faculty",
    page_icon="images/PUPLogo.png",
)

# Function to fetch programs from the database
def fetch_programs(batch):
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT name FROM programs WHERE batch=?", (batch,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Function to fetch sections for a given program from the database
def fetch_sections(program_name):
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT sections FROM programs WHERE name=?", (program_name,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0].split(",")
    else:
        return []

# Function to retrieve subjects and hours for a given program and section from the database
def fetch_subjects_with_hours(program_name, section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_name, hours FROM subjects WHERE program_name=? AND section=?", (program_name, section))
    rows = c.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in rows]

# Function to create the faculty table if it does not exist
def create_faculty_table():
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faculty (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    preferred_day TEXT,
                    preferred_time TEXT,
                    different_time TEXT,
                    batch TEXT,
                    program TEXT,
                    section TEXT,
                    subjects TEXT
                )''')
    conn.commit()
    conn.close()

# Function to save faculty registration to database
def save_faculty_registration(name, preferred_day, preferred_time, different_time, batch, program, section, subjects):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    preferred_day_str = ",".join(preferred_day)
    preferred_time_str = ",".join(preferred_time)
    c.execute("INSERT INTO faculty (name, preferred_day, preferred_time, different_time, batch, program, section, subjects) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (name, preferred_day_str, preferred_time_str, different_time, batch, program, section, ",".join(subjects)))
    conn.commit()
    conn.close()

# Function to retrieve subjects and hours for a given program and section from the database
def fetch_subjects_with_hours(program_name, section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_name, hours FROM subjects WHERE program_name=? AND section=?", (program_name, section))
    rows = c.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in rows]

# Streamlit UI
def main():
    create_faculty_table()  # Create the faculty table if it does not exist
    st.header("Faculty Registration")
    
    # Input fields
    name = st.text_input("Name", placeholder="Type your name (Surname, First name MI.)")
    preferred_day = st.multiselect("Preferred Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    preferred_time = st.multiselect("Preferred Time", ["7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM",
                                                       "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM",
                                                       "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM",
                                                       "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM"])
    different_time = st.text_area("Type here if you have Different Available Time for Different Days",
                                  placeholder="EXAMPLE: Monday-Friday: 5:00 pm - 9:00 pm, Saturday: Wholeday")
    
    # Program filter
    selected_batch = st.selectbox("Select Batch", ["Batch 1", "Batch 2"])
    selected_programs = fetch_programs(selected_batch)
    selected_program = st.selectbox("Select Program", selected_programs)
    
    # Section selection
    selected_sections = st.multiselect("Select Sections", fetch_sections(selected_program))
    
    # Fetch subjects and hours for the selected program and sections
    subjects_with_hours = []
    for section in selected_sections:
        subjects_with_hours.extend(fetch_subjects_with_hours(selected_program, section))

    # Display subjects with hours in the dropdown
    subject_options = {f"{subject} ({hours} hours)": subject for subject, hours in subjects_with_hours}
    selected_subjects = st.multiselect("Select Subjects", list(subject_options.keys()))

    # Button to save registration
    if st.button("Register"):
        save_faculty_registration(name, preferred_day, preferred_time, different_time, selected_batch, selected_program, selected_sections, selected_subjects)
        preferred_day_text = ", ".join(preferred_day)
        preferred_time_text = ", ".join(preferred_time)
        st.success(f"Dear {name}, We've taken note of your available day/s: {preferred_day_text}, and your preferred time: {preferred_time_text}. Additional availability info: {different_time}.Your selected subjects are {selected_subjects} While we will ensure to manage schedules effectively to prevent conflicts with other faculty members, your preferences are duly acknowledged. Thank you, and I wish you a pleasant day ahead!")

if __name__ == "__main__":
    main()
