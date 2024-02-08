import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Faculty",
    page_icon="images/PUPLogo.png",
)

# Function to retrieve faculty names from the database
def fetch_faculty_names():
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("SELECT name FROM faculty")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Function to fetch faculty details by name
def fetch_faculty_details(name):
    conn = sqlite3.connect("faculty.db")
    c = conn.cursor()
    c.execute("SELECT subjects, preferred_day, preferred_time, availability_info FROM faculty WHERE name=?", (name,))
    row = c.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None

# Streamlit UI for faculty selection and display
def main():
    st.header("Faculty Schedule")

    # Faculty selection dropdown
    selected_faculty_name = st.selectbox("Select Faculty Name", fetch_faculty_names())

    # Display faculty details
    if selected_faculty_name:
        faculty_details = fetch_faculty_details(selected_faculty_name)
        if faculty_details:
            subjects, preferred_days, preferred_times, availability_info = faculty_details

            st.markdown("##### Selected Subjects:")
            for subject in subjects.split(","):
                st.write(subject.strip())

            st.markdown("##### Preferred Days:")
            st.write(", ".join(preferred_days.split(",")))

            st.markdown("##### Preferred Times:")
            st.write(", ".join(preferred_times.split(",")))

            st.markdown("##### Other Availability Info:")
            st.write(availability_info.strip())

            # Display timetable or any other visualization here
        else:
            st.write("No details found for the selected faculty.")

if __name__ == "__main__":
    main()
