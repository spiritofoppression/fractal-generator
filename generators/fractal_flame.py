import numpy as np
import random
import json
from PIL import Image

# ==============================================================================
# СИМВОЛЬНЫЕ ДЕРЕВЬЯ ВЫРАЖЕНИЙ
# ==============================================================================

class ExprNode:
    def evaluate(self, z):
        raise NotImplementedError
    def to_dict(self):
        raise NotImplementedError

class Var(ExprNode):
    def evaluate(self, z):
        return z
    def to_dict(self):
        return {"type": "Var"}

class Const(ExprNode):
    def __init__(self):
        self.value = complex(random.uniform(-1, 1), random.uniform(-1, 1))
    def evaluate(self, z):
        return np.full_like(z, self.value)
    def to_dict(self):
        return {"type": "Const", "re": self.value.real, "im": self.value.imag}

class UnaryOp(ExprNode):
    OPERATORS = ['sin', 'cos', 'tan', 'sinh', 'tanh', 
                 'square', 'cube', 'sqrt', 'inverse', 'exp']
    
    def __init__(self, child):
        self.op = random.choice(self.OPERATORS)
        self.child = child
        
    def evaluate(self, z):
        val = self.child.evaluate(z)
        with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
            # Ограничиваем вход для нестабильных функций
            if self.op in ['exp', 'sinh']:
                val = np.clip(val, -3, 3)
            elif self.op in ['tan']:
                val = np.clip(val, -1.5, 1.5)
            
            if self.op == 'sin': res = np.sin(val)
            elif self.op == 'cos': res = np.cos(val)
            elif self.op == 'tan': res = np.tan(val)
            elif self.op == 'sinh': res = np.sinh(val)
            elif self.op == 'tanh': res = np.tanh(val)
            elif self.op == 'square': res = val ** 2
            elif self.op == 'cube': res = val ** 3
            elif self.op == 'sqrt': 
                # Правильный sqrt для комплексных чисел без разрывов
                res = np.sqrt(np.abs(val) + 1e-6) * np.exp(0.5j * np.angle(val))
            elif self.op == 'inverse': res = 1.0 / (val + 1e-6)
            elif self.op == 'exp': res = np.exp(val)
            else: res = val
            
        # Плавное ограничение вместо жёсткого clip
        # tanh сжимает большие значения, но без резких границ
        res = np.tanh(res / 5.0) * 5.0
        return np.nan_to_num(res, nan=0.0, posinf=0.0, neginf=0.0)

    def to_dict(self):
        return {"type": "UnaryOp", "op": self.op, "child": self.child.to_dict()}

class BinaryOp(ExprNode):
    OPERATORS = ['add', 'sub', 'mul', 'div', 'power']
    
    def __init__(self, left, right):
        self.op = random.choice(self.OPERATORS)
        self.left = left
        self.right = right
        
    def evaluate(self, z):
        l_val = self.left.evaluate(z)
        r_val = self.right.evaluate(z)
        with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
            if self.op == 'add': res = l_val + r_val
            elif self.op == 'sub': res = l_val - r_val
            elif self.op == 'mul': res = l_val * r_val
            elif self.op == 'div': res = l_val / (r_val + 1e-6)
            elif self.op == 'power':
                r_clipped = np.clip(r_val, -1.5, 1.5)
                res = np.exp(r_clipped * np.log(np.abs(l_val) + 1e-6) + 1j * np.angle(l_val))
            else: res = l_val
        
        # Плавное ограничение
        res = np.tanh(res / 5.0) * 5.0
        return np.nan_to_num(res, nan=0.0, posinf=0.0, neginf=0.0)

    def to_dict(self):
        return {"type": "BinaryOp", "op": self.op, 
                "left": self.left.to_dict(), "right": self.right.to_dict()}

def generate_random_function(max_depth=4):
    def _generate(depth):
        if depth >= max_depth:
            return Var() if random.random() > 0.3 else Const()
        
        choice = random.random()
        if choice < 0.25:
            return Var()
        elif choice < 0.35:
            return Const()
        elif choice < 0.70:
            return UnaryOp(_generate(depth + 1))
        else:
            return BinaryOp(_generate(depth + 1), _generate(depth + 1))
    
    return _generate(0)

def build_tree_from_dict(d):
    t = d['type']
    if t == 'Const':
        node = Const()
        node.value = complex(d['re'], d['im'])
        return node
    elif t == 'Var':
        return Var()
    elif t == 'UnaryOp':
        return UnaryOp(build_tree_from_dict(d['child']))
    elif t == 'BinaryOp':
        return BinaryOp(build_tree_from_dict(d['left']), build_tree_from_dict(d['right']))
    return Var()

# ==============================================================================
# ГЕНЕРАТОР FRACTAL FLAME
# ==============================================================================

def generate_fractal_flame(
    width=1024, 
    height=1024, 
    num_points=500000, 
    iterations=5,        # Увеличили с 2 до 5
    burn_in=3,           # Новый параметр: итерации "прогрева"
    num_transforms=4, 
    max_depth=4, 
    zoom=1.0, 
    center_x=0.0, 
    center_y=0.0,
    transforms_json=None
):
    transforms = []
    if transforms_json:
        data = json.loads(transforms_json)
        for t_data in data:
            transforms.append({
                'func': build_tree_from_dict(t_data['function_tree']),
                'scale': t_data['scale'],
                'shift': complex(t_data['shift']['re'], t_data['shift']['im']),
                'color': tuple(t_data['color'])
            })
    else:
        for _ in range(num_transforms):
            func_tree = generate_random_function(max_depth)
            scale = random.uniform(0.6, 0.9)
            shift = complex(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            transforms.append({'func': func_tree, 'scale': scale, 'shift': shift, 'color': color})

    # Chaos Game
    N = num_points
    
    # КРУГЛОЕ начальное распределение вместо квадратного
    radius = np.sqrt(np.random.uniform(0, 1, N))
    angle = np.random.uniform(0, 2 * np.pi, N)
    Z = radius * np.cos(angle) + 1j * radius * np.sin(angle)
    
    hist = np.zeros((height, width), dtype=float)
    color_hist = np.zeros((height, width, 3), dtype=float)
    
    scale_x = width / 4.0
    scale_y = height / 4.0

    # Burn-in: первые итерации не рендерим, чтобы точки "забыли" начальное распределение
    for _ in range(burn_in):
        indices = np.random.randint(0, len(transforms), N)
        new_Z = np.zeros_like(Z)
        
        for i, t in enumerate(transforms):
            mask = (indices == i)
            if np.any(mask):
                z_subset = Z[mask]
                new_Z[mask] = t['func'].evaluate(z_subset) * t['scale'] + t['shift']
        
        Z = new_Z

    # Основные итерации с рендерингом
    for _ in range(iterations):
        indices = np.random.randint(0, len(transforms), N)
        new_Z = np.zeros_like(Z)
        
        for i, t in enumerate(transforms):
            mask = (indices == i)
            if np.any(mask):
                z_subset = Z[mask]
                new_Z[mask] = t['func'].evaluate(z_subset) * t['scale'] + t['shift']
        
        Z = new_Z
        
        x = (Z.real - center_x) * zoom * scale_x + width / 2
        y = (Z.imag - center_y) * zoom * scale_y + height / 2
        
        valid = (x >= 0) & (x < width) & (y >= 0) & (y < height)
        x_valid = x[valid].astype(int)
        y_valid = y[valid].astype(int)
        idx_valid = indices[valid]
        
        np.add.at(hist, (y_valid, x_valid), 1)
        for i, t in enumerate(transforms):
            mask = (idx_valid == i)
            if np.any(mask):
                color_hist[y_valid[mask], x_valid[mask]] += np.array(t['color'])

    # Рендеринг
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    log_hist = np.log1p(hist)
    max_log = np.max(log_hist)
    if max_log > 0:
        norm_hist = log_hist / max_log
    else:
        norm_hist = log_hist

    valid_pixels = hist > 0
    if np.any(valid_pixels):
        counts = np.maximum(hist[valid_pixels], 1)[:, np.newaxis]
        avg_colors = color_hist[valid_pixels] / counts
        brightness = norm_hist[valid_pixels, np.newaxis] ** 0.5
        final_colors = (avg_colors * brightness * 255).astype(np.uint8)
        img_array[valid_pixels] = final_colors

    img = Image.fromarray(img_array, 'RGB')
    
    params = {
        'num_points': num_points,
        'iterations': iterations,
        'burn_in': burn_in,
        'num_transforms': num_transforms,
        'max_depth': max_depth,
        'zoom': zoom,
        'center_x': center_x,
        'center_y': center_y,
        'transforms': [
            {
                'function_tree': t['func'].to_dict(),
                'scale': t['scale'],
                'shift': {'re': t['shift'].real, 'im': t['shift'].imag},
                'color': t['color']
            } for t in transforms
        ]
    }
    
    img.info['fractal_type'] = 'fractal_flame'
    img.info['generation_params'] = json.dumps(params)
    
    return img
