#!/usr/bin/env python3
"""
Test Script for DeepFaceLive Performance Optimizations
Demonstrates key optimization concepts without external dependencies
"""

import asyncio
import time
import threading
from collections import deque
import gc

class SimplePerformanceTest:
    """Simple performance test without external dependencies"""
    
    def __init__(self):
        self.frame_times = deque(maxlen=30)
        self.start_time = time.time()
        self.frame_count = 0
    
    def record_frame(self, processing_time):
        """Record frame processing time"""
        self.frame_times.append(processing_time)
        self.frame_count += 1
    
    def get_fps(self):
        """Calculate current FPS"""
        if not self.frame_times:
            return 0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0
    
    def get_stats(self):
        """Get performance statistics"""
        return {
            'fps': self.get_fps(),
            'frames_processed': self.frame_count,
            'uptime': time.time() - self.start_time,
            'avg_frame_time_ms': sum(self.frame_times) * 1000 / len(self.frame_times) if self.frame_times else 0
        }

class SimpleAsyncProcessor:
    """Simple async processor demonstration"""
    
    def __init__(self, buffer_size=3):
        self.input_queue = asyncio.Queue(maxsize=buffer_size)
        self.output_queue = asyncio.Queue(maxsize=buffer_size)
        self.processing = False
        self.worker_task = None
        self.processed_count = 0
    
    async def start(self):
        """Start processing"""
        if self.processing:
            return
        
        self.processing = True
        self.worker_task = asyncio.create_task(self._worker())
        print("✅ Async processor started")
    
    async def stop(self):
        """Stop processing"""
        if not self.processing:
            return
        
        self.processing = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        print("✅ Async processor stopped")
    
    async def process_frame(self, frame_data):
        """Process frame asynchronously"""
        try:
            # Non-blocking put
            self.input_queue.put_nowait(frame_data)
        except asyncio.QueueFull:
            # Drop frame if queue is full (real-time processing)
            print("⚠️  Dropped frame - queue full")
            return None
        
        # Try to get processed result
        try:
            return self.output_queue.get_nowait()
        except asyncio.QueueEmpty:
            return None
    
    async def _worker(self):
        """Background processing worker"""
        while self.processing:
            try:
                # Get frame from input queue
                frame_data = await asyncio.wait_for(
                    self.input_queue.get(), 
                    timeout=1.0
                )
                
                # Simulate processing
                await self._simulate_processing(frame_data)
                
                # Put result in output queue
                result = f"processed_{frame_data}_{self.processed_count}"
                try:
                    self.output_queue.put_nowait(result)
                    self.processed_count += 1
                except asyncio.QueueFull:
                    # Drop oldest result if queue is full
                    try:
                        self.output_queue.get_nowait()
                        self.output_queue.put_nowait(result)
                    except asyncio.QueueEmpty:
                        pass
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
    
    async def _simulate_processing(self, frame_data):
        """Simulate frame processing"""
        # Simulate variable processing time
        import random
        processing_time = random.uniform(0.01, 0.05)  # 10-50ms
        await asyncio.sleep(processing_time)

class SimpleMemoryPool:
    """Simple memory pool for demonstration"""
    
    def __init__(self, max_size=10):
        self.pool = []
        self.max_size = max_size
        self.allocations = 0
        self.reuses = 0
    
    def allocate(self, size):
        """Allocate or reuse memory"""
        if self.pool:
            memory = self.pool.pop()
            self.reuses += 1
            print(f"♻️  Reused memory block (reuses: {self.reuses})")
            return memory
        else:
            memory = bytearray(size)
            self.allocations += 1
            print(f"🆕 Allocated new memory block (total: {self.allocations})")
            return memory
    
    def deallocate(self, memory):
        """Return memory to pool"""
        if len(self.pool) < self.max_size:
            self.pool.append(memory)
            print(f"📦 Returned memory to pool (pool size: {len(self.pool)})")
        else:
            print("🗑️  Pool full, freeing memory")
            del memory
            gc.collect()
    
    def get_stats(self):
        """Get pool statistics"""
        return {
            'pool_size': len(self.pool),
            'max_size': self.max_size,
            'total_allocations': self.allocations,
            'total_reuses': self.reuses,
            'reuse_rate': self.reuses / max(self.allocations, 1)
        }

async def test_async_processing():
    """Test asynchronous processing pipeline"""
    print("\n🚀 Testing Async Processing Pipeline")
    print("=" * 50)
    
    processor = SimpleAsyncProcessor(buffer_size=2)
    perf_test = SimplePerformanceTest()
    
    await processor.start()
    
    # Process frames
    for i in range(20):
        start_time = time.time()
        
        # Submit frame for processing
        result = await processor.process_frame(f"frame_{i}")
        
        # Record performance
        processing_time = time.time() - start_time
        perf_test.record_frame(processing_time)
        
        if result:
            print(f"📄 {result}")
        
        # Log stats every 10 frames
        if i % 10 == 9:
            stats = perf_test.get_stats()
            print(f"📊 Stats: FPS={stats['fps']:.1f}, "
                  f"Avg frame time={stats['avg_frame_time_ms']:.1f}ms")
        
        await asyncio.sleep(0.02)  # 50 FPS target
    
    await processor.stop()
    
    # Final stats
    final_stats = perf_test.get_stats()
    print(f"\n📈 Final Performance:")
    print(f"   FPS: {final_stats['fps']:.1f}")
    print(f"   Frames processed: {final_stats['frames_processed']}")
    print(f"   Avg frame time: {final_stats['avg_frame_time_ms']:.1f}ms")

def test_memory_pooling():
    """Test memory pooling optimization"""
    print("\n🧠 Testing Memory Pooling")
    print("=" * 50)
    
    pool = SimpleMemoryPool(max_size=3)
    
    # Allocate and deallocate memory blocks
    memory_blocks = []
    
    # First round: allocations
    for i in range(5):
        memory = pool.allocate(1024)  # 1KB blocks
        memory_blocks.append(memory)
    
    # Second round: deallocations
    for memory in memory_blocks:
        pool.deallocate(memory)
    
    memory_blocks.clear()
    
    # Third round: should reuse from pool
    for i in range(3):
        memory = pool.allocate(1024)
        memory_blocks.append(memory)
    
    # Final stats
    stats = pool.get_stats()
    print(f"\n📈 Memory Pool Stats:")
    print(f"   Pool size: {stats['pool_size']}")
    print(f"   Total allocations: {stats['total_allocations']}")
    print(f"   Total reuses: {stats['total_reuses']}")
    print(f"   Reuse rate: {stats['reuse_rate']:.1%}")

def test_lazy_loading():
    """Test lazy loading concept"""
    print("\n⏱️  Testing Lazy Loading")
    print("=" * 50)
    
    class LazyModule:
        def __init__(self, name):
            self.name = name
            self._loaded = False
            self._module = None
        
        def load(self):
            if not self._loaded:
                print(f"🔄 Loading {self.name}...")
                time.sleep(0.1)  # Simulate loading time
                self._module = f"loaded_{self.name}"
                self._loaded = True
                print(f"✅ {self.name} loaded")
            return self._module
        
        def is_loaded(self):
            return self._loaded
    
    # Create lazy modules
    modules = [
        LazyModule("GPU_Detection"),
        LazyModule("Model_Cache"),
        LazyModule("Video_Processor"),
        LazyModule("GUI_Components")
    ]
    
    print("📦 Created lazy modules (not loaded yet)")
    
    # Load only when needed
    for i, module in enumerate(modules):
        if i < 2:  # Only load first 2 modules
            result = module.load()
            print(f"🎯 Using {result}")
    
    # Check status
    print(f"\n📊 Module Status:")
    for module in modules:
        status = "✅ Loaded" if module.is_loaded() else "⏳ Not loaded"
        print(f"   {module.name}: {status}")

async def run_comprehensive_test():
    """Run all optimization tests"""
    print("🎯 DeepFaceLive Performance Optimization Tests")
    print("=" * 60)
    
    # Test 1: Async Processing
    await test_async_processing()
    
    # Test 2: Memory Pooling
    test_memory_pooling()
    
    # Test 3: Lazy Loading
    test_lazy_loading()
    
    print("\n" + "=" * 60)
    print("🎉 All optimization tests completed!")
    print("\n💡 Key Benefits Demonstrated:")
    print("   ✅ Async processing: Non-blocking frame processing")
    print("   ✅ Memory pooling: Reduced memory allocations")
    print("   ✅ Lazy loading: Faster startup times")
    print("   ✅ Performance monitoring: Real-time metrics")

if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(run_comprehensive_test())