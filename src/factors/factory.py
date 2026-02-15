from typing import Dict, Type
from .base import BaseFactor
from .momentum.price_momentum import PriceMomentum, ShortTermReversal

class FactorFactor:
    """Factory for creating factor instances"""

    _registry: Dict[str, Type[BaseFactor]] = {}

    @classmethod
    def register(cls, name: str, factor_class: Type[BaseFactor]):
        """Register a factor class"""
        cls._registry[name] = factor_class

    @classmethod
    def create(cls, name: str, **kwargs):
        """Create factor instance"""
        if name not in cls._registry:
            raise ValueError(f"Unknown factor: {name}. Available: {list(cls._registry.keys())}")

        factor_class = cls._registry[name]
        return factor_class(**kwargs)

    @classmethod
    def list_factors(cls) -> list:
        """List all registered factors"""
        return list(cls._registry.keys())

# Register build-in factors
FactorFactor.register('momentum', PriceMomentum)
FactorFactor.register('reversal', ShortTermReversal)