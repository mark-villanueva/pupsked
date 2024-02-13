import streamlit as st
import sqlite3

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

# Function to delete a registration from the database
def delete_registration(name):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("DELETE FROM faculty WHERE name=?", (name,))
    conn.commit()
    conn.close()

# Streamlit UI for displaying responses
def display_responses():
    st.header("Faculty Registrations")
    
    # Fetch registrations
    registrations = fetch_registrations()
    
    # Get unique names
    names = set([row[1] for row in registrations])
    
    # Dropdown for filtering by name
    selected_name = st.selectbox("Filter by Name", ["All"] + sorted(names))
    
    if selected_name != "All":
        registrations = [row for row in registrations if row[1] == selected_name]
    
    if registrations:
        st.write("Here are the current registrations:")
        for row in registrations:
            st.write(f"Name: {row[1]}")
            st.write(f"Preferred Day: {row[2]}")
            st.write(f"Preferred Time: {row[3]}")
            st.write(f"Batch: {row[4]}")
            st.write(f"Program: {row[5]}")
            st.write(f"Section: {row[6]}")
            st.write(f"Subjects: {row[7]}")
            st.write(f"Notes: {row[8]}")
            
            # Delete button based on name
            if st.button(f"Delete {row[1]}"):
                delete_registration(row[1])
                st.success(f"Registration for {row[1]} deleted successfully!")
                st.experimental_rerun()  # Rerun the app to reflect the changes
            
            st.write("---")
    else:
        st.write("No registrations yet.")

if __name__ == "__main__":
    display_responses()
