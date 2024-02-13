import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Subjects",
    page_icon="images/PUPLogo.png",
)

# Function to create the 'subjects' table in the database
def create_subjects_table():
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY,
            program_name TEXT,
            section TEXT,
            subject_name TEXT,
            hours INTEGER,  -- New column for hours per subject
            room TEXT       -- New column for room assignment
        )
    """)
    conn.commit()
    conn.close()

# Call the function to create the table before running the Streamlit app
create_subjects_table()

# Function to fetch programs from the database
def fetch_programs():
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT name FROM programs")
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

# Function to add a new subject to the database
def add_subject_to_db(program_name, section, subject_name, hours, room):  # Modified to include 'hours' and 'room' parameters
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("INSERT INTO subjects (program_name, section, subject_name, hours, room) VALUES (?, ?, ?, ?, ?)", (program_name, section, subject_name, hours, room))  # Included 'hours' and 'room'
    conn.commit()
    conn.close()
    st.success(f"Subject '{subject_name}' added successfully to program '{program_name}' in section '{section}'")

    # Update available hours after adding subject
    available_hours = calculate_available_hours_for_room(program_name, section, room)
    st.sidebar.text(f"{room} availability: {available_hours} hours")

# Function to delete a subject from the database
def delete_subject(program_name, section, subject_name):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("DELETE FROM subjects WHERE program_name=? AND section=? AND subject_name=?", (program_name, section, subject_name))
    conn.commit()
    conn.close()
    st.success(f"Subject '{subject_name}' deleted successfully from program '{program_name}' in section '{section}'")

# Function to retrieve subjects for a given program and section from the database
def fetch_subjects(program_name, section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_name, hours, room FROM subjects WHERE program_name=? AND section=?", (program_name, section))  # Included 'hours' and 'room'
    rows = c.fetchall()
    conn.close()
    return rows

# Function to duplicate subjects from one section to another within the same program
def duplicate_subjects(selected_program, source_section, target_section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_name, hours, room FROM subjects WHERE program_name=? AND section=?", (selected_program, source_section))  # Included 'hours' and 'room'
    rows = c.fetchall()
    for row in rows:
        subject_name, hours, room = row
        c.execute("INSERT INTO subjects (program_name, section, subject_name, hours, room) VALUES (?, ?, ?, ?, ?)",
                  (selected_program, target_section, subject_name, hours, room))
    conn.commit()
    conn.close()
    st.success(f"Subjects duplicated from section '{source_section}' to section '{target_section}'")

# Function to fetch rooms from the database
def fetch_rooms():
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("SELECT room_name FROM rooms")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def calculate_available_hours_for_room(program_name, section, room):
    available_hours = 84  # Total available hours for each room
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()

    # Fetch and sum hours from duplicated subjects in other sections within the same program and batch
    c.execute("SELECT hours FROM subjects WHERE room=? AND program_name=? AND section!=?", (room, program_name, section))
    duplicated_hours_other_sections = sum(row[0] for row in c.fetchall())  # Sum of hours from duplicated subjects in other sections

    # Fetch and sum hours from duplicated subjects in other programs and batches
    c.execute("SELECT hours FROM subjects WHERE room=? AND program_name!=?", (room, program_name))
    duplicated_hours_other_programs = sum(row[0] for row in c.fetchall())  # Sum of hours from duplicated subjects in other programs

    conn.close()

    available_hours -= duplicated_hours_other_sections  # Subtract hours from other sections within the same program and batch
    available_hours -= duplicated_hours_other_programs  # Subtract hours from other programs and batches

    subjects = fetch_subjects(program_name, section)
    for subject in subjects:
        if subject[2] == room:  # Check if subject's room matches the selected room
            hours = subject[1]  # Get the hours for the subject
            available_hours -= hours  # Subtract subject hours from total available hours
    return available_hours


# Streamlit UI
def main():

    st.sidebar.header("Add New Subject")
    # Program filter
    selected_batch = st.sidebar.selectbox("Select Batch", ["Batch 1", "Batch 2"])

    selected_programs = []
    for program_name in fetch_programs():
        conn = sqlite3.connect("programs.db")
        c = conn.cursor()
        c.execute("SELECT batch FROM programs WHERE name=?", (program_name,))
        row = c.fetchone()
        conn.close()
        if row and row[0] == selected_batch:
            selected_programs.append(program_name)

    selected_program = st.sidebar.selectbox("Select Program", selected_programs)
    selected_section = st.sidebar.selectbox("Select Section", fetch_sections(selected_program))
    new_subject_name = st.sidebar.text_input("Subject Name")

    # Add input for hours per subject
    hours_per_subject = st.sidebar.number_input("Hours Per Subject", value=1)  # Default value is 1

    # Add dropdown for room assignment
    available_rooms = fetch_rooms()
    room_assignment = st.sidebar.selectbox("Room Assignment", available_rooms)
    
    # Calculate and display available hours for the selected room
    available_hours = calculate_available_hours_for_room(selected_program, selected_section, room_assignment)
    st.sidebar.text(f"{room_assignment} availability: {available_hours} hours")

    if st.sidebar.button("Add Subject"):
        add_subject_to_db(selected_program, selected_section, new_subject_name, hours_per_subject, room_assignment)  # Pass hours_per_subject and room_assignment

    # Option to delete a subject
    st.sidebar.header("Delete Subject")
    selected_subject = st.sidebar.selectbox("Select Subject to Delete", [row[0] for row in fetch_subjects(selected_program, selected_section)])  # Only fetching subject_name
    if st.sidebar.button("Delete Subject"):
        delete_subject(selected_program, selected_section, selected_subject)

    # Option to duplicate subjects
    st.sidebar.header("Duplicate Subjects")
    source_section = st.sidebar.selectbox("Select Source Section", fetch_sections(selected_program))
    target_section = st.sidebar.multiselect("Select Target Section", fetch_sections(selected_program))
    duplicate_button_key = "duplicate_button"  # Unique key for the button
    if st.sidebar.button("Duplicate Subjects", key=duplicate_button_key):
        duplicate_subjects(selected_program, source_section, target_section)


    # Display subjects in a table
    st.header(f"{selected_program} {selected_section} Subjects")
    subjects = fetch_subjects(selected_program, selected_section)
    if subjects:
        subject_df = pd.DataFrame(subjects, columns=["Subject Name", "Hours", "Room"])  # Column names for the DataFrame
        st.table(subject_df)
    else:
        st.write("No subjects found for the selected program and section.")

if __name__ == "__main__":
    main()
