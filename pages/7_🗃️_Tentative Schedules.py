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

# Function to fetch sections from the database
def fetch_sections():
    sections = set()
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT sections FROM programs")
    rows = c.fetchall()
    conn.close()
    for row in rows:
        sections.update(row[0].split(","))
    return list(sections)

# Function to delete a registration from the database
def delete_registration(name):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("DELETE FROM faculty WHERE name=?", (name,))
    conn.commit()
    conn.close()

# Streamlit UI for displaying responses
def display_responses(selected_faculty, selected_section):
    st.header("Faculty Registrations")
    
    # Fetch registrations
    registrations = fetch_registrations()
    
    if registrations:
        # Filter registrations by selected faculty name
        if selected_faculty:
            registrations = [row for row in registrations if row[1] == selected_faculty]

        # Filter registrations by selected section
        if selected_section:
            registrations = [row for row in registrations if row[6] == selected_section]

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

def main():
    st.header("Faculty Data Filters")

    # Dropdown to select faculty name for filtering
    faculty_names = [row[1] for row in fetch_registrations()]
    selected_faculty = st.selectbox("Select Faculty Name", [""] + faculty_names)

    # Dropdown to select section for filtering
    sections = fetch_sections()
    selected_section = st.selectbox("Select Section", [""] + sections)

    # Display the filtered table
    display_responses(selected_faculty, selected_section)

if __name__ == "__main__":
    main()
