from tkinter import *
from tkinter import ttk, messagebox, StringVar
import tkintermapview
import requests
import customtkinter as ctk
import threading


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
            print("Changed tile server to g maps")
            log_output.set(f"Tile server switched to {server}")
        case "Google Satellite":
            map_widget.set_tile_server(
                tile_servers_dict["Google Satellite"], max_zoom=22)
            print("Changed tile server to g sat")
            log_output.set(f"Tile server switched to {server}")
        case "OS Maps":
            map_widget.set_tile_server(
                tile_servers_dict["OS Maps"], max_zoom=19)
            print("Changed tile server to OS")
            log_output.set(f"Tile server switched to {server}")


def get_coordinates_opencage(address):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={
        address}&key={OPENCAGE_KEY}"
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
search_entry.grid(row=0, column=0, padx=15, pady=10)

search_button = ctk.CTkButton(
    top_frame, text="Search", width=90, height=40, corner_radius=12, command=getAddress)
search_button.grid(row=0, column=1, padx=15)


# Tile Server Buttons
button_frame = ctk.CTkFrame(root, fg_color="white")
button_frame.place(relx=0.035, rely=0.5, anchor="w")

google_maps_button = ctk.CTkButton(
    button_frame, text="Google Maps", width=150, height=50, command=lambda: change_tile_server("Google Maps"))
google_maps_button.pack(pady=10, padx=10)

google_satellite_button = ctk.CTkButton(
    button_frame, text="Satellite", width=150, height=50, command=lambda: change_tile_server("Google Satellite"))
google_satellite_button.pack(pady=10, padx=10)

osm_button = ctk.CTkButton(
    button_frame, text="OS Maps", width=150, height=50, command=lambda: change_tile_server("OS Maps"))
osm_button.pack(pady=10, padx=10)


# Logging output
log_output = StringVar()
log_output.set("Welcome RainItIn! I hope you enjoy my app :)")
log_label = ctk.CTkLabel(root, textvariable=log_output, height=30,
                         fg_color="#e0e0e0", corner_radius=5, anchor="w", padx=10)
log_label.pack(side="bottom", fill="x")


london_polygon = map_widget.set_polygon(
    [
        (51.722002972, -1.1537175776),
        (51.516126327, -1.1901767121),
        (51.301538032, -0.8626944836),
        (51.192197665, -0.43314727484),
        (51.179068124, 0.12579509192),
        (51.284533875, 0.49797646601),
        (51.528586602, 0.47162098553),
        (51.682688365, 0.26010226980),
        (51.766124775, 0.082666508775),
        (51.815788382, -0.22561855295),
        (51.848903847, -0.57421114314),
        (51.870491134, -0.87684831507),
        (51.846885757, -1.076522952),
        (51.722002972, -1.1537175776)
    ],
    fill_color="blue",
    border_width=6,
    name="London and the Chilterns"
)

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

map_widget.set_overlay_tile_server(
    f"{tile_url}/512/{{z}}/{{x}}/{{y}}/1/1_0.png")

root.mainloop()
