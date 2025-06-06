# Debug Camera
#
# This program is used to control the debug camera based on the Picamera2 library
# This script records with a ring buffer meaning it is always recording but only saves recorded footage upon trigger from a PLC.
#
# REV: 1.1
# Author: Jordan Shrauger
try:
   import os
   import logging
   from logging.handlers import RotatingFileHandler
   from tkinter import *
   import customtkinter
   import socket
   import time
   from datetime import datetime
   from pycomm3 import LogixDriver
   from pycomm3.logger import configure_default_logger
   import cv2
   for k, v in os.environ.items():
        if k.startswith("QT_") and "cv2" in v:
            del os.environ[k]
   import numpy as np
   import RPi.GPIO as GPIO
   from libcamera import controls
   from picamera2 import Picamera2, Preview, MappedArray
   from picamera2.encoders import H264Encoder
   from picamera2.outputs import CircularOutput, FfmpegOutput
except:
   logging.error("Failed to import libraries")

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

logFile = 'DebugCamera.log'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

app_log.addHandler(my_handler)
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
hostname = socket.gethostname()
logging.info("Hostname: " + hostname)
tag_tracking_en = True
tag1_tracking_en = True
tag2_tracking_en = True
tag3_tracking_en = True
tag4_tracking_en = True
tag_tracking_text = ""
#Give the camera some time to connect to the netowrk
time.sleep(8)

def test_connection(IP, name):
    status1 = "Failed"
    status2 = "Failed"
    try:
        logging.info("Testing Connection " + IP)
        plc = LogixDriver(IP)
        plc.open()
        status1 = "Connection Sucessful"
        logging.info("Connection Sucessful")
        try:
            logging.info("Testing Cam Tag " + name)
            str = "test"
            plc.write(name + ".Filename", str)
            time.sleep(2)
            str1 = plc.read(name + ".Filename")
            logging.info(str)
            logging.info(str1.value)
            if str1.value == str:
                status2 = "AOI Configured Correctly"
                logging.info("AOI Configured Correctly")
                return status1, status2
            else:
                logging.error("Cam Tag not found")
                status2 = "AOI Not Configured"
                return status1, status2

        except:
            logging.error("Cam Tag not found")
            status2 = "Tag Not Found"
            return status1, status2
    except:
        logging.error("Failed to connect to PLC")
        status1 = "PLC Connection Failed"
        return status1, status2

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


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
       window.geometry("600x400")
       window.resizable(False, False)
       window.configure(bg="#343635")

       def done_pressed():
           if input_mode > 0:
               global setup_req
               global PLC_IP
               global SUBNET
               global GATEWAY
               global pre_time
               global cam_name
               global tag_tracking_text
               global tag_tracking_en
               global tag1_tracking_en
               global tag2_tracking_en
               global tag3_tracking_en
               global tag4_tracking_en
               global tag1
               global tag2
               global tag3
               global tag4
               setup_req = False
               PLC_IP = plc_addr_entry.get()
               cam_name = cam_name_entry.get()
               pre_timestr = pre_trig_time.get()
               pre_time = int(pre_timestr)
               tag1 = tag1_entry.get()
               tag2 = tag2_entry.get()
               tag3 = tag3_entry.get()
               tag4 = tag4_entry.get()
               if tag1 == "" and tag2 == "" and tag3 == "" and tag4 == "":
                   tag_tracking_en = False
               else:
                   tag_tracking_text = "Loading Tags..."
               if tag1 == "":
                   tag1_tracking_en = False
               if tag2 == "":
                   tag2_tracking_en = False
               if tag3 == "":
                   tag3_tracking_en = False
               if tag4 == "":
                   tag4_tracking_en = False
               window.destroy()

       radio_var = IntVar()
       #BG Color #ffffff
       #FG Color #d6d6d6
       #FG Color #68da7b
       PI_IP = get_ip()
       logging.info(PI_IP)
       text_1 = customtkinter.CTkTextbox(master=window, width=400, height=95, bg_color="#454545", fg_color="#454545", text_color="#ffffff", font=("Arial", 12))
       text_1.pack(pady=10, padx=10)
       text_1.insert("0.0", " Please make sure the camera is connected to the Gentex \n Corporate network either over WIFI or Ethernet. Refer to \n the Readme in the camera root directory or on the flash \n drive for setup guide. \n CAM ADDRESS: "+ PI_IP)

       connect_status = customtkinter.CTkTextbox(master=window, width=150, height=5, bg_color="#343635", fg_color="#343635", text_color="#ffffff", font=("Arial", 10))
       connect_status.pack(pady=10, padx=10)
       connect_status.place(x=240, y=280)

       aoi_status = customtkinter.CTkTextbox(master=window, width=150, height=5, bg_color="#343635", fg_color="#343635", text_color="#ffffff", font=("Arial", 10))
       aoi_status.pack(pady=10, padx=10)
       aoi_status.place(x=240, y=300)

       def test_pressed():
           status1 = ""
           status2 = ""
           TEST_IP = plc_addr_entry.get()
           TEST_name = cam_name_entry.get()
           connect_status.delete("1.0",END)
           aoi_status.delete("1.0",END)
           status1, status2 = test_connection(TEST_IP, TEST_name)
           connect_status.insert("0.0", status1)
           aoi_status.insert("0.0", status2)
       

       plc_addr_entry = customtkinter.CTkEntry(
           master=window,
           placeholder_text="PLC ADDRESS",
           placeholder_text_color="#ffffff",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=195,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           )
       plc_addr_entry.place(x=10, y=140)

       cam_name_entry = customtkinter.CTkEntry(
           master=window,
           placeholder_text="Same as in PLC",
           placeholder_text_color="#ffffff",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=195,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           )
       cam_name_entry.place(x=10, y=200)
       cam_name_entry.insert(0, "Cam1")

       pre_trig_time = customtkinter.CTkEntry(
           master=window,
           placeholder_text="Pre Trig",
           placeholder_text_color="#ffffff",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=95,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           )
       pre_trig_time.place(x=250, y=140)
       pre_trig_time.insert(0, "30")

       tag1_entry = customtkinter.CTkEntry(
           master=window,
           placeholder_text="Tag 1",
           placeholder_text_color="#ffffff",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=195,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           )
       tag1_entry.place(x=400, y=140)

       tag2_entry = customtkinter.CTkEntry(
           master=window,
           placeholder_text="Tag 2",
           placeholder_text_color="#ffffff",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=195,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           )
       tag2_entry.place(x=400, y=180)

       tag3_entry = customtkinter.CTkEntry(
           master=window,
           placeholder_text="Tag 3",
           placeholder_text_color="#ffffff",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=195,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           )
       tag3_entry.place(x=400, y=220)

       tag4_entry = customtkinter.CTkEntry(
           master=window,
           placeholder_text="Tag 4",
           placeholder_text_color="#ffffff",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=195,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           )
       tag4_entry.place(x=400, y=260)

       done_button = customtkinter.CTkButton(
           master=window,
           text="DONE",
           font=("undefined", 14),
           text_color="#ffffff",
           hover=True,
           hover_color="#949494",
           height=30,
           width=95,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           command=done_pressed
           )
       done_button.place(x=250, y=340)

       test_button = customtkinter.CTkButton(
           master=window,
           text="TEST",
           font=("undefined", 14),
           text_color="#ffffff",
           hover=True,
           hover_color="#949494",
           height=30,
           width=95,
           border_width=2,
           corner_radius=8,
           border_color="#000000",
           bg_color="#343635",
           fg_color="#2e7039",
           command=test_pressed
           )
       test_button.place(x=250, y=250)

       test_label = customtkinter.CTkLabel(
           master=window,
           text="Test Connection",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=95,
           corner_radius=0,
           bg_color="#343635",
           fg_color="#343635",
           )
       test_label.place(x=250, y=220)

       PLC_ADDR_label = customtkinter.CTkLabel(
           master=window,
           text="PLC Address",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=95,
           corner_radius=0,
           bg_color="#343635",
           fg_color="#343635",
           )
       PLC_ADDR_label.place(x=10, y=110)

       cam_name_label = customtkinter.CTkLabel(
           master=window,
           text="Cam Name",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=95,
           corner_radius=0,
           bg_color="#343635",
           fg_color="#343635",
           )
       cam_name_label.place(x=10, y=170)

       time_label = customtkinter.CTkLabel(
           master=window,
           text="Record Time",
           font=("Arial", 14),
           text_color="#ffffff",
           height=20,
           width=95,
           corner_radius=0,
           bg_color="#343635",
           fg_color="#343635",
           )
       time_label.place(x=250, y=115)

       tag_tracking_label = customtkinter.CTkLabel(
           master=window,
           text="Tag Tracking",
           font=("Arial", 14),
           text_color="#ffffff",
           height=30,
           width=95,
           corner_radius=0,
           bg_color="#343635",
           fg_color="#343635",
           )
       tag_tracking_label.place(x=400, y=110)

       radio_internal = customtkinter.CTkRadioButton(
           master=window,
           variable=radio_var,
           value=8,
           text="Internal",
           text_color="#ffffff",
           border_color="#000000",
           fg_color="#68da7b",
           hover_color="#2F2F2F",
           command=internal_sel
           )
       radio_internal.place(x=10, y=320)

       radio_external = customtkinter.CTkRadioButton(
           master=window,
           variable=radio_var,
           value=7,
           text="External",
           text_color="#ffffff",
           border_color="#000000",
           fg_color="#68da7b",
           hover_color="#2F2F2F",
           command=external_sel
           )
       radio_external.place(x=10, y=290)

       radio_ethernet = customtkinter.CTkRadioButton(
           master=window,
           variable=radio_var,
           value=6,
           text="Ethernet",
           text_color="#ffffff",
           border_color="#000000",
           fg_color="#68da7b",
           hover_color="#2F2F2F",
           command=ethernet_sel
           )
       radio_ethernet.place(x=10, y=260)
       
       #run the main loop
       if setup_req:
           window.mainloop()

if setup_req:
   logging.info("Setup Run")
   setup()

if input_mode == 3:
   #Set ethernet configuration
   logging.info("Applying config...")
# Start Camera
try:
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
   GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
   dur = pre_time
   fps = 40
   fpsSTR = str(fps)
   picam2 = Picamera2()
   colour = (0, 255, 0, 255)
   origin = (0, 60)
   font = cv2.FONT_HERSHEY_SIMPLEX
   scale = 1
   thickness = 2
   def overlay(overlay):

       with MappedArray(overlay, "main") as m:
            cv2.putText(m.array, tag_tracking_text, origin, font, scale, colour, thickness)
   picam2.pre_callback = overlay
   preview_config = picam2.create_preview_configuration(main={"size": (640, 480)}, controls={'FrameRate': 15})
   picam2.configure(preview_config)
   picam2.start_preview(Preview.QTGL)
   micro = int((1 / fps) * 1000000)
   video_config = picam2.create_video_configuration(main={"size": (1920, 1080)}, controls={'FrameRate': fps})
   picam2.configure(video_config)
   encoder = H264Encoder()
   encoder.output = CircularOutput(buffersize=int(fps * (dur + 0.2)), outputtofile=False)


except:
   logging.error("Failed to start camera. Check if the camera is connected and configured properly.")

def main():
   global cam_start
   global tag_tracking_en
   global tag1_tracking_en
   global tag2_tracking_en
   global tag3_tracking_en
   global tag4_tracking_en
   global tag1
   global tag2
   global tag3
   global tag4
   global tag_tracking_text
   plc_initialize = True
   trigger = False
   heartbeat = 0
   # Ethernet Trigger
   while input_mode == 3:
       try:
           if plc_initialize:
               logging.info("Starting PLC connection at: " + PLC_IP)
               plc = LogixDriver(PLC_IP)
               logging.info("Opening connection...")
               plc.open()
               logging.info("Connection opened")
               plc_initialize = False
       except:
           logging.error("Failed to connect to PLC retrying...")
           time.sleep(5)
           plc_initialize = True

       if cam_start:
           #Start recording

           picam2.start()
           picam2.start_encoder(encoder)
           TempName="Temp" + ".h264"
           encoder.output.fileoutput = TempName
           encoder.output.start()
           logging.info("Cam Started")
           cam_start = False
           picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
       try:
           #PLC Communication
           time.sleep(.1)
           response = plc.read(cam_name + ".Trigger_OUT")
           heartbeat = plc.read(cam_name + ".Heartbeat_OUT")
           logging.info(f"Heartbeat_OUT: {heartbeat.value}")
           plc.write(cam_name + ".Heartbeat_IN", heartbeat.value)
           logging.info(f"Heartbeat_IN: {heartbeat.value}")
           PLC_filename_enable = plc.read(cam_name + ".PLC_Filename_EN")
           filename_temp = plc.read(cam_name + ".Filename")
           if tag_tracking_en:
               try:
                   tag1_textfull = ""
                   tag2_textfull = ""
                   tag3_textfull = ""
                   tag4_textfull = ""
                   if tag1_tracking_en:
                        tag1text = plc.read(tag1)
                        tag1_textfull = (tag1+ ": " + str(tag1text.value))
                        logging.info(tag1_textfull)
                   if tag2_tracking_en:
                        tag2text = plc.read(tag2)
                        tag2_textfull = (tag2+ ": " + str(tag2text.value))
                        logging.info(tag2_textfull)
                   if tag3_tracking_en:
                        tag3text = plc.read(tag3)
                        tag3_textfull = (tag3+ ": " + str(tag3text.value))
                        logging.info(tag3_textfull)
                   if tag4_tracking_en:
                        tag4text = plc.read(tag4)
                        tag4_textfull = (tag4+ ": " + str(tag4text.value))
                        logging.info(tag4_textfull)
                   tag_tracking_text = (tag1_textfull + " " + tag2_textfull + " " + tag3_textfull + " " + tag4_textfull)
               except:
                    tag_tracking_text = "Tag Load Error"
                    logging.error("Tag not found")


           if response.value == 1:
                #Save and convert buffer to mp4 upon trigger
                logging.info("Capture Triggered")
                response = 0
                plc.write(cam_name + ".Busy", 1)
                current_datetime = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
                encoder.output.stop()
                logging.info("Converting file to .MP4")
                logging.info(filename_temp.value)
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
                #Set cam_start to true to initialize the camera again
                picam2.stop_encoder(encoder)
                picam2.stop()
                cam_start = True
       except:
           logging.error("Connection lost, retrying...")
           time.sleep(5)
           plc_initialize = True
   #Internal Trigger
   while input_mode == 2:
       if cam_start:
           picam2.start()
           picam2.start_encoder(encoder)
           TempName="Temp" + ".h264"
           encoder.output.fileoutput = TempName
           encoder.output.start()
           logging.info("Cam Started")
           cam_start = False
           picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
       trigger = GPIO.input(17)
       time.sleep(.2)
       if trigger:
           logging.info("Capture Triggered")
           response = 0
           current_datetime = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
           encoder.output.stop()
           logging.info("Converting file to .MP4")
           logging.info(filename_temp.value)
           logging.info(TempName)
           time.sleep(2)
           logging.info(filename)
           cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + filename +'.mp4'
           logging.info(cmd)
           os.system(cmd)
           time.sleep(10)
           logging.info("Done")
           #Set cam_start to true to initialize the camera again
           picam2.stop_encoder(encoder)
           picam2.stop()
           cam_start = True
   #External Trigger
   while input_mode == 1:
       if cam_start:
           picam2.start()
           picam2.start_encoder(encoder)
           TempName="Temp" + ".h264"
           encoder.output.fileoutput = TempName
           encoder.output.start()
           logging.info("Cam Started")
           cam_start = False
           picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
       trigger = GPIO.input(4)
       time.sleep(.2)
       if trigger:
           logging.info("Capture Triggered")
           response = 0
           current_datetime = datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
           encoder.output.stop()
           logging.info("Converting file to .MP4")
           logging.info(filename_temp.value)
           logging.info(TempName)
           time.sleep(2)
           logging.info(filename)
           cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + filename +'.mp4'
           logging.info(cmd)
           os.system(cmd)
           time.sleep(10)
           logging.info("Done")
           #Set cam_start to true to initialize the camera again
           picam2.stop_encoder(encoder)
           picam2.stop()
           cam_start = True

if __name__ == "__main__":
   main()
