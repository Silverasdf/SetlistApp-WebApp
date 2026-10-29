import pandas as pd

import tkinter as tk
from tkinter import filedialog

def run_program():
    # Get the input values
    song_file = input_file_entry.get()

    # Main code
    try:
        songs = pd.read_csv(song_file)
    except Exception as e:
        setlist_generated_text.delete("1.0", tk.END)
        setlist_generated_text.insert(tk.END, f"Error: {e}")
    #If Column does not exist, create it and fill it with the default value
    try:
        songs["Song"]
    except KeyError:
        songs["Song"] = "Unknown Song"
    try:
        songs["Artist"]
    except KeyError:
        songs["Artist"] = "Unknown Artist"
    try:
        songs["Key"]
    except KeyError:
        songs["Key"] = "Misc"
    try:
        songs["Tuning"]
    except KeyError:
        songs["Tuning"] = "E Standard"
    try:
        songs["Time"]
    except KeyError:
        songs["Time"] = "1"
    try:
        songs["Mood"]
    except KeyError:
        songs["Mood"] = "5"
    try:
        songs["Active"]
    except KeyError:
        songs["Active"] = "True"

    try:
        songs = songs[["Song", "Artist", "Key", "Tuning", "Time", "Mood", "Active"]]  # Reorder the columns
        songs["Active"].fillna("True", inplace=True)  # Fill the NaN values in the "Active" column with "True"
        songs["Mood"].fillna("5", inplace=True)  # Fill the NaN values in the "Mood" column with "0"
        songs["Time"].fillna("1", inplace=True)  # Fill the NaN values in the "Time" column with "1"
        songs["Tuning"].fillna("E Standard", inplace=True)  # Fill the NaN values in the "Tuning" column with "E Standard"
        songs["Key"].fillna("Misc", inplace=True)  # Fill the NaN values in the "Key" column with "Misc"
        songs["Artist"].fillna("Unknown Artist", inplace=True)  # Fill the NaN values in the "Artist" column with "Unknown Artist"
        songs["Song"].fillna("Unknown Song", inplace=True)  # Fill the NaN values in the "Song" column with "Unknown Song"
        songs.to_csv(song_file, index=False)

        setlist_generated_text.delete("1.0", tk.END)  # Clear previous message
        setlist_generated_text.insert(tk.END, "CSV Formatted!")
    except Exception as e:
        setlist_generated_text.delete("1.0", tk.END)
        setlist_generated_text.insert(tk.END, f"Error: {e}")

# Create the GUI window
window = tk.Tk()
window.title("CSV Formatter for Setlist Generator")

# Input File Path
input_file_label = tk.Label(window, text="Input File Path:")
input_file_label.pack()
input_file_entry = tk.Entry(window)
input_file_entry.pack()
input_file_button = tk.Button(window, text="Browse", command=lambda: input_file_entry.insert(tk.END, filedialog.askopenfilename()))
input_file_button.pack()

# Run Button
run_button = tk.Button(window, text="Format", command=run_program)
run_button.pack()

# Setlist Generated Message
setlist_generated_text = tk.Text(window, height=1, width=30)
setlist_generated_text.pack()

# Start the GUI event loop
window.mainloop()

if __name__ == '__main__':
    run_program()