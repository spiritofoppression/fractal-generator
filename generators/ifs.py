import numpy as np
from PIL import Image
import random
import math


def generate_ifs(
    width=4096,
    height=4096,
    num_transforms=4,
    num_points=500000,
    transforms=None,
    probabilities=None,
    color_min=100,
    color_max=255,
    background_color=(0, 0, 0),
    point_size=1,
    preset=None,
    zoom=1.0,
    center_x=None,
    center_y=None
):
    """
    Генерирует IFS-фрактал используя алгоритм "chaos game"
    """
    if preset is None:
        preset = 'random'
    
    # Получаем преобразования
    if transforms is None:
        if preset == 'fern':
            transforms = [
                (0.0, 0.0, 0.0, 0.16, 0.0, 0.0),
                (0.85, 0.04, -0.04, 0.85, 0.0, 1.6),
                (0.2, -0.26, 0.23, 0.22, 0.0, 1.6),
                (-0.15, 0.28, 0.26, 0.24, 0.0, 0.44)
            ]
            probabilities = [0.01, 0.85, 0.07, 0.07]
        elif preset == 'triangle':
            transforms = [
                (0.5, 0.0, 0.0, 0.5, 0.0, 0.0),
                (0.5, 0.0, 0.0, 0.5, 0.25, 0.5),
                (0.5, 0.0, 0.0, 0.5, 0.5, 0.0)
            ]
            probabilities = [1/3, 1/3, 1/3]
        elif preset == 'carpet':
            transforms = [
                (1/3, 0.0, 0.0, 1/3, 0.0, 0.0),
                (1/3, 0.0, 0.0, 1/3, 1/3, 0.0),
                (1/3, 0.0, 0.0, 1/3, 2/3, 0.0),
                (1/3, 0.0, 0.0, 1/3, 0.0, 1/3),
                (1/3, 0.0, 0.0, 1/3, 2/3, 1/3),
                (1/3, 0.0, 0.0, 1/3, 0.0, 2/3),
                (1/3, 0.0, 0.0, 1/3, 1/3, 2/3),
                (1/3, 0.0, 0.0, 1/3, 2/3, 2/3)
            ]
            probabilities = [1/8] * 8
        elif preset == 'spiral':
            transforms = [
                (0.78785, -0.42265, 0.24265, 0.85857, 0.0, 0.0),
                (0.2, -0.26, 0.23, 0.22, 0.0, 1.6),
                (-0.15, 0.28, 0.26, 0.24, 0.0, 0.44)
            ]
            probabilities = [0.8, 0.1, 0.1]
        else:  # random
            transforms = _generate_random_ifs(num_transforms)
    
    # Если вероятности не заданы, вычисляем их
    if probabilities is None:
        probabilities = []
        for t in transforms:
            a, b, c, d, e, f = t
            det = abs(a * d - b * c)
            probabilities.append(det)
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
    
    # Алгоритм chaos game
    x, y = 0.0, 0.0
    
    points_x = np.zeros(num_points, dtype=np.float64)
    points_y = np.zeros(num_points, dtype=np.float64)
    points_color_idx = np.zeros(num_points, dtype=np.int32)
    
    # Пропускаем первые 20 итераций
    for _ in range(20):
        transform_idx = random.choices(range(len(transforms)), weights=probabilities, k=1)[0]
        a, b, c, d, e, f = transforms[transform_idx]
        x_new = a * x + b * y + e
        y_new = c * x + d * y + f
        x, y = x_new, y_new
    
    # Генерируем точки
    valid_count = 0
    for i in range(num_points):
        transform_idx = random.choices(range(len(transforms)), weights=probabilities, k=1)[0]
        a, b, c, d, e, f = transforms[transform_idx]
        
        x_new = a * x + b * y + e
        y_new = c * x + d * y + f
        x, y = x_new, y_new
        
        if abs(x) < 1e10 and abs(y) < 1e10:
            points_x[valid_count] = x
            points_y[valid_count] = y
            points_color_idx[valid_count] = transform_idx
            valid_count += 1
    
    if valid_count == 0:
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        img_array[:, :] = background_color
        return Image.fromarray(img_array)
    
    points_x = points_x[:valid_count]
    points_y = points_y[:valid_count]
    points_color_idx = points_color_idx[:valid_count]
    
    # Масштабирование
    x_min, x_max = np.min(points_x), np.max(points_x)
    y_min, y_max = np.min(points_y), np.max(points_y)
    
    x_range = x_max - x_min
    y_range = y_max - y_min
    
    if x_range < 1e-6:
        x_range = 1.0
    if y_range < 1e-6:
        y_range = 1.0
    
    if center_x is None:
        center_x = (x_min + x_max) / 2
    if center_y is None:
        center_y = (y_min + y_max) / 2
    
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
    
    pixel_x = ((points_x - view_center_x) * scale + width / 2).astype(np.int32)
    pixel_y = ((points_y - view_center_y) * scale + height / 2).astype(np.int32)
    
    valid_mask = (pixel_x >= 0) & (pixel_x < width) & (pixel_y >= 0) & (pixel_y < height)
    pixel_x = pixel_x[valid_mask]
    pixel_y = pixel_y[valid_mask]
    points_color_idx = points_color_idx[valid_mask]
    
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    img_array[:, :] = background_color
    
    colors = []
    for _ in range(len(transforms)):
        colors.append((
            random.randint(color_min, color_max),
            random.randint(color_min, color_max),
            random.randint(color_min, color_max)
        ))
    
    for color_idx in range(len(transforms)):
        mask = points_color_idx == color_idx
        if not np.any(mask):
            continue
        
        px = pixel_x[mask]
        py = pixel_y[mask]
        color = colors[color_idx]
        
        if point_size == 1:
            img_array[py, px] = color
        else:
            for dx in range(point_size):
                for dy in range(point_size):
                    valid = (px + dx < width) & (py + dy < height)
                    img_array[py[valid] + dy, px[valid] + dx] = color
    
    return Image.fromarray(img_array)


def _generate_random_ifs(num_transforms):
    """Генерирует случайный IFS с разнообразными преобразованиями"""
    transforms = []
    
    for i in range(num_transforms):
        # Случайный тип преобразования
        transform_type = random.choice(['rotation', 'shear', 'mixed'])
        
        if transform_type == 'rotation':
            # Чистое вращение + масштаб
            angle = random.uniform(0, 2 * math.pi)
            scale = random.uniform(0.2, 0.6)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            a = scale * cos_a
            b = -scale * sin_a
            c = scale * sin_a
            d = scale * cos_a
        elif transform_type == 'shear':
            # Сдвиг + масштаб
            scale = random.uniform(0.3, 0.6)
            shear_x = random.uniform(-0.5, 0.5)
            shear_y = random.uniform(-0.5, 0.5)
            a = scale
            b = scale * shear_x
            c = scale * shear_y
            d = scale
        else:  # mixed
            # Смешанное преобразование
            angle = random.uniform(0, 2 * math.pi)
            scale_x = random.uniform(0.2, 0.6)
            scale_y = random.uniform(0.2, 0.6)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            a = scale_x * cos_a
            b = -scale_y * sin_a
            c = scale_x * sin_a
            d = scale_y * cos_a
        
        # Случайное смещение
        e = random.uniform(-2.0, 2.0)
        f = random.uniform(-2.0, 2.0)
        
        transforms.append((a, b, c, d, e, f))
    
    return transforms
