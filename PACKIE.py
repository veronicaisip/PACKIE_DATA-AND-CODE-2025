#Importing all relevant modules and extensions for everything to work
import threading #Enables Both the Back and Front end code to run within the same file 
from flask import Flask, request, jsonify 
import tkinter as tk #Module needed for Frontend 
from tkinter import ttk, messagebox 
from tkinter import font as tkFont 
from tkcalendar import Calendar 
import requests # Lets Tkinter get data from Flask backend
import time #Delays the Frontend code so that Backened can startup first 
from datetime import datetime #Allows user to input the dates of their trip 

#Creating a Flask Application - "web server" part of the program
app = Flask (__name__) 

#The Flask Route - only accepts POST requests from Tkinter 
#When Tkinter sends data (destination, duration, weather), this processes it
@app.route('/generate', methods = ['POST'])
def generate_packing_list():
    data = request.json #reads JSON data sent from Tkinter
    # data.get retrieves each field
    destination = data.get ('destination', '').capitalize() 
    start_date_str = data.get ('start_date', '')
    end_date_str = data.get ('end_date', '')
    weather = data.get('weather', 'mild').lower()

    #Allowing user to input dates 
    try: 
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        duration = (end_date - start_date).days 
        if duration <=0:
            return jsonify({"error": "End date must be after start date."}), 400 
    
    except Exception as e:
        return jsonify ({"error": f"Invalid date format: {e}"}), 400 

    trip_range = f"{start_date.strftime ('%d %b %Y')} → {end_date.strftime('%d %b %Y')}"

    #List of items that are needed for the trip split into "base" and "weather appropriate"
    base_items = [
        "Toiletries - i.e. skincare, toothbrush, haircare", 
        "Electronic - i.e. chargers", 
        "Passport/ID", 
        "Comfortable Shoes", 
        "Undergarments"
        ]
    
    # More specific recommended items
    weather_items = {
        "hot": ["Hat", "Shorts", "T-Shirts", "Sandals", "Swimwear", "Skirts", "Dresses"],
        "mild": ["Mix of Clothes:", "Short and long sleeves", "Jeans and shorts"],
        "cold": ["Warm Layers:", "Thermal Wear", "Hoodies", "Sweaters"]
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
        "trip_range": trip_range,
        "start_date": start_date_str,
        "end_date": end_date_str, 
        "packing_list": packing_list
    }
    return jsonify (response)

    #Function to Run Flask using a web server port
    # Allows the Flask backend to act like an API for Tkinter to use 
def run_flask():
    app.run (port=5000, debug=False, use_reloader=False)

#TKINTER FRONTEND
#Tkinter GUI will send user inputs to this Flask API endpoint
def run_gui():
    API_URL = "http://127.0.0.1:5000/generate"

#The Button function - gets user inputs from the following fields 
    def generate_list():
        destination = destination_entry.get()
        start_date = start_entry.get()
        end_date = end_entry.get() 

#If the user leaves the fields blank it will shows the following warning popup instead of crashing
        if not destination or not start_date or not end_date:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

#Sending Data to Flask using a POST request and receives the packing list back from Flask
        try:
            data = {
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "weather": weather_var.get()
            }
            response = requests.post(API_URL, json=data)
            result = response.json()

            if "error" in result:
                messagebox.showerror("Error", result["error"])
                return
            
#Tkinter code - some of this was created referencing/pasting from https://realpython.com/python-gui-tkinter/  
        #Clears the text area - prints the trip info and each item line-by-line
            packing_text.delete(1.0, tk.END)
            packing_text.insert(tk.END, f"Destination: {result['destination']}\n")
            packing_text.insert(tk.END, f"Trip Duration: {result['duration']} days\n")
            packing_text.insert(tk.END, f"Weather: {result['weather']}\n\n")
            packing_text.insert(tk.END, "Recommended Packing List:\n")
            for item in result['packing_list']:
                packing_text.insert(tk.END, f"• {item}\n")    

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Flask server.\n{e}")

#Code used by the refresh button to clear all user input 
    def refresh_app():
            destination_entry.delete(0, tk.END)
            start_entry.delete(0, tk.END)
            end_entry.delete(0, tk.END)
            weather_var.set("mild")
            packing_text.delete(1.0, tk.END)

#Tkinter Layout what the main window will look like
    root = tk.Tk()
    root.title ("PACKIE")
    root.geometry ("700x1020")
    root.configure(bg='#7ab7ef')

#Styling the frontend design of the window 
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#7ab7ef", foreground= "white", font=("Arial", 14, "bold"))
    style.configure("TButton", background="#ffffff", foreground= "#333333", font=("Arial", 12), padding=6)
    style.configure("TEntry", fielbackground="white")
    style.configure("TCombobox", fielbackground="white")

    heading_font = tkFont.Font (family= "Comforta", size=100, weight="bold", slant ="italic")
    heading_label = tk.Label(root, text= "PACKIE", font=heading_font, fg="white", bg='#7ab7ef' )
    heading_label.pack(pady=20)

#Creating messageboxes for where the user inputs their travel information 
    ttk.Label (root, text ="Destination", font=("Arial", 14, "bold")).pack(pady=5)
    destination_entry = ttk.Entry(root, width=40)   
    destination_entry.pack()

#Allows the user to type their dates manually or they can also use...
    ttk.Label (root, text ="Start Date").pack(pady=5)
    start_entry = ttk.Entry(root, width=40)
    start_entry.pack()

#...the 'Pick Start Date' button where a Calendar pop-up allows the user to select their dates 
    def pick_start_date():
        top = tk.Toplevel(root)
        top.configure(bg='#7ab7ef')
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)

        def select_date():
            start_entry.delete(0, tk.END)
            start_entry.insert(0, cal.get_date())
            top.destroy()

        ttk.Button(top, text="Select", command=select_date).pack(pady=10)
    ttk.Button(root, text="Pick Start Date", command=pick_start_date).pack(pady=5) 

#SAME CODE USED HERE AS THE START DATE OPTION
    ttk.Label (root, text ="End Date").pack(pady=5)
    end_entry = ttk.Entry(root, width=40)
    end_entry.pack()

    def pick_end_date():
        top = tk.Toplevel(root)
        top.configure(bg='#7ab7ef')
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)

        def select_date():
            end_entry.delete(0, tk.END)
            end_entry.insert(0, cal.get_date())
            top.destroy()

        ttk.Button(top, text="Select", command=select_date).pack(pady=10)
    ttk.Button(root, text="Pick End Date", command=pick_end_date).pack(pady=5)

#Creates a drop down menu for the user to select between: hot, mild or cold 
    ttk.Label (root, text ="Weather Type").pack(pady=5)
    weather_var = tk.StringVar(value="mild")   
    ttk.Combobox(root, textvariable=weather_var, 
                 values=["hot","mild","cold"]).pack()

#Creates a refresh button used by the user to clear the application so they can try different dates or weather options. 
    button_frame =tk.Frame(root, bg='#7ab7ef')
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Generate Packing List", command=generate_list).grid(row=0, column=0, padx=0)
    ttk.Button(button_frame, text ="Refresh", command=refresh_app).grid(row=0,column=1,padx=10)

#creates the area where the text/list will be generated
    packing_text = tk.Text(root, height=45, width=50)
    packing_text.pack(pady=20)

    root.mainloop() #keeps the window open and interactive (delete and re-input multiple times)

#Allows for all this to run under this one file (Simplifing the process)
if __name__=='__main__':
    #Start Flask in a background thread 
    flask_thread = threading.Thread (target=run_flask, daemon=True)
    flask_thread.start()

    #To avoid the application crashing or not working this code allows the FLASK backend to initialise first before the GUI.
    #Ensures that all backend code is ready to start. 
    time.sleep(3)

    #Start Tkinter GUI 
    run_gui()