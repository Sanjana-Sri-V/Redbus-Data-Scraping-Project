import streamlit as st
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
        base_query = f"SELECT DISTINCT * FROM {table_name}";
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

        # Price filter   
        if filters["min_price"] is not None and filters["max_price"] is not None:
            conditions.append("Price BETWEEN %s AND %s")
            params.extend([filters["min_price"], filters["max_price"]])

        # Star Rating filter
        if filters["star_rating_min"] is not None and filters["star_rating_max"] is not None:
            conditions.append("CAST(Star_Rating AS FLOAT) BETWEEN %s AND %s")
            params.extend([filters["star_rating_min"], filters["star_rating_max"]])

        # Seat Availability filter
        if filters["seat_availability"] == "Available":
            conditions.append("Seat_Availability = 'Available'")

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
            bus_type_options = get_filter_options("Bus_Type", selected_table)
            

            # User filters
            selected_route_name = st.multiselect("## Select Route Name", route_name_options)
            selected_bus_type = st.multiselect("## Select Bus Type", bus_type_options)
            price_range = st.slider("Select Price Range", 200, 3000, (200, 3000))  # Adjust min/max as needed
            min_price, max_price = price_range
            
            # Parse Star Rating Range
            star_rating_range = st.selectbox("Ratings", ["2.5 - 3.5", "3.5 - 4", "4 - 4.5", "4.5 - 5"])
            if star_rating_range:
                star_rating_min, star_rating_max = map(float, star_rating_range.split(" - "))
            else:
                star_rating_min, star_rating_max = None, None

            seat_availability = st.selectbox("Seat Availability", ["All", "Available"])

            # Define filters
            filters = {
                "bus_type": selected_bus_type,
                "route_name": selected_route_name,
                "min_price": min_price,
                "max_price": max_price,
                "star_rating_min": star_rating_min,
                "star_rating_max": star_rating_max,
                "seat_availability": seat_availability,
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
