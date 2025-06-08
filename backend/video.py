#!/usr/bin/env python
import cv2
import sys
import numpy
import threading

CAMERAS_TO_CHECK = 4

class CaptureDevice:
    def __init__(self, fullscreen=False):
        self.cam = None
        self.fullscreen = fullscreen
        self.running = False
        self.thread = threading.Thread(target=self.capture)

    def run(self):
        self.thread.start()
        self.thread.join()

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
    
    def cameraIndices(self):
        cameras = []
        # check for cameras
        for index in range(0, CAMERAS_TO_CHECK):
            cam = cv2.VideoCapture(index)
            cv2.setLogLevel(-1)
            if cam.isOpened():
                if type(cam.read()[1]) is numpy.ndarray:
                    # Successfully read a frame from camera. It works.
                    cameras.append({
                        "index": index, 
                        "width": int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                        "height": int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)), 
                        "fps": cam.get(cv2.CAP_PROP_FPS), 
                        "format": int(cam.get(cv2.CAP_PROP_FORMAT))
                    })
                cam.release()

        return cameras

    def capture(self, camIndex=0, exitKey=27):
        cameras = self.cameraIndices()
        print(f"Found {len(cameras)} cameras.")
        props = cameras[camIndex]

        cv2.namedWindow("kvm", cv2.WINDOW_NORMAL)
        if self.fullscreen:
            cv2.setWindowProperty("kvm", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Open the default camera
        cam = cv2.VideoCapture(props["index"])

        try:
            self.running = True
            while cam.isOpened():
                # Display the captured frame
                _, frame = cam.read()
                cv2.imshow('kvm', frame)

                # Default is 'ESC' to exit the loop
                if cv2.waitKey(50) == exitKey or not self.running:
                    cam.release()
        except cv2.error as e:
            print(e, file=sys.stderr)
        finally:
            self.running = False

        # Release the capture and writer objects
        cv2.destroyWindow("kvm")

if __name__ == "__main__":
    cap = CaptureDevice(fullscreen=False)
    cap.capture()