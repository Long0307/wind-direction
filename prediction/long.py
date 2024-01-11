import matplotlib.pyplot as plt
import numpy as np

# Điểm (1, 0) trên trục x
x1, y1 = 1, 0

# Điểm (-1, 0) trên trục x
x2, y2 = -1, 0

# Góc của vectơ đơn vị là 207.51 độ
angle = 207.51
angle_rad = np.radians(angle)

# Tọa độ của điểm mới từ vectơ đơn vị
x_new = np.cos(angle_rad)
y_new = np.sin(angle_rad)

# Vẽ đồ thị
plt.plot([x1, x2, x_new], [y1, y2, y_new], 'o-', label='Vector Points')
plt.axhline(0, color='black',linewidth=0.5)
plt.axvline(0, color='black',linewidth=0.5)

# Đặt tên cho trục x và trục y
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# Chú thích cho các điểm
plt.annotate('(1, 0)', (x1, y1), textcoords="offset points", xytext=(0,10), ha='center')
plt.annotate('(-1, 0)', (x2, y2), textcoords="offset points", xytext=(0,10), ha='center')
plt.annotate(f'({x_new:.2f}, {y_new:.2f})', (x_new, y_new), textcoords="offset points", xytext=(0,10), ha='center')

# Đặt giới hạn cho trục x và trục y
plt.xlim(-1.5, 1.5)
plt.ylim(-1.5, 1.5)

# Hiển thị đồ thị
plt.grid(True)
plt.axhline(0, color='black',linewidth=0.5)
plt.axvline(0, color='black',linewidth=0.5)
plt.title(f'Graph with Vector at {angle} degrees')
plt.legend()
plt.show()
