import numpy as np
import plotly.graph_objs as go

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

fig = go.Figure(data=[go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='markers',
    marker=dict(
        size=4,
        color=z,             # color by height
        colorscale='Viridis',
        opacity=0.8
    )
)])

fig.update_layout(
    title="Interactive 3D LED Coordinate Map (Helical Tree Model)",
    scene=dict(
        xaxis_title='X (in)',
        yaxis_title='Y (in)',
        zaxis_title='Z (in)',
        aspectmode='data'  # ensures equal scale
    ),
    width=800,
    height=900
)
import plotly.io as pio
pio.renderers.default = "browser"   

fig.show()
