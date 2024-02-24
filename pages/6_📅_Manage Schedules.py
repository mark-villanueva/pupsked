import streamlit as st
from streamlit_calendar import calendar

st.set_page_config(page_title="Manage Schedules", page_icon="📆")

mode = "resource-timegrid"

events = [
    {
        "title": "Event 1",
        "color": "#FFBD45",
        "start": "11:30:00",
        "end": "12:30:00",
        "resourceId": "b",
    },
    {
        "title": "Event 2",
        "color": "#FF4B4B",
        "start": "12:30:00",
        "end": "15:30:00",
        "resourceId": "a",
    },
    {
        "title": "Event 3",
        "color": "#3D9DF3",
        "start": "07:30:00",
        "end": "10:30:00",
        "resourceId": "b",
    },
]

calendar_resources = [
    {"id": "a", "title": "Monday"},
    {"id": "b", "title": "Tuesday"},
    {"id": "c", "title": "Wednesday"},
    {"id": "d", "title": "Thursday"},
    {"id": "e", "title": "Friday"},
    {"id": "f", "title": "Saturday"},
]

calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "resources": calendar_resources,
    "selectable": "true",
    "slotMinTime": "07:30:00",
    "slotMaxTime": "21:30:00",
    "displayEventTime": "false", 
    "allDaySlot": False,
    "headerToolbar": {
        "left": "",
        "center": "",
        "right": "",
    }
}

if "resource" in mode:
    
    if mode == "resource-timegrid":
        calendar_options = {
            **calendar_options,
            "initialDate": "2023-07-01",
            "initialView": "resourceTimeGridDay",
        }

# Convert start and end time strings to ISO-formatted strings
for event in events:
    event["start"] = f"2023-07-01T{event['start']}"
    event["end"] = f"2023-07-01T{event['end']}"

state = calendar(
    events=st.session_state.get("events", events),
    options=calendar_options,
    custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
    """,
    key=mode,
)

if state.get("eventsSet") is not None:
    st.session_state["events"] = state["eventsSet"]
