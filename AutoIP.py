
import tkinter as tk
from tkinter import messagebox
import socket
import os
import sys

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
    answer = messagebox.askyesno("Reboot", "Are you sure you want to reboot the Raspberry Pi?")
    if answer:
        os.system("sudo reboot")

def main():
    root = tk.Tk()
    root.title("Raspberry Pi IP Display")

    ip_address = get_local_ip()

    ip_label = tk.Label(root, text=f"Local IP Address:\n{ip_address}", font=("Arial", 18), padx=20, pady=20)
    ip_label.pack()

    reboot_button = tk.Button(root, text="Reboot Pi", font=("Arial", 16), bg="red", fg="white", command=reboot_pi)
    reboot_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
