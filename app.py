import streamlit as st
from datetime import time,timedelta
import mysql.connector
import pandas as pd
from streamlit_option_menu import option_menu


st.set_page_config(
    page_icon=": 🚍",
    page_title="RedBus")

# Function to establish a connection to the MySQL database
def create_connection():
    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="123456789",
            database="red"
        )
    except mysql.connector.Error as err:
        st.error(f"Database connection failed: {err}")
        return None

# Fetch tables dynamically
@st.cache_data
def fetch_tables():
    connection = create_connection()
    if connection:
        query = "SHOW TABLES"
        tables = pd.read_sql(query, connection)
        connection.close()
        return tables.iloc[:, 0].tolist() 
    else:
        return []

# Fetch filter options dynamically
@st.cache_data
def get_filter_options(column_name, table_name):
    connection = create_connection()
    if connection:
        query = f"SELECT DISTINCT {column_name} FROM {table_name}";
        try:
            options = pd.read_sql(query, connection)
            connection.close()
            return options[column_name].dropna().tolist()
        except Exception as e:
            st.error(f"Error fetching options for {column_name}: {e}")
            return []
    else:
        return []

# Function to retrieve filtered data
@st.cache_data
def fetch_filtered_data(table_name, filters):
    connection = create_connection()
    if connection:
        base_query = f"SELECT DISTINCT * FROM {table_name}"
        conditions = []
        params = []

        # Build query based on user inputs
        # Bus Type filter
        if filters["bus_type"]:
            conditions.append(f"Bus_Type IN ({','.join(['%s'] * len(filters['bus_type']))})")
            params.extend(filters["bus_type"])

        # Route Name filter   
        if filters["route_name"]:
            conditions.append(f"Route_Name IN ({','.join(['%s'] * len(filters['route_name']))})")
            params.extend(filters["route_name"])
            
        # Departure time filter
        if filters["min_departure_time"] is not None and filters["max_departure_time"] is not None:
            conditions.append("Departure_Time BETWEEN %s AND %s")
            params.extend([filters["min_departure_time"], filters["max_departure_time"]])

        # Price filter   
        if filters["min_price"] is not None and filters["max_price"] is not None:
            conditions.append("Price BETWEEN %s AND %s")
            params.extend([filters["min_price"], filters["max_price"]])

        # Star Rating filter
        if filters["min_star_rating"] is not None and filters["max_star_rating"] is not None:
            conditions.append("CAST(Star_Rating AS FLOAT) BETWEEN %s AND %s")
            params.extend([filters["min_star_rating"], filters["max_star_rating"]])

        # Seat Availability filter
        if filters["min_seat_availability"] is not None and filters["max_seat_availability"] is not None:
            conditions.append("Seat_Availability BETWEEN %s AND %s")
            params.extend([filters["min_seat_availability"], filters["max_seat_availability"]])

        # Combine conditions
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        try:
            data = pd.read_sql(base_query, connection, params=params)
            connection.close()
            # to remove duplicates
            data = data.drop_duplicates()
            return data
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()


# Sidebar option menu
with st.sidebar:
    menu = option_menu(
        menu_title="RedBus Streamlit Application ",
        options=["Home", "Bus Routes"],
        icons=["house", "map"],
        menu_icon="cast",
        default_index=0,
    )

# Home page
if menu == "Home":
        st.markdown(""" ## <h1 style='text-align: center; color: #d95555;'>🚍 Welcome to the RedBus Ticket Booking Site !""",
                    unsafe_allow_html=True)
        
# Path to the local GIF file
        gif_path = "redbus-logo.gif"  

# Display the local GIF image
        st.image(gif_path, use_column_width=True,width=100)
      
# Problem Statement
        st.markdown(""" ### Problem Statement """)
        st.markdown("""
The goal of this project is to create a **dynamic bus booking platform** for users to scrape **real-time bus data** from RedBus using **Selenium**. The scraped data will be filtered dynamically using **Streamlit** to provide users with specific bus options based on their requirements. 
This project aims to address the challenges of **manually searching** for buses,and  **filtering results**of **real-time bus data**.
""")

# Approach
        st.markdown("### Approach")
        st.markdown("""
1. **Web Scraping**: We use **Selenium** to scrape real-time bus data from the **RedBus** website. The data includes **bus name**, **departure time**, **price**, **availability**, and more.
2. **Dynamic Filtering**: Once data is scraped, we use **Streamlit** to create an interactive interface. Users can apply dynamic filters based on **bus type**, **price**, **departure time**, etc.
3. **Data Storage**: The data can be saved in a **MySQL database** for future use and analysis.
4. **User Interface**: Streamlit provides a simple and intuitive UI to present the scraped data in a structured and readable format.
""")

# Technology Used
        st.markdown("### Technology Used")
        st.markdown("""
- **Python**: The main programming language used for this project.
- **Selenium**: A tool used for web scraping to extract real-time bus data.
- **Streamlit**: A framework used to create the web interface and dynamically filter the scraped data.
- **MySQL**: A relational database used to store the bus data for future analysis.
- **Pandas**: Used for data manipulation and analysis.
""")

# Use Cases
        st.markdown("### Use Cases")
        st.markdown("""
1. **Real-time Bus Search**: Users can search for buses between any two cities and see real-time data on bus availability, prices, departure times, etc.
2. **Filter Options**: Users can filter bus results by **departure time**, **price**, **bus type**, etc., to find the most suitable bus for their journey.
3. **Pricing Analysis**: Users can compare prices across different buses to choose the best option.
4. **Booking Assistance**: The app can be extended to integrate with the booking process, providing users with a seamless experience.
""")

# Conclusion
        st.markdown("### Final Analysis")
        st.markdown("""
            This application allows you to view bus details scraped from RedBus and stored in a MySQL database.The RedBus Streamlit Application is a demo project to showcase how to build a simple and interactive web application using Streamlit. 
    It leverages real-time data scraping and integrates it with a MySQL database for efficient data retrieval and display.
""")

if menu == "Bus Routes":
    st.subheader(":red[:material/filter_alt:]    Explore bus schedules and ticket availability data")
    #st.markdown(" ### Explore bus schedules and ticket availability data")

    # Fetch all table names
    tables = fetch_tables()

    if tables:
        # Table selection
        selected_table = st.selectbox("Select State", tables)

        if selected_table:
            # Fetch filter options
            route_name_options = get_filter_options("Route_Name", selected_table)
            bus_type_groups = {
                "AC Sleeper Buses": [
                    "A/C Sleeper (2+1)", "Volvo Multi Axle B9R A/C Sleeper (2+1)",
                    "Bharat Benz A/C Sleeper (2+1)", "Volvo A/C Sleeper (2+1)",
                    "VE A/C Sleeper (2+1)", "Volvo 9600 Multi-Axle A/C Sleeper (2+1)",
                    "A/C Volvo B11R Multi-Axle Sleeper (2+1)"
                ],
                "AC Seater Buses": [
                    "INDRA(A.C. Seater)", "A/C Seater (2+2)", "Himsuta AC Seater Volvo/Scania 2+2",
                    "Electric A/C Seater (2+2)", "Volvo AC Seater (2+2)",
                    "Janrath AC Seater 2+2", "Pink Express AC Seater 2+2",
                    "Shatabdi AC Seater 2+2", "A/C Executive (2+3)", "A/C Seater (2+3)"
                ],
                "AC Semi Sleeper Buses": [
                    "Volvo Multi-Axle A/C Semi Sleeper (2+2)", "Bharat Benz A/C Semi Sleeper (2+2)",
                    "Scania Multi-Axle AC Semi Sleeper (2+2)", "Mercedes A/C Semi Sleeper (2+2)",
                    "Volvo Multi-Axle I-Shift B11R Semi Sleeper (2+2)", "Volvo A/C B11R Multi Axle Semi Sleeper (2+2)",
                    "Volvo 9600 A/C Semi Sleeper (2+2)", "Volvo 9600 Multi Axle Semi-Sleeper (2+2)",
                    "Rajdhani (AC Semi Sleeper 2+2)", "A/C Semi Sleeper (2+2)", "A/C Semi Sleeper / Sleeper (2+2)"
                ],
                "AC Seater/Sleeper Buses": [
                    "A/C Seater / Sleeper (2+1)", "Bharat Benz A/C Seater / Sleeper (2+1)",
                    "VE A/C Seater / Sleeper (2+1)", "A/C Seater / Sleeper (2+2)",
                    "Volvo Multi Axle B11R AC Seater\Sleeper (2+1)"
                ],
                "Non-AC Sleeper Buses": [
                    "NON A/C Sleeper (2+1)", "NON A/C Seater/ Sleeper (2+1)",
                    "NON AC Seater / Sleeper 2+1"
                ],
                "Non-AC Seater Buses": [
                    "Express(Non AC Seater)", "SUPER LUXURY (NON-AC, 2 + 2 PUSH BACK)", "Non AC Seater (2+2)",
                    "NON A/C Seater (2+1)", "Ordinary 3+2 Non AC Seater", "Himmani Deluxe 2+2 Non AC Seater",
                    "Super Express Non AC Seater Air Bus (2+2)", "Super Fast Non AC Seater (2+3)",
                    "Swift Deluxe Non AC Air Bus (2+2)", "Ordinary Non AC Seater 2+3",
                    "Semi Deluxe Non AC Seater 2+2", "Rajdhani Non AC Seater 2+3"
                ],
                "Non-AC Semi Sleeper Buses": [
                    "NON A/C Seater Semi Sleeper (2+1)"
                ],
                "NON AC Sleeper/Seater Buses": [
                    "NON A/C Seater/ Sleeper (2+1)", "NON AC Seater / Sleeper 2+1"
                ],
                "Deluxe Buses": [
                    "Deluxe AC Seater 2+2", "Super Deluxe Non AC Seater Air Bus (2+2)","SAPTAGIRI EXPRESS"
                ],
                "Ultra Deluxe Buses": [
                    "ULTRA DELUXE (NON-AC, 2+2 PUSH BACK)"
                ]
            }

            
            # User filters
            selected_route_name = st.multiselect("## Select Route Name", route_name_options)
            selected_bus_type = st.multiselect(
            "Select Bus Type",
            options=list(bus_type_groups.keys()),
            format_func=lambda x: f"{x} ({len(bus_type_groups[x])} options)"
            )
            bus_type_values = [bus for group in selected_bus_type for bus in bus_type_groups[group]]

            departure_time_range = st.slider(
                "Select Departure Time Range",
                min_value=time(0, 0),
                max_value=time(23, 59),
                value=(time(0, 0), time(23, 59)),
                step=timedelta(minutes=30),  # Step size as timedelta
                format="HH:mm"
            )


            # Extract min and max departure times
            min_departure_time, max_departure_time = departure_time_range
            price_range = st.slider("Select Price Range", 0, 3000, (0, 3000))  # Adjust min/max as needed
            min_price, max_price = price_range
            
            # Add Star Rating and Seat Availability sliders
            star_rating_range = st.slider('Select Star Rating Range:', min_value=0.0, max_value=5.0, value=(0.0, 5.0), step=0.1)
            seat_availability_range = st.slider("Select Seat Availability Range:", min_value=1, max_value=60, value=(1, 60), step=1)
            
            # Parse into filters dictionary
            filters = {
            "bus_type":  bus_type_values,
            "route_name": selected_route_name,
            "min_departure_time": min_departure_time.strftime("%H:%M:%S"),
            "max_departure_time": max_departure_time.strftime("%H:%M:%S"),
            "min_price": min_price,
            "max_price": max_price,
            "min_star_rating": star_rating_range[0],
            "max_star_rating": star_rating_range[1],
            "min_seat_availability": seat_availability_range[0],
            "max_seat_availability": seat_availability_range[1],
        }

            # Fetch and display filtered data
            data = fetch_filtered_data(selected_table, filters)

            if not data.empty:
                st.subheader(f"Search Results for {selected_table}")
                st.write(f"Number of Buses: {len(data)}")
                st.dataframe(data)
            else:
                st.warning("No data found with the selected filters.")
    else:
        st.warning("No tables found in the database.")
