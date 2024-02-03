import streamlit as st
import folium
import requests
import pandas as pd
from geopy.distance import geodesic

# Function to check if the current location is inside any of the geofences
def is_outside_geofences(current_location, geofences):
    for geofence_center, radius in geofences:
        distance = geodesic(current_location, geofence_center).meters
        if distance <= radius:
            return False
    return True

# Function to get user location based on IP address using the IPinfo API
@st.cache
def get_user_location():
    try:
        response = requests.get("http://ipinfo.io")
        data = response.json()
        return data.get("loc", "").split(",")
    except Exception as e:
        st.warning(f"Error getting user location: {e}")
        return None

# Function to read geofence data from CSV and create a list of tuples
def read_geofences_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    geofences = [((row['Latitude'], row['Longitude']), row['Radius']) for _, row in df.iterrows()]
    return geofences

# Streamlit app
def main():
    st.title("Road Accident App")

    # Specify the path to your CSV file containing geofence data
    csv_path = "gv.csv"

    # Read geofence data from CSV and create the geofences list
    geofences = read_geofences_from_csv(csv_path)

    # Get user location based on IP address
    user_location = get_user_location()

    if user_location:
        st.write(f"User Location (based on IP): Latitude: {user_location[0]}, Longitude: {user_location[1]}")

        # Check if the user's location is outside any of the geofences
        outside_geofences = is_outside_geofences(user_location, geofences)

        # Display result
        if outside_geofences:
            st.success("Safe to navigate")
        else:
            st.error("Beware! You are in an Accident Prone Region")

        # Display the Folium map with geofences and user's location
        m = folium.Map(location=(float(user_location[0]), float(user_location[1])), zoom_start=5)

        # Plot each geofence on the map
        for geofence_center, radius in geofences:
            folium.Circle(geofence_center, radius=radius, color='red', fill=True, fill_color='red').add_to(m)

        folium.Marker((float(user_location[0]), float(user_location[1])), popup="User Location", icon=folium.Icon(color='blue')).add_to(m)

        # Convert Folium map to HTML and display using st.markdown
        map_html = m._repr_html_()
        st.markdown(map_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
