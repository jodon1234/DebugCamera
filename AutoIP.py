
from time import sleep
import tkinter as tk
from tkinter import messagebox
import socket
import os
import sys

validIP = False
def get_local_ip():
    try:
        # Connect to a public DNS server to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unable to get IP"

def reboot_pi():
    answer = messagebox.askyesno("Reboot", "Are you sure you want to reboot the camera?")
    if answer:
        os.system("sudo reboot")

def main():
    global validIP
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.title("Debug Camera Setup")

    if validIP == False:
        ip_address = get_local_ip()
        if ip_address == "Unable to get IP":
            validIP = False
            sleep(5)
            ip_label = tk.Label(root, text="Unable to retrieve IP address.", font=("Arial", 18), padx=20, pady=20)
        else:
            validIP = True

    if validIP == False:
        ip_label = tk.Label(root, text="Unable to retrieve IP address.", font=("Arial", 18), padx=20, pady=20)
        ip_label.pack()
    else:
        ip_label = tk.Label(root, text=f"Camera Setup:\n http://{ip_address}:5000", font=("Arial", 18), padx=20, pady=20)
        ip_label.pack()

    reboot_button = tk.Button(root, text="Reboot", font=("Arial", 16), bg="red", fg="white", command=reboot_pi)
    reboot_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
