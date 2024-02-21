import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Manage Schedule",
    page_icon="images/PUPLogo.png",
)

class CurriculumManager:
    def __init__(self):
        self.subjects_db = "subjects.db"

    def fetch_programs(self):
        conn = sqlite3.connect("programs.db")
        c = conn.cursor()
        c.execute("SELECT name FROM programs")
        rows = c.fetchall()
        conn.close()
        return ["All"] + [row[0] for row in rows]

    def fetch_sections(self, program_name):
        conn = sqlite3.connect("programs.db")
        c = conn.cursor()
        if program_name == "All":
            c.execute("SELECT sections FROM programs")
        else:
            c.execute("SELECT sections FROM programs WHERE name=?", (program_name,))
        rows = c.fetchall()
        conn.close()
        all_sections = set()
        for row in rows:
            all_sections.update(row[0].split(","))
        return ["All"] + list(all_sections)

    def fetch_subjects(self, program_name, section):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()
        if program_name == "All" and section == "All":
            c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, faculty, schedules FROM subjects")
        elif program_name == "All":
            c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, faculty, schedules FROM subjects WHERE section=?", (section,))
        elif section == "All":
            c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, faculty, schedules FROM subjects WHERE program_name=?", (program_name,))
        else:
            c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, faculty, schedules FROM subjects WHERE program_name=? AND section=?", (program_name, section))
        rows = c.fetchall()
        conn.close()
        return rows


# Streamlit UI
def main():
    manager = CurriculumManager()

    selected_program = st.selectbox("Select Program", manager.fetch_programs())
    selected_section = st.selectbox("Select Section", manager.fetch_sections(selected_program))

    st.header(f"Subjects")
    subjects = manager.fetch_subjects(selected_program, selected_section)
    if subjects:
        subject_df = pd.DataFrame(subjects, columns=["Subject Code", "Subject Description", "Lecture Hours", "Lab Hours", "Units", "Total Hours", "Room", "Faculty", "Schedules"])
        st.table(subject_df)
    else:
        st.write("No subjects found for the selected program and section.")

if __name__ == "__main__":
    main()





