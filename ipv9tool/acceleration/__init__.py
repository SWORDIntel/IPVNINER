"""
Hardware Acceleration Module

Leverages Intel NPU and Arc iGPU for smart acceleration:
- Pattern matching (GPU)
- Anomaly detection (NPU)
- ML inference (OpenVINO)
- Parallel processing (oneAPI)
"""

from .intel import (
    IntelAccelerator,
    AcceleratorType,
    get_intel_accelerator,
    configure_intel_acceleration
)

__all__ = [
    'IntelAccelerator',
    'AcceleratorType',
    'get_intel_accelerator',
    'configure_intel_acceleration'
]
