import os
import importlib
import inspect
from typing import Dict
from runners.base_runner import BaseRunner

class RunnerRegistry:
    """Реестр всех доступных runner'ов"""
    
    _runners: Dict[str, BaseRunner] = {}
    
    @classmethod
    def register(cls, runner_class: type):
        """
        Регистрирует runner в реестре.
        
        Args:
            runner_class: Класс runner'а (должен наследоваться от BaseRunner)
        """
        if not issubclass(runner_class, BaseRunner):
            raise TypeError(f"{runner_class.__name__} must inherit from BaseRunner")
        
        instance = runner_class()
        cls._runners[instance.fractal_type] = instance
    
    @classmethod
    def get(cls, fractal_type: str) -> BaseRunner:
        """
        Получает runner по типу фрактала.
        
        Args:
            fractal_type: Тип фрактала
            
        Returns:
            BaseRunner: Экземпляр runner'а
            
        Raises:
            KeyError: Если runner не найден
        """
        if fractal_type not in cls._runners:
            raise KeyError(f"Runner for '{fractal_type}' not found. Available: {list(cls._runners.keys())}")
        return cls._runners[fractal_type]
    
    @classmethod
    def list_available(cls) -> list:
        """Возвращает список доступных типов фракталов"""
        return list(cls._runners.keys())
    
    @classmethod
    def auto_discover(cls):
        """
        Автоматически обнаруживает и регистрирует все runner'ы в папке runners.
        Ищет все классы, наследующиеся от BaseRunner (кроме самого BaseRunner).
        """
        runners_dir = os.path.dirname(__file__)
        
        for filename in os.listdir(runners_dir):
            if filename.endswith('_runner.py') and not filename.startswith('_'):
                module_name = filename[:-3]  # Убираем .py
                module = importlib.import_module(f'runners.{module_name}')
                
                # Ищем все классы в модуле
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Проверяем, что это наследник BaseRunner и не сам BaseRunner
                    if issubclass(obj, BaseRunner) and obj is not BaseRunner:
                        cls.register(obj)
