import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="Manage Schedules",
    page_icon="images/PUPLogo.png",
)

# Function to fetch programs from the database
def fetch_programs():
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT name FROM programs")
    rows = c.fetchall()
    conn.close()
    return ["All"] + [row[0] for row in rows]

# Function to fetch sections for a given program from the database
def fetch_sections(program_name):
    if program_name == "All":
        return ["All"]
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT sections FROM programs WHERE name=?", (program_name,))
    row = c.fetchone()
    conn.close()
    if row:
        return ["All"] + row[0].split(",")
    else:
        return []

import pandas as pd

# Function to retrieve subjects for a given program and section from the database
def fetch_subjects(program_name, section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    if program_name == "All" or section == "All":
        c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, program_name, section FROM subjects")
    else:
        c.execute("SELECT subject_code, subject_name, lec, lab, unit, hours, room, program_name, section FROM subjects WHERE program_name=? AND section=?", (program_name, section))
    rows = c.fetchall()
    
    # Fetch faculty data
    faculty_conn = sqlite3.connect("faculty_registration.db")
    faculty_cursor = faculty_conn.cursor()
    
    # Create a DataFrame to hold the subjects data
    subjects_df = pd.DataFrame(rows, columns=["Subject Code", "Subject Name", "Lecture", "Lab", "Unit", "Hours", "Room", "Program", "Section"])
    
    # Iterate through each subject
    for i, row in subjects_df.iterrows():
        subject_program = row["Program"]
        subject_section = row["Section"]
        subject_name = row["Subject Name"]
        
        # Fetch faculty name from faculty data
        faculty_cursor.execute("SELECT name FROM registrations WHERE program_section=? AND subjects LIKE ?", (f"{subject_program}_{subject_section}", f"%{subject_name}%"))
        faculty_row = faculty_cursor.fetchone()
        if faculty_row:
            faculty_name = faculty_row[0]
            subjects_df.at[i, "Faculty"] = faculty_name
    
    conn.close()
    faculty_conn.close()
    
    return subjects_df


# Fetch programs from the database
programs = fetch_programs()

# Display dropdown to select program
selected_program = st.selectbox("Select Program", programs)

# Fetch sections based on the selected program
sections = fetch_sections(selected_program)

# Display dropdown to select section
selected_section = st.selectbox("Select Section", sections)

# Fetch subjects based on the selected program and section
subjects = fetch_subjects(selected_program, selected_section)

# Create a DataFrame for subjects
subjects_df = pd.DataFrame(subjects, columns=["Subject Code", "Subject Name", "Lecture", "Lab", "Unit", "Hours", "Room", "Program", "Section"])

# Add new columns "Faculty" and "Schedules" to the DataFrame
subjects_df["Faculty"] = ""
subjects_df["Schedules"] = ""

# Filter subjects by room
available_rooms = subjects_df["Room"].unique()
selected_room = st.selectbox("Filter by Room", ["All"] + list(available_rooms))
if selected_room != "All":
    subjects_df = subjects_df[subjects_df["Room"] == selected_room]

# Display the combined table
st.write("Schedules:")
# Set larger width for the table
st.write(subjects_df.style.set_table_styles([dict(selector='table', props=[('width', '100%')])]))



#FACULTY DATA CODES

# Function to create database connection
def create_connection():
    conn = sqlite3.connect("faculty_registration.db")
    return conn

# Function to create the registrations table
def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            batches TEXT,
                            program_section TEXT,  -- Add program_section column
                            subjects TEXT,
                            preferences TEXT,
                            notes TEXT
                          )''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)



# Streamlit UI
def main():
    conn = create_connection()
    create_table(conn)

    # Dropdown to select faculty name for filtering
    faculty_names = []
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name FROM registrations")
    rows = cursor.fetchall()
    for row in rows:
        faculty_names.append(row[0])
    conn.close()

    selected_name = st.selectbox("Select Faculty Name", faculty_names)

    # Display responses for the selected faculty in a table
    st.subheader(f"Faculty Data for {selected_name}")
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations WHERE name=?", (selected_name,))
    rows = cursor.fetchall()
    
    # Prepare data for table display
    table_data = []
    for row in rows:
        name = row[1]
        batches = row[2]
        program_sections = row[3]
        notes = row[6]
        
        # Parse and prepare subject preferences
        preferences = eval(row[5])  # Assuming preferences are stored as a string representation of a dictionary
        for batch, programs in preferences.items():
            for program, sections in programs.items():
                for section, subjects in sections.items():
                    for subject, pref in subjects.items():
                        preferred_days, preferred_times = pref
                        table_data.append({
                            "Name": name,
                            "Batches": batches,
                            "Program": program,
                            "Section": section,
                            "Subject": subject,
                            "Preferred Days": ', '.join(preferred_days),
                            "Preferred Times": ', '.join(preferred_times),
                            "Notes": notes
                        })

    # Display table
    st.table(table_data)

    conn.close()


if __name__ == "__main__":
    main()








