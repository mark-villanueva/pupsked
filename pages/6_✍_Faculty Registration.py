import streamlit as st
import sqlite3

# Set Streamlit page configuration
st.set_page_config(
    page_title="Faculty Registration",
    page_icon="images/PUPLogo.png",
)

# Function to create database connection
def create_connection():
    conn = sqlite3.connect("faculty_registration.db")
    return conn

## Function to create the registrations table
def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            batches TEXT,
                            program_section TEXT,  -- Add program_section column
                            subjects TEXT,
                            preferences TEXT,
                            notes TEXT
                          )''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)

# Function to insert faculty registration data into the database
def insert_registration(conn, name, selected_batches, program_sections, selected_subjects, subject_preferences, notes):
    try:
        cursor = conn.cursor()
        
        # Insert faculty registration data into the 'registrations' table
        cursor.execute('''INSERT INTO registrations (name, batches, program_section, subjects, preferences, notes) 
                          VALUES (?, ?, ?, ?, ?, ?)''', (name, ", ".join(selected_batches), ", ".join(program_sections), 
                                                         ", ".join(selected_subjects), str(subject_preferences), notes))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(e)  # Print the error message to the console for debugging
        return False


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

# Function to retrieve previously saved subjects for a given program, section, and batch from the database
def fetch_saved_subjects(batch, program, section):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT subjects FROM registrations WHERE batches=? AND program_section=?",
              (batch, f"{program} ({section})"))
    rows = c.fetchall()
    conn.close()
    saved_subjects = []
    for row in rows:
        saved_subjects.extend(row[0].split(", "))
    return saved_subjects

# Modify the function to fetch subjects for a given program, section, and batch from the database
def fetch_subjects(program_name, section, batch, selected_subjects):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_code, subject_name FROM subjects WHERE program_name=? AND section=?", (program_name, section))
    rows = c.fetchall()
    conn.close()

    # Extract available subjects from the database rows
    available_subjects = [(f"{code} - {name}") for code, name in rows]

    # Fetch previously saved subjects for the selected faculty
    saved_subjects = set()
    for batch_data in selected_subjects.values():
        for program_data in batch_data.values():
            for section_data in program_data.values():
                saved_subjects.update(section_data)

    # Extract subject codes from the saved subjects
    saved_subject_codes = set([subject.split(" - ")[0] for subject in saved_subjects])

    # Exclude already saved subject codes from available subjects
    available_subjects = [subject for subject in available_subjects if subject.split(" - ")[0] not in saved_subject_codes]

    return available_subjects




# Streamlit UI
def main():
    conn = create_connection()
    create_table(conn)
    
    st.header("Faculty Registration")
    
    # Input fields
    name = st.text_input("Name", placeholder="Type your name")
    
    selected_batches = st.multiselect("Select Batch", ["Batch 1", "Batch 2"])

    program_sections = {}

    # Collect program and section selections for each batch
    for batch in selected_batches:
        selected_programs = st.multiselect(f"Select Program for {batch}", fetch_programs(batch))
        program_sections[batch] = {}
        for program in selected_programs:
            sections = fetch_sections(program)
            selected_sections = st.multiselect(f"Select Sections for {program} in {batch}", sections)
            program_sections[batch][program] = selected_sections

    # Initialize selected_subjects as a dictionary
    selected_subjects = {}

    # Fetch subjects for the selected program and sections
    for batch, programs in program_sections.items():
        selected_subjects[batch] = {}
        for program, sections in programs.items():
            selected_subjects[batch][program] = {}
            for section in sections:
                # Fetch subjects for the current program, section, and batch
                subjects = fetch_subjects(program, section, batch, selected_subjects[batch][program])


                selected_subjects[batch][program][section] = st.multiselect(f"Select Subjects for {program} in {batch} ({section})", subjects, key=f"{batch}-{program}-{section}")


    # Preferences and notes
    subject_preferences = {}
    for batch, programs in selected_subjects.items():
        subject_preferences[batch] = {}
        for program, sections in programs.items():
            subject_preferences[batch][program] = {}
            for section, subjects in sections.items():
                subject_preferences[batch][program][section] = {}
                for subject in subjects:
                    preferred_day = st.multiselect(f"Preferred Day for {subject}", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
                    preferred_time = st.multiselect(f"Preferred Time for {subject}", 
                                                    ["7:30 AM - 8:00 AM", "8:00 AM - 8:30 AM", "8:30 AM - 9:00 AM",
                                                    "9:00 AM - 9:30 AM", "9:30 AM - 10:00 AM", "10:00 AM - 10:30 AM",
                                                    "10:30 AM - 11:00 AM", "11:00 AM - 11:30 AM", "11:30 AM - 12:00 PM",
                                                    "12:00 PM - 12:30 PM", "12:30 PM - 1:00 PM", "1:00 PM - 1:30 PM",
                                                    "1:30 PM - 2:00 PM", "2:00 PM - 2:30 PM", "2:30 PM - 3:00 PM", 
                                                    "3:00 PM - 3:30 PM", "3:30 PM - 4:00 PM", "4:00 PM - 4:30 PM", 
                                                    "4:30 PM - 5:00 PM", "5:00 PM - 5:30 PM", "5:30 PM - 6:00 PM",
                                                    "6:00 PM - 6:30 PM", "6:30 PM - 7:00 PM", "7:00 PM - 7:30 PM",
                                                    "7:30 PM - 8:00 PM", "8:00 PM - 8:30 PM", "8:30 PM - 9:00 PM"])
                    subject_preferences[batch][program][section][subject] = (preferred_day, preferred_time)

    notes = st.text_area("Type Here Your General Day & Time of Availability",
                                  placeholder="Ex: Monday - Friday: 5:00 PM - 8:00 PM, Saturday: Wholeday")

    # Save button
    if st.button("Register"):
        selected_program_sections = []
        for batch, programs in program_sections.items():
            for program, sections in programs.items():
                for section in sections:
                    selected_program_sections.append(f"{program} ({section})")
                    for subject, preferences in subject_preferences[batch][program][section].items():
                        preferred_days = preferences[0]  # Extracting preferred days from preferences
                        st.success(f"Dear {name},\n\nWe've taken note of your preferred days: {preferred_days},\n\nYour preferred time: {preferred_time}.\n\nYour notes: {notes}.\n\nYour selected program: {program}, sections: {section}\n\nSelected subject is {subject}.\n\nWhile we will ensure to manage schedules effectively to prevent conflicts with other faculty members, your preferences are duly acknowledged.\n\nThank you, and I wish you a pleasant day ahead!")
        if insert_registration(conn, name, selected_batches, selected_program_sections, selected_subjects, subject_preferences, notes):
            st.success("Faculty registration saved successfully!")
        else:
            st.error("An error occurred while saving faculty registration.")
        conn.close()

if __name__ == "__main__":
    main()

