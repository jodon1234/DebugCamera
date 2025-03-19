import os
import subprocess
from tkinter import *
import customtkinter
import signal
import time
import RPi.GPIO as GPIO
from libcamera import controls
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput, FfmpegOutput
from datetime import datetime
from pycomm3 import LogixDriver
print(f"Starting...")
cam_start = True
setup_req = True
input_mode = 0
# Define the IP address of the PLC
PLC_IP = '192.168.2.10'
PI_IP = '192.168.2.248'
SUBNET = '255.255.255.0'
GATEWAY = '192.168.1.1'
pre_time = 90

def setup():
    while setup_req:

        def external_sel():
            global input_mode
            input_mode = 1
        
        def internal_sel():
            global input_mode
            input_mode = 2

        def ethernet_sel():
            global input_mode
            input_mode = 3
       
        # Main Window Properties
        window = Tk()
        window.title("Camera Setup")
        window.geometry("380x380")
        window.configure(bg="#ffffff")
        def done_pressed():
            if input_mode > 0:
                global setup_req
                global PLC_IP
                global PI_IP
                global SUBNET
                global GATEWAY
                global pre_time
                setup_req = False
                PLC_IP = plc_addr_entry.get()
                PI_IP = pi_addr_entry.get()
                SUBNET = subnet_entry.get()
                GATEWAY = gateway_entry.get()
                pre_timestr = pre_trig_time.get()
                pre_time = int(pre_timestr)
                print("Done")
                print (setup_req)
                window.destroy()

        radio_var = IntVar()
        #BG Color #ffffff
        #FG Color #d6d6d6
        #FG Color #68da7b
        pi_addr_entry = customtkinter.CTkEntry(
            master=window,
            placeholder_text="NOT WORKING",
            placeholder_text_color="#454545",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=195,
            border_width=2,
            corner_radius=6,
            border_color="#000000",
            bg_color="#ffffff",
            fg_color="#d6d6d6",
            )
        pi_addr_entry.place(x=10, y=210)

        plc_addr_entry = customtkinter.CTkEntry(
            master=window,
            placeholder_text="PLC ADDRESS",
            placeholder_text_color="#454545",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=195,
            border_width=2,
            corner_radius=6,
            border_color="#000000",
            bg_color="#ffffff",
            fg_color="#ffffff",
            )
        plc_addr_entry.place(x=10, y=30)

        subnet_entry = customtkinter.CTkEntry(
            master=window,
            placeholder_text="NOT WORKING",
            placeholder_text_color="#454545",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=195,
            border_width=2,
            corner_radius=6,
            border_color="#000000",
            bg_color="#ffffff",
            fg_color="#d6d6d6",
            )
        subnet_entry.place(x=10, y=90)

        gateway_entry = customtkinter.CTkEntry(
            master=window,
            placeholder_text="NOT WORKING",
            placeholder_text_color="#454545",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=195,
            border_width=2,
            corner_radius=6,
            border_color="#000000",
            bg_color="#ffffff",
            fg_color="#d6d6d6",
            )
        gateway_entry.place(x=10, y=150)

        pre_trig_time = customtkinter.CTkEntry(
            master=window,
            placeholder_text="Pre Trig",
            placeholder_text_color="#454545",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=95,
            border_width=2,
            corner_radius=6,
            border_color="#000000",
            bg_color="#ffffff",
            fg_color="#ffffff",
            )
        pre_trig_time.place(x=200, y=270)

        #post_trig_time = customtkinter.CTkEntry(
            #master=window,
            #placeholder_text="Post Trig",
            #placeholder_text_color="#454545",
            #font=("Arial", 14),
            #text_color="#000000",
            #height=30,
            #width=95,
            #border_width=2,
            #corner_radius=6,
            #border_color="#000000",
            #bg_color="#ffffff",
            #fg_color="#d6d6d6",
            #)
        #post_trig_time.place(x=200, y=300)

        done_button = customtkinter.CTkButton(
            master=window,
            text="DONE",
            font=("undefined", 14),
            text_color="#000000",
            hover=True,
            hover_color="#949494",
            height=30,
            width=95,
            border_width=2,
            corner_radius=6,
            border_color="#000000",
            bg_color="#ffffff",
            fg_color="#68da7b",
            command=done_pressed
            )
        done_button.place(x=130, y=340)

        cam_ADDR_label = customtkinter.CTkLabel(
            master=window,
            text="CAM ADDR",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=95,
            corner_radius=0,
            bg_color="#ffffff",
            fg_color="#ffffff",
            )
        cam_ADDR_label.place(x=10, y=180)

        PLC_ADDR_label = customtkinter.CTkLabel(
            master=window,
            text="PLC ADDR",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=95,
            corner_radius=0,
            bg_color="#ffffff",
            fg_color="#ffffff",
            )
        PLC_ADDR_label.place(x=10, y=0)

        subnet_label = customtkinter.CTkLabel(
            master=window,
            text="SUBNET MASK",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=95,
            corner_radius=0,
            bg_color="#ffffff",
            fg_color="#ffffff",
            )
        subnet_label.place(x=20, y=60)

        gateway_label = customtkinter.CTkLabel(
            master=window,
            text="GATEWAY",
            font=("Arial", 14),
            text_color="#000000",
            height=30,
            width=95,
            corner_radius=0,
            bg_color="#ffffff",
            fg_color="#ffffff",
            )
        gateway_label.place(x=10, y=120)

        time_label = customtkinter.CTkLabel(
            master=window,
            text="Record Time",
            font=("Arial", 14),
            text_color="#000000",
            height=20,
            width=95,
            corner_radius=0,
            bg_color="#ffffff",
            fg_color="#ffffff",
            )
        time_label.place(x=200, y=245)

        radio_internal = customtkinter.CTkRadioButton(
            master=window,
            variable=radio_var,
            value=8,
            text="Internal",
            text_color="#000000",
            border_color="#000000",
            fg_color="#68da7b",
            hover_color="#2F2F2F",
            command=internal_sel
            )
        radio_internal.place(x=10, y=310)

        radio_external = customtkinter.CTkRadioButton(
            master=window,
            variable=radio_var,
            value=7,
            text="External",
            text_color="#000000",
            border_color="#000000",
            fg_color="#68da7b",
            hover_color="#2F2F2F",
            command=external_sel
            )
        radio_external.place(x=10, y=280)

        radio_ethernet = customtkinter.CTkRadioButton(
            master=window,
            variable=radio_var,
            value=6,
            text="Ethernet",
            text_color="#000000",
            border_color="#000000",
            fg_color="#68da7b",
            hover_color="#2F2F2F",
            command=ethernet_sel
            )
        radio_ethernet.place(x=10, y=250)
        
        #run the main loop
        if setup_req:
            print(setup_req)
            window.mainloop()

if setup_req:
    print("Setup Run")
    print(setup_req)
    setup()

if input_mode == 3:
    #Set ethernet configuration
    print("Applying config...")
    #subprocess.run(['sudo','ifconfig', 'eth0', 'down'], stdout = subprocess.DEVNULL)
    #time.sleep(2)
    #subprocess.run(['sudo','ifconfig', 'eth0', PI_IP], stdout = subprocess.DEVNULL)
    #subprocess.run(['sudo','ifconfig', 'eth0', 'netmask', SUBNET], stdout = subprocess.DEVNULL)
    #subprocess.run(['sudo', 'ip','route', 'del', 'default', 'eth0'], stdout = subprocess.DEVNULL)
    #time.sleep(1)
    #subprocess.run(['sudo', 'ip', 'route', 'add', 'default', 'via', GATEWAY, 'dev', 'eth0'], stdout = subprocess.DEVNULL)
    #time.sleep(2)
    #subprocess.run(['sudo','ifconfig', 'eth0', 'up'], stdout = subprocess.DEVNULL)
    #time.sleep(1)

# Start Camera
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
dur = pre_time
fps = 30
fpsSTR = str(fps)
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)}, controls={'FrameRate': 15})
picam2.start_preview(Preview.QTGL)
picam2.configure(preview_config)
micro = int((1 / fps) * 1000000)
video_config = picam2.create_video_configuration(main={"size": (1920, 1080)}, controls={'FrameRate': fps})
picam2.configure(video_config)
encoder = H264Encoder()
encoder.output = CircularOutput(buffersize=int(fps * (dur + 0.2)), outputtofile=False)
picam2.start()
picam2.start_encoder(encoder)

def main():
    global cam_start
    trigger = False
    # Ethernet Trigger
    while input_mode == 3:
        if cam_start:
            current_datetime = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
            TempName="Temp" + ".h264"
            encoder.output.fileoutput = TempName
            encoder.output.start()
            print(f"Cam Started")
            cam_start = False
            picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        try:
            with LogixDriver(PLC_IP) as plc:
                # Read the tag that indicates the command from the PLC
                response = plc.read('Cam1.Trigger_OUT')
                heartbeat = plc.read('Cam1.Heartbeat_OUT')
                plc.write('Cam1.Heartbeat_IN', heartbeat.value)
                print(heartbeat)
                if response.value == 1:
                    response = 0
                    PLC_filename_enable = plc.read('Cam1.PLC_Filename_EN')
                    plc.write('Cam1.Busy', 1)
                    encoder.output.stop()
                    print(f"Converting file to .MP4")
                    print(TempName)
                    time.sleep(2)
                    if PLC_filename_enable:
                        filename = plc.read('Cam1.Filename')
                    if not PLC_filename_enable:
                        filename = current_datetime
                    cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + filename +'.mp4'
                    print(cmd)
                    os.system(cmd)
                    time.sleep(10)
                    plc.write('Cam1.Done', 1)
                    plc.write('Cam1.Trigger_OUT', 0)
                    plc.write('Cam1.Busy', 0)
                    print(f"Done")
                    cam_start = True
        except:
            print(f"Connection lost, retrying...")
            time.sleep(5)
    #Internal Trigger
    while input_mode == 2:
        if cam_start:
            current_datetime = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
            TempName="Temp" + ".h264"
            encoder.output.fileoutput = TempName
            print(f"Cam Started")
            encoder.output.start()
            cam_start = False
            picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        trigger = GPIO.input(17)
        if trigger:
            response = 0
            encoder.output.stop()
            print(f"Converting file to .MP4")
            print(TempName)
            time.sleep(2)
            cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + current_datetime +'.mp4'
            print(cmd)
            os.system(cmd)
            time.sleep(10)
            print(f"Done")
            cam_start = True
    #External Trigger
    while input_mode == 1:
        if cam_start:
            current_datetime = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
            TempName="Temp" + ".h264"
            encoder.output.fileoutput = TempName
            print(f"Cam Started")
            encoder.output.start()
            cam_start = False
            picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        trigger = GPIO.input(4)
        if trigger:
            response = 0
            encoder.output.stop()
            print(f"Converting file to .MP4")
            print(TempName)
            time.sleep(2)
            cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + current_datetime +'.mp4'
            print(cmd)
            os.system(cmd)
            time.sleep(10)
            print(f"Done")
            cam_start = True
if __name__ == "__main__":
      main()
