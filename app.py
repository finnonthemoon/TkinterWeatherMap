from tkinter import *
from tkinter import ttk, messagebox, StringVar
import tkintermapview
import requests
import customtkinter as ctk
import threading
from datetime import datetime, timedelta, timezone

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

tile_servers_dict = {
    "Google Maps": "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
    "Google Satellite": "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
    "OS Maps": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
}

# Tkinter window setup
root = ctk.CTk()
root.geometry(f"{1300}x{950}")
root.title("Weather Map")
root.configure(fg_color="#ffffff")
root.state("zoomed")

# OpenWeatherMap API Key

OPENCAGE_KEY = "668c51611f5042ee8636cb2d7426a6c0"


def change_tile_server(server):
    match server:
        case "Google Maps":
            map_widget.set_tile_server(
                tile_servers_dict["Google Maps"], max_zoom=22)
            log_output.set(f"Tile server switched to {server}")
        case "Google Satellite":
            map_widget.set_tile_server(
                tile_servers_dict["Google Satellite"], max_zoom=22)
            log_output.set(f"Tile server switched to {server}")
        case "OS Maps":
            map_widget.set_tile_server(
                tile_servers_dict["OS Maps"], max_zoom=19)
            log_output.set(f"Tile server switched to {server}")


def get_coordinates_opencage(address):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={OPENCAGE_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        if not data["results"]:
            log_output.set("❌ An error occurred retrieving data")
            messagebox.showerror(
                title="Error", message="An error occurred retrieving data", icon="warning")

        if "confidence" in data["results"][0]["annotations"]:
            confidence = data["results"][0]["annotations"]["confidence"]
            if confidence < 6:
                messagebox.showerror(
                    title="Invalid Address", message="Please enter a valid address", icon="warning")

        lat = data["results"][0]["geometry"]["lat"]
        lon = data["results"][0]["geometry"]["lng"]
        log_output.set("Found coordinates...")
        return lat, lon
    else:
        # log_output.set("An error occurred")
        response.raise_for_status()


def getAddress():
    inputted_place = search_entry.get()
    if inputted_place:
        try:
            lat, lon = get_coordinates_opencage(inputted_place)
            map_widget.set_position(lat, lon)
            map_widget.set_marker(lat, lon, text=inputted_place)
            log_output.set(
                f"Found: {inputted_place} (Lat: {lat}, Lon: {lon})")
            map_widget.set_zoom(14)
        except ValueError as e:
            log_output.set(f"⚠️ Error: {e}")  # Log the error
            messagebox.showerror(
                title="Error", message=f"Error: {e}", icon="cancel")
    else:
        log_output.set("⚠️ Please enter a valid address")  # Log empty input
        messagebox.showerror(
            title="Error", message="Please enter a valid address", icon="warning")


map_widget = tkintermapview.TkinterMapView(
    root, width=1200, height=900, corner_radius=5)
map_widget.pack(fill="both", expand=True)

map_widget.set_tile_server(
    "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)


map_widget.set_tile_server(tile_servers_dict["Google Maps"])
map_widget.set_zoom(9)
map_widget.set_position(51.5074, -0.1278)


# Search bar
top_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=20)
top_frame.place(relx=0.98, rely=0.03, anchor="ne")

search_var = StringVar()
search_entry = ctk.CTkEntry(
    top_frame,
    textvariable=search_var,
    placeholder_text="Search for a location...",
    width=325,
    height=45,
    corner_radius=12,
    fg_color="white")
search_entry.grid(row=0, column=0, padx=12, pady=10)

search_button = ctk.CTkButton(
    top_frame, text="Search", width=90, height=40, corner_radius=12, command=getAddress, font=("helvetica", 17))
search_button.grid(row=0, column=1, padx=12)


# Tile Server Buttons
button_frame = ctk.CTkFrame(root, fg_color="white")
button_frame.place(relx=0.035, rely=0.5, anchor="w")

google_maps_button = ctk.CTkButton(
    button_frame, text="Google Maps", font=("helvetica", 20), width=150, height=50, command=lambda: change_tile_server("Google Maps"))
google_maps_button.pack(pady=10, padx=10)

google_satellite_button = ctk.CTkButton(
    button_frame, text="Satellite", font=("helvetica", 20), width=150, height=50, command=lambda: change_tile_server("Google Satellite"))
google_satellite_button.pack(pady=10, padx=10)

osm_button = ctk.CTkButton(
    button_frame, text="OS Maps", font=("helvetica", 20), width=150, height=50, command=lambda: change_tile_server("OS Maps"))
osm_button.pack(pady=10, padx=10)


def add_marker_event(coords):
    if not coords:
        log_output.set("Something went wrong!")
    new_marker = map_widget.set_marker(
        coords[0], coords[1], font="Helvetica 11 bold", text_color="#333333", text=f"{address_from_coords(coords[0], coords[1])}")


map_widget.add_right_click_menu_command(label="Add Marker",
                                        command=add_marker_event,
                                        pass_coords=True)


def address_from_coords(lat, lon):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={OPENCAGE_KEY}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            components = data["results"][0]["components"]

            road = components.get("road", None)

            area = components.get("neighbourhood") or components.get(
                "suburb") or components.get("town")

            if road and area:
                return f"{road}, {area}"
            elif road:
                return road
            elif area:
                return area
            else:
                return "Unknown Location"
        else:
            return "No address found"
    else:
        return f"Error: {response.status_code}"


# Logging output
log_output = StringVar()
log_output.set("Welcome RainItIn! I hope you enjoy my app :)")
log_label = ctk.CTkLabel(root, textvariable=log_output, height=30,
                         fg_color="#e0e0e0", corner_radius=5, anchor="w", padx=10)
log_label.pack(side="bottom", fill="x")

API_URL = "https://api.rainviewer.com/public/weather-maps.json"


def fetch_weather_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        log_output.set(f"⚠️ Error fetching data: {response.status_code}")
        return None


data = fetch_weather_data()


def get_latest_radar_url(data):
    if data and "radar" in data:
        radar_frames = data["radar"].get(
            "nowcast", []) or data["radar"].get("past", [])
        if radar_frames:
            latest_frame = radar_frames[-1]
            return f"{data['host']}{latest_frame['path']}"
    return None


tile_url = get_latest_radar_url(data)
overlay_url = f"{tile_url}/512/{{z}}/{{x}}/{{y}}/1/1_0.png"


rain_map_active = False
previous_tile_server = tile_servers_dict["Google Maps"]


def toggle_rain_map():
    global rain_map_active, previous_tile_server

    if rain_map_toggle.get() == 1:
        overlay_url = f"{tile_url}/512/{{z}}/{{x}}/{{y}}/1/1_0.png"
        if overlay_url:
            previous_tile_server = map_widget.tile_server
            map_widget.set_overlay_tile_server(overlay_url)
            log_output.set("🌧 Rainfall map enabled")

        map_widget.set_tile_server(previous_tile_server)

    else:
        map_widget.set_overlay_tile_server(None)
        map_widget.set_tile_server(previous_tile_server)

        log_output.set("🌤 Rainfall map disabled")


rain_map_toggle = ctk.CTkSwitch(
    root, text="Rainfall Map", width=150, height=35, font=("helvetica", 14), command=toggle_rain_map)
rain_map_toggle.place(relx=0.045, rely=0.25, anchor=NW)

def get_radar_url(timestamp):
    data = fetch_weather_data()
    if data and "radar" in data:
        radar_frames = data["radar"].get(
            "nowcast", []) or data["radar"].get("past", [])
        for frame in radar_frames:
            if frame["time"] == timestamp:
                return f"{data['host']}{frame['path']}"
    return None


def generate_time_labels():
    now = datetime.now()
    current_minute = (now.minute // 10 + 1) * 10

    if current_minute == 60:  # Handle hour overflow
        now = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
    else:
        now = now.replace(minute=current_minute, second=0, microsecond=0)

    times = [now] + [now + timedelta(minutes=10 * i) for i in range(1, 3)]

    return [(t, t.strftime("%H:%M")) for t in times]


def update_rain_map(selected_time):
    global tile_url

    formatted_time = selected_time.strftime("%Y%m%d%H%M")
    radar_url = get_radar_url(int(selected_time.timestamp()))

    if not radar_url:
        log_output.set(
            f"⚠️ No data available for {selected_time.strftime('%H:%M')}")
        return

    new_overlay_url = f"{radar_url}/512/{{z}}/{{x}}/{{y}}/1/1_0.png"

    current_tile_server = map_widget.tile_server
    map_widget.set_tile_server("")
    map_widget.set_tile_server(current_tile_server)

    map_widget.set_overlay_tile_server(new_overlay_url)

    log_output.set(
        f"✅ Weather data updated for {selected_time.strftime('%H:%M')}")
    print(f"🛰 Overlay URL: {new_overlay_url}")


def create_time_buttons():
    time_frame = ctk.CTkFrame(root, fg_color="white")
    time_frame.place(relx=0.5, rely=0.95, anchor="s")

    for t, label in generate_time_labels():
        btn = ctk.CTkButton(time_frame, text=label, width=60,
                            height=40, command=lambda t=t: update_rain_map(t))
        btn.pack(side="left", padx=5)


create_time_buttons()

root.mainloop()
