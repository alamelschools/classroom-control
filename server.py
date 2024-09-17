import tkinter as tk
from tkinter import simpledialog, ttk
import socket
import threading
import numpy as np
import time

ADMIN_PASSWORD = "emirkugic"
THRESHOLD_DB = 50
listening = True
connected_students = []
student_sound_levels = {}

def handle_student(client_socket, address):
    """Receives sound level data from students."""
    global listening
    while listening:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                sound_level = float(data)
                student_sound_levels[address] = sound_level
        except ConnectionResetError:
            break

def accept_connections(server_socket):
    """Accept connections from students."""
    while listening:
        client_socket, client_address = server_socket.accept()
        connected_students.append(client_socket)
        threading.Thread(target=handle_student, args=(client_socket, client_address)).start()

def start_server():
    """Starts the server to listen to students."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 12345))  # Listen on all available interfaces
    server_socket.listen(5)
    threading.Thread(target=accept_connections, args=(server_socket,)).start()

def broadcast_to_students(message):
    """Sends a message to all connected students."""
    for student in connected_students:
        student.send(message.encode())

def update_progress(progress, teacher_window):
    """Update the progress bar based on student sound levels."""
    while listening:
        if student_sound_levels:
            max_sound_level = max(student_sound_levels.values())
            progress.set(min(int(max_sound_level), 100))  # Update progress bar

            if max_sound_level > THRESHOLD_DB:
                broadcast_to_students("CLOSE_APPS")  # Instruct students to close apps
        time.sleep(1)

def teacher_mode():
    """Displays progress bar and starts the server."""
    password = simpledialog.askstring("Password", "Enter admin password:", show='*')
    if password == ADMIN_PASSWORD:
        teacher_window = tk.Toplevel()
        teacher_window.geometry("300x100")
        
        progress = tk.IntVar()
        progress_bar = ttk.Progressbar(teacher_window, maximum=100, variable=progress)
        progress_bar.pack(expand=True, fill=tk.BOTH)

        start_server()  # Start listening to student computers

        threading.Thread(target=update_progress, args=(progress, teacher_window)).start()
        teacher_window.mainloop()
    else:
        tk.messagebox.showerror("Error", "Incorrect password.")

def main():
    """Main UI with Teacher/Student selection."""
    root = tk.Tk()
    root.title("Classroom Monitor")
    root.geometry("300x150")
    
    teacher_button = tk.Button(root, text="Teacher", command=teacher_mode, height=2, width=20)
    teacher_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
