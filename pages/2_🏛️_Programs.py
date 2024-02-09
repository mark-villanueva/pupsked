import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Programs and Sections",
    page_icon="images/PUPLogo.png",
)

# Function to create the programs table if it doesn't exist
def create_table():
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS programs (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    sections TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

# Function to fetch programs from the database
def fetch_programs():
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("SELECT name FROM programs")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Function to add a new program to the database
def add_program_to_db(program_name, sections):
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("INSERT INTO programs (name, sections) VALUES (?, ?)", (program_name, ",".join(sections)))
    conn.commit()
    conn.close()
    st.success(f"Program '{program_name}' added successfully with sections: {sections}")

# Function to delete a program from the database
def delete_program(program_name):
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("DELETE FROM programs WHERE name=?", (program_name,))
    conn.commit()
    conn.close()
    st.success(f"Program '{program_name}' deleted successfully")

# Function to update sections of a program in the database
def update_program_sections(program_name, new_sections):
    conn = sqlite3.connect("programs.db")
    c = conn.cursor()
    c.execute("UPDATE programs SET sections=? WHERE name=?", (",".join(new_sections), program_name))
    conn.commit()
    conn.close()
    st.success(f"Sections for program '{program_name}' updated successfully")

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

# Create programs table if not exists
create_table()

# Streamlit UI
st.title("Programs and Sections")

# Option to add more programs
st.sidebar.header("Add New Program")
new_program_name = st.sidebar.text_input("Program Name")
new_sections = st.sidebar.text_input("Sections (comma-separated)")

if st.sidebar.button("Add Program"):
    sections_list = [section.strip() for section in new_sections.split(",")]
    add_program_to_db(new_program_name, sections_list)
    # Update the list of programs
    selected_program = new_program_name

# Program filter
selected_program = st.selectbox("Select Program", fetch_programs())

# Display sections for selected program
if selected_program:
    st.write(f"Sections for {selected_program}:")
    sections = get_sections(selected_program)
    if sections:
        new_sections = st.text_input("Edit Sections (comma-separated)", ",".join(sections))
        if st.button("Update Sections"):
            updated_sections = [section.strip() for section in new_sections.split(",")]
            update_program_sections(selected_program, updated_sections)
            st.write(f"Sections updated for {selected_program}: {updated_sections}")


# Option to delete a program
st.sidebar.header("Delete Program")
program_to_delete = st.sidebar.selectbox("Select Program to Delete", fetch_programs())
if st.sidebar.button("Delete Program"):
    delete_program(program_to_delete)
