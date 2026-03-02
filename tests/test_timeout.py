"""Unit tests for command timeout functionality"""

import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch
from exceptions import CommandTimeoutError
from config import Config


class TestCommandTimeoutError:
    """Test CommandTimeoutError exception"""
    
    def test_exception_creation(self):
        """Test basic exception creation"""
        error = CommandTimeoutError(
            "Timeout occurred",
            command="test_cmd",
            timeout=30
        )
        assert error.command == "test_cmd"
        assert error.timeout == 30
        assert error.elapsed is None
    
    def test_exception_with_elapsed_time(self):
        """Test exception with elapsed time"""
        error = CommandTimeoutError(
            "Timeout occurred",
            command="test_cmd",
            timeout=30,
            elapsed=35.5
        )
        assert error.elapsed == 35.5
        assert "35.50s" in str(error)
    
    def test_exception_string_representation(self):
        """Test string representation of exception"""
        error = CommandTimeoutError(
            "Timeout occurred",
            command="backup",
            timeout=300,
            elapsed=310.25
        )
        error_str = str(error)
        assert "backup" in error_str
        assert "300s" in error_str
        assert "310.25s" in error_str


class TestConfig:
    """Test Config timeout functionality"""
    
    def test_default_timeout(self):
        """Test default timeout retrieval"""
        timeout = Config.get_command_timeout("unknown_command")
        assert timeout == Config.DEFAULT_COMMAND_TIMEOUT
    
    def test_command_specific_timeout(self):
        """Test command-specific timeout"""
        Config.COMMAND_TIMEOUTS['test_cmd'] = 60
        timeout = Config.get_command_timeout("test_cmd")
        assert timeout == 60
    
    def test_set_command_timeout(self):
        """Test setting timeout at runtime"""
        Config.set_command_timeout("dynamic_cmd", 120)
        timeout = Config.get_command_timeout("dynamic_cmd")
        assert timeout == 120
    
    @patch.dict('os.environ', {'TIMEOUT_ENVTEST': '99'})
    def test_environment_variable_timeout(self):
        """Test timeout from environment variable"""
        timeout = Config.get_command_timeout("envtest")
        assert timeout == 99
    
    @patch.dict('os.environ', {'TIMEOUT_INVALID': 'not_a_number'})
    def test_invalid_environment_variable(self):
        """Test handling of invalid environment variable"""
        # Should fall back to default
        timeout = Config.get_command_timeout("invalid")
        assert timeout == Config.DEFAULT_COMMAND_TIMEOUT


@pytest.mark.asyncio
class TestTimeoutIntegration:
    """Integration tests for timeout functionality"""
    
    async def test_fast_command_completes(self):
        """Test that fast commands complete normally"""
        async def fast_command():
            await asyncio.sleep(0.1)
            return "completed"
        
        result = await asyncio.wait_for(fast_command(), timeout=5)
        assert result == "completed"
    
    async def test_slow_command_times_out(self):
        """Test that slow commands raise TimeoutError"""
        async def slow_command():
            await asyncio.sleep(10)
            return "completed"
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_command(), timeout=1)
    
    async def test_exact_timeout_edge_case(self):
        """Test command that completes exactly at timeout"""
        async def exact_command():
            await asyncio.sleep(1.0)
            return "completed"
        
        # Should complete (1.1s timeout for 1.0s command)
        result = await asyncio.wait_for(exact_command(), timeout=1.1)
        assert result == "completed"
    
    async def test_zero_timeout(self):
        """Test zero timeout behavior"""
        async def instant_command():
            return "completed"
        
        # Even instant commands might timeout with 0 timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(instant_command(), timeout=0)


class TestTimeoutMetrics:
    """Test timeout-related metrics"""
    
    def test_execution_time_tracking(self):
        """Test that execution time is properly tracked"""
        start_time = time.time()
        time.sleep(0.1)
        elapsed = time.time() - start_time
        
        assert elapsed >= 0.1
        assert elapsed < 0.2  # Should not be significantly longer
    
    def test_timeout_calculation(self):
        """Test timeout vs elapsed time calculation"""
        timeout = 30
        elapsed = 35
        
        exceeded = elapsed > timeout
        assert exceeded is True
        
        margin = elapsed - timeout
        assert margin == 5
