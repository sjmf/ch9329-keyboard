#!/usr/bin/env python
import cv2
import numpy
import threading
import logging

logger = logging.getLogger(__name__)

CAMERAS_TO_CHECK = 4

class CaptureDeviceException(Exception):
    pass

class CaptureDevice:
    def __init__(self, fullscreen=False, threaded=False):
        self.cam = None
        self.fullscreen = fullscreen
        self.running = False
        if threaded:
            self.thread = threading.Thread(target=self.capture)
        else:
            self.thread = None

    def run(self):
        if not isinstance(self.thread, threading.Thread):
            raise CaptureDeviceException("Capture device not running in thread")
        
        self.thread.start()
        self.thread.join()

    def start(self):
        if not isinstance(self.thread, threading.Thread):
            raise CaptureDeviceException("Capture device not running in thread")
        
        self.thread.start()

    def stop(self):
        self.running = False

        if isinstance(self.thread, threading.Thread):
            self.thread.join()

    def _cameraIndices(self):
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
        logger.info(f"Starting video in {"fullscreen" if self.fullscreen else "window"}...")

        cameras = self._cameraIndices()
        logger.info(f"Found {len(cameras)} cameras.")
        logger.debug(cameras)

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
                # 50 = 20fps?
                if cv2.waitKey(50) == exitKey or not self.running:
                    cam.release()
        except cv2.error as e:
            logger.error(e)
        finally:
            self.running = False

            # Release the capture and writer objects
            logger.info("Camera released. Destroying video window...")
            cv2.destroyWindow("kvm")

if __name__ == "__main__":
    cap = CaptureDevice(fullscreen=False)
    cap.capture()