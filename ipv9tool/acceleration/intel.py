#!/usr/bin/env python3
"""
Intel Hardware Acceleration Module

Leverages Intel NPU (Neural Processing Unit) and Arc iGPU for smart
acceleration of network intelligence operations.

Supported Intel Technologies:
- Intel NPU: ML-based pattern recognition and anomaly detection
- Intel Arc iGPU: Parallel processing for data analysis
- Intel OpenVINO: Optimized inference engine
- Intel oneAPI: SYCL/DPC++ for heterogeneous computing
"""

import logging
import os
from typing import Optional, Dict, Any, List
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class AcceleratorType(Enum):
    """Hardware accelerator types"""
    NPU = "npu"
    GPU = "gpu"
    CPU = "cpu"


class IntelAccelerator:
    """
    Intel Hardware Acceleration Manager

    Detects and utilizes Intel NPU and Arc iGPU for accelerated operations:
    - Pattern matching (GPU)
    - Anomaly detection (NPU)
    - Data processing (GPU/NPU)
    - ML inference (OpenVINO on NPU/GPU)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Intel accelerator

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.verbose = self.config.get('scanner', {}).get('verbose', False)

        # Acceleration settings
        self.enable_npu = self.config.get('acceleration', {}).get('enable_npu', True)
        self.enable_gpu = self.config.get('acceleration', {}).get('enable_gpu', True)
        self.prefer_npu = self.config.get('acceleration', {}).get('prefer_npu', True)

        # Hardware detection
        self.npu_available = False
        self.gpu_available = False
        self.openvino_available = False
        self.oneapi_available = False

        # Active accelerator
        self.active_accelerator = AcceleratorType.CPU

        # Initialize hardware
        self._detect_hardware()
        self._initialize_accelerators()

    def _detect_hardware(self):
        """Detect available Intel hardware"""
        if self.verbose:
            logger.info("  ► Detecting Intel hardware accelerators...")

        # Detect Intel NPU
        self.npu_available = self._detect_npu()

        # Detect Intel Arc iGPU
        self.gpu_available = self._detect_igpu()

        # Detect OpenVINO
        self.openvino_available = self._detect_openvino()

        # Detect oneAPI
        self.oneapi_available = self._detect_oneapi()

        if self.verbose:
            logger.info(f"  ► Intel NPU: {'DETECTED' if self.npu_available else 'NOT FOUND'}")
            logger.info(f"  ► Intel Arc iGPU: {'DETECTED' if self.gpu_available else 'NOT FOUND'}")
            logger.info(f"  ► Intel OpenVINO: {'INSTALLED' if self.openvino_available else 'NOT INSTALLED'}")
            logger.info(f"  ► Intel oneAPI: {'INSTALLED' if self.oneapi_available else 'NOT INSTALLED'}")

    def _detect_npu(self) -> bool:
        """
        Detect Intel NPU (Neural Processing Unit)

        Intel NPU is available on:
        - Intel Core Ultra (Meteor Lake) processors
        - Intel Core Ultra Series 2 (Lunar Lake) processors
        - Future Intel processors with integrated AI accelerators

        Returns:
            True if NPU detected
        """
        try:
            # Check for Intel NPU via OpenVINO
            if self.openvino_available:
                try:
                    from openvino.runtime import Core
                    core = Core()
                    devices = core.available_devices

                    # Intel NPU device name
                    npu_devices = [d for d in devices if 'NPU' in d]

                    if npu_devices:
                        if self.verbose:
                            logger.info(f"    Intel NPU devices: {npu_devices}")
                        return True
                except Exception as e:
                    logger.debug(f"OpenVINO NPU detection failed: {e}")

            # Check via sysfs (Linux)
            npu_paths = [
                '/sys/class/accel/accel0',  # Intel NPU driver
                '/dev/accel/accel0',
                '/sys/devices/pci0000:00/0000:00:0b.0',  # Intel NPU PCI device
            ]

            for path in npu_paths:
                if os.path.exists(path):
                    if self.verbose:
                        logger.info(f"    Found NPU at: {path}")
                    return True

            # Check via lspci (if available)
            try:
                import subprocess
                result = subprocess.run(
                    ['lspci'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if 'Neural' in result.stdout or 'NPU' in result.stdout:
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

            return False

        except Exception as e:
            logger.debug(f"NPU detection error: {e}")
            return False

    def _detect_igpu(self) -> bool:
        """
        Detect Intel Arc iGPU (Integrated Graphics)

        Intel Arc iGPU is available on:
        - Intel Arc Alchemist (12th gen and later)
        - Intel Iris Xe Graphics
        - Intel UHD Graphics (with compute support)

        Returns:
            True if Intel iGPU detected
        """
        try:
            # Check via OpenVINO
            if self.openvino_available:
                try:
                    from openvino.runtime import Core
                    core = Core()
                    devices = core.available_devices

                    # Intel GPU device
                    gpu_devices = [d for d in devices if 'GPU' in d]

                    if gpu_devices:
                        if self.verbose:
                            logger.info(f"    Intel GPU devices: {gpu_devices}")
                        return True
                except Exception as e:
                    logger.debug(f"OpenVINO GPU detection failed: {e}")

            # Check via sysfs/DRI (Linux)
            gpu_paths = [
                '/dev/dri/renderD128',  # Intel GPU render node
                '/dev/dri/card0',
                '/sys/class/drm/card0',
            ]

            for path in gpu_paths:
                if os.path.exists(path):
                    # Verify it's Intel
                    try:
                        vendor_path = f"{path}/device/vendor"
                        if os.path.exists(vendor_path):
                            with open(vendor_path, 'r') as f:
                                vendor = f.read().strip()
                                if vendor == '0x8086':  # Intel PCI vendor ID
                                    if self.verbose:
                                        logger.info(f"    Found Intel GPU at: {path}")
                                    return True
                    except Exception:
                        pass

            # Check via lspci
            try:
                import subprocess
                result = subprocess.run(
                    ['lspci'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if 'Intel' in result.stdout and ('VGA' in result.stdout or 'Display' in result.stdout):
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

            return False

        except Exception as e:
            logger.debug(f"iGPU detection error: {e}")
            return False

    def _detect_openvino(self) -> bool:
        """
        Detect Intel OpenVINO Toolkit

        OpenVINO provides optimized inference for Intel hardware.

        Returns:
            True if OpenVINO is installed
        """
        try:
            import openvino
            if self.verbose:
                logger.info(f"    OpenVINO version: {openvino.__version__}")
            return True
        except ImportError:
            return False

    def _detect_oneapi(self) -> bool:
        """
        Detect Intel oneAPI

        oneAPI provides SYCL/DPC++ for heterogeneous computing.

        Returns:
            True if oneAPI is installed
        """
        try:
            # Check for oneAPI environment variables
            oneapi_root = os.environ.get('ONEAPI_ROOT')
            if oneapi_root and os.path.exists(oneapi_root):
                return True

            # Check for SYCL libraries
            try:
                import dpctl
                if self.verbose:
                    logger.info(f"    oneAPI/dpctl version: {dpctl.__version__}")
                return True
            except ImportError:
                pass

            return False

        except Exception as e:
            logger.debug(f"oneAPI detection error: {e}")
            return False

    def _initialize_accelerators(self):
        """Initialize available accelerators"""
        if self.verbose:
            logger.info("  ► Initializing hardware accelerators...")

        # Determine active accelerator based on priority and availability
        if self.enable_npu and self.npu_available and self.prefer_npu:
            self.active_accelerator = AcceleratorType.NPU
            if self.verbose:
                logger.info("  ✓ Active accelerator: INTEL NPU")

        elif self.enable_gpu and self.gpu_available:
            self.active_accelerator = AcceleratorType.GPU
            if self.verbose:
                logger.info("  ✓ Active accelerator: INTEL ARC iGPU")

        else:
            self.active_accelerator = AcceleratorType.CPU
            if self.verbose:
                logger.info("  ► Active accelerator: CPU (no Intel accelerators available)")

        # Initialize OpenVINO if available
        if self.openvino_available:
            self._initialize_openvino()

    def _initialize_openvino(self):
        """Initialize OpenVINO runtime"""
        try:
            from openvino.runtime import Core

            self.ov_core = Core()

            if self.verbose:
                logger.info("  ✓ OpenVINO runtime initialized")
                available_devices = self.ov_core.available_devices
                logger.info(f"    Available devices: {available_devices}")

        except Exception as e:
            logger.warning(f"OpenVINO initialization failed: {e}")
            self.openvino_available = False

    def accelerate_pattern_matching(self, patterns: List[str], targets: List[str]) -> Dict[str, List[str]]:
        """
        GPU-accelerated pattern matching

        Uses Intel Arc iGPU for parallel pattern matching across large datasets.

        Args:
            patterns: List of regex patterns to match
            targets: List of strings to match against

        Returns:
            Dict mapping patterns to matching targets
        """
        if self.verbose:
            logger.info(f"  ► Pattern matching: {len(patterns)} patterns × {len(targets)} targets")
            logger.info(f"  ► Accelerator: {self.active_accelerator.value}")

        # GPU-accelerated implementation would go here
        # For now, fallback to CPU
        results = {}

        import re
        for pattern in patterns:
            compiled = re.compile(pattern)
            matches = [t for t in targets if compiled.match(t)]
            results[pattern] = matches

        if self.verbose:
            total_matches = sum(len(v) for v in results.values())
            logger.info(f"  ✓ Pattern matching complete: {total_matches} matches found")

        return results

    def accelerate_anomaly_detection(self, data: np.ndarray) -> np.ndarray:
        """
        NPU-accelerated anomaly detection

        Uses Intel NPU for ML-based anomaly detection in network data.

        Args:
            data: Network data array (samples × features)

        Returns:
            Anomaly scores (higher = more anomalous)
        """
        if self.verbose:
            logger.info(f"  ► Anomaly detection: {data.shape[0]} samples")
            logger.info(f"  ► Accelerator: {self.active_accelerator.value}")

        # NPU-accelerated ML inference would go here
        # For now, simple statistical anomaly detection
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        z_scores = np.abs((data - mean) / (std + 1e-10))
        anomaly_scores = np.max(z_scores, axis=1)

        if self.verbose:
            anomalies = np.sum(anomaly_scores > 3)  # 3-sigma threshold
            logger.info(f"  ✓ Anomaly detection complete: {anomalies} anomalies detected")

        return anomaly_scores

    def get_stats(self) -> Dict[str, Any]:
        """Get hardware acceleration statistics"""
        return {
            'npu_available': self.npu_available,
            'gpu_available': self.gpu_available,
            'openvino_available': self.openvino_available,
            'oneapi_available': self.oneapi_available,
            'active_accelerator': self.active_accelerator.value,
            'acceleration_enabled': self.active_accelerator != AcceleratorType.CPU
        }


# Global accelerator instance
_intel_accelerator: Optional[IntelAccelerator] = None


def get_intel_accelerator(config: Optional[Dict[str, Any]] = None) -> IntelAccelerator:
    """Get global Intel accelerator instance"""
    global _intel_accelerator
    if _intel_accelerator is None:
        _intel_accelerator = IntelAccelerator(config)
    return _intel_accelerator


def configure_intel_acceleration(config: Dict[str, Any]):
    """Configure global Intel accelerator"""
    global _intel_accelerator
    _intel_accelerator = IntelAccelerator(config)
