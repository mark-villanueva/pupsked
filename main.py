from st_pages import Page, show_pages, add_page_title


# Specify what pages should be shown in the sidebar, and what their titles and icons
show_pages(
    [
        Page("Dashboard.py", "Dashboard", "📊"),
        Page("Programs.py", "Programs", "🏛️"),
        Page("Rooms.py", "Rooms", "🏤"),
        Page("Curriculum.py", "Curriculum", "📚"),
        Page("Faculty Registration.py", "Faculty Registration", "✍"), 
        Page("Faculty Data.py", "Faculty Data", "👩‍🏫"),
        Page("Manage Schedules.py", "Manage Schedules", "📅"),
        Page("Archives.py", "Archives", "🗃️"),

    ]
)
