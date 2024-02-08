import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Create Schedule",
    page_icon="images/PUPLogo.png",
)

st.header("Create Schedule")

# Function to fetch programs from the database
def fetch_programs():
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT name FROM programs")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Function to retrieve sections for a given program
def get_sections(program_name):
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT sections FROM programs WHERE name=?", (program_name,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0].split(",")
    else:
        return []

# Program filter
selected_program = st.selectbox("Select Program", fetch_programs())

# Display sections for selected program
if selected_program:
    st.write(f"Sections for {selected_program}:")
    sections = get_sections(selected_program)
    if sections:
        selected_section = st.selectbox("Sections", sections, index=0)  # Define selected_section here

        # Function to retrieve subjects for a given program and section from the database
        def fetch_subjects(program_name, section):
            conn = sqlite3.connect("subjects.db")
            c = conn.cursor()
            c.execute("SELECT subject_name FROM subjects WHERE program_name=? AND section=?", (program_name, section))
            rows = c.fetchall()
            conn.close()
            return [row[0] for row in rows]

        # Display subjects in a dropdown
        st.write(f"{selected_program} {selected_section} Subjects:")
        subjects = fetch_subjects(selected_program, selected_section)
        if subjects:
            selected_subject = st.selectbox("Subjects", subjects)
        else:
            st.write("No subjects found for the selected program and section.")
    else:
        st.write("No sections found for the selected program.")

# Function to retrieve rooms from the database
def fetch_rooms():
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("SELECT room_name FROM rooms")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Display rooms in a dropdown
st.write("Available Rooms:")
rooms_data = fetch_rooms()
if rooms_data:
    selected_room = st.selectbox("Rooms", rooms_data)
else:
    st.write("No rooms found.")

# Function to retrieve faculty names from the database
def fetch_faculty_names():
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("SELECT name FROM faculty")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Function to fetch faculty details by name
def fetch_faculty_details(name):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("SELECT subjects, preferred_day, preferred_time, availability_info FROM faculty WHERE name=?", (name,))
    row = c.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None

# Faculty selection dropdown
selected_faculty_name = st.selectbox("Select Faculty Name", fetch_faculty_names())

# Display faculty details
if selected_faculty_name:
    faculty_details = fetch_faculty_details(selected_faculty_name)
    if faculty_details:
        subjects, preferred_days, preferred_times, availability_info = faculty_details

        st.markdown("###### Selected Subjects:")
        for subject in subjects.split(","):
            st.write(subject.strip())

        st.markdown("###### Preferred Days:")
        st.write(", ".join(preferred_days.split(",")))

        st.markdown("###### Preferred Times:")
        st.write(", ".join(preferred_times.split(",")))

        st.markdown("###### Other Availability Info:")
        st.write(availability_info.strip())

        # Display timetable or any other visualization here
    else:
        st.write("No details found for the selected faculty.")


preferred_day = st.multiselect("Set Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
preferred_time = st.multiselect("Set Time", ["7:00 AM", "7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM",
                                                           "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM",
                                                           "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM",
                                                           "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM"])
