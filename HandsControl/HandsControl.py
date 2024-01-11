import time

import cv2
import mediapipe as mp
import pyautogui
import mouse

from .utils import *


class HandsData:
    def __init__(self):
        x, y = 0, 0
        self.cords = [x, y]
        self.map_cords = [x, y]

    def set_data(self, cords):
        self.cords = cords
        self.map_cords = [
            remap(self.cords[0], 0, 1280 + 50, 0, 1920 + 50),
            remap(self.cords[1], 0, 720 + 50, 0, 1080 + 50),
        ]


class AiHands:
    """
    dist_to_click: px
    flip_code: 1 - horizontal, 0 - vertical
    camera_frame_width: px,
    camera_frame_height: px,
    """

    # pyautogui.MINIMUM_DURATION = 0.1
    # pyautogui.MINIMUM_SLEEP = 0.1
    # pyautogui.PAUSE = 0.1

    def __init__(
            self,
            dist_to_click: int = 50,
            camera_frame_width: int = 1280,
            camera_frame_height: int = 720,
            screen_width: int = get_screensize()[0],
            screen_height: int = get_screensize()[1],
            flip_code: int = None,
            camera_id: int = 0,
            window_title: str = "AiHands"
    ):
        self.f1 = HandsData()
        self.f2 = HandsData()

        # self.timer = 0

        self.dist_to_click = dist_to_click
        self.cam_width = camera_frame_width
        self.cam_height = camera_frame_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.flip_code = flip_code
        self.window_title = window_title

        self.camera = cv2.VideoCapture(camera_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils

    def control(self):
        """
        mouse control
        :return: None
        """
        # if (
        #         # (xy[0][0] > 50 and xy[0][1] > 50)
        #         # and (xy[1][0] < 1280 - 50 and xy[1][1] < 720 - 50)
        #         1
        # ):

        # millis = time.time() * 1000

        # if millis - self.timer >= 100:
        #     self.timer = millis
        #     mouse.move(self.f1.map_cords[0], self.f1.map_cords[1], absolute=True, duration=0)
        #     pyautogui.moveTo(self.f1.map_cords[0], self.f1.map_cords[1], duration=0)

        edist = e_dist(
            self.f1.cords[0], self.f1.cords[1],
            self.f2.cords[0], self.f2.cords[1]
        )
        # print('[INFO]', edist)
        x_start, y_start = mouse.get_position()

        mouse.move(self.f1.map_cords[0], self.f1.map_cords[1], absolute=True, duration=0)
        if edist < self.dist_to_click:
            # pyautogui.leftClick(
            #     self.f1.map_cords[0],
            #     self.f1.map_cords[1],
            #     interval=0.1
            # )
            # mouse.click('left')

            # mouse.drag(x_start, y_start, self.f1.map_cords[0], self.f1.map_cords[1], absolute=False, duration=0)
            # mouse.drag(x_start, y_start, self.f1.map_cords[0], self.f1.map_cords[1], absolute=True, duration=0)
            mouse.press('left')
            print("[LOG] LEFT")
        else:
            mouse.release('left')
            # mouse.move(self.f1.map_cords[0], self.f1.map_cords[1], absolute=True, duration=0)

    def processing(self):
        """
        processing incoming information from camera
        :return: None
        """
        while True:
            good, img = self.camera.read()
            if self.flip_code is not None:
                img = cv2.flip(img, self.flip_code)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # cv2.rectangle(img, (self.dist_to_click, self.dist_to_click),
            #               (self.camera_frame_width - self.dist_to_click,
            #                self.camera_frame_height - self.dist_to_click), (255, 255, 255), 2)

            results = self.hands.process(imgRGB)
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

                    for id, point in enumerate(handLms.landmark):
                        width, height, color = img.shape
                        width, height = int(point.x * height), int(point.y * width)

                        cv2.putText(img, str(id), (width, height),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                        if id == 8:
                            cv2.circle(img, (width, height), 10, (255, 0, 255), cv2.FILLED)
                            self.f1.set_data([width, height])
                        if id == 4:
                            cv2.circle(img, (width, height), 10, (0, 255, 255), cv2.FILLED)
                            self.f2.set_data([width, height])

                    self.control()

            cv2.imshow(self.window_title, img)

            if cv2.waitKey(1) == 27:
                break
        self.camera.release()
        cv2.destroyAllWindows()
