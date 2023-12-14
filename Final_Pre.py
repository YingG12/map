'''
Name: Yinghong Gao
CS230 Section-2
Data: Cannabis Registry
URL: http://localhost:8507/

Description: This program will display the map of the Cannabis Registry in boston and allow user
to input their location and help them find the closest cannabis location and show it on the map.
n addition, user can also choose to see the distribution of app_license_category and app_license_status of cannabis registry.
'''
import pandas as pd
import streamlit as st
import pydeck as pdk
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt

# Function to calculate Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

# Function to display the map
def display_map(df, closest_location=None):
    # Set up the initial view state
    view_state = pdk.ViewState(
        latitude=df["latitude"].mean(),
        longitude=df["longitude"].mean(),
        zoom=11,
        pitch=0
    )

    # Define the first ScatterplotLayer
    layer1 = pdk.Layer('ScatterplotLayer',
                      data=df,
                      get_position='[longitude, latitude]',
                      get_radius=100,
                      get_color=[0, 0, 255],  # big red circle
                      pickable=True
                      )

    # Define the second ScatterplotLayer
    layer2 = pdk.Layer('ScatterplotLayer',
                      data=df,
                      get_position='[longitude, latitude]',
                      get_radius=20,
                      get_color=[255, 0, 255],  # purple circle
                      pickable=True
                      )

    # Add a third layer for the closest location (if available)
    if closest_location is not None:
        closest_layer = pdk.Layer('ScatterplotLayer',
                                  data=pd.DataFrame([closest_location]),
                                  get_position='[longitude, latitude]',
                                  get_radius=500,
                                  get_color=[0, 255, 0],  # green circle
                                  pickable=True
                                  )
        layers = [layer1, layer2, closest_layer]
    else:
        layers = [layer1, layer2]

    # Tool tip configuration
    tool_tip = {
        "html": "<b>Registry Name:</b> {app_business_name}<br/>"
                "<b>Registry Address:</b> {facility_address}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    # Create the Pydeck map
    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        initial_view_state=view_state,
        layers=layers,
        tooltip=tool_tip
    )

    # Display the map using Streamlit
    st.title("The Map of Cannabis Registries in Boston")
    st.pydeck_chart(map)

# Read the CSV file
locations = pd.read_csv("Cannabis_Registry.csv")

# Create a DataFrame with selected columns
df = pd.DataFrame(locations, columns=["app_business_name", "app_license_category", "app_license_status",
                                      "equity_program_designation", "facility_address", "facility_zip_code",
                                      "longitude", "latitude"])

# Display the map initially
display_map(df)

# Dropdown list to choose an action
action = st.selectbox("Choose an action:", ["Find the closest cannabis location",
                                            "Check the distribution of app_license_status",
                                            "Check the distribution of app_license_category",
                                            "Exit"])

if action == "Find the closest cannabis location":
    # Get user input for address
    user_address = st.text_input("Enter Your Address:")

    # Geocode the address to obtain latitude and longitude
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(user_address)

    # Display the closest location details if a valid location is obtained
    if location:
        user_latitude, user_longitude = location.latitude, location.longitude

        # Calculate distances using Haversine formula
        df['distance'] = df.apply(lambda row: haversine(user_latitude, user_longitude, row['latitude'], row['longitude']),
                                  axis=1)

        # Find the closest location
        closest_location = df.loc[df['distance'].idxmin()]

        # Display the closest location details
        st.write(f"Closest Location to {user_address}:")
        st.write(f"Registry Name: {closest_location['app_business_name']}")
        st.write(f"Registry Address: {closest_location['facility_address']}")
        st.write("The closest location will be displayed in green in the map")
        display_map(df, closest_location)
    else:
        st.warning("Please enter a valid address.")

elif action == "Check the distribution of app_license_status":
    st.title("Bar Chart: APP License Status")
    app_license_status_chart = st.bar_chart(df['app_license_status'].value_counts())
    selected_app_license_status = st.radio("Select an APP license status:", df['app_license_status'].unique())
    st.write(f"Number of businesses with {selected_app_license_status}: {df['app_license_status'].value_counts().get(selected_app_license_status, 0)}")

    # Pie chart
    #plt.subplots() creates a figure (fig) and a set of subplots (ax). In this case, we are creating a single subplot.
    fig, ax = plt.subplots()
    app_license_status_counts = df['app_license_status'].value_counts()
    #ax.pie() creates the pie chart. It takes the counts (app_license_status_counts) and other optional parameters
    ax.pie(app_license_status_counts, labels=app_license_status_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

elif action == "Check the distribution of app_license_category":
    # Replace empty or whitespace values in app_license_category with "N/A"
    df['app_license_category'] = df['app_license_category'].replace(r'^\s*$', 'N/A', regex=True)

    st.title("Bar Chart: License Categories")

    # Use st.multiselect to allow selecting multiple license categories
    selected_license_categories = st.multiselect("Select license categories:", df['app_license_category'].unique())

    # Filter the DataFrame based on selected license categories
    filtered_df = df[df['app_license_category'].isin(selected_license_categories)]

    # Display the bar chart for selected license categories
    license_category_chart = st.bar_chart(filtered_df['app_license_category'].value_counts())

    # Display the count for each selected license category
    for selected_category in selected_license_categories:
        st.write(f"Number of businesses with {selected_category}: {filtered_df['app_license_category'].value_counts().get(selected_category, 0)}")

else:
    st.write("Thank you for visiting!")