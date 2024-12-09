from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkintermapview
import requests

tile_servers_dict = {
    "Google Maps": "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
    "Google Satellite": "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
    "OS Maps": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
}

# Tkinter window setup
root = Tk()
root.geometry(f"{1200}x{900}")
root.title("Rainfall Map")

# OpenWeatherMap API Key
API_KEY = "c72b8237acd5ac5cbd79f7d38cc0bbb9"


def change_tile_server(server):
    match server:
        case "Google Maps":
            map_widget.set_tile_server(
                tile_servers_dict["Google Maps"], max_zoom=22)
        case "Google Satellite":
            map_widget.set_tile_server(
                tile_servers_dict["Google Satellite"], max_zoom=22)
        case "OS Maps":
            map_widget.set_tile_server(
                tile_servers_dict["OS Maps"], max_zoom=22)


def get_coordinates_opencage(address):
    OPENCAGE_KEY = "668c51611f5042ee8636cb2d7426a6c0"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={
        address}&key={OPENCAGE_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            lat = data["results"][0]["geometry"]["lat"]
            lon = data["results"][0]["geometry"]["lng"]
            return lat, lon
        else:
            raise ValueError("No results found for the given address.")
    else:
        response.raise_for_status()


def getAddress():
    inputted_place = entry_str.get()
    if inputted_place:
        try:
            # Get latitude and longitude using OpenCage
            lat, lon = get_coordinates_opencage(inputted_place)

            # Set position on the map
            map_widget.set_position(lat, lon)
            map_widget.set_marker(lat, lon, text=inputted_place)

            output_string.set(
                f"Found: {inputted_place} (Lat: {lat}, Lon: {lon})")
            map_widget.set_zoom(14)
        except Exception as e:
            messagebox.showerror(f"Error: {e}")
    else:
        messagebox.showerror('Please enter a valid address')
        # output_string.set("Please enter a valid address.")


map_widget = tkintermapview.TkinterMapView(
    root, width=1200, height=900, corner_radius=5)
map_widget.place(relx=0.5, rely=0.5, anchor=CENTER)

title_label = ttk.Label(
    master=root,
    text='Enter address',
    font='Helvetica 24 bold')
title_label.pack()

# Frame for user input (Entry and Button)
input_frame = ttk.Frame(master=root)
entry_str = StringVar()
entry = ttk.Entry(master=input_frame, textvariable=entry_str)
button = ttk.Button(master=input_frame, text='Search', command=getAddress)
entry.pack(side='left')
button.pack(side='left')
input_frame.pack(pady=0)

map_widget.set_tile_server(
    "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

map_widget.set_tile_server(tile_servers[0])
map_widget.set_zoom(9)
map_widget.set_position(51.5074, -0.1278)

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

output_string = StringVar()
output_label = ttk.Label(
    master=root,
    text='Output',
    font='Helvetica 24 ',
    textvariable=output_string)
output_label.pack(pady=5)

output_string2 = StringVar()
output_label = ttk.Label(
    master=root,
    text='Output',
    font='Helvetica 16',
    textvariable=output_string2)
output_label.pack(pady=5)

# Frame for tile server buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# Create buttons for each tile server
google_maps_button = ttk.Button(
    button_frame, text="Google Maps", command=lambda server="Google Maps": change_tile_server(server))
google_maps_button.grid(row=0, column=0, padx=5)


google_satellite_button = ttk.Button(
    button_frame, text="Google Satellite", command=lambda server="Google Satellite": change_tile_server(server))
google_satellite_button.grid(row=0, column=1, padx=5)


openstreetmap_button = ttk.Button(
    button_frame, text="OS Map", command=lambda server="OS Maps": change_tile_server(server))
openstreetmap_button.grid(row=0, column=2, padx=5)

root.mainloop()
