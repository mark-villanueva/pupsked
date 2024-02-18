import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Curriculum",
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
            subject_code TEXT,  -- New column for subject code
            subject_name TEXT,
            lec INTEGER,  -- New column for lecture hours
            lab INTEGER,  -- New column for lab hours
            unit INTEGER,  -- New column for units
            hours INTEGER,
            room TEXT
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
def add_subject_to_db(program_name, section, subject_code, subject_name, lec, lab, unit, hours):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("INSERT INTO subjects (program_name, section, subject_code, subject_name, lec, lab, unit, hours) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
              (program_name, section, subject_code, subject_name, lec, lab, unit, hours))
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
    st.rerun()

# Function to retrieve subjects for a given program and section from the database
def fetch_subjects(program_name, section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours FROM subjects WHERE program_name=? AND section=?", (program_name, section))
    rows = c.fetchall()
    conn.close()
    return rows

# Function to duplicate subjects from one section to another within the same program
def duplicate_subjects(selected_program, source_section, target_sections):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    for target_section in target_sections:
        c.execute("INSERT INTO subjects (program_name, section, subject_code, subject_name, lec, lab, unit, hours) SELECT program_name, ?, subject_code, subject_name, lec, lab, unit, hours FROM subjects WHERE program_name=? AND section=?",
                  (target_section, selected_program, source_section))
    conn.commit()
    conn.close()
    st.success(f"Subjects duplicated from section '{source_section}' to sections: {', '.join(target_sections)}")


# Streamlit UI
def main():
    st.sidebar.header("Add New Subject")
    selected_program = st.sidebar.selectbox("Select Program", fetch_programs())
    selected_section = st.sidebar.selectbox("Select Section", fetch_sections(selected_program))
    new_subject_code = st.sidebar.text_input("Subject Code")
    new_subject_name = st.sidebar.text_input("Subject Description")
    lec = st.sidebar.number_input("Lecture Hours", value=1)
    lab = st.sidebar.number_input("Lab Hours", value=0)
    unit = st.sidebar.number_input("Units", value=1)
    hours_per_subject = lec + lab
    
    if st.sidebar.button("Add Subject"):
        add_subject_to_db(selected_program, selected_section, new_subject_code, new_subject_name, lec, lab, unit, hours_per_subject)

    st.header(f"{selected_program} {selected_section} Subjects")
    subjects = fetch_subjects(selected_program, selected_section)
    if subjects:
        subject_df = pd.DataFrame(subjects, columns=["Subject Code", "Subject Description", "Lecture Hours", "Lab Hours", "Units", "Total Hours"])
        st.table(subject_df)
    else:
        st.write("No subjects found for the selected program and section.")

    # Option to delete a subject
    st.sidebar.header("Delete Subject")
    selected_subject = st.sidebar.selectbox("Select Subject to Delete", [row[1] for row in fetch_subjects(selected_program, selected_section)])  # Selecting subject_name from the fetched subjects
    if st.sidebar.button("Delete Subject"):
        delete_subject(selected_program, selected_section, selected_subject)

    # Option to duplicate subjects
    st.sidebar.header("Duplicate Subjects")
    source_section = st.sidebar.selectbox("Select Source Section", fetch_sections(selected_program))
    target_section = st.sidebar.multiselect("Select Target Section", fetch_sections(selected_program))
    duplicate_button_key = "duplicate_button"  # Unique key for the button
    if st.sidebar.button("Duplicate Subjects", key=duplicate_button_key):
        duplicate_subjects(selected_program, source_section, target_section)

if __name__ == "__main__":
    main()
