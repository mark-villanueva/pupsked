import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Faculty",
    page_icon="images/PUPLogo.png",
)

# Function to create the 'faculty' table in the database
def create_faculty_table():
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY,
            name TEXT,
            subjects TEXT,
            preferred_day TEXT,
            preferred_time TEXT,
            availability_info TEXT
        )
    """)
    conn.commit()
    conn.close()

# Call the function to create the table before running the Streamlit app
create_faculty_table()

# Function to add a new faculty member to the database
def add_faculty_to_db(name, subjects, preferred_day, preferred_time, availability_info):
    # Convert lists to strings
    subjects_str = ', '.join(subjects)
    preferred_day_str = ', '.join(preferred_day)
    preferred_time_str = ', '.join(preferred_time)
    
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("INSERT INTO faculty (name, subjects, preferred_day, preferred_time, availability_info) VALUES (?, ?, ?, ?, ?)", (name, subjects_str, preferred_day_str, preferred_time_str, availability_info))
    conn.commit()
    conn.close()
    st.success(f"Faculty member '{name}' added successfully")

# Function to retrieve subjects from the database
def fetch_subjects():
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_name FROM subjects")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Streamlit UI for faculty registration
def main():
    st.header("Faculty Registration & Availability")

    # Faculty input form
    with st.form("faculty_form"):
        name = st.text_input("Name", placeholder="Type your name (First name MI. Surname)")
        subjects = st.multiselect("Select Subjects", fetch_subjects())
        preferred_day = st.multiselect("Preferred Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        preferred_time = st.multiselect("Preferred Time", ["7:00 AM", "7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM",
                                                           "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM",
                                                           "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM",
                                                           "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM"])
        availability_info = st.text_area("Type here if you have Different Available Time for Different Days",placeholder= "EXAMPLE: Monday-Friday: 5:00 pm - 9:00 pm, Saturday: Wholeday")
        submit_button = st.form_submit_button("Submit")

        # Show confirmation popup
        if submit_button:
            subjects_text = ', '.join(subjects)
            preferred_day_text = ', '.join(preferred_day)
            preferred_time_text = ', '.join(preferred_time)
            st.success(f"Dear {name}, We've taken note of your preferred subjects: {subjects_text}, your available day/s: {preferred_day_text}, and your preferred time: {preferred_time_text}. Additional availability info: {availability_info}. While we will ensure to manage schedules effectively to prevent conflicts with other faculty members, your preferences are duly acknowledged. Thank you, and I wish you a pleasant day ahead!")

    # Handling form submission
    if submit_button:
        add_faculty_to_db(name, subjects, preferred_day, preferred_time, availability_info)

if __name__ == "__main__":
    main()
