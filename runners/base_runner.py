from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseRunner(ABC):
    """
    Абстрактный базовый класс для всех runner'ов фракталов.
    Все runner'ы должны наследоваться от этого класса и реализовать все абстрактные методы.
    """
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """
        Возвращает параметры по умолчанию для данного типа фрактала.
        
        Returns:
            Dict[str, Any]: Словарь с параметрами по умолчанию
        """
        pass
    
    @abstractmethod
    def get_random_params(self) -> Dict[str, Any]:
        """
        Генерирует случайные параметры для данного типа фрактала.
        
        Returns:
            Dict[str, Any]: Словарь со случайными параметрами
        """
        pass
    
    @abstractmethod
    def run(self, params: Dict[str, Any], output_dir: str) -> str:
        """
        Запускает генерацию фрактала с указанными параметрами.
        
        Args:
            params: Параметры генерации
            output_dir: Директория для сохранения результата
            
        Returns:
            str: Путь к сохранённому файлу
        """
        pass
    
    @property
    @abstractmethod
    def fractal_type(self) -> str:
        """
        Возвращает строковый идентификатор типа фрактала.
        
        Returns:
            str: Идентификатор типа (например, "newton", "ifs")
        """
        pass
