import numpy as np
from time import sleep
import sys
import shutil

theta_spacing = 0.07
phi_spacing = 0.02
illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")

A = 1
B = 1
R1 = 1
R2 = 2
K2 = 5

def render_frame(A: float, B: float) -> np.ndarray:
    # Pega tamanho real do terminal
    term_size = shutil.get_terminal_size()
    width = term_size.columns
    height = term_size.lines

    # Mantém proporção correta
    screen_size = min(height, width)

    K1 = screen_size * K2 * 3 / (8 * (R1 + R2))

    cos_A = np.cos(A)
    sin_A = np.sin(A)
    cos_B = np.cos(B)
    sin_B = np.sin(B)

    output = np.full((height, width), " ")
    zbuffer = np.zeros((height, width))

    phi = np.arange(0, 2 * np.pi, phi_spacing)
    theta = np.arange(0, 2 * np.pi, theta_spacing)

    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    circle_x = R2 + R1 * cos_theta
    circle_y = R1 * sin_theta

    x = (np.outer(cos_B * cos_phi + sin_A * sin_B * sin_phi, circle_x)
         - circle_y * cos_A * sin_B).T

    y = (np.outer(sin_B * cos_phi - sin_A * cos_B * sin_phi, circle_x)
         + circle_y * cos_A * cos_B).T

    z = ((K2 + cos_A * np.outer(sin_phi, circle_x))
         + circle_y * sin_A).T

    ooz = 1 / z

    # CENTRALIZA AQUI 🔥
    xp = (width / 2 + K1 * ooz * x).astype(int)
    yp = (height / 2 - K1 * ooz * y).astype(int)

    L1 = (((np.outer(cos_phi, cos_theta) * sin_B)
           - cos_A * np.outer(sin_phi, cos_theta))
          - sin_A * sin_theta)

    L2 = cos_B * (cos_A * sin_theta
                  - np.outer(sin_phi, cos_theta * sin_A))

    L = np.around((L1 + L2) * 8).astype(int).T
    mask_L = L >= 0
    chars = illumination[np.clip(L, 0, len(illumination)-1)]

    for i in range(x.shape[0]):
        valid = (
            (xp[i] >= 0) & (xp[i] < width) &
            (yp[i] >= 0) & (yp[i] < height)
        )

        mask = mask_L[i] & valid & (ooz[i] > zbuffer[yp[i], xp[i]])

        zbuffer[yp[i], xp[i]] = np.where(mask, ooz[i], zbuffer[yp[i], xp[i]])
        output[yp[i], xp[i]] = np.where(mask, chars[i], output[yp[i], xp[i]])

    return output


print("\033[2J", end="")
print("\033[?25l", end="")

while True:
    A += theta_spacing
    B += phi_spacing

    frame = render_frame(A, B)

    sys.stdout.write("\033[H")
    sys.stdout.write("\n".join("".join(row) for row in frame))
    sys.stdout.flush()

    sleep(0.01)