import numpy as np
from PIL import Image
import random
import math


def generate_fractal_flame(
    width=4096,
    height=4096,
    num_transforms=5,
    num_points=1000000,
    variations=None,
    color_palette=None,
    gamma=2.5,
    brightness=1.0,
    background_color=(0, 0, 0),
    zoom=1.0,
    center_x=None,
    center_y=None
):
    """
    Генерирует fractal flame
    
    variations: список названий вариаций для каждого преобразования
    color_palette: список из 256 цветов (RGB кортежи)
    gamma: гамма-коррекция для логарифмического масштабирования
    brightness: общая яркость изображения
    """
    # Если вариации не заданы, генерируем случайные
    if variations is None:
        variations = _generate_random_variations(num_transforms)
    
    # Если палитра не задана, генерируем случайную
    if color_palette is None:
        color_palette = _generate_random_palette()
    
    # Генерируем аффинные преобразования
    transforms = _generate_affine_transforms(num_transforms)
    
    # Инициализируем аккумуляторы для цвета и плотности
    color_accum = np.zeros((height, width, 3), dtype=np.float64)
    density_accum = np.zeros((height, width), dtype=np.float64)
    
    # Начальная точка
    x, y = 0.0, 0.0
    current_color = 0.0
    
    # Пропускаем первые 20 итераций
    for _ in range(20):
        transform_idx = random.randint(0, num_transforms - 1)
        a, b, c, d, e, f = transforms[transform_idx]
        x_new = a * x + b * y + e
        y_new = c * x + d * y + f
        
        # Применяем вариацию
        var_func = _get_variation_function(variations[transform_idx])
        x_new, y_new = var_func(x_new, y_new)
        
        x, y = x_new, y_new
        current_color = (current_color + 1.0 / num_transforms) % 1.0
    
    # Генерируем точки
    for i in range(num_points):
        transform_idx = random.randint(0, num_transforms - 1)
        a, b, c, d, e, f = transforms[transform_idx]
        
        # Аффинное преобразование
        x_new = a * x + b * y + e
        y_new = c * x + d * y + f
        
        # Применяем вариацию
        var_func = _get_variation_function(variations[transform_idx])
        x_new, y_new = var_func(x_new, y_new)
        
        x, y = x_new, y_new
        current_color = (current_color + 1.0 / num_transforms) % 1.0
        
        # Преобразуем в пиксельные координаты
        px, py = _world_to_pixel(x, y, width, height, zoom, center_x, center_y)
        
        # Если точка в пределах изображения
        if 0 <= px < width and 0 <= py < height:
            # Получаем цвет из палитры
            color_idx = int(current_color * 255)
            r, g, b = color_palette[color_idx]
            
            # Добавляем в аккумуляторы
            color_accum[py, px, 0] += r
            color_accum[py, px, 1] += g
            color_accum[py, px, 2] += b
            density_accum[py, px] += 1
    
    # Применяем логарифмическое масштабирование и гамма-коррекцию
    img_array = _apply_log_scaling(color_accum, density_accum, gamma, brightness)
    
    return Image.fromarray(img_array)


def _generate_affine_transforms(num_transforms):
    """Генерирует случайные аффинные преобразования"""
    transforms = []
    for _ in range(num_transforms):
        angle = random.uniform(0, 2 * math.pi)
        scale = random.uniform(0.3, 0.7)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        a = scale * cos_a
        b = -scale * sin_a
        c = scale * sin_a
        d = scale * cos_a
        e = random.uniform(-1.0, 1.0)
        f = random.uniform(-1.0, 1.0)
        
        transforms.append((a, b, c, d, e, f))
    
    return transforms


def _generate_random_variations(num_transforms):
    """Генерирует случайные вариации для каждого преобразования"""
    variation_names = [
        'linear', 'sinusoidal', 'spherical', 'swirl',
        'horseshoe', 'heart', 'disc', 'spiral',
        'hyperbolic', 'diamond', 'ex', 'julian'
    ]
    return [random.choice(variation_names) for _ in range(num_transforms)]


def _get_variation_function(variation_name):
    """Возвращает функцию вариации по имени"""
    if variation_name == 'linear':
        return lambda x, y: (x, y)
    elif variation_name == 'sinusoidal':
        return lambda x, y: (math.sin(x), math.sin(y))
    elif variation_name == 'spherical':
        return lambda x, y: (x / (x*x + y*y + 1e-10), y / (x*x + y*y + 1e-10))
    elif variation_name == 'swirl':
        def swirl(x, y):
            r2 = x*x + y*y
            return (x * math.sin(r2) - y * math.cos(r2),
                    x * math.cos(r2) + y * math.sin(r2))
        return swirl
    elif variation_name == 'horseshoe':
        def horseshoe(x, y):
            r = math.sqrt(x*x + y*y + 1e-10)
            return ((x*x - y*y) / r, 2*x*y / r)
        return horseshoe
    elif variation_name == 'heart':
        def heart(x, y):
            r = math.sqrt(x*x + y*y + 1e-10)
            return (r * math.sin(x * r), -r * math.cos(y * r))
        return heart
    elif variation_name == 'disc':
        def disc(x, y):
            r = math.pi * math.sqrt(x*x + y*y + 1e-10)
            return (x / r * math.sin(math.pi * r),
                    y / r * math.cos(math.pi * r))
        return disc
    elif variation_name == 'spiral':
        def spiral(x, y):
            r = math.sqrt(x*x + y*y + 1e-10)
            theta = math.atan2(y, x)
            return ((math.sin(theta) + math.cos(r)) / r,
                    (math.cos(theta) - math.sin(r)) / r)
        return spiral
    elif variation_name == 'hyperbolic':
        def hyperbolic(x, y):
            r2 = x*x + y*y + 1e-10
            return (x / r2, math.atan2(y, x) / math.pi)
        return hyperbolic
    elif variation_name == 'diamond':
        def diamond(x, y):
            r = math.sqrt(x*x + y*y + 1e-10)
            return (math.sin(x) * math.cos(r), math.cos(y) * math.sin(r))
        return diamond
    elif variation_name == 'ex':
        def ex(x, y):
            r = math.sqrt(x*x + y*y + 1e-10)
            n0 = math.atan2(y, x)
            return (r * math.sin(n0 + r), r * math.cos(n0 - r))
        return ex
    elif variation_name == 'julian':
        def julian(x, y):
            r = math.sqrt(x*x + y*y + 1e-10)
            theta = math.atan2(y, x)
            return (r**0.5 * math.cos(theta/3), r**0.5 * math.sin(theta/3))
        return julian
    else:
        return lambda x, y: (x, y)


def _generate_random_palette():
    """Генерирует случайную цветовую палитру из 256 цветов"""
    palette = []
    
    # Выбираем 3-5 опорных цветов
    num_keyframes = random.randint(3, 5)
    keyframes = []
    for _ in range(num_keyframes):
        keyframes.append((
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        ))
    
    # Интерполируем между опорными цветами
    for i in range(256):
        t = i / 255.0
        idx = t * (num_keyframes - 1)
        idx_int = int(idx)
        idx_frac = idx - idx_int
        
        if idx_int >= num_keyframes - 1:
            palette.append(keyframes[-1])
        else:
            c1 = keyframes[idx_int]
            c2 = keyframes[idx_int + 1]
            
            # Плавная интерполяция
            r = int(c1[0] * (1 - idx_frac) + c2[0] * idx_frac)
            g = int(c1[1] * (1 - idx_frac) + c2[1] * idx_frac)
            b = int(c1[2] * (1 - idx_frac) + c2[2] * idx_frac)
            
            palette.append((r, g, b))
    
    return palette


def _world_to_pixel(x, y, width, height, zoom, center_x, center_y):
    """Преобразует мировые координаты в пиксельные"""
    # Определяем центр, если не задан
    if center_x is None:
        center_x = 0.0
    if center_y is None:
        center_y = 0.0
    
    # Масштабируем и центрируем
    scale = min(width, height) / 4.0 * zoom
    px = int((x - center_x) * scale + width / 2)
    py = int((y - center_y) * scale + height / 2)
    
    return px, py


def _apply_log_scaling(color_accum, density_accum, gamma, brightness):
    """Применяет логарифмическое масштабирование и гамма-коррекцию"""
    height, width = density_accum.shape
    
    # Находим максимум плотности
    max_density = np.max(density_accum)
    if max_density == 0:
        return np.zeros((height, width, 3), dtype=np.uint8)
    
    # Нормализуем плотность и применяем логарифм
    log_density = np.log(density_accum + 1) / np.log(max_density + 1)
    
    # Применяем гамма-коррекцию
    log_density = np.power(log_density, 1.0 / gamma) * brightness
    
    # Применяем к цветам
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    for c in range(3):
        img_array[:, :, c] = np.clip(color_accum[:, :, c] * log_density, 0, 255).astype(np.uint8)
    
    return img_array
