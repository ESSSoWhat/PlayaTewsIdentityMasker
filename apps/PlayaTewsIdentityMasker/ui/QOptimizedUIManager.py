#!/usr/bin/env python3
"""
Optimized UI Manager for DeepFaceLive
Implements lazy loading, batched updates, and performance optimization
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from localization import L
from xlib import qt as qtx

from .widgets.QOptimizedFrameViewer import QOptimizedFrameViewer


@dataclass
class UIComponent:
    """UI component with lazy loading support"""

    name: str
    create_func: Callable
    widget: Optional[qtx.QXWidget] = None
    is_loaded: bool = False
    is_visible: bool = False
    load_priority: int = 0  # Higher number = higher priority
    last_used: float = 0.0


class QOptimizedUIManager:
    """Optimized UI manager with lazy loading and performance monitoring"""

    def __init__(self, max_loaded_components: int = 10):
        self.max_loaded_components = max_loaded_components
        self.components: Dict[str, UIComponent] = {}
        self.loaded_components: List[str] = []

        # Performance tracking
        self.update_batch_size = 5
        self.update_queue = deque()
        self.last_batch_update = time.time()
        self.batch_update_interval = 0.1  # 100ms between batch updates

        # Monitoring
        self.performance_stats = {
            "total_updates": 0,
            "batched_updates": 0,
            "lazy_loads": 0,
            "component_unloads": 0,
            "avg_update_time": 0.0,
        }

        # Threading
        self.update_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # Start update timer
        self.update_timer = qtx.QXTimer(
            interval=50, timeout=self._process_batch_updates, start=True
        )

    def register_component(
        self, name: str, create_func: Callable, load_priority: int = 0
    ) -> str:
        """Register a UI component for lazy loading"""
        if name in self.components:
            self.logger.warning(f"Component {name} already registered")
            return name

        component = UIComponent(
            name=name,
            create_func=create_func,
            load_priority=load_priority,
            last_used=time.time(),
        )

        self.components[name] = component
        self.logger.info(f"Registered component: {name} (priority: {load_priority})")
        return name

    def get_component(self, name: str) -> Optional[qtx.QXWidget]:
        """Get a component, loading it if necessary"""
        if name not in self.components:
            self.logger.error(f"Component {name} not registered")
            return None

        component = self.components[name]
        component.last_used = time.time()

        # Load component if not loaded
        if not component.is_loaded:
            self._load_component(component)

        return component.widget

    def _load_component(self, component: UIComponent):
        """Load a component and manage memory"""
        try:
            # Check if we need to unload other components
            if len(self.loaded_components) >= self.max_loaded_components:
                self._unload_lowest_priority_component()

            # Create the component
            start_time = time.time()
            component.widget = component.create_func()
            component.is_loaded = True

            load_time = time.time() - start_time
            self.logger.info(f"Loaded component {component.name} in {load_time:.3f}s")

            # Add to loaded list
            self.loaded_components.append(component.name)
            self.performance_stats["lazy_loads"] += 1

        except Exception as e:
            self.logger.error(f"Failed to load component {component.name}: {e}")
            component.is_loaded = False

    def _unload_lowest_priority_component(self):
        """Unload the component with lowest priority and oldest usage"""
        if not self.loaded_components:
            return

        # Find component to unload
        lowest_priority = float("inf")
        oldest_time = float("inf")
        component_to_unload = None

        for name in self.loaded_components:
            component = self.components[name]
            if component.load_priority < lowest_priority or (
                component.load_priority == lowest_priority
                and component.last_used < oldest_time
            ):
                lowest_priority = component.load_priority
                oldest_time = component.last_used
                component_to_unload = name

        if component_to_unload:
            self._unload_component(component_to_unload)

    def _unload_component(self, name: str):
        """Unload a specific component"""
        if name not in self.components:
            return

        component = self.components[name]
        if component.is_loaded and component.widget:
            try:
                # Clean up widget
                if hasattr(component.widget, "cleanup"):
                    component.widget.cleanup()

                component.widget.deleteLater()
                component.widget = None
                component.is_loaded = False

                # Remove from loaded list
                if name in self.loaded_components:
                    self.loaded_components.remove(name)

                self.performance_stats["component_unloads"] += 1
                self.logger.info(f"Unloaded component: {name}")

            except Exception as e:
                self.logger.error(f"Error unloading component {name}: {e}")

    def queue_update(self, component_name: str, update_func: Callable):
        """Queue an update for batched processing"""
        with self.update_lock:
            self.update_queue.append((component_name, update_func))

    def _process_batch_updates(self):
        """Process batched updates for better performance"""
        current_time = time.time()

        # Check if it's time for batch update
        if (
            current_time - self.last_batch_update < self.batch_update_interval
            or len(self.update_queue) < self.update_batch_size
        ):
            return

        with self.update_lock:
            if not self.update_queue:
                return

            # Process batch
            batch_start = time.time()
            processed_count = 0

            while self.update_queue and processed_count < self.update_batch_size:
                component_name, update_func = self.update_queue.popleft()

                try:
                    component = self.components.get(component_name)
                    if component and component.is_loaded and component.widget:
                        update_func(component.widget)
                        processed_count += 1
                except Exception as e:
                    self.logger.error(f"Update error for {component_name}: {e}")

            # Update performance stats
            batch_time = time.time() - batch_start
            self.performance_stats["total_updates"] += processed_count
            self.performance_stats["batched_updates"] += 1

            # Update average time
            if self.performance_stats["batched_updates"] > 0:
                current_avg = self.performance_stats["avg_update_time"]
                new_avg = (
                    current_avg * (self.performance_stats["batched_updates"] - 1)
                    + batch_time
                ) / self.performance_stats["batched_updates"]
                self.performance_stats["avg_update_time"] = new_avg

            self.last_batch_update = current_time

            if processed_count > 0:
                self.logger.debug(
                    f"Processed {processed_count} updates in {batch_time:.3f}s"
                )

    def set_component_visibility(self, name: str, visible: bool):
        """Set component visibility and optimize loading"""
        if name not in self.components:
            return

        component = self.components[name]
        component.is_visible = visible

        if visible and not component.is_loaded:
            # Load component when it becomes visible
            self._load_component(component)
        elif not visible and component.is_loaded:
            # Consider unloading if not visible for a while
            component.last_used = time.time() - 60  # Mark as older

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        return {
            **self.performance_stats,
            "loaded_components": len(self.loaded_components),
            "total_components": len(self.components),
            "queue_size": len(self.update_queue),
            "memory_efficiency": len(self.loaded_components)
            / max(len(self.components), 1),
        }

    def optimize_for_performance(self, target_fps: int = 30):
        """Optimize UI for target performance"""
        # Adjust batch update interval based on target FPS
        self.batch_update_interval = 1.0 / target_fps

        # Adjust batch size based on performance
        if self.performance_stats["avg_update_time"] > 0.016:  # > 16ms
            self.update_batch_size = max(3, self.update_batch_size - 1)
        elif self.performance_stats["avg_update_time"] < 0.008:  # < 8ms
            self.update_batch_size = min(10, self.update_batch_size + 1)

        self.logger.info(
            f"Performance optimization: batch_size={self.update_batch_size}, "
            f"interval={self.batch_update_interval:.3f}s"
        )

    def cleanup(self):
        """Clean up all components and resources"""
        self.logger.info("Cleaning up UI manager...")

        # Stop timer
        if hasattr(self, "update_timer"):
            self.update_timer.stop()

        # Unload all components
        for name in list(self.loaded_components):
            self._unload_component(name)

        # Clear queues
        with self.update_lock:
            self.update_queue.clear()

        self.logger.info("UI manager cleanup completed")


# Global UI manager instance
_ui_manager: Optional[QOptimizedUIManager] = None


def get_ui_manager() -> QOptimizedUIManager:
    """Get the global UI manager instance"""
    global _ui_manager
    if _ui_manager is None:
        _ui_manager = QOptimizedUIManager()
    return _ui_manager


def cleanup_ui_manager():
    """Clean up the global UI manager"""
    global _ui_manager
    if _ui_manager:
        _ui_manager.cleanup()
        _ui_manager = None
