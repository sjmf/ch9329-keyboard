#!/usr/bin/env python
from typing import List
import cv2
import numpy
import threading
import logging

logger = logging.getLogger(__name__)

CAMERAS_TO_CHECK = 10
MAX_CAM_FAILURES = 1


class CaptureDeviceException(Exception):
    pass


class CameraProperties:
    """
    Describe a reference to a camera attached to the system
    """

    index: int
    width: int
    height: int
    fps: int
    format: int

    FORMAT_STRINGS = ["CV_8U", "CV_8S", "CV_16U", "CV_16S", "CV_32S", "CV_32F", "CV_64F", "Unknown"]

    def __init__(self, index, width, height, fps, format):
        self.index = index
        self.width = width
        self.height = height
        self.fps = fps
        self.format = format

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        return f"{self.index}: {self.width}x{self.height}@{self.fps}fps ({self.FORMAT_STRINGS[self.format % 8]}/{self.format})"


class CaptureDevice:
    def __init__(self, cam: cv2.VideoCapture = None, fullscreen=False, threaded=False):
        self.cam = cam
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

    @staticmethod
    def getCameras() -> List[CameraProperties]:
        cameras: List[CameraProperties] = []
        failures = 0

        # check for cameras
        for index in range(0, CAMERAS_TO_CHECK):
            cam = cv2.VideoCapture(index)
            cv2.setLogLevel(-1)
            if cam.isOpened():
                if type(cam.read()[1]) is numpy.ndarray:
                    # Successfully read a frame from camera. It works.
                    cameras.append(
                        CameraProperties(
                            index=index,
                            width=int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
                            height=int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                            fps=int(cam.get(cv2.CAP_PROP_FPS)),
                            format=int(cam.get(cv2.CAP_PROP_FORMAT)),
                        )
                    )
                else:
                    failures += 1
                cam.release()
            else:
                failures += 1

            if failures >= MAX_CAM_FAILURES:
                break

        logger.info(f"Found {len(cameras)} cameras.")
        logger.debug(cameras)

        return cameras

    def openWindow(self, windowTitle="kvm"):
        windowstring = "fullscreen" if self.fullscreen else "window"
        logger.info(f"Starting video in {windowstring} for window '{windowTitle}'...")

        cv2.namedWindow(windowTitle, cv2.WINDOW_NORMAL)
        if self.fullscreen:
            cv2.setWindowProperty(windowTitle, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def capture(self, exitKey=27, windowTitle="kvm"):
        # Autonomous capture method can be called to do everything in one
        if not self.cam:
            self.autoSelectCamera()
        self.openWindow()
        self.frameLoop(exitKey=exitKey, windowTitle=windowTitle)

    def autoSelectCamera(self, camIndex=0):
        # Open the default camera
        cameras = CaptureDevice.getCameras()
        self.setCamera(camIndex=cameras[camIndex].index)

    def setCamera(self, camIndex=0):
        self.cam = cv2.VideoCapture(camIndex)

    def frameLoop(self, exitKey=27, windowTitle="kvm"):
        try:
            self.running = True
            while self.cam.isOpened():
                # Display the captured frame
                _, frame = self.cam.read()
                cv2.imshow(windowTitle, frame)

                # Default is 'ESC' to exit the loop
                # 50 = 20fps?
                if cv2.waitKey(50) == exitKey or not self.running:
                    self.cam.release()
        except cv2.error as e:
            logger.error(e)
        finally:
            self.running = False

            # Release the capture and writer objects
            logger.info(f"Camera released. Destroying video window '{windowTitle}'...")
            cv2.destroyWindow(windowTitle)


if __name__ == "__main__":
    cap = CaptureDevice(fullscreen=False)
    cap.capture()
