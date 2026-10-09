import numpy as np
from PIL import Image
import random

def generate_newton(
    width=2160, 
    height=2160, 
    degree=3, 
    zoom=1.0, 
    center_x=0.0, 
    center_y=0.0, 
    max_iter=60,
    formula_offset=0.5,
    formula_exponent_offset=0.5,
    epsilon=1e-6,
    convergence_threshold=1e-5,
    log_base=10.0,
    color_min=140,
    color_max=255,
    gamma=1.85
):
    """
    Генерирует фрактал Ньютона для модифицированного уравнения
    с глобальной нормализацией и плавным контрастным градиентом
    """
    x = np.linspace(center_x - 1.0/zoom, center_x + 1.0/zoom, width)
    y = np.linspace(center_y - 1.0/zoom, center_y + 1.0/zoom, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    roots = [np.exp(2j * np.pi * k / degree) for k in range(degree)]

    smooth_iterations = np.zeros(Z.shape, dtype=float)
    converged = np.zeros(Z.shape, dtype=int)

    with np.errstate(divide='ignore', invalid='ignore'):
        for i in range(max_iter):
            # Модифицированная формула Ньютона
            Z_new = Z - (Z**degree - formula_offset) / (degree * Z**(degree - formula_exponent_offset) + epsilon)
            
            not_converged = (converged == 0)
            diff = np.abs(Z_new - Z)
            newly_converged = not_converged & (diff < convergence_threshold)
            
            if np.any(newly_converged):
                Z_conv = Z_new[newly_converged]
                dists = np.abs(Z_conv[:, np.newaxis] - roots)
                closest_root_idx = np.argmin(dists, axis=1)
                
                converged[newly_converged] = closest_root_idx + 1
                
                final_dist = np.abs(Z_conv - np.array(roots)[closest_root_idx])
                smooth_val = i + 1.0 - np.log(np.maximum(final_dist, 1e-10)) / np.log(log_base)
                smooth_iterations[newly_converged] = smooth_val
            
            Z = Z_new

    # Генерация случайных цветов
    palette = [(0, 0, 0)]
    for _ in range(degree):
        palette.append((random.randint(color_min, color_max), 
                       random.randint(color_min, color_max), 
                       random.randint(color_min, color_max)))
    
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Глобальная нормализация
    mask_converged = (converged > 0)
    if np.any(mask_converged):
        global_min = np.min(smooth_iterations[mask_converged])
        global_max = np.max(smooth_iterations[mask_converged])

        if global_max > global_min:
            normalized_all = (smooth_iterations - global_min) / (global_max - global_min)
        else:
            normalized_all = np.zeros_like(smooth_iterations)

        # Гамма-коррекция
        normalized_gamma = np.power(normalized_all, gamma)
        shade = 1.0 - normalized_gamma
        
        for r_idx in range(1, degree + 1):
            mask = (converged == r_idx)
            if np.any(mask):
                color = np.array(palette[r_idx])
                img_array[mask] = (color * shade[mask, np.newaxis]).astype(np.uint8)

    return Image.fromarray(img_array)
