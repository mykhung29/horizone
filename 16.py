import cv2

# Đọc ảnh từ file
image = cv2.imread('2024-04-16 15 19 14.png')

# Chuyển ảnh sang màu xám
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

# Hiển thị ảnh màu xám
cv2.imshow('Gray Image', gray_image)

# Hiển thị ảnh xám đã làm mờ
cv2.imshow('Blurred Gray Image', blurred_image)

# Chờ nhấn một phím bất kỳ để đóng cửa sổ
cv2.waitKey(0)

# Đóng cửa sổ khi nhận input từ người dùng
cv2.destroyAllWindows()
