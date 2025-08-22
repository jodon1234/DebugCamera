
# Debug Camera
#
# This program is used to control the debug camera based on the Picamera2 library
# This script records with a ring buffer meaning it is always recording but only saves recorded footage upon trigger from a PLC.
#
# REV: 1.2 (Web UI)
# Author: Jordan Shrauger

try:
    import os
    import logging
    from logging.handlers import RotatingFileHandler
    import socket
    import time
    import platform
    import psutil
    from datetime import datetime
    from pycomm3 import LogixDriver
    from pycomm3.logger import configure_default_logger
    from flask import Flask, render_template_string, request, redirect, url_for
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
except Exception as e:
    logging.error(f"Failed to import libraries: {e}")

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = 'DebugCamera.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)
logging.info("Starting...")

cam_start = True
setup_req = True
input_mode = 0
PLC_IP = '192.168.2.10'
PI_IP = '192.168.2.248'
SUBNET = '255.255.255.0'
GATEWAY = '192.168.1.1'
Captures = 0
pre_time = 90
fps = 30
cam_name = 'Cam1'
hostname = socket.gethostname()
logging.info("Hostname: " + hostname)
tag_tracking_en = True
tag1_tracking_en = True
tag2_tracking_en = True
tag3_tracking_en = True
tag4_tracking_en = True
tag_tracking_text = ""
tag1 = ""
tag2 = ""
tag3 = ""
tag4 = ""
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
            str_test = "test"
            plc.write(name + ".Filename", str_test)
            time.sleep(2)
            str1 = plc.read(name + ".Filename")
            logging.info(str_test)
            logging.info(str1.value)
            if str1.value == str_test:
                status2 = "AOI Configured Correctly"
                logging.info("AOI Configured Correctly")
                return status1, status2
            else:
                logging.error("Cam Tag not found")
                status2 = "AOI Not Configured"
                return status1, status2
        except Exception as e:
            logging.error(f"Cam Tag not found: {e}")
            status2 = "Tag Not Found"
            return status1, status2
    except Exception as e:
        logging.error(f"Failed to connect to PLC: {e}")
        status1 = "PLC Connection Failed"
        return status1, status2

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_system_info():
    try:
        info = {
            "Hostname": socket.gethostname(),
            "OS": platform.platform(),
            "Python": platform.python_version(),
            "CPU": platform.processor(),
            "CPU Cores": psutil.cpu_count(logical=True),
            "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "Disk": f"{round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
            "Uptime": f"{int(time.time() - psutil.boot_time()) // 3600}h {(int(time.time() - psutil.boot_time()) % 3600) // 60}m",
            "Captures:": Captures
        }
    except Exception as e:
        info = {"Error": str(e)}
    return info

# --- Web UI using Flask ---
app = Flask(__name__)

SETUP_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Camera Setup</title>
    <style>
        body { background: #343635; color: #fff; font-family: Arial, sans-serif; }
        .container { width: 600px; margin: 40px auto; background: #454545; padding: 30px; border-radius: 10px; }
        label { display: block; margin-top: 15px; }
        input[type=text], input[type=number] { width: 95%; padding: 8px; border-radius: 5px; border: 1px solid #2e7039; background: #2e7039; color: #fff; }
        .radio-group { margin-top: 15px; }
        .radio-group label { display: inline-block; margin-right: 20px; }
        .btn { margin-top: 20px; padding: 10px 30px; background: #2e7039; color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .btn:hover { background: #68da7b; color: #343635; }
        .status { margin-top: 10px; color: #68da7b; }
        .sysinfo { margin-top: 30px; background: #2e7039; color: #fff; padding: 15px; border-radius: 8px; }
        .sysinfo h3 { margin-top: 0; color: #68da7b; }
        .sysinfo table { width: 100%; color: #fff; }
        .sysinfo td { padding: 4px 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Camera Setup</h2>
        <p>Please make sure the camera is connected to the Gentex Corporate network either over WIFI or Ethernet.<br>
        Refer to the Readme in the camera root directory or on the flash drive for setup guide. FTP LOGIN USER: admin PASS: password<br>
        <b>CAM ADDRESS: {{ pi_ip }}</b></p>
        <form method="post">
            <label>PLC Address</label>
            <input type="text" name="plc_addr" value="{{ plc_addr }}" required>
            <label>Cam Name</label>
            <input type="text" name="cam_name" value="{{ cam_name }}" required>
            <label>Record Time (seconds)</label>
            <input type="number" name="pre_time" value="{{ pre_time }}" min="1" required>
            <label>FPS (30 recommended, higher than 60 may cause instability)</label>
            <input type="number" name="fps" value="{{ fps }}" min="15" required>
            <label>Tag 1</label>
            <input type="text" name="tag1" value="{{ tag1 }}">
            <label>Tag 2</label>
            <input type="text" name="tag2" value="{{ tag2 }}">
            <label>Tag 3</label>
            <input type="text" name="tag3" value="{{ tag3 }}">
            <label>Tag 4</label>
            <input type="text" name="tag4" value="{{ tag4 }}">
            <div class="radio-group">
                <label><input type="radio" name="input_mode" value="1" {% if input_mode==1 %}checked{% endif %}> External</label>
                <label><input type="radio" name="input_mode" value="2" {% if input_mode==2 %}checked{% endif %}> Internal</label>
                <label><input type="radio" name="input_mode" value="3" {% if input_mode==3 %}checked{% endif %}> Ethernet</label>
            </div>
            <button class="btn" type="submit" name="action" value="done">Done</button>
            <button class="btn" type="submit" name="action" value="test">Test Connection</button>
        </form>
        {% if status1 %}
            <div class="status">PLC: {{ status1 }}</div>
        {% endif %}
        {% if status2 %}
            <div class="status">AOI: {{ status2 }}</div>
        {% endif %}
        <div class="sysinfo">
            <h3>System Information</h3>
            <table>
            {% for k, v in sysinfo.items() %}
                <tr><td><b>{{ k }}</b></td><td>{{ v }}</td></tr>
            {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def setup_web():
    global setup_req, PLC_IP, SUBNET, GATEWAY, pre_time, cam_name, tag_tracking_text, fps
    global tag_tracking_en, tag1_tracking_en, tag2_tracking_en, tag3_tracking_en, tag4_tracking_en
    global tag1, tag2, tag3, tag4, input_mode

    status1 = status2 = None
    if request.method == "POST":
        PLC_IP = request.form.get("plc_addr", PLC_IP)
        cam_name = request.form.get("cam_name", cam_name)
        pre_time = int(request.form.get("pre_time", pre_time))
        fps = int(request.form.get("fps", fps))
        tag1 = request.form.get("tag1", "")
        tag2 = request.form.get("tag2", "")
        tag3 = request.form.get("tag3", "")
        tag4 = request.form.get("tag4", "")
        input_mode = int(request.form.get("input_mode", 0))

        tag_tracking_en = not (tag1 == "" and tag2 == "" and tag3 == "" and tag4 == "")
        tag_tracking_text = "Loading Tags..." if tag_tracking_en else ""
        tag1_tracking_en = tag1 != ""
        tag2_tracking_en = tag2 != ""
        tag3_tracking_en = tag3 != ""
        tag4_tracking_en = tag4 != ""

        if request.form.get("action") == "test":
            status1, status2 = test_connection(PLC_IP, cam_name)
        elif request.form.get("action") == "done":
            setup_req = False
            return redirect(url_for("setup_done"))

    sysinfo = get_system_info()
    return render_template_string(
        SETUP_FORM,
        pi_ip=get_ip(),
        plc_addr=PLC_IP,
        cam_name=cam_name,
        pre_time=pre_time,
        fps=fps,
        tag1=tag1,
        tag2=tag2,
        tag3=tag3,
        tag4=tag4,
        input_mode=input_mode,
        status1=status1,
        status2=status2,
        sysinfo=sysinfo
    )


@app.route("/done")
def setup_done():
    return "<h2 style='color:#68da7b;background:#343635;padding:40px;text-align:center;'>Setup Complete. You may close this window.</h2>"

def run_setup_web():
    from threading import Thread
    def run():
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    t = Thread(target=run, daemon=True)
    t.start()
    # Wait for setup_req to become False
    while setup_req:
        time.sleep(1)

if setup_req:
    logging.info("Setup Run (Web UI)")
    run_setup_web()

if input_mode == 3:
    logging.info("Applying config...")

# Start Camera
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    dur = pre_time
    fpsSTR = str(fps)
    picam2 = Picamera2()
    text_color_bg = (0, 0, 0, 0)
    color = (0, 255, 0, 255)
    origin = (0, 20)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1
    thickness = 2
    def overlay(overlay):
        with MappedArray(overlay, "main") as m:
            x, y = origin
            text_size, _ = cv2.getTextSize(tag_tracking_text, font, scale, thickness)
            text_w, text_h = text_size
            cv2.rectangle(m.array, origin, (x + text_w, y + text_h), text_color_bg, -1)
            cv2.putText(m.array, tag_tracking_text, (x, y + text_h + scale - 1), font, scale, color, thickness)
    picam2.pre_callback = overlay
    preview_config = picam2.create_preview_configuration(main={"size": (640, 480)}, controls={'FrameRate': 15})
    picam2.configure(preview_config)
    picam2.start_preview(Preview.QTGL)
    micro = int((1 / fps) * 1000000)
    video_config = picam2.create_video_configuration(main={"size": (1920, 1080)}, controls={'FrameRate': fps})
    picam2.configure(video_config)
    encoder = H264Encoder()
    encoder.output = CircularOutput(buffersize=int(fps * (dur + 0.2)), outputtofile=False)
except Exception as e:
    logging.error(f"Failed to start camera. Check if the camera is connected and configured properly. {e}")

def main():
    global cam_start
    global tag_tracking_en
    global tag1_tracking_en
    global tag2_tracking_en
    global tag3_tracking_en
    global tag4_tracking_en
    global Captures
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
        except Exception:
            logging.error("Failed to connect to PLC retrying...")
            time.sleep(5)
            plc_initialize = True

        if cam_start:
            picam2.start()
            picam2.start_encoder(encoder)
            TempName="Temp" + ".h264"
            encoder.output.fileoutput = TempName
            encoder.output.start()
            logging.info("Cam Started")
            cam_start = False
            picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        try:
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
                except Exception:
                    tag_tracking_text = "Tag Load Error"
                    logging.error("Tag not found")
            if response.value == 1:
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
                Captures = Captures + 1
                picam2.stop_encoder(encoder)
                picam2.stop()
                cam_start = True
        except Exception:
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
            logging.info(TempName)
            time.sleep(2)
            filename = current_datetime
            logging.info(filename)
            cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + filename +'.mp4'
            logging.info(cmd)
            os.system(cmd)
            time.sleep(10)
            logging.info("Done")
            Captures = Captures + 1
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
            logging.info(TempName)
            time.sleep(2)
            filename = current_datetime
            logging.info(filename)
            cmd = 'ffmpeg -r '+ fpsSTR + ' -i ' + TempName + ' -c copy ' + filename +'.mp4'
            logging.info(cmd)
            os.system(cmd)
            time.sleep(10)
            logging.info("Done")
            Captures = Captures + 1
            picam2.stop_encoder(encoder)
            picam2.stop()
            cam_start = True

if __name__ == "__main__":
    main()

