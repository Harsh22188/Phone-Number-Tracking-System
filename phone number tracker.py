import tkinter as tk
from tkinter import ttk
import tkintermapview
import phonenumbers
import sqlite3
from phonenumbers import geocoder, carrier
from tkinter import messagebox
from opencage.geocoder import OpenCageGeocode

# Assign your actual OpenCage API key
key = ''YOUR_API_KEY''

# Initialize the main window
root = tk.Tk()
root.geometry("600x800")
root.title("Phone Number Tracker")
root.configure(bg='#f5f5f5')

# Create a SQLite database connection
conn = sqlite3.connect('search_history.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        phone_number TEXT,
        location TEXT,
        service_provider TEXT,
        latitude REAL,
        longitude REAL,
        address TEXT
    )
''')
conn.commit()

# Frame for the header
header_frame = tk.Frame(root, bg='#3498db', pady=10)
header_frame.pack(fill=tk.X)

label1 = tk.Label(header_frame, text="Phone Number Tracker", font=('calibri', 22, 'bold'), bg='#3498db', fg='white')
label1.pack()

# Frame for the input area
input_frame = tk.Frame(root, pady=20, bg='#f5f5f5')
input_frame.pack(pady=20)

number_label = tk.Label(input_frame, text="Enter Phone Number (with country code):", font=('calibri', 12), bg='#f5f5f5')
number_label.grid(row=0, column=0, padx=10)

number = tk.Entry(input_frame, font=('calibri', 14), width=25, bd=2, relief="solid")
number.grid(row=0, column=1, padx=10)

# Frame for buttons
button_frame = tk.Frame(root, bg='#f5f5f5')
button_frame.pack(pady=20)

style = ttk.Style()
style.configure("TButton", font=('calibri', 12, 'bold'), borderwidth='4')
style.map('TButton', foreground=[('active', '!disabled', 'green')], background=[('active', 'black')])

# Main functionality: Get result based on number
def getResult():
    num = number.get().strip()
    try:
        num1 = phonenumbers.parse(num)
        location = geocoder.description_for_number(num1, "en")
        service_provider = carrier.name_for_number(num1, "en")

        ocg = OpenCageGeocode(key)
        query = str(location)
        result = ocg.geocode(query)

        if result and len(result) > 0:
            lat = result[0]['geometry']['lat']
            lng = result[0]['geometry']['lng']
            formatted_address = result[0]['formatted']

            # Map Frame
            map_frame = tk.LabelFrame(root, bg='#f5f5f5', padx=10, pady=10)
            map_frame.pack(pady=20)

            map_widget = tkintermapview.TkinterMapView(map_frame, width=480, height=400, corner_radius=10)
            map_widget.set_position(lat, lng)
            map_widget.set_marker(lat, lng, text="Phone Location")
            map_widget.set_zoom(12)
            map_widget.pack()

            # Result Display
            result_display.delete("1.0", tk.END)
            result_display.insert(tk.END, f"Location: {location}\n")
            result_display.insert(tk.END, f"Service Provider: {service_provider}\n")
            result_display.insert(tk.END, f"Latitude: {lat}\nLongitude: {lng}\nAddress: {formatted_address}\n")

            # Save to database
            c.execute('''
                INSERT INTO history (phone_number, location, service_provider, latitude, longitude, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (num, location, service_provider, lat, lng, formatted_address))
            conn.commit()
        else:
            messagebox.showerror("Error", "No results found for the location.")

    except phonenumbers.NumberParseException:
        messagebox.showerror("Invalid Number", "The phone number entered is not valid.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Button for searching phone number
search_button = ttk.Button(button_frame, text="Search", command=getResult, style="TButton")
search_button.pack(side=tk.LEFT, padx=10)

# Button for viewing search history
def view_history():
    history_window = tk.Toplevel(root)
    history_window.title("Search History")
    history_window.geometry("500x300")

    c.execute('SELECT * FROM history')
    rows = c.fetchall()

    history_text = tk.Text(history_window, wrap=tk.WORD, font=('calibri', 12))
    history_text.pack(fill=tk.BOTH, expand=1)

    for row in rows:
        history_text.insert(tk.END, f"Phone Number: {row[1]}\nLocation: {row[2]}\n")
        history_text.insert(tk.END, f"Service Provider: {row[3]}\nLatitude: {row[4]}\nLongitude: {row[5]}\n")
        history_text.insert(tk.END, f"Address: {row[6]}\n\n")

history_button = ttk.Button(button_frame, text="View History", command=view_history, style="TButton")
history_button.pack(side=tk.RIGHT, padx=10)

# Text area for displaying result
result_display = tk.Text(root, height=8, width=50, font=('calibri', 12), bd=2, relief="solid")
result_display.pack(pady=10)

root.mainloop()
