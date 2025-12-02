import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

N_led = 500

H = 7*12            # tree height [in]
R_bottom = 18.5     # radius at bottom [in]
R_top = 1.5         # radius at top [in]
N_turns = 27        # number of full wraps bottom->top
theta0 = 0.0        # starting angle offset

indices = np.arange(N_led)
t = indices / (N_led - 1)

z = H * t
R = R_bottom + (R_top - R_bottom) * t
theta = 2 * np.pi * N_turns * t + theta0

x = R * np.cos(theta)
y = R * np.sin(theta)

coords = np.stack([x, y, z], axis=1)  # shape (500, 3)

fig = plt.figure(figsize=(8, 10))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(x, y, z, c=z, cmap='viridis', s=10)

ax.set_title("3D LED Coordinate Map (Helical Tree Model)")
ax.set_xlabel("X (in)")
ax.set_ylabel("Y (in)")
ax.set_zlabel("Z (in)")

# Make axes equal so the tree looks correct
max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max() / 2.0

mid_x = (x.max()+x.min()) * 0.5
mid_y = (y.max()+y.min()) * 0.5
mid_z = (z.max()+z.min()) * 0.5

ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)

plt.show()
