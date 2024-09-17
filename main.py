import tkinter as tk
from tkinter import messagebox, simpledialog
import pyaudio
import numpy as np
import threading
import psutil
import os
import time

# Set the admin password for teacher mode
ADMIN_PASSWORD = "emir_kgc"
THRESHOLD_DB = 50  # Set your loudness threshold in decibels

# Global variable to stop listening
listening = True

def close_apps():
    """Closes apps like Roblox and browsers if noise threshold is surpassed."""
    # List of common browser processes and Roblox process names
    apps_to_close = ["firefox.exe", "roblox.exe", "msedge.exe"]
    
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() in apps_to_close:
                proc.terminate()  # Close the process
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def sound_listener():
    """Listens to the microphone for loudness levels."""
    global listening
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    while listening:
        data = np.frombuffer(stream.read(1024), dtype=np.int16)
        volume_norm = np.linalg.norm(data) / 1024
        decibel = 20 * np.log10(volume_norm + 1e-10)  # Calculate decibel level

        if decibel > THRESHOLD_DB:
            close_apps()  # Close apps if sound exceeds threshold
        time.sleep(1)  # Adjust to monitor in intervals

    stream.stop_stream()
    stream.close()
    p.terminate()

def start_listening():
    """Starts the sound listener in a new thread."""
    listener_thread = threading.Thread(target=sound_listener)
    listener_thread.daemon = True
    listener_thread.start()

def student_mode():
    """Locks the student's computer and starts the sound listener."""
    def request_password():
        password = simpledialog.askstring("Password Required", "Enter password to exit:", show='*')
        if password == ADMIN_PASSWORD:
            listening = False  # Stop the listening
            student_window.destroy()
        else:
            messagebox.showerror("Error", "Incorrect password.")

    student_window = tk.Toplevel()
    student_window.geometry("100x50")
    student_window.protocol("WM_DELETE_WINDOW", request_password)
    
    # Indicate listening status
    label = tk.Label(student_window, text="Listening...")
    label.pack()

    start_listening()

    # Prevent students from closing the window without password
    student_window.mainloop()

def teacher_mode():
    """Displays progress bar and controls student devices."""
    password = simpledialog.askstring("Password", "Enter admin password:", show='*')
    if password == ADMIN_PASSWORD:
        teacher_window = tk.Toplevel()
        teacher_window.geometry("300x100")
        
        progress = tk.IntVar()
        progress_bar = tk.ttk.Progressbar(teacher_window, maximum=100, variable=progress)
        progress_bar.pack(expand=True, fill=tk.BOTH)

        def update_progress():
            """Update the progress bar based on noise levels."""
            while listening:
                time.sleep(1)
                # Simulate progress based on sound levels (you would replace this with actual loudness levels)
                sound_level = np.random.randint(0, 100)
                progress.set(sound_level)
                teacher_window.update()

        threading.Thread(target=update_progress).start()
        teacher_window.mainloop()
    else:
        messagebox.showerror("Error", "Incorrect password.")

def main():
    """Main UI with Teacher/Student selection."""
    root = tk.Tk()
    root.title("Classroom Monitor")
    root.geometry("300x150")
    
    teacher_button = tk.Button(root, text="Teacher", command=teacher_mode, height=2, width=20)
    teacher_button.pack(pady=10)
    
    student_button = tk.Button(root, text="Student", command=student_mode, height=2, width=20)
    student_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
