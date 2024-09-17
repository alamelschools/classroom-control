import tkinter as tk
from tkinter import simpledialog
import pyaudio
import numpy as np
import socket
import threading
import psutil
import os
import time

ADMIN_PASSWORD = "emir"
THRESHOLD_DB = 50
SERVER_IP = "192.168.1.100"  # Replace with the teacher's computer IP
SERVER_PORT = 12345
listening = True

def close_apps():
    """Closes apps like Roblox and browsers when instructed by the teacher."""
    apps_to_close = ["chrome.exe", "firefox.exe", "roblox.exe", "msedge.exe"]
    
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() in apps_to_close:
                proc.terminate()  # Close the process
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def listen_for_instructions(client_socket):
    """Listens for instructions from the teacher (e.g., to close apps)."""
    while listening:
        try:
            message = client_socket.recv(1024).decode()
            if message == "CLOSE_APPS":
                close_apps()
        except ConnectionResetError:
            break

def send_sound_level(client_socket):
    """Sends the current sound level to the teacher."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    while listening:
        data = np.frombuffer(stream.read(1024), dtype=np.int16)
        volume_norm = np.linalg.norm(data) / 1024
        decibel = 20 * np.log10(volume_norm + 1e-10)  # Calculate decibel level
        try:
            client_socket.send(str(decibel).encode())
        except BrokenPipeError:
            break
        time.sleep(1)

    stream.stop_stream()
    stream.close()
    p.terminate()

def student_mode():
    """Connects to the teacher and sends sound levels."""
    def request_password():
        password = simpledialog.askstring("Password Required", "Enter password to exit:", show='*')
        if password == ADMIN_PASSWORD:
            listening = False  # Stop the listening
            student_window.destroy()
        else:
            tk.messagebox.showerror("Error", "Incorrect password.")

    student_window = tk.Toplevel()
    student_window.geometry("100x50")
    student_window.protocol("WM_DELETE_WINDOW", request_password)
    
    # Indicate listening status
    label = tk.Label(student_window, text="Listening...")
    label.pack()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    threading.Thread(target=send_sound_level, args=(client_socket,)).start()
    threading.Thread(target=listen_for_instructions, args=(client_socket,)).start()

    student_window.mainloop()

def main():
    """Main UI with Teacher/Student selection."""
    root = tk.Tk()
    root.title("Classroom Monitor")
    root.geometry("300x150")
    
    student_button = tk.Button(root, text="Student", command=student_mode, height=2, width=20)
    student_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
