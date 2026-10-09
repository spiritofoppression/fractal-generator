import numpy as np
from PIL import Image
import random


def generate_lyapunov(
    width=4096,
    height=4096,
    sequence="AABAB",
    a_min=0.0,
    a_max=4.0,
    b_min=0.0,
    b_max=4.0,
    num_iterations=1000,
    warmup_iterations=500,
    color_positive=None,
    color_negative=None,
    gamma=1.0,
    background_color=(0, 0, 0)
):
    """
    Генерирует фрактал Ляпунова
    
    sequence: строка из 'A' и 'B' (например "AABAB")
    a_min, a_max: диапазон параметра 'a' (обычно 0-4)
    b_min, b_max: диапазон параметра 'b' (обычно 0-4)
    num_iterations: количество итераций для вычисления показателя
    warmup_iterations: количество "разогревочных" итераций (не учитываются)
    color_positive: цвет для хаотических областей (показатель > 0)
    color_negative: цвет для стабильных областей (показатель < 0)
    gamma: гамма-коррекция
    """
    # Если цвета не заданы, генерируем случайные
    if color_positive is None:
        color_positive = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
    if color_negative is None:
        color_negative = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100)
        )
    
    # Создаём сетку параметров
    a_values = np.linspace(a_min, a_max, width)
    b_values = np.linspace(b_min, b_max, height)
    
    # Массив для показателей Ляпунова
    lyapunov_exponents = np.zeros((height, width), dtype=np.float64)
    
    # Для каждой точки (a, b) вычисляем показатель Ляпунова
    for i, b in enumerate(b_values):
        for j, a in enumerate(a_values):
            lyapunov_exponents[i, j] = _compute_lyapunov_exponent(
                a, b, sequence, num_iterations, warmup_iterations
            )
    
    # Раскрашиваем изображение
    img_array = _colorize(lyapunov_exponents, color_positive, color_negative, gamma, background_color)
    
    return Image.fromarray(img_array)


def _compute_lyapunov_exponent(a, b, sequence, num_iterations, warmup_iterations):
    """
    Вычисляет показатель Ляпунова для заданных параметров a, b и последовательности.
    
    Логистическое отображение: x_{n+1} = r_n * x_n * (1 - x_n)
    где r_n чередуется между a и b согласно последовательности
    """
    x = 0.5  # Начальное значение
    
    total_lambda = 0.0
    seq_len = len(sequence)
    
    # Разогревочные итерации (не учитываются в показателе)
    for i in range(warmup_iterations):
        r = a if sequence[i % seq_len] == 'A' else b
        x = r * x * (1 - x)
        
        # Если x выходит за пределы [0, 1] или становится NaN, возвращаем большое значение
        if x <= 0 or x >= 1 or np.isnan(x):
            return 1.0  # Хаос
    
    # Основные итерации
    for i in range(num_iterations):
        r = a if sequence[(warmup_iterations + i) % seq_len] == 'A' else b
        x = r * x * (1 - x)
        
        # Если x выходит за пределы, это хаос
        if x <= 0 or x >= 1 or np.isnan(x):
            return 1.0
        
        # Вычисляем логарифм производной: ln|r * (1 - 2*x)|
        derivative = abs(r * (1 - 2 * x))
        if derivative > 0:
            total_lambda += np.log(derivative)
    
    # Среднее значение
    lambda_avg = total_lambda / num_iterations
    
    return lambda_avg


def _colorize(lyapunov_exponents, color_positive, color_negative, gamma, background_color):
    """
    Раскрашивает изображение на основе показателей Ляпунова.
    
    Показатель > 0 (хаос) — color_positive
    Показатель < 0 (стабильность) — color_negative
    """
    height, width = lyapunov_exponents.shape
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Находим диапазон значений для нормализации
    min_lambda = np.min(lyapunov_exponents)
    max_lambda = np.max(lyapunov_exponents)
    
    # Нормализуем в диапазон [-1, 1]
    if max_lambda > 0:
        normalized = lyapunov_exponents / max(abs(min_lambda), abs(max_lambda))
    else:
        normalized = np.zeros_like(lyapunov_exponents)
    
    # Применяем гамма-коррекцию
    normalized_gamma = np.power(np.abs(normalized), 1.0 / gamma) * np.sign(normalized)
    
    # Раскрашиваем
    for i in range(height):
        for j in range(width):
            val = normalized_gamma[i, j]
            
            if val > 0:
                # Хаос — используем color_positive
                intensity = min(1.0, val)
                img_array[i, j, 0] = int(color_positive[0] * intensity)
                img_array[i, j, 1] = int(color_positive[1] * intensity)
                img_array[i, j, 2] = int(color_positive[2] * intensity)
            elif val < 0:
                # Стабильность — используем color_negative
                intensity = min(1.0, abs(val))
                img_array[i, j, 0] = int(color_negative[0] * intensity)
                img_array[i, j, 1] = int(color_negative[1] * intensity)
                img_array[i, j, 2] = int(color_negative[2] * intensity)
            else:
                # Граница — background
                img_array[i, j] = background_color
    
    return img_array
