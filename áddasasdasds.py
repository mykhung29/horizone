import matplotlib.pyplot as plt


def find_intersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # Tính hệ số góc của mỗi đoạn thẳng
    m1 = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else float('inf')
    m2 = (y4 - y3) / (x4 - x3) if (x4 - x3) != 0 else float('inf')

    # Tính hệ số góc y-tổng của mỗi đoạn thẳng
    b1 = y1 - m1 * x1 if m1 != float('inf') else float('inf')
    b2 = y3 - m2 * x3 if m2 != float('inf') else float('inf')

    # Kiểm tra xem hai đoạn thẳng có song song không
    if m1 == m2:
        if b1 == b2:
            return "Hai đoạn thẳng trùng nhau"
        else:
            return "Hai đoạn thẳng song song, không có giao điểm"

    # Tìm tọa độ x của điểm giao nhau
    x_intersect = (b2 - b1) / (m1 - m2)

    # Tìm tọa độ y của điểm giao nhau
    y_intersect = m1 * x_intersect + b1

    return (x_intersect, y_intersect)


# Tọa độ của hai đoạn thẳng
line1 = [767, 502, 934, 457]
line2 = [709, 365, 1026, 541]

# Chuyển đổi tọa độ thành các cặp (x, y) cho mỗi đoạn thẳng
x_values1 = [line1[0], line1[2]]
y_values1 = [line1[1], line1[3]]

x_values2 = [line2[0], line2[2]]
y_values2 = [line2[1], line2[3]]

# Tìm điểm giao điểm của hai đoạn thẳng
intersection = find_intersection(line1, line2)
print(intersection)
# Vẽ đồ thị
plt.plot(x_values1, y_values1, label='Đường thẳng thứ nhất ', color='blue')
plt.plot(x_values2, y_values2, label='Đường thẳng thứ hai', color='red')

# In điểm giao điểm lên đồ thị
# if isinstance(intersection, tuple):
#     plt.scatter(*intersection, color='green', label='Intersection')

# Đặt tiêu đề và nhãn trục
plt.title('Biểu đồ đoạn thẳng và điểm giao điểm trên tọa độ XY')
plt.xlabel('Trục X')
plt.ylabel('Trục Y')

# Hiển thị chú thích
plt.legend()

# Hiển thị đồ thị
plt.grid(True)
plt.gca().invert_yaxis()  # Đảo ngược trục y để phù hợp với hệ tọa độ thông thường
plt.show()
