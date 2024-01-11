import math

# # Chuyển đổi 17 độ thành radian
# degree = 1.96
# radian = math.radians(degree)

# # Tính sin của góc 17 độ
# sin_value = math.sin(1.00036816406)
# print(sin_value)
# # Nhân kết quả với 4.4
# result = sin_value * 3.95

# print(result)  # In ra kết quả

# result = math.sqrt((1.687384377*1.687384377) + (2.7548370786*2.7548370786))

# print(1.687384377 + 2.7548370786)  # In ra kết quả

# import math

# center_lat = 35.4475107474
# center_lot = 129.3075294254 
# ws = 3.23
# vec_x = 1.687384377
# vec_y = 2.7548370786

# # Tính độ dài vector đường chéo 
# length = math.sqrt(vec_x**2 + vec_y**2)

# # Áp dụng Pytago
# wd2 = length**2 - ws**2 

# # Tính wd
# wd = math.sqrt(wd2)

# print(wd)

# import math

# v = 35.456703  # Thành phần hoành độ của vectơ gió
# u = 129.328354  # Thành phần tung độ của vectơ gió

# # Tính hướng gió
# direction = math.atan2(v, u)

# # Chuyển đổi từ radian sang độ
# direction_degree = math.degrees(direction)

# print(f"Hướng gió: {direction_degree} độ")

# import math

# vec_x = 1.687384377  # Thành phần hoành độ của vectơ gió
# vec_y = 2.7548370786  # Thành phần tung độ của vectơ gió

# # Tính hướng giós
# if vec_x > 0:
#     wind_direction = (90 - math.atan(vec_y / vec_x) * 180 / math.pi) % 360
# elif vec_x < 0:
#     wind_direction = (270 - math.atan(vec_y / vec_x) * 180 / math.pi) % 360
# else:
#     if vec_y > 0:
#         wind_direction = 0
#     elif vec_y < 0:
#         wind_direction = 180
#     else:
#         wind_direction = None

# print(f"Hướng gió: {wind_direction} độ")

# import math

# x = 0.612  # Góc được tính sin

# sin_value = math.sin(x)
# sin_in_degrees = math.degrees(math.asin(sin_value))

# print(f"sin(0.612) ≈ {sin_value}")
# print(f"sin(0.612) ≈ {sin_in_degrees} độ")

# import matplotlib.pyplot as plt

# # Tạo hệ tọa độ
# plt.figure(figsize=(8, 6))
# plt.axhline(0, color='black',linewidth=0.5)
# plt.axvline(0, color='black',linewidth=0.5)

# # Thông số vectơ
# vec_x = 1.687384377  # Thành phần hoành độ của vectơ gió
# vec_y = 2.7548370786  # Thành phần tung độ của vectơ gió
# center_lot = 129.3075294254  # Kinh độ tâm
# center_lat = 35.4475107474  # Vĩ độ tâm

# # Vẽ vectơ từ tọa độ (center_lot, center_lat) đến (vec_x, vec_y)
# plt.quiver(center_lot, center_lat, vec_x, vec_y, angles='xy', scale_units='xy', scale=1, color='blue', label='Vector wind')

# # Đặt tên cho các trục và tiêu đề
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.title('Vector Wind')

# # Hiển thị hướng vector
# plt.text(center_lot + vec_x, center_lat + vec_y, f"wd = 211.49°, ws = 3.23", color='blue')

# # Hiển thị grid
# plt.grid(visible=True)

# # Hiển thị chú thích
# plt.legend()

# # Hiển thị hình vẽ
# plt.show()

import math

# print(math.degrees(math.sin(-1.348693/2.923)))
# w1 = (1/0.0228)/((1/0.0228)+(1/0.0213)+(1/0.0218))
# w2 = (1/0.0213)/((1/0.0228)+(1/0.0213)+(1/0.0218))
# w3 = (1/0.0218)/((1/0.0228)+(1/0.0213)+(1/0.0218))
# # result = math1 + math3 + math2
# v1 = ((w1*0.056)+(w2*0.135)+(w3*(-4.218)))
# v2 = ((w1*(-2.549))+(w2*(-3.947))+(w3*(-1.249)))
# v1 = -1.4015495056628557
# ws = 1.94
# ws = math.sqrt((v1*v1)+(v2*v2))

# cal = v1/ws

# degree_angle = math.degrees(cal)

# print("v1 = ", v1)
# print("v2 = ", v2)
# print("ws = ", ws)
# degree_angle = 270 + (90 - (degree_angle * (-1)))
# print("Độ thật = ", (degree_angle * (-1))+90)
# print("math 2 = ", math2
# print("math 3 = ", math3)
# print("result = ", result)

vec_x = -1.3331792325414331

# vec_y = 1.3995899497340596

# ws = math.sqrt((vec_x*vec_x)+(vec_y*vec_y))

ws = 2.9237683424694527

print("ws = ", ws)

radian_angle = math.asin(vec_x/ws)

degree_angle = math.degrees(radian_angle)

print("degree_angle = ", degree_angle)