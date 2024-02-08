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
            hours INTEGER  -- New column for hours per subject
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
def add_subject_to_db(program_name, section, subject_name, hours):  # Modified to include 'hours' parameter
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("INSERT INTO subjects (program_name, section, subject_name, hours) VALUES (?, ?, ?, ?)", (program_name, section, subject_name, hours))  # Included 'hours'
    conn.commit()
    conn.close()
    st.success(f"Subject '{subject_name}' added successfully to program '{program_name}' in section '{section}'")

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
    c.execute("SELECT subject_name, hours FROM subjects WHERE program_name=? AND section=?", (program_name, section))  # Included 'hours'
    rows = c.fetchall()
    conn.close()
    return rows

# Function to duplicate subjects from one section to another within the same program
def duplicate_subjects(selected_program, source_section, target_section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_name, hours FROM subjects WHERE program_name=? AND section=?", (selected_program, source_section))
    rows = c.fetchall()
    for row in rows:
        subject_name, hours = row
        c.execute("INSERT INTO subjects (program_name, section, subject_name, hours) VALUES (?, ?, ?, ?)",
                  (selected_program, target_section, subject_name, hours))
    conn.commit()
    conn.close()
    st.success(f"Subjects duplicated from section '{source_section}' to section '{target_section}'")


# Streamlit UI
def main():

    st.sidebar.header("Add New Subject")
    selected_program = st.sidebar.selectbox("Select Program", fetch_programs())
    selected_section = st.sidebar.selectbox("Select Section", fetch_sections(selected_program))
    new_subject_name = st.sidebar.text_input("Subject Name")

    # Add input for hours per subject
    hours_per_subject = st.sidebar.number_input("Hours Per Subject", value=1)  # Default value is 1

    if st.sidebar.button("Add Subject"):
        add_subject_to_db(selected_program, selected_section, new_subject_name, hours_per_subject)  # Pass hours_per_subject

    # Option to delete a subject
    st.sidebar.header("Delete Subject")
    selected_subject = st.sidebar.selectbox("Select Subject to Delete", [row[0] for row in fetch_subjects(selected_program, selected_section)])  # Only fetching subject_name
    if st.sidebar.button("Delete Subject"):
        delete_subject(selected_program, selected_section, selected_subject)

    # Option to duplicate subjects
    st.sidebar.header("Duplicate Subjects")
    source_section = st.sidebar.selectbox("Select Source Section", fetch_sections(selected_program))
    target_section = st.sidebar.selectbox("Select Target Section", fetch_sections(selected_program))
    if st.sidebar.button("Duplicate Subjects"):
        duplicate_subjects(selected_program, source_section, target_section)

    # Display subjects in a table
    st.header(f"{selected_program} {selected_section} Subjects")
    subjects = fetch_subjects(selected_program, selected_section)
    if subjects:
        subject_df = pd.DataFrame(subjects, columns=["Subject Name", "Hours"])  # Column names for the DataFrame
        st.table(subject_df)
    else:
        st.write("No subjects found for the selected program and section.")

if __name__ == "__main__":
    main()
