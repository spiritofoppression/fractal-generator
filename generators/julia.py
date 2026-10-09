import numpy as np
from PIL import Image
import random

def generate_julia(
    width=4096,
    height=4096,
    c_real=-0.7,
    c_imag=0.27015,
    zoom=1.0,
    center_x=0.0,
    center_y=0.0,
    max_iter=200,
    escape_radius=2.0,
    color_min=100,
    color_max=255,
    gamma=1.0,
    background_color=(0, 0, 0)
):
    """
    Генерирует множество Жюлиа по формуле z_{n+1} = z_n^2 + c
    """
    # Сетка координат
    x = np.linspace(center_x - 1.5/zoom, center_x + 1.5/zoom, width)
    y = np.linspace(center_y - 1.5/zoom, center_y + 1.5/zoom, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    c = complex(c_real, c_imag)
    
    iterations = np.zeros(Z.shape, dtype=float)
    escaped = np.zeros(Z.shape, dtype=bool)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        for i in range(max_iter):
            Z = Z * Z + c
            magnitude = np.abs(Z)
            newly_escaped = (~escaped) & (magnitude > escape_radius)
            
            if np.any(newly_escaped):
                # Smooth coloring
                smooth_val = i + 1 - np.log(np.log(magnitude[newly_escaped]) / np.log(escape_radius)) / np.log(2)
                iterations[newly_escaped] = smooth_val
            
            escaped = escaped | (magnitude > escape_radius)
            if np.all(escaped):
                break
    
    # Раскрашивание
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    img_array[:, :] = background_color
    
    mask_escaped = escaped
    if np.any(mask_escaped):
        min_iter = np.min(iterations[mask_escaped])
        max_iter_val = np.max(iterations[mask_escaped])
        
        if max_iter_val > min_iter:
            normalized = (iterations[mask_escaped] - min_iter) / (max_iter_val - min_iter)
        else:
            normalized = np.zeros(np.sum(mask_escaped))
        
        normalized_gamma = np.power(np.clip(normalized, 0.0, 1.0), gamma)
        
        # --- ЦИКЛИЧЕСКАЯ ПАЛИТРА С ВОЛНАМИ ---
        # Создаём плавные цветовые волны через синусоиды с разными фазами для R, G, B
        # Это даёт красивые переливы без ступенек
        phase_r = random.uniform(0, 2 * np.pi)
        phase_g = random.uniform(0, 2 * np.pi)
        phase_b = random.uniform(0, 2 * np.pi)
        
        freq = random.uniform(3.0, 8.0)  # Частота волн
        
        # Вычисляем цвет для каждой точки
        r = (np.sin(freq * normalized_gamma * 2 * np.pi + phase_r) * 0.5 + 0.5)
        g = (np.sin(freq * normalized_gamma * 2 * np.pi + phase_g) * 0.5 + 0.5)
        b = (np.sin(freq * normalized_gamma * 2 * np.pi + phase_b) * 0.5 + 0.5)
        
        # Масштабируем в диапазон [color_min, color_max]
        r_scaled = (color_min + (color_max - color_min) * r).astype(np.uint8)
        g_scaled = (color_min + (color_max - color_min) * g).astype(np.uint8)
        b_scaled = (color_min + (color_max - color_min) * b).astype(np.uint8)
        
        # Записываем в изображение
        img_array[mask_escaped, 0] = r_scaled
        img_array[mask_escaped, 1] = g_scaled
        img_array[mask_escaped, 2] = b_scaled
    
    return Image.fromarray(img_array)
