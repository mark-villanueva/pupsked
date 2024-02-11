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

# Streamlit UI for displaying responses
def display_responses():
    st.header("Faculty Registrations")
    registrations = fetch_registrations()
    if registrations:
        st.write("Here are the current registrations:")
        for row in registrations:
            st.write(f"Name: {row[1]}")
            st.write(f"Preferred Day: {row[2]}")
            st.write(f"Preferred Time: {row[3]}")
            st.write(f"Different Time: {row[4]}")
            st.write(f"Batch: {row[5]}")
            st.write(f"Program: {row[6]}")
            st.write(f"Section: {row[7]}")
            st.write(f"Subjects: {row[8]}")
            st.write("---")
    else:
        st.write("No registrations yet.")

if __name__ == "__main__":
    display_responses()

    