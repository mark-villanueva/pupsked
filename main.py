from st_pages import Page, show_pages, add_page_title


# Specify what pages should be shown in the sidebar, and what their titles and icons
show_pages(
    [
        Page("pages/Dashboard.py", "Dashboard", "📊"),
        Page("pages/Programs.py", "Programs", "🏛️"),
        Page("pages/Rooms.py", "Rooms", "🏤"),
        Page("pages/Curriculum.py", "Curriculum", "📚"),
        Page("pages/Faculty Registration.py", "Faculty Registration", "✍"), 
        Page("pages/Faculty Data.py", "Faculty Data", "👩‍🏫"),
        Page("pages/Manage Schedules.py", "Manage Schedules", "📅"),
        Page("pages/Archives.py", "Archives", "🗃️"),

    ]
)
