import os
import random
from datetime import datetime
from generators import lsystem
from utils import metadata
from runners.base_runner import BaseRunner


class LSystemRunner(BaseRunner):
    """Runner для L-систем"""
    
    @property
    def fractal_type(self) -> str:
        return "lsystem"
    
    def get_default_params(self):
        return {
            'width': 4096,
            'height': 4096,
            'axiom': 'F',
            'rules': {'F': 'F+F--F+F'},
            'angle': 60,
            'length': 10,
            'initial_angle': 0,
            'iterations': 4,
            'line_width': 2,
            'color_min': 100,
            'color_max': 255,
            'background_color': (0, 0, 0),
            'preset': 'koch',
            'zoom': 1.0,
            'center_x': None,
            'center_y': None
        }
    
    def get_random_params(self):
        """Генерирует случайные параметры для L-системы"""
        preset = random.choice([
            'koch', 'dragon', 'gosper', 'tree', 'bush',
            'sierpinski', 'square_koch', 'levy', 'plant', 'hilbert'
        ])
        
        # Количество итераций зависит от пресета (некоторые растут очень быстро)
        if preset in ['gosper', 'plant', 'penrose']:
            iterations = random.randint(3, 4)
        elif preset in ['dragon', 'hilbert']:
            iterations = random.randint(8, 12)
        elif preset in ['koch', 'square_koch', 'levy', 'sierpinski']:
            iterations = random.randint(4, 6)
        else:
            iterations = random.randint(3, 5)
        
        # Вариация угла (±10% от базового)
        base_angle = self._get_base_angle(preset)
        angle_variation = base_angle * random.uniform(-0.1, 0.1)
        angle = base_angle + angle_variation
        
        return {
            'width': 4096,
            'height': 4096,
            'axiom': None,  # Будет взято из пресета
            'rules': None,  # Будет взято из пресета
            'angle': angle,
            'length': 10,
            'initial_angle': None,  # Будет взято из пресета
            'iterations': iterations,
            'line_width': random.choice([3, 3, 6, 6, 9]),
            'color_min': random.randint(120, 160),
            'color_max': random.randint(200, 255),
            'background_color': (20, 20, 20),
            'preset': preset,
            'zoom': random.uniform(1.0, 2.0),
            'center_x': None,
            'center_y': None
        }
    
    def _get_base_angle(self, preset):
        """Возвращает базовый угол для пресета"""
        angles = {
            'koch': 60,
            'dragon': 90,
            'gosper': 60,
            'tree': 25.7,
            'bush': 20,
            'sierpinski': 120,
            'square_koch': 90,
            'levy': 45,
            'plant': 22.5,
            'hilbert': 90,
            'penrose': 36
        }
        return angles.get(preset, 90)
    
    def run(self, params, output_dir):
        type_output = os.path.join(output_dir, self.fractal_type)
        os.makedirs(type_output, exist_ok=True)
        
        img = lsystem.generate_lsystem(**params)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = os.path.join(type_output, f"{self.fractal_type}_{timestamp}.png")
        
        metadata.save_with_metadata(img, filename, self.fractal_type, params, timestamp)
        
        return filename
