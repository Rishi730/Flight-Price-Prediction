import tkinter as tk
from tkinter import ttk, messagebox
import joblib
import pickle
import pandas as pd
from datetime import datetime

# Load models and encoders
rf_model = pickle.load(open("C:/Users/rishi/OneDrive/Desktop/Flight_Price/rf_model.pkl", "rb")) 
airline_le = joblib.load("C:/Users/rishi/OneDrive/Desktop/Flight_Price/rf_model.pkl/airline_label_encoder.pkl")
city_le = joblib.load("C:/Users/rishi/OneDrive/Desktop/Flight_Price/rf_model.pkl/city_label_encoder.pkl")


# Column order
required_columns = [
    "from", "to", "day", "month", "weekday",
    "duration_mins", "dep_hour", "dep_min",
    "arr_hour", "arr_min", "airline_encoded"
]

# Main app
class FlightPriceApp:
    def _init_(self, root):
        self.root = root
        root.title("✈ Flight Price Predictor")
        root.geometry("500x600")
        root.resizable(False, False)
        root.configure(bg="#f5f5f5")

        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 10), background="#f5f5f5")
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", font=("Segoe UI", 10))

        # Form fields
        self.airline = tk.StringVar()
        self.from_city = tk.StringVar()
        self.to_city = tk.StringVar()
        self.dep_time = tk.StringVar()
        self.arr_time = tk.StringVar()
        self.travel_date = tk.StringVar()
        self.duration = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        row = 0
        ttk.Label(self.root, text="Airline").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.airline_cb = ttk.Combobox(self.root, textvariable=self.airline, values=list(airline_le.classes_), state="readonly")
        self.airline_cb.grid(row=row, column=1, padx=10, pady=10)

        row += 1
        ttk.Label(self.root, text="From City").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.from_cb = ttk.Combobox(self.root, textvariable=self.from_city, values=list(city_le.classes_), state="readonly")
        self.from_cb.grid(row=row, column=1, padx=10, pady=10)

        row += 1
        ttk.Label(self.root, text="To City").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.to_cb = ttk.Combobox(self.root, textvariable=self.to_city, values=list(city_le.classes_), state="readonly")
        self.to_cb.grid(row=row, column=1, padx=10, pady=10)

        row += 1
        ttk.Label(self.root, text="Departure Time (HH:MM)").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.root, textvariable=self.dep_time).grid(row=row, column=1, padx=10, pady=10)

        row += 1
        ttk.Label(self.root, text="Arrival Time (HH:MM)").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.root, textvariable=self.arr_time).grid(row=row, column=1, padx=10, pady=10)

        row += 1
        ttk.Label(self.root, text="Travel Date (YYYY-MM-DD)").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.root, textvariable=self.travel_date).grid(row=row, column=1, padx=10, pady=10)

        row += 1
        ttk.Label(self.root, text="Duration (e.g. 2h 50m)").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.root, textvariable=self.duration).grid(row=row, column=1, padx=10, pady=10)

        row += 1
        ttk.Button(self.root, text="Predict Price 💸", command=self.predict).grid(row=row, columnspan=2, pady=20)

        self.result_label = ttk.Label(self.root, text="", font=("Segoe UI", 12, "bold"), foreground="#007f00")
        self.result_label.grid(row=row+1, columnspan=2)

    def predict(self):
        try:
            airline_enc = airline_le.transform([self.airline.get()])[0]
            from_enc = city_le.transform([self.from_city.get()])[0]
            to_enc = city_le.transform([self.to_city.get()])[0]

            dep_hour, dep_min = map(int, self.dep_time.get().split(":"))
            arr_hour, arr_min = map(int, self.arr_time.get().split(":"))
            date_obj = datetime.strptime(self.travel_date.get(), "%Y-%m-%d")
            day, month, weekday = date_obj.day, date_obj.month, date_obj.weekday()

            # Duration parsing
            duration_str = self.duration.get().lower()
            duration = 0
            if "h" in duration_str:
                h_part = int(duration_str.split("h")[0].strip())
                duration += h_part * 60
                if "m" in duration_str:
                    m_part = duration_str.split("h")[1].replace("m", "").strip()
                    if m_part:
                        duration += int(m_part)
            elif "m" in duration_str:
                duration += int(duration_str.replace("m", "").strip())

            input_data = {
                "from": from_enc,
                "to": to_enc,
                "day": day,
                "month": month,
                "weekday": weekday,
                "duration_mins": duration,
                "dep_hour": dep_hour,
                "dep_min": dep_min,
                "arr_hour": arr_hour,
                "arr_min": arr_min,
                "airline_encoded": airline_enc
            }

            input_df = pd.DataFrame([[input_data[col] for col in required_columns]], columns=required_columns)
            prediction = rf_model.predict(input_df)
            self.result_label.config(text=f"Predicted Price: ₹{round(prediction[0], 2)}")
        except Exception as e:
            messagebox.showerror("Input Error", f"❌ Something went wrong:\n{e}")

# Run the app
if _name_ == "_main_":
    root = tk.Tk()
    app = FlightPriceApp(root)
    root.mainloop()