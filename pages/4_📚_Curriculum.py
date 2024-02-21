import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Curriculum",
    page_icon="images/PUPLogo.png",
)


class CurriculumManager:
    def __init__(self):
        self.subjects_db = "subjects.db"
        self.rooms_db = "rooms.db"

    def create_subjects_table(self):
        conn = sqlite3.connect(self.subjects_db)
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

    def fetch_programs(self):
        conn = sqlite3.connect("programs.db")
        c = conn.cursor()
        c.execute("SELECT name FROM programs")
        rows = c.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def fetch_sections(self, program_name):
        conn = sqlite3.connect("programs.db")
        c = conn.cursor()
        c.execute("SELECT sections FROM programs WHERE name=?", (program_name,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0].split(",")
        else:
            return []

    def fetch_rooms(self):
        conn = sqlite3.connect(self.rooms_db)
        c = conn.cursor()
        c.execute("SELECT room_name FROM rooms")
        rows = c.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def add_subject_to_db(self, program_name, section, subject_code, subject_name, lec, lab, unit, hours, room):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()
        c.execute("INSERT INTO subjects (program_name, section, subject_code, subject_name, lec, lab, unit, hours, room) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  (program_name, section, subject_code, subject_name, lec, lab, unit, hours, room))
        conn.commit()
        conn.close()
        st.success(f"Subject '{subject_name}' added successfully to program '{program_name}' in section '{section}'")

    def delete_subject(self, program_name, section, subject_name):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()
        c.execute("DELETE FROM subjects WHERE program_name=? AND section=? AND subject_name=?", (program_name, section, subject_name))
        conn.commit()
        conn.close()
        st.success(f"Subject '{subject_name}' deleted successfully from program '{program_name}' in section '{section}'")
        st.experimental_rerun()

    def fetch_subjects(self, program_name, section):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()
        c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room FROM subjects WHERE program_name=? AND section=?", (program_name, section))
        rows = c.fetchall()
        conn.close()
        return rows

    def duplicate_subjects(self, selected_program, source_section, target_sections):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()
        for target_section in target_sections:
            c.execute("INSERT INTO subjects (program_name, section, subject_code, subject_name, lec, lab, unit, hours, room) SELECT program_name, ?, subject_code, subject_name, lec, lab, unit, hours, room FROM subjects WHERE program_name=? AND section=?",
                      (target_section, selected_program, source_section))
        conn.commit()
        conn.close()
        st.success(f"Subjects duplicated from section '{source_section}' to sections: {', '.join(target_sections)}")

# Streamlit UI
def main():

    manager = CurriculumManager()

    # Call the function to create the table before running the Streamlit app
    manager.create_subjects_table()

    st.sidebar.header("Add New Subject")
    selected_program = st.sidebar.selectbox("Select Program", manager.fetch_programs())
    selected_section = st.sidebar.selectbox("Select Section", manager.fetch_sections(selected_program))
    new_subject_code = st.sidebar.text_input("Subject Code")
    new_subject_name = st.sidebar.text_input("Subject Description")
    lec = st.sidebar.number_input("Lecture Hours", value=1)
    lab = st.sidebar.number_input("Lab Hours", value=0)
    unit = st.sidebar.number_input("Units", value=1)
    hours_per_subject = lec + lab
    available_rooms = manager.fetch_rooms()
    room_assignment = st.sidebar.selectbox("Room Assignment", available_rooms)
    
    if st.sidebar.button("Add Subject"):
        manager.add_subject_to_db(selected_program, selected_section, new_subject_code, new_subject_name, lec, lab, unit, hours_per_subject, room_assignment)

    st.header(f"{selected_program} {selected_section} Subjects")
    subjects = manager.fetch_subjects(selected_program, selected_section)
    if subjects:
        subject_df = pd.DataFrame(subjects, columns=["Subject Code", "Subject Description", "Lecture Hours", "Lab Hours", "Units", "Total Hours", "Room"])
        st.table(subject_df)
    else:
        st.write("No subjects found for the selected program and section.")

    # Option to delete a subject
    st.sidebar.header("Delete Subject")
    selected_subject = st.sidebar.selectbox("Select Subject to Delete", [row[1] for row in manager.fetch_subjects(selected_program, selected_section)])  # Selecting subject_name from the fetched subjects
    if st.sidebar.button("Delete Subject"):
        manager.delete_subject(selected_program, selected_section, selected_subject)

    # Option to duplicate subjects
    st.sidebar.header("Duplicate Subjects")
    source_section = st.sidebar.selectbox("Select Source Section", manager.fetch_sections(selected_program))
    target_section = st.sidebar.multiselect("Select Target Section", manager.fetch_sections(selected_program))
    duplicate_button_key = "duplicate_button"  # Unique key for the button
    if st.sidebar.button("Duplicate Subjects", key=duplicate_button_key):
        manager.duplicate_subjects(selected_program, source_section, target_section)

if __name__ == "__main__":
    main()
