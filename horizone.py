import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
class SkylineDetectionApp:
    def __init__(self, master):
        self.video_width = None
        self.video_height = None

        self.master = master
        self.master.title("Skyline Detection Video Player")

        self.video_path = None
        self.video_player = None
        self.paused = False

        # Tạo các thành phần giao diện
        self.label = tk.Label(master, text="Chọn video để phát:")
        self.label.pack(pady=10)

        self.browse_button = tk.Button(master, text="Chọn Video", command=self.choose_video)
        self.browse_button.pack(pady=10)

        self.play_button = tk.Button(master, text="Phát/Tạm dừng", command=self.toggle_play_pause)
        self.play_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Dừng", command=self.stop_video)
        self.stop_button.pack(pady=10)

    def choose_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        self.label.config(text=f"Đang phát: {self.video_path}")
        self.play_video()

    def play_video(self):
        if self.video_path:
            self.video_player = cv2.VideoCapture(self.video_path)
            self.play()

    def play(self):
        if self.video_player.isOpened() and not self.paused:
            ret, frame = self.video_player.read()
            if ret:
                # Gọi hàm detect_skyline để phát hiện đường chân trời
                frame_with_skyline = self.detect_skyline(frame)

                # Hiển thị video với đường chân trời được làm nổi bật
                cv2.imshow("Skyline Detection Video Player", frame_with_skyline)
                self.master.after(10, self.play)
            else:
                self.video_player.release()
                cv2.destroyAllWindows()

    def toggle_play_pause(self):
        self.paused = not self.paused
        if not self.paused:
            self.play()

    def stop_video(self):
        if self.video_player:
            self.video_player.release()
            cv2.destroyAllWindows()
            self.label.config(text="Chọn video để phát:")

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
        intersection_point = self.find_intersection(left_lane, right_lane)

        # Vẽ các đường kẻ đường lên ảnh gốc
        self.draw_lane_lines(frame, left_lane)
        self.draw_lane_lines(frame, right_lane)

        # Vẽ điểm giao lên ảnh gốc
        # cv2.circle(frame, intersection_point, 10, (0, 0, 255), -1)
        cv2.line(frame, (0, intersection_point[1]), (frame.shape[1], intersection_point[1]), (0, 0, 255), 2)

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

        return intersection_point

    def draw_lane_lines(self, frame, lane):
        if lane:
            for line in lane:
                x1, y1, x2, y2 = line
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

if __name__ == "__main__":
    root = tk.Tk()
    app = SkylineDetectionApp(root)
    root.mainloop()
