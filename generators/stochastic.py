import numpy as np
from PIL import Image
import random

def generate_stochastic(
    width=4096,
    height=4096,
    roughness=0.5,
    seed=None,
    color_min=50,
    color_max=255,
    gradient_type='linear',
    color_mode='grayscale',
    num_layers=1,
    layer_blend='multiply'
):
    """
    Генерирует стохастический фрактал (алгоритм Diamond-Square)
    
    roughness: коэффициент шероховатости (0.0-1.0)
               0.0 = очень гладкий, 1.0 = очень шероховатый
    seed: сид для воспроизводимости (None = случайный)
    gradient_type: тип градиента ('linear', 'radial', 'diagonal')
    color_mode: режим раскрашивания ('grayscale', 'rgb', 'palette')
    num_layers: количество слоёв для наложения (для цветных режимов)
    layer_blend: способ наложения слоёв ('multiply', 'screen', 'overlay')
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Размер должен быть степенью 2 + 1
    # Находим ближайшую степень 2
    size = 1
    while size < max(width, height):
        size *= 2
    size += 1
    
    # Создаём массив значений
    grid = np.zeros((size, size), dtype=float)
    
    # Инициализируем углы случайными значениями
    grid[0, 0] = random.uniform(0, 1)
    grid[0, size-1] = random.uniform(0, 1)
    grid[size-1, 0] = random.uniform(0, 1)
    grid[size-1, size-1] = random.uniform(0, 1)
    
    # Алгоритм Diamond-Square
    step = size - 1
    scale = 1.0
    
    while step > 1:
        half = step // 2
        
        # Diamond step: вычисляем центры квадратов
        for y in range(0, size - 1, step):
            for x in range(0, size - 1, step):
                avg = (grid[y, x] + grid[y, x + step] + 
                       grid[y + step, x] + grid[y + step, x + step]) / 4.0
                grid[y + half, x + half] = avg + random.uniform(-scale, scale)
        
        # Square step: вычисляем середины рёбер
        for y in range(0, size, half):
            for x in range((y + half) % step, size, step):
                count = 0
                total = 0.0
                
                if y >= half:
                    total += grid[y - half, x]
                    count += 1
                if y + half < size:
                    total += grid[y + half, x]
                    count += 1
                if x >= half:
                    total += grid[y, x - half]
                    count += 1
                if x + half < size:
                    total += grid[y, x + half]
                    count += 1
                
                if count > 0:
                    grid[y, x] = total / count + random.uniform(-scale, scale)
        
        step //= 2
        scale *= (2.0 ** (-roughness))
    
    # Нормализуем значения в диапазон [0, 1]
    grid_min = np.min(grid)
    grid_max = np.max(grid)
    if grid_max > grid_min:
        grid = (grid - grid_min) / (grid_max - grid_min)
    else:
        grid = np.zeros_like(grid)
    
    # Обрезаем до нужного размера
    grid = grid[:height, :width]
    
    # Применяем градиентный тип
    if gradient_type == 'radial':
        # Радиальный градиент от центра
        y_coords, x_coords = np.ogrid[:height, :width]
        center_y, center_x = height / 2, width / 2
        distance = np.sqrt((y_coords - center_y)**2 + (x_coords - center_x)**2)
        max_distance = np.sqrt(center_y**2 + center_x**2)
        gradient = 1.0 - (distance / max_distance)
        grid = grid * gradient
    elif gradient_type == 'diagonal':
        # Диагональный градиент
        y_coords, x_coords = np.ogrid[:height, :width]
        gradient = (y_coords / height + x_coords / width) / 2.0
        grid = grid * gradient
    
    # Раскрашивание
    if color_mode == 'grayscale':
        img_array = _apply_grayscale(grid, color_min, color_max)
    elif color_mode == 'rgb':
        img_array = _apply_rgb(grid, color_min, color_max, num_layers, layer_blend)
    elif color_mode == 'palette':
        img_array = _apply_palette(grid, color_min, color_max)
    else:
        img_array = _apply_grayscale(grid, color_min, color_max)
    
    return Image.fromarray(img_array)

def _apply_grayscale(grid, color_min, color_max):
    """Применяет grayscale раскрашивание"""
    height, width = grid.shape
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Масштабируем значения в диапазон [color_min, color_max]
    values = (color_min + (color_max - color_min) * grid).astype(np.uint8)
    
    # Одинаковые значения для R, G, B
    img_array[:, :, 0] = values
    img_array[:, :, 1] = values
    img_array[:, :, 2] = values
    
    return img_array

def _apply_rgb(grid, color_min, color_max, num_layers, layer_blend):
    """Применяет RGB раскрашивание с несколькими слоями"""
    height, width = grid.shape
    img_array = np.zeros((height, width, 3), dtype=float)
    
    for channel in range(3):
        # Генерируем отдельный слой для каждого цветового канала
        layer = np.zeros((height, width), dtype=float)
        
        for i in range(num_layers):
            # Смещаем и масштабируем исходную сетку
            offset_x = random.randint(-width // 4, width // 4)
            offset_y = random.randint(-height // 4, height // 4)
            scale = random.uniform(0.5, 2.0)
            
            # Создаём смещённую версию
            shifted = np.roll(grid, (offset_y, offset_x), axis=(0, 1))
            layer += shifted * scale
        
        # Нормализуем
        layer_min = np.min(layer)
        layer_max = np.max(layer)
        if layer_max > layer_min:
            layer = (layer - layer_min) / (layer_max - layer_min)
        
        # Масштабируем в диапазон цветов
        img_array[:, :, channel] = color_min + (color_max - color_min) * layer
    
    # Применяем способ наложения
    if layer_blend == 'multiply':
        img_array = img_array / 255.0
        for channel in range(1, 3):
            img_array[:, :, channel] *= img_array[:, :, 0]
    elif layer_blend == 'screen':
        img_array = img_array / 255.0
        for channel in range(1, 3):
            img_array[:, :, channel] = 1.0 - (1.0 - img_array[:, :, 0]) * (1.0 - img_array[:, :, channel])
    
    return (img_array * 255).astype(np.uint8)

def _apply_palette(grid, color_min, color_max):
    """Применяет палитру с плавными переходами"""
    height, width = grid.shape
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Генерируем 3-5 случайных цветов
    num_colors = random.randint(3, 5)
    palette = []
    for _ in range(num_colors):
        palette.append(np.array([
            random.randint(color_min, color_max),
            random.randint(color_min, color_max),
            random.randint(color_min, color_max)
        ], dtype=float))
    
    # Интерполируем между цветами палитры
    for y in range(height):
        for x in range(width):
            val = grid[y, x]
            pos = val * (num_colors - 1)
            idx = int(pos)
            t = pos - idx
            
            if idx >= num_colors - 1:
                color = palette[-1]
            else:
                # Плавная интерполяция (smoothstep)
                t_smooth = t * t * (3 - 2 * t)
                color = palette[idx] * (1 - t_smooth) + palette[idx + 1] * t_smooth
            
            img_array[y, x] = color.astype(np.uint8)
    
    return img_array
