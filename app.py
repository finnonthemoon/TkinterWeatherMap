# ============================
# IMPORTS & CONFIGURATION
# ============================

import requests
import tkinter as tk
from tkinter import ttk, messagebox, StringVar
import tkintermapview
import customtkinter as ctk
from datetime import datetime, timedelta
from PIL import Image, ImageTk

# Set CustomTkinter appearance and theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# OpenCage API Key for geocoding
OPENCAGE_KEY = "668c51611f5042ee8636cb2d7426a6c0"

# Rainviewer API URL
API_URL = "https://api.rainviewer.com/public/weather-maps.json"

# Tile server dictionary
TILE_SERVERS = {
    "Google Maps": "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
    "Google Satellite": "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
    "OS Maps": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
}

# ============================
# MAIN WINDOW SETUP
# ============================

root = ctk.CTk()
root.geometry("1300x950")
root.title("Weather Map")
root.configure(fg_color="#ffffff")
root.state("zoomed")

# ============================
# MAP WIDGET SETUP
# ============================

map_widget = tkintermapview.TkinterMapView(root, width=1200, height=900, corner_radius=5)
map_widget.pack(fill="both", expand=True)
map_widget.set_tile_server(TILE_SERVERS["Google Maps"])
map_widget.set_zoom(9)
map_widget.set_position(51.5074, -0.1278)  # Default to London

# ============================
# TILE SERVER SWITCHING FUNCTION
# ============================

def change_tile_server(server):
    """Switch the map to a different tile server."""
    if server in TILE_SERVERS:
        map_widget.set_tile_server(TILE_SERVERS[server], max_zoom=22)
        log_output.set(f"Tile server switched to {server}")

# ============================
# ADDRESS SEARCH FUNCTIONS
# ============================

def get_coordinates_opencage(address):
    """Fetches coordinates from OpenCage API based on user input."""
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={OPENCAGE_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if not data["results"]:
            messagebox.showerror("Error", "An error occurred retrieving data", icon="warning")
            return None, None

        confidence = data["results"][0]["annotations"].get("confidence", 10)
        if confidence < 6:
            messagebox.showerror("Invalid Address", "Please enter a valid address", icon="warning")
            return None, None

        lat, lon = data["results"][0]["geometry"]["lat"], data["results"][0]["geometry"]["lng"]
        return lat, lon
    else:
        response.raise_for_status()

def search_address():
    """Handles searching for an address and updating the map."""
    inputted_place = search_entry.get()
    if inputted_place:
        try:
            lat, lon = get_coordinates_opencage(inputted_place)
            if lat and lon:
                map_widget.set_position(lat, lon)
                map_widget.set_marker(lat, lon, text=inputted_place)
                map_widget.set_zoom(14)
                log_output.set(f"Found: {inputted_place} (Lat: {lat}, Lon: {lon})")
        except ValueError as e:
            log_output.set(f"⚠️ Error: {e}")
            messagebox.showerror("Error", f"Error: {e}", icon="cancel")
    else:
        log_output.set("⚠️ Please enter a valid address")
        messagebox.showerror("Error", "Please enter a valid address", icon="warning")

# ============================
# SEARCH BAR UI
# ============================

top_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=20)
top_frame.place(relx=0.98, rely=0.03, anchor="ne")

search_var = StringVar()
search_entry = ctk.CTkEntry(top_frame, textvariable=search_var, placeholder_text="Search for a location...",
                            width=325, height=45, corner_radius=12, fg_color="white")
search_entry.grid(row=0, column=0, padx=12, pady=10)

search_button = ctk.CTkButton(top_frame, text="Search", width=90, height=40, corner_radius=12, 
                              command=search_address, font=("helvetica", 17))
search_button.grid(row=0, column=1, padx=12)

# ============================
# TILE SERVER BUTTONS
# ============================

button_frame = ctk.CTkFrame(root, fg_color="white")
button_frame.place(relx=0.035, rely=0.5, anchor="w")

for name in TILE_SERVERS.keys():
    ctk.CTkButton(button_frame, text=name, font=("helvetica", 20), width=150, height=50, 
                  command=lambda s=name: change_tile_server(s)).pack(pady=10, padx=10)

# ============================
# WEATHER DATA FETCHING
# ============================

def fetch_weather_data():
    """Fetches weather radar data from Rainviewer API."""
    response = requests.get(API_URL)
    return response.json() if response.status_code == 200 else None

def get_latest_radar_url():
    """Gets the latest weather radar overlay URL."""
    data = fetch_weather_data()
    if data and "radar" in data:
        frames = data["radar"].get("nowcast", []) or data["radar"].get("past", [])
        return f"{data['host']}{frames[-1]['path']}" if frames else None
    return None

# ============================
# TOGGLE RAIN MAP OVERLAY
# ============================

def toggle_rain_map():
    """Enable or disable the rain map overlay."""
    if rain_map_toggle.get() == 1:
        overlay_url = get_latest_radar_url()
        if overlay_url:
            map_widget.set_overlay_tile_server(f"{overlay_url}/512/{{z}}/{{x}}/{{y}}/1/1_0.png")
            log_output.set("🌧 Rainfall map enabled")
    else:
        map_widget.set_overlay_tile_server(None)
        log_output.set("🌤 Rainfall map disabled")

rain_map_toggle = ctk.CTkSwitch(root, text="Rainfall Map", width=150, height=35, font=("helvetica", 14), 
                                command=toggle_rain_map)
rain_map_toggle.place(relx=0.045, rely=0.25, anchor="nw")

# ============================
# STATUS LOG UI
# ============================

log_output = StringVar()
log_output.set("Welcome to RainItIn! I hope you enjoy my app :)")

log_label = ctk.CTkLabel(root, textvariable=log_output, height=30, fg_color="#e0e0e0",
                         corner_radius=5, anchor="w", padx=10)
log_label.pack(side="bottom", fill="x")

# ============================
# WEATHER KEY IMAGE
# ============================

key_frame = ctk.CTkFrame(root, width=200, height=350, fg_color="#1b1c1f")
key_frame.place(relx=0.97, rely=0.5, anchor="e")

rain_key_img = Image.open("rainkey.png").resize((160, 240), Image.LANCZOS)
image = ImageTk.PhotoImage(rain_key_img)

image_label = ctk.CTkLabel(key_frame, text="", image=image)
image_label.pack(expand=True, fill="both", padx=12, pady=12)

# ============================
# MAIN EVENT LOOP
# ============================

root.mainloop()
