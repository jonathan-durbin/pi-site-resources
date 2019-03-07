#! /usr/bin/env python3
# french_mandelbrot.py
"""Generate a fractal using a normal map technique."""


def mandel(save_name: ('<DIRECTORY>/', 'positional'), th,
           angle: ('Angle of light', 'positional', None, float),
           image_size=(340*5, 200*5),
           cent_point: ('Center of image', 'option', 'c', tuple) = (-0.75, 0),
           zoom_level: ('Zoom Level', 'option', 'z', 'float') = 1):
    """Generate the mandelbrot set."""
    from PIL import Image
    from math import pi
    from cmath import exp  # math with complex numbers
    from datetime import datetime
    from colour import Color

    start_time = datetime.now()

    # Initialize a black image,
    #   load in the pixels of the image to an array 'pixel'
    image = Image.new('RGB', image_size, 'white')
    pixel = image.load()

    # Find the boundaries of the complex plane,
    #   which the fractal will be generated based on the aspect ratio.
    # Calculate image bounds like normal
    x_max = 2
    aspect_ratio = image_size[1]/image_size[0]
    if aspect_ratio > 1:
        y_max = x_max / aspect_ratio
    else:
        y_max = x_max * aspect_ratio
    x_min = -x_max
    y_min = -y_max

    # Zooming, if desired
    x_max = cent_point[0] + x_max * 1/zoom_level
    y_max = cent_point[1] + y_max * 1/zoom_level
    x_min = cent_point[0] + x_min * 1/zoom_level
    y_min = cent_point[1] + y_min * 1/zoom_level

    # Set the scaling factor -
    #   the mandelbrot set is defined between -2 and 2,
    #   not the pixel size of the image
    x_size = (x_max - x_min)/image.size[0]
    y_size = (y_max - y_min)/image.size[1]

    # coloring function
    # list of colors for the whole image across x values
    #  cp1 = [[19, 89, 152],
    #         [20, 131, 199],
    #         [77, 159, 221],
    #         [145, 225, 242],
    #         [88, 195, 192]]
    cp2 = [[1, 31, 75],
           [3, 57, 108],
           [0, 91, 150],
           [100, 151, 177],
           [179, 205, 224]]

    cp3 = [[216,216,216],
           [177,177,177],
           [126,126,126],
           [71,71,71],
           [26,26,26]]
    cp3=list(reversed(cp3))

    def create_smooth_color_list(color_palette, thickness=100):
        n_cp = [[i/255 for i in j] for j in color_palette]
        color_list = []
        for i, _ in enumerate(n_cp):
            cfrom = Color(rgb=tuple(n_cp[i % len(n_cp)]))
            cto = Color(rgb=tuple(n_cp[(i+1) % len(n_cp)]))
            color_object_list = list(cfrom.range_to(cto, thickness))
            color_list.append([j.rgb for j in color_object_list])
        # flatten the list
        color_list = [item for sublist in color_list for item in sublist]
        return color_list

    # initialize a smooth list of colors, taken from a palette
    color_list = create_smooth_color_list(cp3, th)

    # For each pixel in the image, iterate z_next = z^2 + c,
    #   where z is imaginary and c is the complex coordinate value
    ITERATIONS = 250
    height_factor = 1.5  # height factor for incoming light
    angle = angle * pi/180  # incoming direction of light, converted to radians
    vec = exp(1j*angle)  # unit 2D vector in this direction
    # 3D vector: (v.real, v.imag, height_factor)

    R = 100  # don't make this too small

    for x in range(image.size[0]):
        if x % 10 == 0:
            percentage = round((x+10)/image_size[0] * 100)
            print(str(percentage) + '%', end='\r')
#        if x == image.size[0]-1:
#            print()
        for y in range(image.size[1]):
            c = complex((x_min + x * x_size),
                        (y_min + y * y_size))
            z = c
            dc = 1 + 0j
            der = dc
            reason = 'INSIDE'
            for n in range(ITERATIONS):
                if abs(z) > R*R:
                    reason = 'OUTSIDE'
                    break
                new_z = z**2 + c
                new_der = der*2*z + dc
                z = new_z
                der = new_der
            if reason == 'INSIDE':
                # final_tuple = funky_colors(x, y, z)
                dist = abs(z) * len(color_list)
                color_tuple = color_list[int(dist) % len(color_list)]
                pixel[x, y] = (int(color_tuple[0]*255),
                               int(color_tuple[1]*255),
                               int(color_tuple[2]*255))
            else:  # reason == OUTSIDE
                u = z/der
                u = u/abs(u)  # normal vector: (u.re, u.im, 1)
                # dot product with incoming light
                t = u.real*vec.real + u.imag*vec.imag + height_factor  # * 1
                t = t/(1+height_factor)  # rescale so t is not bigger than 1
                if t < 0:
                    t = 0
                pixel[x, y] = (int(t*255), int(t*255), int(t*255))

    # calculate total time in minutes
    total_time = (datetime.now() - start_time).total_seconds()/60
    if '.png' not in save_name:
        print('appending ".png"')
        save_name += '.png'

    print('fractal created in', round(total_time, 3), 'minutes\n',
          'saved as', save_name)

    # Save the image
    image.save(save_name)


def array_to_image(arr):
    """Convert a numpy array to grayscale or RGB image.

    The numpy array `arr` can either have the shape (w, h) for a grayscale
        image result or a (3, w, h) shape for an RGB image.
    `arr` is expected to have values in the range of 0.0..1.0.
        THIS FUNCTION IS FROM:
        github.com/dbohdan/unflattener/blob/master/unflattener/normalmapgen.py
    """
    from PIL import Image

    def make_image(arr):
        """Convert numpy array to image."""
        return Image.fromarray((arr * 255).astype('uint8'))

    # Produce an RGB image from an array with three values per point.
    if arr.ndim == 3:
        ni = list(range(3))
        for i in ni:
            ni[i] = make_image(arr[i])
        else:
            res = Image.merge('RGB', ni)
    # Produce a grayscale image from a 1-value array.
    elif arr.ndim == 2:
        res = make_image(arr)
    else:
        raise ValueError
    return res


if __name__ == '__main__':
    #  import plac
    #  plac.call(mandel)
    #  from math import pi, cos, sin
    mandel(save_name='images/smoke_color_reversed.png',
           th=100,
           angle=270,
           image_size=(340*10, 200*10),
           cent_point=(-0.75, 0),
           zoom_level=1)

#    from time import sleep
#    from numpy import arange
#    for th in arange(10, 200, 5):
#        print('generating ' + str(round(th, 3)))
##        theta = pi*i
##        r = (1 - cos(theta))/2
##        x = r*cos(theta)+0.25
##        y = r*sin(theta)
#        mandel(save_name='changing_color_thickness/'+str(round(th, 3))+'.png',
#               th=round(th, 3),
#               angle=270,
#               image_size=(340*5, 200*5),
#               cent_point=(-0.75, 0),
#               zoom_level=1)
#        sleep(20)
