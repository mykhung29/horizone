import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import PIL.Image, PIL.ImageTk
import numpy as np
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

    # brightness = cv2.mean(frame)[0]
    # print(brightness)
    # brightness_threshold = 140
    # if brightness < brightness_threshold:
    #     brightness_factor = 2  # Có thể điều chỉnh giá trị này để tăng hoặc giảm độ sáng
    #     frame = cv2.convertScaleAbs(frame, alpha=brightness_factor, beta=0)
    def open_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.flv")])
        self.play_button.config(state=tk.NORMAL)

    def update_video(self):
        if not self.is_playing or self.video is None:
            return

        ret, frame = self.video.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (5, 5), 0)

        # Phát hiện cạnh bằng thuật toán Canny
        frame = cv2.Canny(frame, 70, 150)
        left_lane, right_lane = self.detect_lanes(frame)
        if ret:
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
        edges = cv2.Canny(blurred, 70, 150)

        # Tìm đường kẻ đường bên trái và bên phải
        left_lane, right_lane = self.detect_lanes(edges)

        # Tìm điểm giao của hai lane
        intersection_point = self.find_intersection(left_lane, right_lane)

        # last_five_point = intersection_point[-5:]
        # print(intersection_point)
        #
        # print(last_five_point)




        # Vẽ các đường kẻ đường lên ảnh gốc
        self.draw_lane_lines(frame, left_lane)
        self.draw_lane_lines(frame, right_lane)

        # Vẽ điểm giao lên ảnh gốc
        # cv2.circle(frame, intersection_point, 10, (0, 0, 255), -1)
        cv2.line(frame, (0, intersection_point[1]), (frame.shape[1], intersection_point[1]), (0, 0, 255), 2)

        return frame

    def detect_lanes(self, edges):
        # Thực hiện HoughLinesP để tìm các đoạn thẳng biểu diễn vạch kẻ đường
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=130, maxLineGap=30)

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
        intersection_point = (0, 0)

        if left_lane and right_lane:
            left_slope = (left_lane[0][3] - left_lane[0][1]) / (left_lane[0][2] - left_lane[0][0])
            right_slope = (right_lane[0][3] - right_lane[0][1]) / (right_lane[0][2] - right_lane[0][0])

            # Kiểm tra để đảm bảo không có giá trị NaN
            if not np.isnan(left_slope) and not np.isnan(right_slope) and left_slope != right_slope:
                x_intersection = int((left_slope * left_lane[0][0] - right_slope * right_lane[0][0] +
                                      right_lane[0][1] - left_lane[0][1]) / (left_slope - right_slope))
                y_intersection = int(left_slope * (x_intersection - left_lane[0][0]) + left_lane[0][1])

                intersection_point = (x_intersection, y_intersection)
                print("lane trai",left_lane)
                print("lane phai",right_lane)
                print(intersection_point)

        return intersection_point

    def draw_lane_lines(self, frame, lane):
        if lane:
            for line in lane:
                x1, y1, x2, y2 = line
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
app = VideoPlayer()
app.mainloop()

