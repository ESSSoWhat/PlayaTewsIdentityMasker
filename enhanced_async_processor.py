#!/usr/bin/env python3
"""
Enhanced Asynchronous Video Processing Pipeline for DeepFaceLive
Advanced real-time processing with adaptive optimization and intelligent resource management
"""

import asyncio
import time
import logging
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Callable, Any, Dict, List, Tuple
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import weakref
from contextlib import contextmanager

@dataclass
class ProcessingTask:
    """Enhanced processing task container"""
    frame_id: int
    frame: np.ndarray
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    max_retries: int = 2
    retry_count: int = 0
    processing_time: float = 0.0
    result: Any = None
    error: Optional[Exception] = None

class ProcessingMode(Enum):
    """Processing mode options"""
    REALTIME = "realtime"      # Drop frames to maintain speed
    QUALITY = "quality"        # Process all frames, may queue
    BALANCED = "balanced"      # Adaptive between realtime and quality
    BATCH = "batch"           # Batch processing mode

class FrameSkipStrategy(Enum):
    """Frame skipping strategies"""
    DROP_OLDEST = "drop_oldest"       # Drop oldest frames in queue
    DROP_LOWEST_PRIORITY = "drop_low" # Drop lowest priority frames
    ADAPTIVE = "adaptive"             # Adaptive based on processing load
    NONE = "none"                     # Never drop frames

@dataclass
class ProcessingStats:
    """Processing performance statistics"""
    frames_processed: int = 0
    frames_dropped: int = 0
    frames_failed: int = 0
    avg_processing_time: float = 0.0
    max_processing_time: float = 0.0
    queue_size: int = 0
    effective_fps: float = 0.0
    cpu_utilization: float = 0.0
    memory_usage_mb: float = 0.0

class AdaptiveQualityController:
    """Adaptive quality control based on performance metrics"""
    
    def __init__(self, target_fps: float = 30.0):
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        self.current_quality = 1.0  # 0.1 to 1.0
        self.performance_history: deque = deque(maxlen=30)
        self.adjustment_factor = 0.1
        
    def update_performance(self, processing_time: float, queue_size: int):
        """Update performance metrics and adjust quality"""
        self.performance_history.append({
            'processing_time': processing_time,
            'queue_size': queue_size,
            'timestamp': time.time()
        })
        
        if len(self.performance_history) >= 5:
            self._adjust_quality()
    
    def _adjust_quality(self):
        """Adjust quality based on recent performance"""
        recent_times = [p['processing_time'] for p in list(self.performance_history)[-10:]]
        avg_time = sum(recent_times) / len(recent_times)
        
        recent_queue_sizes = [p['queue_size'] for p in list(self.performance_history)[-5:]]
        avg_queue_size = sum(recent_queue_sizes) / len(recent_queue_sizes)
        
        # Adjust quality based on performance
        if avg_time > self.target_frame_time * 1.5 or avg_queue_size > 3:
            # Reduce quality to improve performance
            self.current_quality = max(0.1, self.current_quality - self.adjustment_factor)
        elif avg_time < self.target_frame_time * 0.8 and avg_queue_size < 2:
            # Increase quality if performance allows
            self.current_quality = min(1.0, self.current_quality + self.adjustment_factor)
    
    def get_quality_settings(self) -> Dict[str, Any]:
        """Get current quality settings"""
        return {
            'quality_factor': self.current_quality,
            'resolution_scale': max(0.5, self.current_quality),
            'processing_scale': self.current_quality,
            'skip_frames': max(0, int((1.0 - self.current_quality) * 3))
        }

class EnhancedAsyncVideoProcessor:
    """Enhanced asynchronous video processing pipeline"""
    
    def __init__(self, 
                 buffer_size: int = 5,
                 max_workers: int = 4,
                 processing_mode: ProcessingMode = ProcessingMode.BALANCED,
                 skip_strategy: FrameSkipStrategy = FrameSkipStrategy.ADAPTIVE,
                 target_fps: float = 30.0):
        """
        Initialize enhanced async video processor
        
        Args:
            buffer_size: Maximum frames in processing queue
            max_workers: Number of processing threads
            processing_mode: Processing mode strategy
            skip_strategy: Frame skipping strategy
            target_fps: Target processing FPS
        """
        self.buffer_size = buffer_size
        self.max_workers = max_workers
        self.processing_mode = processing_mode
        self.skip_strategy = skip_strategy
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        
        # Processing queues
        self.input_queue = asyncio.Queue(maxsize=buffer_size)
        self.output_queue = asyncio.Queue(maxsize=buffer_size)
        self.priority_queue = queue.PriorityQueue(maxsize=buffer_size * 2)
        
        # Processing pipeline
        self.processors: List[Callable] = []
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="VideoProcessor")
        self.processing_tasks: Dict[int, asyncio.Task] = {}
        
        # State management
        self.running = False
        self.paused = False
        self.stats = ProcessingStats()
        self.frame_counter = 0
        self.last_stats_update = time.time()
        
        # Adaptive quality control
        self.quality_controller = AdaptiveQualityController(target_fps)
        
        # Performance monitoring
        self.processing_times: deque = deque(maxlen=100)
        self.frame_timestamps: deque = deque(maxlen=60)  # For FPS calculation
        
        # Callbacks
        self.on_frame_processed: Optional[Callable] = None
        self.on_frame_dropped: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        self.logger = logging.getLogger(__name__)
        
    async def start(self):
        """Start the processing pipeline"""
        if self.running:
            return
            
        self.running = True
        self.logger.info(f"Starting enhanced video processor with {self.max_workers} workers")
        
        # Start processing loops
        self.processing_task = asyncio.create_task(self._processing_loop())
        self.output_task = asyncio.create_task(self._output_loop())
        self.stats_task = asyncio.create_task(self._stats_loop())
        
    async def stop(self):
        """Stop the processing pipeline"""
        if not self.running:
            return
            
        self.running = False
        self.logger.info("Stopping video processor")
        
        # Cancel tasks
        if hasattr(self, 'processing_task'):
            self.processing_task.cancel()
        if hasattr(self, 'output_task'):
            self.output_task.cancel()
        if hasattr(self, 'stats_task'):
            self.stats_task.cancel()
            
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
    def pause(self):
        """Pause processing"""
        self.paused = True
        self.logger.info("Video processor paused")
        
    def resume(self):
        """Resume processing"""
        self.paused = False
        self.logger.info("Video processor resumed")
        
    def add_processor(self, processor: Callable, priority: int = 0):
        """Add a processing function to the pipeline"""
        self.processors.append((processor, priority))
        self.processors.sort(key=lambda x: x[1])  # Sort by priority
        
    async def process_frame(self, frame: np.ndarray, metadata: Dict[str, Any] = None) -> bool:
        """Submit a frame for processing"""
        if not self.running or self.paused:
            return False
            
        frame_id = self.frame_counter
        self.frame_counter += 1
        
        task = ProcessingTask(
            frame_id=frame_id,
            frame=frame,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        # Apply frame skipping strategy
        if not await self._should_process_frame(task):
            self.stats.frames_dropped += 1
            if self.on_frame_dropped:
                self.on_frame_dropped(task)
            return False
            
        try:
            await self.input_queue.put(task)
            return True
        except asyncio.QueueFull:
            # Handle queue full based on strategy
            return await self._handle_queue_full(task)
    
    async def get_processed_frame(self, timeout: float = 1.0) -> Optional[ProcessingTask]:
        """Get a processed frame"""
        try:
            return await asyncio.wait_for(self.output_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    async def _should_process_frame(self, task: ProcessingTask) -> bool:
        """Determine if a frame should be processed based on strategy"""
        if self.skip_strategy == FrameSkipStrategy.NONE:
            return True
            
        queue_size = self.input_queue.qsize()
        
        if self.skip_strategy == FrameSkipStrategy.ADAPTIVE:
            # Adaptive strategy based on current performance
            if queue_size > self.buffer_size * 0.7:  # 70% full
                # Check if we're behind target FPS
                if self.processing_times:
                    avg_time = sum(self.processing_times) / len(self.processing_times)
                    if avg_time > self.target_frame_time * 1.2:  # 20% slower than target
                        return False
            return True
            
        elif self.skip_strategy == FrameSkipStrategy.DROP_OLDEST:
            return queue_size < self.buffer_size
            
        elif self.skip_strategy == FrameSkipStrategy.DROP_LOWEST_PRIORITY:
            return task.priority >= 0  # Only process non-negative priority
            
        return True
    
    async def _handle_queue_full(self, task: ProcessingTask) -> bool:
        """Handle when input queue is full"""
        if self.processing_mode == ProcessingMode.REALTIME:
            # Drop the frame
            self.stats.frames_dropped += 1
            if self.on_frame_dropped:
                self.on_frame_dropped(task)
            return False
        elif self.processing_mode == ProcessingMode.QUALITY:
            # Wait for space (blocking)
            await self.input_queue.put(task)
            return True
        else:  # BALANCED
            # Try to drop an older frame
            return await self._try_drop_older_frame(task)
    
    async def _try_drop_older_frame(self, new_task: ProcessingTask) -> bool:
        """Try to drop an older frame to make space for new one"""
        # This is a simplified implementation
        # In practice, would need to access internal queue
        try:
            await asyncio.wait_for(self.input_queue.put(new_task), timeout=0.1)
            return True
        except asyncio.TimeoutError:
            self.stats.frames_dropped += 1
            if self.on_frame_dropped:
                self.on_frame_dropped(new_task)
            return False
    
    async def _processing_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(0.1)
                    continue
                    
                # Get task from input queue
                task = await self.input_queue.get()
                
                # Submit to thread pool for processing
                future = self.executor.submit(self._process_task, task)
                
                # Store task for tracking
                self.processing_tasks[task.frame_id] = asyncio.create_task(
                    self._handle_processing_result(future, task)
                )
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                if self.on_error:
                    self.on_error(e)
    
    def _process_task(self, task: ProcessingTask) -> ProcessingTask:
        """Process a single task in thread pool"""
        start_time = time.time()
        
        try:
            # Get current quality settings
            quality_settings = self.quality_controller.get_quality_settings()
            
            # Apply quality settings to task
            task.metadata.update(quality_settings)
            
            # Process through all processors
            current_frame = task.frame
            for processor, _ in self.processors:
                current_frame = processor(current_frame, task.metadata)
                if current_frame is None:
                    raise ValueError("Processor returned None")
            
            task.result = current_frame
            task.processing_time = time.time() - start_time
            self.stats.frames_processed += 1
            
        except Exception as e:
            task.error = e
            task.processing_time = time.time() - start_time
            self.stats.frames_failed += 1
            self.logger.error(f"Processing failed for frame {task.frame_id}: {e}")
            
        return task
    
    async def _handle_processing_result(self, future, task: ProcessingTask):
        """Handle the result of processing"""
        try:
            completed_task = await asyncio.get_event_loop().run_in_executor(None, future.result)
            
            # Update performance metrics
            self.processing_times.append(completed_task.processing_time)
            self.quality_controller.update_performance(
                completed_task.processing_time, 
                self.input_queue.qsize()
            )
            
            # Add to output queue
            try:
                await self.output_queue.put(completed_task)
            except asyncio.QueueFull:
                # Drop oldest result if output queue is full
                try:
                    self.output_queue.get_nowait()
                    await self.output_queue.put(completed_task)
                except asyncio.QueueEmpty:
                    pass
            
            # Callback
            if self.on_frame_processed:
                self.on_frame_processed(completed_task)
                
        except Exception as e:
            self.logger.error(f"Error handling processing result: {e}")
            if self.on_error:
                self.on_error(e)
        finally:
            # Cleanup
            if task.frame_id in self.processing_tasks:
                del self.processing_tasks[task.frame_id]
    
    async def _output_loop(self):
        """Output queue management loop"""
        while self.running:
            try:
                # Just maintain the queue for now
                # Actual output is handled by get_processed_frame()
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in output loop: {e}")
    
    async def _stats_loop(self):
        """Statistics update loop"""
        while self.running:
            try:
                await asyncio.sleep(1.0)  # Update stats every second
                self._update_stats()
            except Exception as e:
                self.logger.error(f"Error in stats loop: {e}")
    
    def _update_stats(self):
        """Update processing statistics"""
        current_time = time.time()
        
        # Calculate effective FPS
        self.frame_timestamps.append(current_time)
        if len(self.frame_timestamps) > 1:
            time_span = self.frame_timestamps[-1] - self.frame_timestamps[0]
            if time_span > 0:
                self.stats.effective_fps = len(self.frame_timestamps) / time_span
        
        # Update average processing time
        if self.processing_times:
            self.stats.avg_processing_time = sum(self.processing_times) / len(self.processing_times)
            self.stats.max_processing_time = max(self.processing_times)
        
        # Update queue size
        self.stats.queue_size = self.input_queue.qsize()
        
        self.last_stats_update = current_time
    
    def get_stats(self) -> ProcessingStats:
        """Get current processing statistics"""
        return self.stats
    
    def get_quality_info(self) -> Dict[str, Any]:
        """Get current quality information"""
        return {
            'current_quality': self.quality_controller.current_quality,
            'quality_settings': self.quality_controller.get_quality_settings(),
            'performance_history_size': len(self.quality_controller.performance_history)
        }
    
    def set_processing_mode(self, mode: ProcessingMode):
        """Change processing mode"""
        self.processing_mode = mode
        self.logger.info(f"Processing mode changed to: {mode.value}")
    
    def set_skip_strategy(self, strategy: FrameSkipStrategy):
        """Change frame skip strategy"""
        self.skip_strategy = strategy
        self.logger.info(f"Frame skip strategy changed to: {strategy.value}")
    
    def set_target_fps(self, fps: float):
        """Change target FPS"""
        self.target_fps = fps
        self.target_frame_time = 1.0 / fps
        self.quality_controller.target_fps = fps
        self.quality_controller.target_frame_time = self.target_frame_time
        self.logger.info(f"Target FPS changed to: {fps}")
    
    @contextmanager
    def performance_context(self, label: str = ""):
        """Context manager for performance monitoring"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            elapsed = end_time - start_time
            memory_delta = end_memory - start_memory
            
            self.logger.debug(f"Performance {label}: {elapsed:.3f}s, Memory: {memory_delta:.1f}MB")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

class BatchProcessor:
    """Batch processing for non-realtime scenarios"""
    
    def __init__(self, batch_size: int = 8, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.processors: List[Callable] = []
        
    def add_processor(self, processor: Callable):
        """Add a processing function"""
        self.processors.append(processor)
    
    def process_batch(self, frames: List[np.ndarray], metadata: List[Dict] = None) -> List[np.ndarray]:
        """Process a batch of frames"""
        if metadata is None:
            metadata = [{}] * len(frames)
            
        # Split into batches
        batches = []
        for i in range(0, len(frames), self.batch_size):
            batch_frames = frames[i:i + self.batch_size]
            batch_metadata = metadata[i:i + self.batch_size]
            batches.append((batch_frames, batch_metadata))
        
        # Process batches in parallel
        futures = []
        for batch_frames, batch_metadata in batches:
            future = self.executor.submit(self._process_batch, batch_frames, batch_metadata)
            futures.append(future)
        
        # Collect results
        results = []
        for future in as_completed(futures):
            batch_results = future.result()
            results.extend(batch_results)
        
        return results
    
    def _process_batch(self, frames: List[np.ndarray], metadata: List[Dict]) -> List[np.ndarray]:
        """Process a single batch"""
        results = []
        for frame, meta in zip(frames, metadata):
            current_frame = frame
            for processor in self.processors:
                current_frame = processor(current_frame, meta)
            results.append(current_frame)
        return results

# Global processor instance
_global_processor = None

def get_global_processor() -> EnhancedAsyncVideoProcessor:
    """Get global video processor instance"""
    global _global_processor
    if _global_processor is None:
        _global_processor = EnhancedAsyncVideoProcessor()
    return _global_processor

def optimize_for_realtime():
    """Optimize global processor for real-time processing"""
    processor = get_global_processor()
    processor.set_processing_mode(ProcessingMode.REALTIME)
    processor.set_skip_strategy(FrameSkipStrategy.ADAPTIVE)
    processor.set_target_fps(30.0)

def optimize_for_quality():
    """Optimize global processor for quality processing"""
    processor = get_global_processor()
    processor.set_processing_mode(ProcessingMode.QUALITY)
    processor.set_skip_strategy(FrameSkipStrategy.NONE)
    processor.set_target_fps(24.0)