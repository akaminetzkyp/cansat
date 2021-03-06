import picamera
import datetime


class Camera:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.recording = False

        self.run = True

    def start_recording(self):
        if self.recording:
            formatted_time = datetime.datetime.utcnow().isoformat()
            print('[{}][Camera.start_recording] Already recording'.format(
                formatted_time))
        else:
            formatted_datetime = datetime.datetime.utcnow().strftime(
                '%Y%m%d-%H%M%S')
            self.camera.start_recording('/home/pi/Desktop/CanSat/videos/'
                                        'video_{}.h264'.format(
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
