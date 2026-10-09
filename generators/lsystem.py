import numpy as np
from PIL import Image, ImageDraw
import random
import math


def generate_lsystem(
    width=4096,
    height=4096,
    axiom=None,
    rules=None,
    angle=90,
    length=10,
    initial_angle=None,
    iterations=4,
    line_width=2,
    color_min=100,
    color_max=255,
    background_color=(0, 0, 0),
    preset=None,
    zoom=1.0,
    center_x=None,
    center_y=None
):
    """
    Генерирует L-систему (систему Линденмайера)
    """
    # Получаем параметры из пресета
    preset_params = None
    if preset is not None:
        preset_params = _get_preset(preset)
    
    # Если параметры не заданы, берём из пресета
    if preset_params is not None:
        if axiom is None:
            axiom = preset_params['axiom']
        if rules is None:
            rules = preset_params['rules']
        if initial_angle is None:
            initial_angle = preset_params.get('initial_angle', 0)
    
    # Дефолтные значения, если всё ещё None
    if axiom is None:
        axiom = 'F'
    if rules is None:
        rules = {'F': 'F'}
    if initial_angle is None:
        initial_angle = 0
    
    # Генерируем строку через итерации подстановки
    current = axiom
    for _ in range(iterations):
        next_str = []
        for char in current:
            if char in rules:
                next_str.append(rules[char])
            else:
                next_str.append(char)
        current = ''.join(next_str)
        
        # Ограничиваем длину строки
        if len(current) > 5_000_000:
            break
    
    # Интерпретируем строку через черепашью графику
    points = _turtle_interpretation(current, angle, length, initial_angle)
    
    if len(points) < 2:
        img = Image.new('RGB', (width, height), background_color)
        return img
    
    # Преобразуем в numpy массив для масштабирования
    points = np.array(points)
    
    # Находим границы
    x_min, x_max = np.min(points[:, 0]), np.max(points[:, 0])
    y_min, y_max = np.min(points[:, 1]), np.max(points[:, 1])
    
    x_range = x_max - x_min
    y_range = y_max - y_min
    
    if x_range < 1e-6:
        x_range = 1.0
    if y_range < 1e-6:
        y_range = 1.0
    
    # Автоцентр
    if center_x is None:
        center_x = (x_min + x_max) / 2
    if center_y is None:
        center_y = (y_min + y_max) / 2
    
    # Зум
    if zoom <= 1.0:
        view_x_min = x_min
        view_x_max = x_max
        view_y_min = y_min
        view_y_max = y_max
    else:
        view_range_x = x_range / zoom
        view_range_y = y_range / zoom
        view_x_min = center_x - view_range_x / 2
        view_x_max = center_x + view_range_x / 2
        view_y_min = center_y - view_range_y / 2
        view_y_max = center_y + view_range_y / 2
    
    view_range_x = view_x_max - view_x_min
    view_range_y = view_y_max - view_y_min
    
    if view_range_x < 1e-6:
        view_range_x = 1.0
    if view_range_y < 1e-6:
        view_range_y = 1.0
    
    margin = 0.05
    scale_x = (1 - 2 * margin) * width / view_range_x
    scale_y = (1 - 2 * margin) * height / view_range_y
    scale = min(scale_x, scale_y)
    
    view_center_x = (view_x_min + view_x_max) / 2
    view_center_y = (view_y_min + view_y_max) / 2
    
    # Масштабируем точки
    pixel_points = np.zeros_like(points, dtype=np.float64)
    pixel_points[:, 0] = (points[:, 0] - view_center_x) * scale + width / 2
    pixel_points[:, 1] = (points[:, 1] - view_center_y) * scale + height / 2
    
    # Создаём изображение
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Генерируем случайный цвет для линии
    line_color = (
        random.randint(color_min, color_max),
        random.randint(color_min, color_max),
        random.randint(color_min, color_max)
    )
    
    # Рисуем линии
    segment_start = 0
    for i in range(len(pixel_points)):
        if pixel_points[i, 0] == -1 and pixel_points[i, 1] == -1:
            if i > segment_start:
                for j in range(segment_start, i - 1):
                    x1, y1 = int(pixel_points[j, 0]), int(pixel_points[j, 1])
                    x2, y2 = int(pixel_points[j + 1, 0]), int(pixel_points[j + 1, 1])
                    draw.line([(x1, y1), (x2, y2)], fill=line_color, width=line_width)
            segment_start = i + 1
    
    # Рисуем последний сегмент
    if segment_start < len(pixel_points) - 1:
        for j in range(segment_start, len(pixel_points) - 1):
            x1, y1 = int(pixel_points[j, 0]), int(pixel_points[j, 1])
            x2, y2 = int(pixel_points[j + 1, 0]), int(pixel_points[j + 1, 1])
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=line_width)
    
    return img


def _turtle_interpretation(string, angle, length, initial_angle):
    """
    Интерпретирует строку L-системы через черепашью графику.
    """
    points = []
    x, y = 0.0, 0.0
    direction = math.radians(initial_angle)
    
    stack = []
    angle_rad = math.radians(angle)
    
    for char in string:
        if char == 'F' or char == 'G':
            new_x = x + length * math.cos(direction)
            new_y = y + length * math.sin(direction)
            points.append((x, y))
            points.append((new_x, new_y))
            x, y = new_x, new_y
        elif char == 'f':
            x += length * math.cos(direction)
            y += length * math.sin(direction)
            points.append((-1, -1))
        elif char == '+':
            direction -= angle_rad
        elif char == '-':
            direction += angle_rad
        elif char == '[':
            stack.append((x, y, direction))
        elif char == ']':
            if stack:
                x, y, direction = stack.pop()
                points.append((-1, -1))
    
    return points


def _get_preset(preset_name):
    """Возвращает параметры для известного пресета L-системы"""
    presets = {
        'koch': {
            'axiom': 'F',
            'rules': {'F': 'F+F--F+F'},
            'angle': 60,
            'initial_angle': 0
        },
        'dragon': {
            'axiom': 'F',
            'rules': {'F': 'F+G', 'G': 'F-G'},
            'angle': 90,
            'initial_angle': 0
        },
        'gosper': {
            'axiom': 'F',
            'rules': {'F': 'F+G++G-F--FF-G+', 'G': '-F+GG++G+F--F-G'},
            'angle': 60,
            'initial_angle': 0
        },
        'tree': {
            'axiom': 'F',
            'rules': {'F': 'F[+F]F[-F]F'},
            'angle': 25.7,
            'initial_angle': -90
        },
        'bush': {
            'axiom': 'F',
            'rules': {'F': 'F[+F]F[-F][F]'},
            'angle': 20,
            'initial_angle': -90
        },
        'sierpinski': {
            'axiom': 'F-G-G',
            'rules': {'F': 'F-G+F+G-F', 'G': 'GG'},
            'angle': 120,
            'initial_angle': 0
        },
        'square_koch': {
            'axiom': 'F',
            'rules': {'F': 'F+F-F-F+F'},
            'angle': 90,
            'initial_angle': 0
        },
        'levy': {
            'axiom': 'F',
            'rules': {'F': '+F--F+'},
            'angle': 45,
            'initial_angle': 0
        },
        'plant': {
            'axiom': 'X',
            'rules': {'X': 'F+[[X]-X]-F[-FX]+X', 'F': 'FF'},
            'angle': 22.5,
            'initial_angle': -65
        },
        'hilbert': {
            'axiom': 'L',
            'rules': {'L': '+RF-LFL-FR+', 'R': '-LF+RFR+FL-'},
            'angle': 90,
            'initial_angle': 0
        },
        'penrose': {
            'axiom': '[7]++[7]++[7]++[7]++[7]',
            'rules': {'6': '81++91----71[-81----61]++',
                      '7': '+81--91[---61--71]+',
                      '8': '-61++71[+++81++91]-',
                      '9': '--81++++61[+91++++71]++71',
                      '1': ''},
            'angle': 36,
            'initial_angle': 0
        }
    }
    
    return presets.get(preset_name)
