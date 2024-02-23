import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Faculty List",
    page_icon="images/PUPLogo.png",
)

# Function to create the 'faculty' table in the database
def create_faculty_table():
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY,
            faculty_name TEXT
        )
    """)
    conn.commit()
    conn.close()

# Call the function to create the table before running the Streamlit app
create_faculty_table()

# Function to add a new faculty member to the database
def add_faculty_to_db(faculty_name):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("INSERT INTO faculty (faculty_name) VALUES (?)", (faculty_name,))
    conn.commit()
    conn.close()
    st.success(f"Faculty member '{faculty_name}' added successfully")

# Function to delete a faculty member from the database
def delete_faculty(faculty_name):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("DELETE FROM faculty WHERE faculty_name=?", (faculty_name,))
    conn.commit()
    conn.close()
    st.success(f"Faculty member '{faculty_name}' deleted successfully")

# Function to retrieve faculty members from the database
def fetch_faculty():
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("SELECT faculty_name FROM faculty")
    rows = c.fetchall()
    conn.close()
    return rows

# Streamlit UI for managing faculty members
def main():

    st.sidebar.header("Add New Faculty Member")
    new_faculty_name = st.sidebar.text_input("Faculty Name")

    if st.sidebar.button("Add Faculty"):
        add_faculty_to_db(new_faculty_name)

    # Option to delete a faculty member
    st.sidebar.header("Delete Faculty Member")
    faculty = [member[0] for member in fetch_faculty()]
    selected_faculty = st.sidebar.selectbox("Select Faculty Member to Delete", faculty)
    if st.sidebar.button("Delete Faculty"):
        delete_faculty(selected_faculty)

    # Display faculty in a table
    st.header("Faculty Members")
    faculty_data = fetch_faculty()
    if faculty_data:
        # Converting data to list of dictionaries
        faculty_dict_list = [{"Faculty Members": name} for name, in faculty_data]
        st.table(faculty_dict_list)  # Displaying data as a table
    else:
        st.write("No faculty members found.")

if __name__ == "__main__":
    main()
