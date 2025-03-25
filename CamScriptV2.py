try:
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
   import logging
except:
   logging.error("Error importing libraries. Ensure all required libraries are installed.")

logging.basicConfig(filename='DebugCamera.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting...")

cam_start = True
setup_req = True
input_mode = 0
# Define the IP address of the PLC
PLC_IP = '192.168.2.10'
PI_IP = '192.168.2.248'
SUBNET = '255.255.255.0'
GATEWAY = '192.168.1.1'
pre_time = 90
cam_name = 'Cam1'

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
               global cam_name
               setup_req = False
               PLC_IP = plc_addr_entry.get()
               cam_name = cam_name_entry.get()
               #PI_IP = pi_addr_entry.get()
               #SUBNET = subnet_entry.get()
               #GATEWAY = gateway_entry.get()
               pre_timestr = pre_trig_time.get()
               pre_time = int(pre_timestr)
               logging.info("Done")
               logging.info(setup_req)
               window.destroy()

       radio_var = IntVar()
       #BG Color #ffffff
       #FG Color #d6d6d6
       #FG Color #68da7b
       ##pi_addr_entry = customtkinter.CTkEntry(
       ##    master=window,
       ##    placeholder_text="NOT WORKING",
       ##    placeholder_text_color="#454545",
       ##    font=("Arial", 14),
       ##    text_color="#000000",
       ##    height=30,
       ##    width=195,
       ##    border_width=2,
       ##    corner_radius=6,
       ##    border_color="#000000",
       ##    bg_color="#ffffff",
       ##    fg_color="#d6d6d6",
       ##    )
       ##pi_addr_entry.place(x=10, y=210)

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

       cam_name_entry = customtkinter.CTkEntry(
           master=window,
           placeholder_text="Same as in PLC",
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
       cam_name_entry.place(x=10, y=90)

       ##subnet_entry = customtkinter.CTkEntry(
       ##    master=window,
       ##    placeholder_text="NOT WORKING",
       ##    placeholder_text_color="#454545",
       ##    font=("Arial", 14),
       ##    text_color="#000000",
       ##    height=30,
       ##    width=195,
       ##    border_width=2,
       ##    corner_radius=6,
       ##    border_color="#000000",
       ##    bg_color="#ffffff",
       ##    fg_color="#d6d6d6",
       ##    )
       ##subnet_entry.place(x=10, y=90)

       ##gateway_entry = customtkinter.CTkEntry(
       ##    master=window,
       ##    placeholder_text="NOT WORKING",
       ##    placeholder_text_color="#454545",
       ##    font=("Arial", 14),
       ##    text_color="#000000",
       ##    height=30,
       ##    width=195,
       ##    border_width=2,
       ##    corner_radius=6,
       ##    border_color="#000000",
       ##    bg_color="#ffffff",
       ##    fg_color="#d6d6d6",
       ##    )
       ##gateway_entry.place(x=10, y=150)

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

       ##cam_ADDR_label = customtkinter.CTkLabel(
       ##    master=window,
       ##    text="CAM ADDR",
       ##    font=("Arial", 14),
       ##    text_color="#000000",
       ##    height=30,
       ##    width=95,
       ##    corner_radius=0,
       ##    bg_color="#ffffff",
       ##    fg_color="#ffffff",
       ##    )
       ##cam_ADDR_label.place(x=10, y=180)

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

       cam_name_label = customtkinter.CTkLabel(
           master=window,
           text="Cam Name",
           font=("Arial", 14),
           text_color="#000000",
           height=30,
           width=95,
           corner_radius=0,
           bg_color="#ffffff",
           fg_color="#ffffff",
           )
       cam_name_label.place(x=10, y=60)

       ##subnet_label = customtkinter.CTkLabel(
       ##    master=window,
       ##    text="SUBNET MASK",
       ##    font=("Arial", 14),
       ##    text_color="#000000",
       ##    height=30,
       ##    width=95,
       ##    corner_radius=0,
       ##    bg_color="#ffffff",
       ##    fg_color="#ffffff",
       ##    )
       ##subnet_label.place(x=20, y=60)

       ##gateway_label = customtkinter.CTkLabel(
       ##    master=window,
       ##    text="GATEWAY",
       ##    font=("Arial", 14),
       ##    text_color="#000000",
       ##    height=30,
       ##    width=95,
       ##    corner_radius=0,
       ##    bg_color="#ffffff",
       ##    fg_color="#ffffff",
       ##    )
       ##gateway_label.place(x=10, y=120)

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
           logging.info(setup_req)
           window.mainloop()

if setup_req:
   logging.info("Setup Run")
   logging.info(setup_req)
   setup()

if input_mode == 3:
   #Set ethernet configuration
   logging.info("Applying config...")
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
try:
   logging.info(cam_name + ".Busy")
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
except:
   logging.error("Failed to start camera. Check if the camera is connected and configured properly.")

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
           logging.info("Cam Started")
           cam_start = False
           picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
       try:
           with LogixDriver(PLC_IP) as plc:
               # Read the tag that indicates the command from the PLC
               response = plc.read(cam_name + ".Trigger_OUT")
               heartbeat = plc.read(cam_name + ".Heartbeat_OUT")
               plc.write(cam_name + ".Heartbeat_IN", heartbeat.value)
               PLC_filename_enable = plc.read(cam_name + ".PLC_Filename_EN")
               logging.info(heartbeat)
               if response.value == 1:
                   response = 0
                   plc.write(cam_name + ".Busy", 1)
                   encoder.output.stop()
                   logging.info("Converting file to .MP4")
                   logging.info(TempName)
                   time.sleep(2)
                   if PLC_filename_enable.value == 1:
                       filename = filename_temp.value
                   if PLC_filename_enable.value == 0:
                       filename = current_datetime
                   logging.info(filename)
                   cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + filename +'.mp4'
                   logging.info(cmd)
                   os.system(cmd)
                   time.sleep(10)
                   plc.write(cam_name + ".Done", 1)
                   plc.write(cam_name + ".Trigger_OUT", 0)
                   plc.write(cam_name + ".Busy", 0)
                   logging.info("Done")
                   cam_start = True
       except:
           logging.error("Connection lost, retrying...")
           time.sleep(5)
   #Internal Trigger
   while input_mode == 2:
       if cam_start:
           current_datetime = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
           TempName="Temp" + ".h264"
           encoder.output.fileoutput = TempName
           logging.info("Cam Started")
           encoder.output.start()
           cam_start = False
           picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
       trigger = GPIO.input(17)
       if trigger:
           response = 0
           encoder.output.stop()
           logging.info("Converting file to .MP4")
           logging.info(TempName)
           time.sleep(2)
           cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + current_datetime +'.mp4'
           logging.info(cmd)
           os.system(cmd)
           time.sleep(10)
           logging.info("Done")
           cam_start = True
   #External Trigger
   while input_mode == 1:
       if cam_start:
           current_datetime = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
           TempName="Temp" + ".h264"
           encoder.output.fileoutput = TempName
           logging.info("Cam Started")
           encoder.output.start()
           cam_start = False
           picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
       trigger = GPIO.input(4)
       if trigger:
           response = 0
           encoder.output.stop()
           logging.info("Converting file to .MP4")
           logging.info(TempName)
           time.sleep(2)
           cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + current_datetime +'.mp4'
           logging.info(cmd)
           os.system(cmd)
           time.sleep(10)
           logging.info("Done")
           cam_start = True

if __name__ == "__main__":
   main()
