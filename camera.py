import picamera
import datetime
import time


class Camera:
    def __init__(self):
        self.camera = picamera.Picamera()
        self.recording = False

    def record_time(self, seconds):
        self.start_recording()
        time.sleep(seconds)
        self.stop_recording()

    def start_recording(self):
        if self.recording:
            formatted_time = datetime.datetime.utcnow().isoformat()
            print('[{}][Camera.start_recording] Already recording'.format(
                formatted_time))
        else:
            formatted_datetime = datetime.datetime.utcnow().strftime(
                "%Y%m%d-%H%M%S")
            self.camera.start_recording('video_{}.h264'.format(
                formatted_datetime))
            self.recording = True

            formatted_time = datetime.datetime.utcnow().isoformat()
            print('[{}][Camera.start_recording] Recording started'.format(
                formatted_time))

    def stop_recording(self):
        if not self.recording:
            print('[Camera.stop_recording] Not recording')
        else:
            self.camera.stop_recording()
            self.recording = False

            formatted_time = datetime.datetime.utcnow().isoformat()
            print('[{}][Camera.stop_recording] Recording stopped'.format(
                formatted_time))
