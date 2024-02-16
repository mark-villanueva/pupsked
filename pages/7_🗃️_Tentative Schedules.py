import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="Faculty Data",
    page_icon="images/PUPLogo.png",
)

# Function to fetch registrations from the database
def fetch_registrations():
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("SELECT * FROM faculty")
    rows = c.fetchall()
    conn.close()
    return rows

# Function to fetch rooms from the database
def fetch_rooms():
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("SELECT room_name FROM rooms")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

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

def save_faculty_registration(name, preferred_day, preferred_time, notes, selected_batches, selected_programs, selected_sections, selected_subjects):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    preferred_day_str = ",".join(preferred_day) if preferred_day else ""
    preferred_time_str = ",".join(preferred_time) if preferred_time else ""
    selected_batches_str = ",".join(selected_batches) if selected_batches else ""
    selected_programs_str = ",".join(selected_programs) if selected_programs else ""
    selected_sections_str = ",".join(selected_sections) if selected_sections else ""
    selected_subjects_str = ",".join(selected_subjects) if selected_subjects else ""
    
    # Assign rooms to subjects
    room_assignments = {}
    for program, section, subject in zip(selected_programs, selected_sections, selected_subjects):
        rooms = fetch_rooms()  # Fetch available rooms
        if rooms:
            room = rooms.pop(0)  # Assign the first available room
            room_assignments[subject] = room
        else:
            room_assignments[subject] = "No room available"
    
    # Convert room assignments to a string
    room_assignments_str = ",".join([f"{subject}: {room}" for subject, room in room_assignments.items()])

    c.execute("INSERT INTO faculty (name, preferred_day, preferred_time, notes, batch, program, section, subjects, room_assignment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (name, preferred_day_str, preferred_time_str, notes, selected_batches_str, selected_programs_str, selected_sections_str, selected_subjects_str, room_assignments_str))
    
    conn.commit()
    conn.close()


# Streamlit UI for displaying responses
def display_responses(selected_faculty):
    
    # Fetch registrations
    registrations = fetch_registrations()
    
    if registrations:
        # Filter registrations by selected faculty name
        if selected_faculty:
            registrations = [row for row in registrations if row[1] == selected_faculty]

        # Create a DataFrame to hold the schedule
        columns = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        rows = [
            "7:00 AM - 7:30 AM", "7:30 AM - 8:00 AM", "8:00 AM - 8:30 AM", "8:30 AM - 9:00 AM",
            "9:00 AM - 9:30 AM", "9:30 AM - 10:00 AM", "10:00 AM - 10:30 AM",
            "10:30 AM - 11:00 AM", "11:00 AM - 11:30 AM", "11:30 AM - 12:00 PM",
            "12:00 PM - 12:30 PM", "12:30 PM - 1:00 PM", "1:00 PM - 1:30 PM",
            "1:30 PM - 2:00 PM", "2:00 PM - 2:30 PM", "2:30 PM - 3:00 PM", 
            "3:00 PM - 3:30 PM", "3:30 PM - 4:00 PM", "4:00 PM - 4:30 PM", 
            "4:30 PM - 5:00 PM", "5:00 PM - 5:30 PM", "5:30 PM - 6:00 PM",
            "6:00 PM - 6:30 PM", "6:30 PM - 7:00 PM", "7:00 PM - 7:30 PM",
            "7:30 PM - 8:00 PM", "8:00 PM - 8:30 PM", "8:30 PM - 9:00 PM" 
        ]
        faculty_schedule = pd.DataFrame(index=rows, columns=columns)
        
        # Populate the schedule
        for row in registrations:
            preferred_day = row[2]
            preferred_time = row[3]
            program = row[5]
            section = row[6]
            subject = row[7]
            # Split the preferred_time to get the start and end time
            preferred_times = preferred_time.split(',')
            for pt in preferred_times:
                # Assign the registration to the corresponding time slot and day
                faculty_schedule.loc[pt.strip(), preferred_day] = f"{program} {section}\n{subject}"
        
        # Display the schedule
        st.write(faculty_schedule)
        
    else:
        st.write("No registrations yet.")

# Function to fetch rooms from the database
def fetch_rooms():
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("SELECT room_name FROM rooms")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def main():
    create_faculty_table()  # Create the faculty table if it does not exist

    st.header("Tentative Schedules")

    # Dropdown to select faculty name for filtering
    faculty_names = [row[1] for row in fetch_registrations()]
    selected_faculty = st.selectbox("Select Faculty Name", [""] + faculty_names)

    # Display the filtered table
    display_responses(selected_faculty)

    

if __name__ == "__main__":
    main()
