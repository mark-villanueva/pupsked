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
