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
                    batch TEXT,
                    program TEXT,
                    section TEXT,
                    subjects TEXT,
                    notes TEXT
                )''')
    conn.commit()
    conn.close()

# Function to save faculty registration to database
def save_faculty_registration(name, preferred_day, preferred_time, notes, batch, program, selected_sections, subjects):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    preferred_day_str = ",".join(preferred_day)
    preferred_time_str = ",".join(preferred_time)
    selected_sections_str = ",".join(selected_sections)  # Convert selected_sections list to string
    c.execute("INSERT INTO faculty (name, preferred_day, preferred_time, notes, batch, program, section, subjects) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (name, preferred_day_str, preferred_time_str, notes, batch, program, selected_sections_str, ",".join(subjects)))
    conn.commit()
    conn.close()

# Streamlit UI
def main():
    create_faculty_table()  # Create the faculty table if it does not exist
    st.header("Faculty Registration")
    
    # Input fields
    name = st.text_input("Name", placeholder="Type your name (Surname, First name MI.)")
    preferred_day = st.multiselect("Preferred Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    
    preferred_time_option = None
    if preferred_day:
        preferred_time_option = st.selectbox("Time for Selected Day/s", ["Same Time", "Varied Time"])

    if preferred_time_option == "Same Time":
        preferred_time = st.multiselect("Preferred Time", ["7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM",
                                                           "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM",
                                                           "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM",
                                                           "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM"])
    else:
        preferred_time = None
        if preferred_day:
            preferred_time_per_day = {}
            for day in preferred_day:
                preferred_time_per_day[day] = st.multiselect(f"Preferred Time for {day}", ["7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM",
                                                                                           "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM",
                                                                                           "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM",
                                                                                           "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM"])
    
    
    # Program filter
    selected_batches = st.multiselect("Select Batch", ["Batch 1", "Batch 2"])
    selected_programs = []
    for batch in selected_batches:
        selected_programs.extend(fetch_programs(batch))
    selected_programs = list(set(selected_programs))  # Remove duplicates
    selected_program = st.multiselect("Select Program", selected_programs)
    
    # Section selection
    selected_sections = []
    for program in selected_program:
        selected_sections.extend(st.multiselect(f"Select Sections for {program}", fetch_sections(program)))
    selected_sections = list(set(selected_sections))  # Remove duplicates
    
    # Fetch subjects and hours for the selected program and sections
    subjects_with_hours = []
    for section in selected_sections:
        for program in selected_program:
            subjects_with_hours.extend(fetch_subjects_with_hours(program, section))

    # Display subjects with hours in the dropdown
    subject_options = {f"{subject} ({hours} hours)": subject for subject, hours in subjects_with_hours}
    selected_subjects = st.multiselect("Select Subjects", list(subject_options.keys()))


    #Notes text area
    notes = st.text_area("Type here if you have additional notes for your schedule",
                                  placeholder="Hello there!. Your unique scheduling preferences will be duly noted and accommodated. Many thanks for your cooperation!")

    # Button to save registration
    if st.button("Register"):
        if name and preferred_day and selected_batches and selected_programs and selected_sections and selected_subjects:
            if preferred_time_option == "Same Time":
                preferred_time_text = ", ".join(preferred_time)
            else:
                preferred_time_text = ", ".join([f"{day}: {', '.join(preferred_time_per_day[day])}" for day in preferred_day])
            
            save_faculty_registration(name, preferred_day, preferred_time,notes, selected_batches, selected_programs, selected_sections, selected_subjects)
            preferred_day_text = ", ".join(preferred_day)
            st.success(f"Dear {name}, We've taken note of your available day/s: {preferred_day_text}, and your preferred time: {preferred_time_text}. Your notes: {notes}. Your selected subjects are {selected_subjects} While we will ensure to manage schedules effectively to prevent conflicts with other faculty members, your preferences are duly acknowledged. Thank you, and I wish you a pleasant day ahead!")
        else:
            st.warning("Please fill in all required fields.")


if __name__ == "__main__":
    main()
