import pygame
from numba import jit
import numpy as np

# sets viewing area of fractal
MIN_X = DEFAULT_MIN_X = -2
MAX_X = DEFAULT_MAX_X = 2
MIN_Y = DEFAULT_MIN_Y = -2
MAX_Y = DEFAULT_MAX_Y = 2

# sets viewing area of display
WIDTH, HEIGHT = 1000, 1000
MAX_ITERATIONS_DEFAULT = MAX_ITERATIONS_COUNT = 200


# colorsys function to convert hsv color to rgb color values
@jit(nopython=True)
def hsv_to_rgb(h, s, v):
    if s == 0.0: v*=255; return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)


# convert a value from one range to another
@jit(nopython=True)
def convert_ranges(value, value_min, value_max, new_min, new_max):
    return (((value - value_min) * (new_max - new_min)) / (value_max - value_min)) + new_min


# calculates the escape radius of a complex number
@jit(nopython=True)
def num_iterations_mandelbrot(c, MAX_ITERATIONS):  # c must be complex number
    i = 0
    z = 0
    while z.real < 2.0 and z.imag < 2.0 and i < MAX_ITERATIONS:
        z = z**2 + c
        i += 1
    return i


# populates an array with rgb values of mandelbrot set
@jit(nopython=True)
def create_Mandelbrot(MIN_X, MAX_X, MIN_Y, MAX_Y, MAX_ITERATIONS):
    mandelbrot_array = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)

    x_count = y_count = -1
    num_iterations = 0
    rgb_color = 0

    for x in np.linspace(MIN_X, MAX_X, WIDTH):
        y_count = -1  # reset y_count every new row
        x_count += 1
        for y in np.linspace(MIN_Y, MAX_Y, HEIGHT):
            y_count += 1
            num_iterations = num_iterations_mandelbrot(
                complex(x, y), MAX_ITERATIONS)
            if num_iterations < MAX_ITERATIONS:
                rgb_color = hsv_to_rgb(num_iterations/MAX_ITERATIONS, 1, 1) 
                # rgb_color = [num_iterations*5, num_iterations*2, num_iterations*3]
                mandelbrot_array[x_count, y_count, 0:3] = rgb_color
    return mandelbrot_array


pygame.init()
pygame.display.set_caption("Fractal Viewer")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
array = create_Mandelbrot(MIN_X, MAX_X, MIN_Y, MAX_Y, MAX_ITERATIONS_COUNT)
pygame.surfarray.blit_array(screen, array)

running = True
x = 0
y = 0
zoom_change = 5
iteration_change = 200
zoom = 1
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x = convert_ranges(pygame.mouse.get_pos()[
                               0], 0, WIDTH, MIN_X, MAX_X)
            y = convert_ranges(pygame.mouse.get_pos()[
                               1], 0, HEIGHT, MIN_Y, MAX_Y)
            # print(f"{x:.30f}, {y:.30f}")
            if event.button == 1: # right click
                MAX_ITERATIONS_COUNT += iteration_change
                zoom /= zoom_change
                MIN_X = x - zoom
                MAX_X = x + zoom
                MIN_Y = y - zoom
                MAX_Y = y + zoom

            elif event.button == 3: # left click
                if MAX_ITERATIONS_COUNT - iteration_change < MAX_ITERATIONS_DEFAULT:
                    MAX_ITERATIONS_COUNT = MAX_ITERATIONS_DEFAULT
                else:
                    MAX_ITERATIONS_COUNT -= iteration_change
                zoom *= zoom_change
                MIN_X = x - zoom
                MAX_X = x + zoom
                MIN_Y = y - zoom
                MAX_Y = y + zoom

            elif event.button == 2: # middle click
                MAX_ITERATIONS_COUNT = MAX_ITERATIONS_DEFAULT
                zoom = 1
                MIN_X = DEFAULT_MIN_X
                MAX_X = DEFAULT_MAX_X
                MIN_Y = DEFAULT_MIN_Y
                MAX_Y = DEFAULT_MAX_Y

            array = create_Mandelbrot(
                MIN_X, MAX_X, MIN_Y, MAX_Y, MAX_ITERATIONS_COUNT)
            pygame.surfarray.blit_array(screen, array)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pygame.image.save(screen, f"{x}, {y}.png")

        pygame.display.flip()
pygame.quit()
