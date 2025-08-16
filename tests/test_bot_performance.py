# test_bot_performance.py
# Performance and stress testing for the Discord bot
# Tests load handling, memory usage, response times, and concurrent execution

import unittest
import asyncio
import time
import psutil
import os
from unittest.mock import AsyncMock, MagicMock, patch
from bot import bot, run_bot
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestBotPerformance(unittest.IsolatedAsyncioTestCase):
    """Performance testing suite for Discord bot"""

    async def asyncSetUp(self):
        """Set up performance test fixtures"""
        self.ctx = MagicMock()
        self.ctx.send = AsyncMock()
        self.process = psutil.Process(os.getpid())

    def get_memory_usage(self):
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024

    async def test_command_response_time(self):
        """Test that commands respond within acceptable time limits"""
        commands_to_test = ["help", "resume", "events", "resources"]
        max_response_time = float(os.getenv('TEST_MAX_RESPONSE_TIME', '0.5'))  # 500ms default, configurable
        
        for cmd_name in commands_to_test:
            ctx = MagicMock()
            ctx.send = AsyncMock()
            
            start_time = time.perf_counter()
            await bot.get_command(cmd_name).callback(ctx)
            end_time = time.perf_counter()
            
            response_time = end_time - start_time
            self.assertLess(response_time, max_response_time,
                          f"Command {cmd_name} took {response_time:.3f}s, exceeds {max_response_time}s limit")

    async def test_concurrent_command_execution(self):
        """Test bot performance under concurrent command execution"""
        num_concurrent = 50
        commands = ["help", "resume", "events", "resources"]
        
        tasks = []
        start_time = time.perf_counter()
        
        for i in range(num_concurrent):
            ctx = MagicMock()
            ctx.send = AsyncMock()
            cmd = commands[i % len(commands)]
            task = bot.get_command(cmd).callback(ctx)
            tasks.append(task)
        
        # Execute all tasks concurrently
        await asyncio.gather(*tasks)
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        avg_time_per_command = total_time / num_concurrent
        
        # Should complete all commands in reasonable time
        self.assertLess(total_time, 5.0, f"Concurrent execution took {total_time:.3f}s")
        self.assertLess(avg_time_per_command, 0.1, 
                       f"Average time per command: {avg_time_per_command:.3f}s")

    async def test_memory_usage_under_load(self):
        """Test memory usage doesn't grow excessively under load"""
        initial_memory = self.get_memory_usage()
        
        # Execute many commands
        for _ in range(100):
            ctx = MagicMock()
            ctx.send = AsyncMock()
            await bot.get_command("help").callback(ctx)
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 10MB)
        self.assertLess(memory_increase, 10.0,
                       f"Memory increased by {memory_increase:.2f}MB")

    async def test_rapid_sequential_commands(self):
        """Test bot handling rapid sequential command execution"""
        num_commands = 1000
        start_time = time.perf_counter()
        
        for i in range(num_commands):
            ctx = MagicMock()
            ctx.send = AsyncMock()
            await bot.get_command("help").callback(ctx)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        commands_per_second = num_commands / total_time
        
        # Should handle at least 100 commands per second
        self.assertGreater(commands_per_second, 100,
                          f"Only {commands_per_second:.1f} commands/sec")

    async def test_command_execution_consistency(self):
        """Test that command execution time is consistent"""
        num_iterations = 50
        response_times = []
        
        for _ in range(num_iterations):
            ctx = MagicMock()
            ctx.send = AsyncMock()
            
            start_time = time.perf_counter()
            await bot.get_command("help").callback(ctx)
            end_time = time.perf_counter()
            
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # Variance should be low (max shouldn't be more than 10x min)
        self.assertLess(max_time / min_time, 10,
                       f"High variance: min={min_time:.4f}s, max={max_time:.4f}s")
        
        # Average should be reasonable
        self.assertLess(avg_time, 0.05, f"Average response time too high: {avg_time:.4f}s")

    def test_bot_startup_time(self):
        """Test bot startup performance"""
        with patch("bot.bot.run") as mock_run, \
             patch("os.getenv", return_value="test_token"), \
             patch("bot.load_dotenv", return_value=True):
            
            start_time = time.perf_counter()
            run_bot()
            end_time = time.perf_counter()
            
            startup_time = end_time - start_time
            # Startup should be very fast (mostly just function calls)
            self.assertLess(startup_time, 0.1, f"Startup took {startup_time:.3f}s")

    async def test_command_with_varying_load(self):
        """Test command performance under varying load conditions"""
        load_levels = [1, 5, 10, 25, 50]
        results = {}
        
        for load in load_levels:
            tasks = []
            start_time = time.perf_counter()
            
            for _ in range(load):
                ctx = MagicMock()
                ctx.send = AsyncMock()
                task = bot.get_command("help").callback(ctx)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            end_time = time.perf_counter()
            
            total_time = end_time - start_time
            avg_time = total_time / load
            results[load] = avg_time
        
        # Performance should scale reasonably (not exponentially worse)
        for i in range(1, len(load_levels)):
            current_load = load_levels[i]
            previous_load = load_levels[i-1]
            
            # Performance degradation should be reasonable
            performance_ratio = results[current_load] / results[previous_load]
            self.assertLess(performance_ratio, 3.0,
                          f"Performance degraded too much at load {current_load}")

    async def test_error_handling_performance(self):
        """Test that error handling doesn't significantly impact performance"""
        # Test normal execution
        ctx_normal = MagicMock()
        ctx_normal.send = AsyncMock()
        
        start_time = time.perf_counter()
        await bot.get_command("help").callback(ctx_normal)
        normal_time = time.perf_counter() - start_time
        
        # Test with exception
        ctx_error = MagicMock()
        ctx_error.send = AsyncMock(side_effect=Exception("Test error"))
        
        start_time = time.perf_counter()
        try:
            await bot.get_command("help").callback(ctx_error)
        except Exception:
            pass
        error_time = time.perf_counter() - start_time
        
        # Error handling shouldn't be significantly slower
        self.assertLess(error_time / normal_time, 5.0,
                       f"Error handling too slow: {error_time/normal_time:.2f}x slower")


class TestBotStressTest(unittest.IsolatedAsyncioTestCase):
    """Stress testing for extreme load scenarios"""

    async def test_extreme_concurrent_load(self):
        """Test bot under extreme concurrent load"""
        num_concurrent = 200
        timeout_seconds = 10
        
        tasks = []
        for i in range(num_concurrent):
            ctx = MagicMock()
            ctx.send = AsyncMock()
            task = bot.get_command("help").callback(ctx)
            tasks.append(task)
        
        try:
            # Use timeout to prevent hanging
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            self.fail(f"Stress test timed out after {timeout_seconds}s")
        
        # If we get here, the test passed

    async def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation"""
        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        # Run many operations
        for cycle in range(10):
            tasks = []
            for _ in range(50):
                ctx = MagicMock()
                ctx.send = AsyncMock()
                task = bot.get_command("help").callback(ctx)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            # Check memory periodically
            if cycle % 5 == 0:
                current_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                # Memory shouldn't grow excessively
                self.assertLess(memory_increase, 50.0,
                               f"Potential memory leak: {memory_increase:.2f}MB increase")

    async def test_command_isolation(self):
        """Test that commands don't interfere with each other under load"""
        num_iterations = 100
        commands = ["help", "resume", "events", "resources"]
        
        # Execute all commands concurrently many times
        for _ in range(num_iterations):
            tasks = []
            contexts = {}
            
            for cmd in commands:
                ctx = MagicMock()
                ctx.send = AsyncMock()
                contexts[cmd] = ctx
                task = bot.get_command(cmd).callback(ctx)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            # Verify each command was called exactly once
            for cmd in commands:
                contexts[cmd].send.assert_called_once()


class TestBotResourceUsage(unittest.TestCase):
    """Test resource usage and efficiency"""

    def test_import_efficiency(self):
        """Test that bot imports don't consume excessive resources"""
        import sys
        initial_modules = len(sys.modules)
        
        # Import should be efficient
        from bot import bot
        
        final_modules = len(sys.modules)
        new_modules = final_modules - initial_modules
        
        # Shouldn't import too many additional modules
        self.assertLess(new_modules, 20, f"Imported {new_modules} additional modules")

    def test_bot_object_size(self):
        """Test that bot object doesn't consume excessive memory"""
        import sys
        
        bot_size = sys.getsizeof(bot)
        # Bot object should be reasonably sized (less than 1MB)
        self.assertLess(bot_size, 1024 * 1024, f"Bot object size: {bot_size} bytes")


if __name__ == "__main__":
    # Run performance tests with detailed output
    unittest.main(verbosity=2) 