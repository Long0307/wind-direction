import matplotlib.pyplot as plt
import numpy as np

# Định nghĩa các vector và góc của chúng
vectors = {
    'A': 133.75,
    'B': 133.55,
    'C': 191.01
}

# Vẽ các vector và góc của chúng trên đồ thị
fig, ax = plt.subplots()
ax.set_aspect('equal')

for vector, angle in vectors.items():
    # Chuyển đổi góc sang radian
    angle_rad = np.deg2rad(angle)
    # Tính toạ độ của đầu vector
    x = np.cos(angle_rad)
    y = np.sin(angle_rad)

    # Màu sắc của từng vector
    color = 'blue' if vector == 'A' else 'red' if vector == 'B' else 'yellow'

    # Vẽ vector
    ax.quiver(0, 0, x, y, angles='xy', scale_units='xy', scale=1, color=color, label=f'Vector {vector}')
    
    # Vẽ góc ở trên trục toạ độ
    ax.plot([0, x], [0, 0], color=color, linestyle='--')
    ax.text(x * 0.5, 0.1, f'{angle}°', color=color)

# Cấu hình đồ thị
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.axhline(0, color='black',linewidth=0.5)
ax.axvline(0, color='black',linewidth=0.5)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.legend()

# Hiển thị đồ thị
plt.title('Biểu diễn vector và góc trên trục toạ độ')
plt.grid()
plt.show()
