import streamlit as st
import numpy as np
from genetic_algorithm import GeneticAlgorithm # Import your genetic algorithm implementation

# Set Streamlit page configuration
st.set_page_config(
    page_title="Dashboard",
    page_icon="images/PUPLogo.png",
)

st.title("Dashboard")

# Define Streamlit UI elements
st.title("Class Scheduling with Genetic Algorithm")

# Define sidebar inputs
st.sidebar.header("Parameters")
num_classes = st.sidebar.number_input("Number of Classes", min_value=1, max_value=10, value=5, step=1)
num_students = st.sidebar.number_input("Number of Students", min_value=1, max_value=100, value=20, step=1)
num_rooms = st.sidebar.number_input("Number of Rooms", min_value=1, max_value=10, value=3, step=1)
num_timeslots = st.sidebar.number_input("Number of Timeslots", min_value=1, max_value=10, value=3, step=1)

# Generate random data based on user input
# Here, you can replace this with your actual data loading mechanism
# For simplicity, let's assume random generation
def generate_random_data(num_classes, num_students, num_rooms, num_timeslots):
    # Generate random class schedule data
    classes = [f"Class {i}" for i in range(1, num_classes + 1)]
    students = [f"Student {i}" for i in range(1, num_students + 1)]
    rooms = [f"Room {i}" for i in range(1, num_rooms + 1)]
    timeslots = [f"Timeslot {i}" for i in range(1, num_timeslots + 1)]

    # Assign random classes to students
    student_class_mapping = {student: np.random.choice(classes) for student in students}

    return classes, students, rooms, timeslots, student_class_mapping

# Display generated data
classes, students, rooms, timeslots, student_class_mapping = generate_random_data(num_classes, num_students, num_rooms, num_timeslots)
st.subheader("Generated Data")
st.write(f"Classes: {classes}")
st.write(f"Students: {students}")
st.write(f"Rooms: {rooms}")
st.write(f"Timeslots: {timeslots}")
st.write("Student-Class Mapping:")
st.write(student_class_mapping)

# Define a function to run genetic algorithm
def run_genetic_algorithm():
    # Initialize genetic algorithm
    ga = GeneticAlgorithm(classes, students, rooms, timeslots, student_class_mapping)

    # Run the genetic algorithm
    best_schedule = ga.evolve()

    return best_schedule

# Button to start the genetic algorithm
if st.button("Run Genetic Algorithm"):
    best_schedule = run_genetic_algorithm()
    st.subheader("Best Schedule")
    st.write(best_schedule)
