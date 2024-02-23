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
                subject_code TEXT,
                subject_name TEXT,
                lec INTEGER,
                lab INTEGER,
                unit INTEGER,
                hours INTEGER,
                room TEXT,
                faculty_member TEXT,  
                preferred_days TEXT,      
                preferred_times TEXT,
                notes TEXT            
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
    
    st.cache_data
    def add_subject_to_db(self, program_name, section, subject_code, subject_name, lec, lab, unit, hours, room, faculty_member=None, preferred_days=None, preferred_times=None, notes=None):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()

        # Check if the subject already exists in the database
        c.execute("SELECT * FROM subjects WHERE subject_code = ? AND program_name = ? AND section = ?", 
                (subject_code, program_name, section))
        existing_subject = c.fetchone()
        
        if existing_subject:
            # Update the existing subject with new information
            c.execute("UPDATE subjects SET subject_name = ?, lec = ?, lab = ?, unit = ?, hours = ?, room = ?, faculty_member = ?, preferred_days = ?, preferred_times = ?, notes = ? WHERE id = ?", 
                    (subject_name, lec, lab, unit, hours, room, faculty_member, preferred_days, preferred_times, notes, existing_subject[0]))
            st.success(f"Faculty: {faculty_member} added successfully to {subject_name} in {program_name} {section}")
        else:
            # Insert a new subject into the database
            c.execute("INSERT INTO subjects (program_name, section, subject_code, subject_name, lec, lab, unit, hours, room, faculty_member, preferred_days, preferred_times, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (program_name, section, subject_code, subject_name, lec, lab, unit, hours, room, faculty_member, preferred_days, preferred_times, notes))
            st.success(f"Subject {subject_name} added successfully to program {program_name} in section {section}")

        conn.commit()
        conn.close()



    st.cache_data
    def delete_subject(self, program_name, section, subject_name):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()
        c.execute("DELETE FROM subjects WHERE program_name=? AND section=? AND subject_name=?", (program_name, section, subject_name))
        conn.commit()
        conn.close()
        st.success(f"Subject '{subject_name}' deleted successfully from program '{program_name}' in section '{section}'")
        
    st.cache_data
    def fetch_subjects(self, program_name, section):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()
        c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, faculty_member, preferred_days, preferred_times, notes FROM subjects WHERE program_name=? AND section=?", (program_name, section))
        rows = c.fetchall()
        conn.close()
        return rows

    st.cache_data
    def duplicate_subjects(self, selected_program, source_section, target_sections):
        conn = sqlite3.connect(self.subjects_db)
        c = conn.cursor()
        for target_section in target_sections:
            c.execute("INSERT INTO subjects (program_name, section, subject_code, subject_name, lec, lab, unit, hours, room) SELECT program_name, ?, subject_code, subject_name, lec, lab, unit, hours, room FROM subjects WHERE program_name=? AND section=?",
                      (target_section, selected_program, source_section))
        conn.commit()
        conn.close()
        st.success(f"Subjects duplicated from section '{source_section}' to sections: {', '.join(target_sections)}")

   
    # Function to retrieve faculty members from the database
    st.cache_data
    def fetch_faculty(self):
        conn = sqlite3.connect("faculty.db")
        c = conn.cursor()
        c.execute("SELECT faculty_name FROM faculty")
        rows = c.fetchall()
        conn.close()
        return [row[0] for row in rows]
    
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
        manager.add_subject_to_db(selected_program, selected_section, new_subject_code, new_subject_name, lec, lab, unit, hours_per_subject, room_assignment, None, None, None, None)


    st.header(f"{selected_program} {selected_section} Subjects")
    subjects = manager.fetch_subjects(selected_program, selected_section)
    if subjects:
        subject_df = pd.DataFrame(subjects, columns=["Subject Code", "Subject Description", "Lecture Hours", "Lab Hours", "Units", "Total Hours", "Room", "Faculty Member", "Preferred Day", "Preferred Time", "Notes"])
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


# Input fields faculty preference
    st.subheader("Assign Faculty to Subjects")
    faculty_names = manager.fetch_faculty()
    selected_faculty_name = st.selectbox("Faculty Name", faculty_names, placeholder="Type your name")

    # Dropdown to select program
    selected_program_for_faculty = st.selectbox("Select Program", manager.fetch_programs(), key="program_select")

    # Dropdown to select section
    selected_section_for_faculty = st.selectbox("Select Section", manager.fetch_sections(selected_program_for_faculty), key="section_select")

    # Dropdown to select subject
    selected_subjects_for_faculty = [row[1] for row in manager.fetch_subjects(selected_program_for_faculty, selected_section_for_faculty)]
    selected_subject_for_faculty = st.selectbox("Select Subject", selected_subjects_for_faculty, key="subject_select")

    # Multiselect to select preferred day for the subject
    preferred_days = st.selectbox(f"Preferred Day for {selected_subject_for_faculty}", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])

    # Multiselect to select preferred time for the subject
    preferred_times = st.multiselect(f"Preferred Time for {selected_subject_for_faculty}", 
                                    ["7:30 AM - 8:00 AM", "8:00 AM - 8:30 AM", "8:30 AM - 9:00 AM",
                                    "9:00 AM - 9:30 AM", "9:30 AM - 10:00 AM", "10:00 AM - 10:30 AM",
                                    "10:30 AM - 11:00 AM", "11:00 AM - 11:30 AM", "11:30 AM - 12:00 PM",
                                    "12:00 PM - 12:30 PM", "12:30 PM - 1:00 PM", "1:00 PM - 1:30 PM",
                                    "1:30 PM - 2:00 PM", "2:00 PM - 2:30 PM", "2:30 PM - 3:00 PM", 
                                    "3:00 PM - 3:30 PM", "3:30 PM - 4:00 PM", "4:00 PM - 4:30 PM", 
                                    "4:30 PM - 5:00 PM", "5:00 PM - 5:30 PM", "5:30 PM - 6:00 PM",
                                    "6:00 PM - 6:30 PM", "6:30 PM - 7:00 PM", "7:00 PM - 7:30 PM",
                                    "7:30 PM - 8:00 PM", "8:00 PM - 8:30 PM", "8:30 PM - 9:00 PM"])

    notes = st.text_area("Type Here Your General Day & Time of Availability and Special Requests",
                                placeholder="Ex: Monday - Friday: 5:00 PM - 8:00 PM, Saturday: Wholeday")

    # Button to add preferences for the selected faculty
    if st.button("Add Preferences"):
        # Convert preferred_days to string
        preferred_days_str = str(preferred_days)
        # Convert preferred_times list to string
        preferred_times_str = ", ".join(preferred_times) if preferred_times else None

        # Retrieve other subject details from the database based on the selected subject
        subject_details = manager.fetch_subjects(selected_program_for_faculty, selected_section_for_faculty)
        # Find the selected subject details
        selected_subject_details = next((subject for subject in subject_details if subject[1] == selected_subject_for_faculty), None)
        if selected_subject_details:
            # Extracting required details from the selected subject
            subject_code = selected_subject_details[0]
            subject_name = selected_subject_details[1]
            lec = selected_subject_details[2]
            lab = selected_subject_details[3]
            unit = selected_subject_details[4]
            hours = selected_subject_details[5]
            room = selected_subject_details[6]
            # Call the method to add preferences to the database
            manager.add_subject_to_db(selected_program_for_faculty, selected_section_for_faculty, subject_code, subject_name, lec, lab, unit, hours, room, selected_faculty_name, preferred_days_str, preferred_times_str, notes)
          



if __name__ == "__main__":
    main()
