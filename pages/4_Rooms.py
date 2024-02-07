import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Rooms",
    page_icon="images/PUPLogo.png",
)

# Function to create the 'rooms' table in the database
def create_rooms_table():
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            room_name TEXT
        )
    """)
    conn.commit()
    conn.close()

# Call the function to create the table before running the Streamlit app
create_rooms_table()

# Function to add a new room to the database
def add_room_to_db(room_name):
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("INSERT INTO rooms (room_name) VALUES (?)", (room_name,))
    conn.commit()
    conn.close()
    st.success(f"Room '{room_name}' added successfully")

# Function to delete a room from the database
def delete_room(room_name):
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("DELETE FROM rooms WHERE room_name=?", (room_name,))
    conn.commit()
    conn.close()
    st.success(f"Room '{room_name}' deleted successfully")

# Function to retrieve rooms from the database
def fetch_rooms():
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("SELECT room_name FROM rooms")
    rows = c.fetchall()
    conn.close()
    return rows

# Streamlit UI for managing rooms
def main():

    st.sidebar.header("Add New Room")
    new_room_name = st.sidebar.text_input("Room Name")

    if st.sidebar.button("Add Room"):
        add_room_to_db(new_room_name)

    # Option to delete a room
    st.sidebar.header("Delete Room")
    rooms = [room[0] for room in fetch_rooms()]
    selected_room = st.sidebar.selectbox("Select Room to Delete", rooms)
    if st.sidebar.button("Delete Room"):
        delete_room(selected_room)

    # Display rooms in a table
    st.header("Rooms")
    rooms_data = fetch_rooms()
    if rooms_data:
        st.table(rooms_data)
    else:
        st.write("No rooms found.")

if __name__ == "__main__":
    main()
