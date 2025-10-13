#Importing all relevant modules and extensions for everything to work
import threading #Enables Both the Back and Front end code to run within the same file 
from flask import Flask, request, jsonify 
import tkinter as tk #Module needed for Frontend 
from tkinter import ttk, messagebox #
import requests # Lets Tkinter get data from Flask backend
import time #Delays the Frontend code so that Backened can startup first 

#Creating a Flask Application - "web server" part of the program
app = Flask (__name__) 

#The Flask Route - only accepts POST requests from Tkinter 
#When Tkinter sends data (destination, duration, weather), this processes it
@app.route('/generate', methods = ['POST'])
def generate_packing_list():
    data = request.json #reads JSON data sent from Tkinter
    # data.get retrieves each field
    destination = data.get ('destination', '').capitalize() 
    duration = int(data.get('duration',3))
    weather = data.get('weather', 'mild').lower()

#List of items that are needed for the trip split into "base" and "weather appropriate"
    base_items = ["Toiletries - i.e. skincare, toothbrush, haircare", "Electronic - i.e. chargers", "Passport/ID", "Comfortable Shoes", "Undergarments"]
    #Dictionary mapping weather conditions -> more specific recommended items
    weather_items = {
        "hot": ["Hat", "Shorts", "T-Shirts", "Sandals", "Swimwear", "Skirts", "Dresses"],
        "mild": ["Mix of Clothes i.e. short and long sleeves, Jeans and shorts" ],
        "cold": ["Warm Layers - i.e. Thermal Wear", "Hoodies and Sweaters"]
    }

#Combines the packing lists 
    packing_list = base_items + weather_items.get(weather, [])
    if duration > 5: 
        packing_list.append ("Extra Clothes")

#Returns the JSON Object back to Tkinter 
    response = {
        "destination": destination, 
        "duration": duration, 
        "weather": weather, 
        "packing_list": packing_list 
    }
    return jsonify (response)

#Function to Run Flask using a web server port
def run_flask():
    app.run (port=5000, debug=False, use_reloader=False)

#TKINTER FRONTEND
#Tkinter GUI will send user inputs to this Flask API endpoint
def run_gui():
    API_URL = "http://127.0.0.1:5000/generate"

#The Button function - gets user inputs from the following fields 
    def generate_list():
        destination = destination_entry.get()
        duration = duration_entry.get()
        weather = weather_var.get()

#If the user leaves the fields blank it will shows the following warning popup instead of crashing
        if not destination or not duration:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

#Sending Data to Flask using a POST request and receives the packing list back from Flask
        try:
            data = {
                "destination": destination,
                "duration": int(duration),
                "weather": weather
            }
            response = requests.post(API_URL, json=data)
            result = response.json()

#Clears the text area - prints the trip info and each item line-by-line
            packing_text.delete(1.0, tk.END)
            packing_text.insert(tk.END, f"Destination: {result['destination']}\n")
            packing_text.insert(tk.END, f"Duration: {result['duration']} days\n")
            packing_text.insert(tk.END, f"Weather: {result['weather']}\n\n")
            packing_text.insert(tk.END, "Recommended Packing List:\n")
            for item in result['packing_list']:
                packing_text.insert(tk.END, f"• {item}\n")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Flask server.\n{e}")

#Tkinter Layout what the main window will look like
    root = tk.Tk()
    root.title ("PACKIE")
    root.geometry ("400x500")

    ttk.Label (root, text ="Destination").pack(pady=5)
    destination_entry = ttk.Entry(root, width=40)   
    destination_entry.pack()

    ttk.Label (root, text ="Duration (days):").pack(pady=5)
    duration_entry = ttk.Entry(root, width=40)   
    duration_entry.pack()

    ttk.Label (root, text ="Weather Type").pack(pady=5)
    weather_var = tk.StringVar(value="mild")   
    ttk.Combobox(root, textvariable=weather_var, 
                 values=["hot","mild","cold"]).pack()

    ttk.Button(root, text="Generate Packing List", command=generate_list).pack(pady=10)

#creates the area where the text/list will be generated
    packing_text = tk.Text(root, height=15, width=45)
    packing_text.pack(pady=10)

    root.mainloop() #keeps the window open and interactive (delete and re-input multiple times)

#Allows for all this to run under this one file (Simplifing the process)
if __name__=='__main__':
    #Start Flask in a background thread 
    flask_thread = threading.Thread (target=run_flask, daemon=True)
    flask_thread.start()

    #Wait a moment to ensure Flask is ready 
    time.sleep(2)

    #Start Tkinter GUI 
    run_gui()
