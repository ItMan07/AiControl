import cv2
import mediapipe as mp
import pyautogui

from utils import *


class HandsData:
    def __init__(
            self,
            xy=None,
            map_xy=None
    ):
        if map_xy is None:
            map_xy = []
        if xy is None:
            xy = []
        self.xy = xy
        self.map_xy = map_xy

    def __call__(self):
        return self.xy, self.map_xy


class AiHands:
    def __init__(
            self,
            dist_to_click=50,
            camera_frame_width=1280,
            camera_frame_height=720,
            screen_width=get_screensize()[0],
            screen_height=get_screensize()[1],
            flip_code=1,
            camera_id=0,
    ):
        self.dist_to_click = dist_to_click
        self.cam_width = camera_frame_width
        self.cam_height = camera_frame_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.flip_code = flip_code  # 0 - horizontal, 1 - vertical

        self.camera = cv2.VideoCapture(camera_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils

    def recognition(self):
        pass
        # while True:
        #     xy = self.get_cords()

    def get_cords(self):
        x, y = 0, 0
        xy = [[x, y] for _ in range(5)]
        xy_rm = [[x, y] for _ in range(5)]

        for _ in iter(int, 1):
            good, img = self.camera.read()
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
                            xy[0] = [width, height]
                            f1 = HandsData([width, height])
                            print(f1.xy)
                        if id == 4:
                            cv2.circle(img, (width, height), 10, (0, 255, 255), cv2.FILLED)
                            xy[1] = [width, height]
                            f2 = HandsData([width, height])

                    if (
                            # (xy[0][0] > 50 and xy[0][1] > 50)
                            # and (xy[1][0] < 1280 - 50 and xy[1][1] < 720 - 50)
                            1
                    ):
                        xy_rm[0][0] = remap(xy[0][0], 0, self.cam_width, 0,
                                            self.screen_width + self.dist_to_click)
                        xy_rm[0][1] = remap(xy[0][1], 0, self.cam_height, 0,
                                            self.screen_height + self.dist_to_click)
                        print(xy_rm[0][0], xy_rm[0][1])

                        pyautogui.moveTo(xy_rm[0][0], xy_rm[0][1], duration=0)

                        if e_dist(xy[0][0], xy[0][1], xy[1][0], xy[1][1]) < self.dist_to_click:
                            pyautogui.leftClick(x=xy_rm[0][0], y=xy_rm[0][1], interval=0.5)
                            print("OK")

            cv2.imshow("Image", img)

            if cv2.waitKey(1) == 27:
                break
        self.camera.release()
        cv2.destroyAllWindows()
