import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import PIL.Image, PIL.ImageTk

class VideoPlayer(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Video Player")
        self.video_width = None
        self.video_height = None
        self.frame = tk.Frame(self)
        self.frame.pack()

        self.video_frame = tk.Label(self.frame)
        self.video_frame.pack()

        self.play_button = tk.Button(self.frame, text="Play", command=self.play_video)
        self.play_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.frame, text="Pause", command=self.pause_video)
        self.pause_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.frame, text="Stop", command=self.stop_video)
        self.stop_button.pack(side=tk.LEFT)

        self.open_button = tk.Button(self.frame, text="Open Video", command=self.open_video)
        self.open_button.pack(side=tk.LEFT)

        self.video = None
        self.video_path = None
        self.is_playing = False

    def play_video(self):
        if self.is_playing:
            return

        self.is_playing = True
        self.play_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)

        self.video = cv2.VideoCapture(self.video_path)
        self.update_video()

    def pause_video(self):
        self.is_playing = False
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    def stop_video(self):
        self.is_playing = False
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.video.release()
        self.video = None

    def open_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.flv")])
        self.play_button.config(state=tk.NORMAL)

    def update_video(self):
        if not self.is_playing or self.video is None:
            return

        ret, frame = self.video.read()
        if ret:
            self.detect_skyline(frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = PIL.Image.fromarray(frame)
            imgtk = PIL.ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.config(image=imgtk)

            self.video_frame.after(10, self.update_video)
        else:
            self.is_playing = False
            self.play_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            self.video.release()
            self.video = None

    def detect_skyline(self, frame):
        # Chuyển đổi ảnh sang ảnh xám
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Làm mờ ảnh để giảm nhiễu
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Phát hiện cạnh bằng thuật toán Canny
        edges = cv2.Canny(blurred, 50, 150)

        # Tìm đường kẻ đường bên trái và bên phải
        left_lane, right_lane = self.detect_lanes(edges)

        # Tìm điểm giao của hai lane
        intersection_points = self.find_intersection(left_lane, right_lane)
        # last_five_point = intersection_points[-5:]

        # print(len(last_five_point))
        # intersection_point = np.mean(last_five_point, axis=0)
        # intersection_point = (int(intersection_point[0]), int(intersection_point[1]))
        # print(intersection_point)

        # Vẽ các đường kẻ đường lên ảnh gốc
        self.draw_lane_lines(frame, left_lane)
        self.draw_lane_lines(frame, right_lane)

        # Vẽ điểm giao lên ảnh gốc
        # cv2.circle(frame, intersection_point, 10, (0, 0, 255), -1)
        cv2.line(frame, (0, intersection_points[1]), (frame.shape[1], intersection_points[1]), (0, 0, 255), 2)

        return frame

    def detect_lanes(self, edges):
        # Thực hiện HoughLinesP để tìm các đoạn thẳng biểu diễn vạch kẻ đường
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=150, maxLineGap=50)

        # Phân tách các đoạn thẳng thành lane bên trái và bên phải dựa trên hướng
        left_lane = []
        right_lane = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                # Kiểm tra x2 không bằng x1 để tránh lỗi chia cho 0
                if x2 != x1:
                    slope = (y2 - y1) / (x2 - x1)
                    if slope < 0:  # Lane bên trái có độ dốc âm
                        left_lane.append(line[0])
                    elif slope > 0:  # Lane bên phải có độ dốc dương
                        right_lane.append(line[0])

        return left_lane, right_lane

    def find_intersection(self, left_lane, right_lane):
        # Tính điểm giao của hai lane
        intersection_points = []

        nLane = len(right_lane)
        if len(left_lane) < len(right_lane):
            nLane = len(left_lane)

        if left_lane and right_lane:
            for i in range(nLane):
                llane = left_lane[i]
                rlane = right_lane[i]
                left_slope = (llane[3] - llane[1]) / (llane[2] - llane[0])
                right_slope = (rlane[3] - rlane[1]) / (rlane[2] - rlane[0])

                # Kiểm tra để đảm bảo không có giá trị NaN
                if not np.isnan(left_slope) and not np.isnan(right_slope) and left_slope != right_slope:
                    x_intersection = int((left_slope * llane[0] - right_slope * rlane[0] +
                                          rlane[1] - llane[1]) / (left_slope - right_slope))
                    y_intersection = int(left_slope * (x_intersection - llane[0]) + llane[1])

                    intersection_points.append([x_intersection, y_intersection])

        return intersection_points

    def draw_lane_lines(self, frame, lane):
        if lane:
            for line in lane:
                x1, y1, x2, y2 = line
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
app = VideoPlayer()
app.mainloop()

