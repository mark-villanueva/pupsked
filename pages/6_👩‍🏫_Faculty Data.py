import streamlit as st
import sqlite3

# Set Streamlit page configuration
st.set_page_config(
    page_title="Faculty Data",
    page_icon="images/PUPLogo.png",
)

# Function to create database connection
def create_connection():
    conn = sqlite3.connect("faculty_registration.db")
    return conn

## Function to create the registrations table
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

# Function to retrieve subjects for a given program and section from the database
def fetch_subjects(program_name, section):
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute("SELECT subject_code, subject_name FROM subjects WHERE program_name=? AND section=?", (program_name, section))
    rows = c.fetchall()
    conn.close()

    # Extract available subjects from the database rows
    available_subjects = [(f"{code} - {name}") for code, name in rows]

    return available_subjects

# Function to delete registrations by faculty name
def delete_registration_by_name(conn, faculty_name):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registrations WHERE name=?", (faculty_name,))
        conn.commit()
        st.success("Faculty data deleted successfully!")
    except sqlite3.Error as e:
        print(e)
        st.error("An error occurred while deleting faculty data.")

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

    # Delete button to remove data for selected faculty
    if st.button("Delete Faculty Data"):
        conn = create_connection()
        delete_registration_by_name(conn, selected_name)
        conn.close()

   # Display responses for the selected faculty
    st.subheader(f"Faculty Data for {selected_name}")
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations WHERE name=?", (selected_name,))
    rows = cursor.fetchall()
    for row in rows:
        st.write(f"Name: {row[1]}")
        st.write(f"Batches: {row[2]}")
        st.write(f"Program Sections: {row[3]}")
        
        # Parse and display subject preferences
        preferences = eval(row[5])  # Assuming preferences are stored as a string representation of a dictionary
        for batch, programs in preferences.items():
            for program, sections in programs.items():
                for section, subjects in sections.items():
                    st.write(f"Program: {program}, Section: {section}")
                    for subject, pref in subjects.items():
                        preferred_days, preferred_times = pref
                        st.write(f"Subject: {subject}")
                        st.write(f"Preferred Days: {', '.join(preferred_days)}")
                        st.write(f"Preferred Times: {', '.join(preferred_times)}")

    st.write(f"Notes: {row[6]}")
    conn.close()


if __name__ == "__main__":
    main()
