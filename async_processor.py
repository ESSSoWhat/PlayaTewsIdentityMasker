#!/usr/bin/env python3
"""
Asynchronous Video Processing Pipeline for DeepFaceLive
Optimizes real-time video processing with non-blocking operations
"""

import asyncio
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Callable, Any, Dict, List
from collections import deque
from dataclasses import dataclass
import numpy as np

@dataclass
class ProcessingTask:
    """Video processing task container"""
    frame_id: int
    frame: np.ndarray
    timestamp: float
    metadata: Dict[str, Any]

class AsyncVideoProcessor:
    """Asynchronous video processing pipeline"""
    
    def __init__(self, 
                 buffer_size: int = 3,
                 max_workers: int = 2,
                 drop_frames: bool = True):
        """
        Initialize async video processor
        
        Args:
            buffer_size: Maximum frames in processing queue
            max_workers: Number of processing threads
            drop_frames: Drop frames when queue is full (for real-time)
        """
        self.buffer_size = buffer_size
        self.max_workers = max_workers
        self.drop_frames = drop_frames
        
        # Processing queues
        self.input_queue = asyncio.Queue(maxsize=buffer_size)
        self.output_queue = asyncio.Queue(maxsize=buffer_size)
        
        # Processing pipeline
        self.processors: List[Callable] = []
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # State tracking
        self.processing = False
        self.worker_tasks: List[asyncio.Task] = []
        self.frame_counter = 0
        self.dropped_frames = 0
        
        # Performance metrics
        self.processing_times = deque(maxlen=100)
        self.queue_sizes = {'input': deque(maxlen=100), 'output': deque(maxlen=100)}
        
        self.logger = logging.getLogger(__name__)
    
    def add_processor(self, processor: Callable[[np.ndarray], np.ndarray]):
        """Add a processing function to the pipeline"""
        self.processors.append(processor)
        self.logger.info(f"Added processor: {processor.__name__}")
    
    async def start_processing(self):
        """Start the asynchronous processing pipeline"""
        if self.processing:
            return
        
        self.processing = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            task = asyncio.create_task(self._processing_worker(i))
            self.worker_tasks.append(task)
        
        # Start monitoring task
        monitor_task = asyncio.create_task(self._monitor_performance())
        self.worker_tasks.append(monitor_task)
        
        self.logger.info(f"Started {self.max_workers} processing workers")
    
    async def stop_processing(self):
        """Stop the processing pipeline"""
        if not self.processing:
            return
        
        self.processing = False
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("Processing pipeline stopped")
    
    async def process_frame_async(self, frame: np.ndarray, 
                                 metadata: Optional[Dict] = None) -> Optional[np.ndarray]:
        """
        Process frame asynchronously
        
        Args:
            frame: Input frame
            metadata: Optional frame metadata
            
        Returns:
            Processed frame or None if not ready
        """
        if not self.processing:
            await self.start_processing()
        
        # Create processing task
        task = ProcessingTask(
            frame_id=self.frame_counter,
            frame=frame.copy(),
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.frame_counter += 1
        
        # Try to add to input queue
        try:
            self.input_queue.put_nowait(task)
        except asyncio.QueueFull:
            if self.drop_frames:
                # Drop oldest frame and add new one
                try:
                    dropped_task = self.input_queue.get_nowait()
                    self.dropped_frames += 1
                    self.logger.debug(f"Dropped frame {dropped_task.frame_id}")
                except asyncio.QueueEmpty:
                    pass
                
                try:
                    self.input_queue.put_nowait(task)
                except asyncio.QueueFull:
                    self.dropped_frames += 1
                    return None
            else:
                # Block until space available
                await self.input_queue.put(task)
        
        # Try to get processed frame
        try:
            result_task = self.output_queue.get_nowait()
            return result_task.frame
        except asyncio.QueueEmpty:
            return None
    
    def process_frame_sync(self, frame: np.ndarray, 
                          metadata: Optional[Dict] = None) -> Optional[np.ndarray]:
        """Synchronous wrapper for frame processing"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.process_frame_async(frame, metadata)
            )
        finally:
            loop.close()
    
    async def _processing_worker(self, worker_id: int):
        """Background processing worker"""
        self.logger.info(f"Processing worker {worker_id} started")
        
        while self.processing:
            try:
                # Get task from input queue
                task = await asyncio.wait_for(
                    self.input_queue.get(), 
                    timeout=1.0
                )
                
                start_time = time.time()
                
                # Process frame through pipeline
                processed_frame = await self._process_through_pipeline(task.frame)
                
                # Update task with processed frame
                task.frame = processed_frame
                task.metadata['processing_time'] = time.time() - start_time
                task.metadata['worker_id'] = worker_id
                
                # Add to output queue
                try:
                    self.output_queue.put_nowait(task)
                except asyncio.QueueFull:
                    # Drop oldest output if queue is full
                    try:
                        self.output_queue.get_nowait()
                        self.output_queue.put_nowait(task)
                    except asyncio.QueueEmpty:
                        pass
                
                # Record processing time
                processing_time = time.time() - start_time
                self.processing_times.append(processing_time)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
        
        self.logger.info(f"Processing worker {worker_id} stopped")
    
    async def _process_through_pipeline(self, frame: np.ndarray) -> np.ndarray:
        """Process frame through all processors in pipeline"""
        current_frame = frame
        
        for processor in self.processors:
            try:
                # Run processor in thread pool for CPU-bound operations
                loop = asyncio.get_event_loop()
                current_frame = await loop.run_in_executor(
                    self.executor, processor, current_frame
                )
            except Exception as e:
                self.logger.error(f"Processor {processor.__name__} error: {e}")
                # Continue with unprocessed frame
                pass
        
        return current_frame
    
    async def _monitor_performance(self):
        """Monitor and log performance metrics"""
        while self.processing:
            try:
                # Record queue sizes
                self.queue_sizes['input'].append(self.input_queue.qsize())
                self.queue_sizes['output'].append(self.output_queue.qsize())
                
                # Log performance every 10 seconds
                await asyncio.sleep(10)
                
                if self.processing_times:
                    avg_processing_time = sum(self.processing_times) / len(self.processing_times)
                    max_processing_time = max(self.processing_times)
                    
                    avg_input_queue = sum(self.queue_sizes['input']) / len(self.queue_sizes['input'])
                    avg_output_queue = sum(self.queue_sizes['output']) / len(self.queue_sizes['output'])
                    
                    self.logger.info(
                        f"Performance - Avg processing: {avg_processing_time*1000:.1f}ms, "
                        f"Max: {max_processing_time*1000:.1f}ms, "
                        f"Dropped frames: {self.dropped_frames}, "
                        f"Avg queues: in={avg_input_queue:.1f}, out={avg_output_queue:.1f}"
                    )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
    
    def get_performance_stats(self) -> Dict:
        """Get current performance statistics"""
        if not self.processing_times:
            return {}
        
        return {
            'avg_processing_time_ms': (sum(self.processing_times) / len(self.processing_times)) * 1000,
            'max_processing_time_ms': max(self.processing_times) * 1000,
            'total_frames': self.frame_counter,
            'dropped_frames': self.dropped_frames,
            'drop_rate': self.dropped_frames / max(self.frame_counter, 1),
            'input_queue_size': self.input_queue.qsize(),
            'output_queue_size': self.output_queue.qsize(),
            'workers_active': len(self.worker_tasks) - 1  # Exclude monitor task
        }

class FrameBuffer:
    """Ring buffer for efficient frame management"""
    
    def __init__(self, size: int = 10):
        self.size = size
        self.buffer = [None] * size
        self.index = 0
        self.count = 0
    
    def put(self, frame: np.ndarray) -> int:
        """Add frame to buffer, returns frame ID"""
        frame_id = self.index
        self.buffer[self.index] = frame.copy()
        self.index = (self.index + 1) % self.size
        self.count = min(self.count + 1, self.size)
        return frame_id
    
    def get(self, frame_id: int) -> Optional[np.ndarray]:
        """Get frame by ID if still in buffer"""
        if self.count == 0:
            return None
        
        # Calculate if frame is still in buffer
        start_id = (self.index - self.count) % self.size
        if frame_id >= start_id or (start_id > self.index and frame_id < self.index):
            buffer_index = frame_id % self.size
            return self.buffer[buffer_index]
        
        return None
    
    def get_latest(self) -> Optional[np.ndarray]:
        """Get the most recent frame"""
        if self.count == 0:
            return None
        
        latest_index = (self.index - 1) % self.size
        return self.buffer[latest_index]

class OptimizedVideoStreamer:
    """High-performance video streaming with async processing"""
    
    def __init__(self, 
                 target_fps: int = 30,
                 buffer_size: int = 5):
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        
        # Processing components
        self.processor = AsyncVideoProcessor(buffer_size=buffer_size)
        self.frame_buffer = FrameBuffer(size=buffer_size * 2)
        
        # Streaming state
        self.streaming = False
        self.stream_task: Optional[asyncio.Task] = None
        self.last_frame_time = 0
        
        # Callbacks
        self.on_frame_ready: Optional[Callable[[np.ndarray], None]] = None
        
        self.logger = logging.getLogger(__name__)
    
    def set_processors(self, processors: List[Callable]):
        """Set processing pipeline"""
        for processor in processors:
            self.processor.add_processor(processor)
    
    async def start_streaming(self, frame_source: Callable[[], np.ndarray]):
        """Start streaming with frame source"""
        if self.streaming:
            return
        
        self.streaming = True
        await self.processor.start_processing()
        
        self.stream_task = asyncio.create_task(
            self._streaming_loop(frame_source)
        )
        
        self.logger.info(f"Started streaming at {self.target_fps} FPS")
    
    async def stop_streaming(self):
        """Stop streaming"""
        if not self.streaming:
            return
        
        self.streaming = False
        
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
        
        await self.processor.stop_processing()
        self.logger.info("Streaming stopped")
    
    async def _streaming_loop(self, frame_source: Callable[[], np.ndarray]):
        """Main streaming loop"""
        while self.streaming:
            try:
                current_time = time.time()
                
                # Maintain target FPS
                if current_time - self.last_frame_time < self.frame_interval:
                    await asyncio.sleep(0.001)  # Small sleep to prevent busy waiting
                    continue
                
                # Get new frame
                frame = frame_source()
                if frame is not None:
                    # Store in buffer
                    frame_id = self.frame_buffer.put(frame)
                    
                    # Process frame
                    processed_frame = await self.processor.process_frame_async(frame)
                    
                    # Send processed frame if available
                    if processed_frame is not None and self.on_frame_ready:
                        self.on_frame_ready(processed_frame)
                
                self.last_frame_time = current_time
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Streaming error: {e}")
                await asyncio.sleep(0.1)  # Prevent rapid error loops

# Example usage and testing
if __name__ == "__main__":
    import cv2
    
    async def test_async_processor():
        """Test the async video processor"""
        
        # Create test processors
        def blur_processor(frame):
            return cv2.GaussianBlur(frame, (15, 15), 0)
        
        def resize_processor(frame):
            height, width = frame.shape[:2]
            return cv2.resize(frame, (width//2, height//2))
        
        # Setup processor
        processor = AsyncVideoProcessor(buffer_size=2, max_workers=2)
        processor.add_processor(blur_processor)
        processor.add_processor(resize_processor)
        
        # Test with dummy frames
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        print("Testing async processor...")
        await processor.start_processing()
        
        # Process frames
        for i in range(10):
            processed = await processor.process_frame_async(test_frame)
            if processed is not None:
                print(f"Processed frame {i}: {processed.shape}")
            await asyncio.sleep(0.1)
        
        # Print stats
        stats = processor.get_performance_stats()
        print("Performance stats:", stats)
        
        await processor.stop_processing()
    
    # Run test
    asyncio.run(test_async_processor())