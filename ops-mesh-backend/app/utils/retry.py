"""
Retry Utility

This module provides retry mechanisms for operations that may fail
due to temporary issues like network problems or database locks.
"""

import asyncio
import time
import logging
from typing import Any, Callable, Optional, Union, Type, Tuple
from functools import wraps
import random

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Exception raised when all retry attempts are exhausted."""
    pass


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        backoff_factor: float = 1.0
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.backoff_factor = backoff_factor


class RetryManager:
    """Manages retry logic for operations."""
    
    @staticmethod
    def calculate_delay(attempt: int, config: RetryConfig) -> float:
        """
        Calculate delay for the next retry attempt.
        
        Args:
            attempt: Current attempt number (0-based)
            config: Retry configuration
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = config.base_delay * (config.exponential_base ** attempt)
        
        # Apply backoff factor
        delay *= config.backoff_factor
        
        # Cap at max delay
        delay = min(delay, config.max_delay)
        
        # Add jitter to prevent thundering herd
        if config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    @staticmethod
    def retry(
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        on_retry: Optional[Callable] = None
    ):
        """
        Decorator for retrying function calls.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            exceptions: Tuple of exception types to retry on
            on_retry: Optional callback function called on each retry
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                config = RetryConfig(
                    max_attempts=max_attempts,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter
                )
                
                last_exception = None
                
                for attempt in range(config.max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == config.max_attempts - 1:
                            # Last attempt failed
                            logger.error(
                                f"Function {func.__name__} failed after {config.max_attempts} attempts. "
                                f"Last error: {e}"
                            )
                            raise RetryError(
                                f"Function {func.__name__} failed after {config.max_attempts} attempts"
                            ) from e
                        
                        # Calculate delay for next attempt
                        delay = RetryManager.calculate_delay(attempt, config)
                        
                        logger.warning(
                            f"Function {func.__name__} failed on attempt {attempt + 1}/{config.max_attempts}. "
                            f"Retrying in {delay:.2f} seconds. Error: {e}"
                        )
                        
                        # Call retry callback if provided
                        if on_retry:
                            try:
                                on_retry(attempt + 1, e, delay)
                            except Exception as callback_error:
                                logger.error(f"Retry callback failed: {callback_error}")
                        
                        # Wait before retry
                        time.sleep(delay)
                
                # This should never be reached, but just in case
                raise RetryError(f"Function {func.__name__} failed after {config.max_attempts} attempts")
            
            return wrapper
        return decorator
    
    @staticmethod
    async def async_retry(
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        on_retry: Optional[Callable] = None
    ):
        """
        Decorator for retrying async function calls.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            exceptions: Tuple of exception types to retry on
            on_retry: Optional callback function called on each retry
            
        Returns:
            Decorated async function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                config = RetryConfig(
                    max_attempts=max_attempts,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter
                )
                
                last_exception = None
                
                for attempt in range(config.max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == config.max_attempts - 1:
                            # Last attempt failed
                            logger.error(
                                f"Async function {func.__name__} failed after {config.max_attempts} attempts. "
                                f"Last error: {e}"
                            )
                            raise RetryError(
                                f"Async function {func.__name__} failed after {config.max_attempts} attempts"
                            ) from e
                        
                        # Calculate delay for next attempt
                        delay = RetryManager.calculate_delay(attempt, config)
                        
                        logger.warning(
                            f"Async function {func.__name__} failed on attempt {attempt + 1}/{config.max_attempts}. "
                            f"Retrying in {delay:.2f} seconds. Error: {e}"
                        )
                        
                        # Call retry callback if provided
                        if on_retry:
                            try:
                                if asyncio.iscoroutinefunction(on_retry):
                                    await on_retry(attempt + 1, e, delay)
                                else:
                                    on_retry(attempt + 1, e, delay)
                            except Exception as callback_error:
                                logger.error(f"Retry callback failed: {callback_error}")
                        
                        # Wait before retry
                        await asyncio.sleep(delay)
                
                # This should never be reached, but just in case
                raise RetryError(f"Async function {func.__name__} failed after {config.max_attempts} attempts")
            
            return wrapper
        return decorator


# Convenience functions for common retry scenarios
def retry_database_operation(func: Callable) -> Callable:
    """Retry decorator for database operations."""
    from sqlalchemy.exc import OperationalError, DisconnectionError, TimeoutError
    
    return RetryManager.retry(
        max_attempts=3,
        base_delay=0.5,
        max_delay=10.0,
        exponential_base=2.0,
        jitter=True,
        exceptions=(OperationalError, DisconnectionError, TimeoutError)
    )(func)


def retry_network_operation(func: Callable) -> Callable:
    """Retry decorator for network operations."""
    import requests.exceptions
    
    return RetryManager.retry(
        max_attempts=3,
        base_delay=1.0,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=True,
        exceptions=(
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException
        )
    )(func)


async def retry_async_database_operation(func: Callable) -> Callable:
    """Retry decorator for async database operations."""
    from sqlalchemy.exc import OperationalError, DisconnectionError, TimeoutError
    
    return RetryManager.async_retry(
        max_attempts=3,
        base_delay=0.5,
        max_delay=10.0,
        exponential_base=2.0,
        jitter=True,
        exceptions=(OperationalError, DisconnectionError, TimeoutError)
    )(func)


async def retry_async_network_operation(func: Callable) -> Callable:
    """Retry decorator for async network operations."""
    import aiohttp
    
    return RetryManager.async_retry(
        max_attempts=3,
        base_delay=1.0,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=True,
        exceptions=(
            aiohttp.ClientError,
            aiohttp.ClientTimeout,
            asyncio.TimeoutError
        )
    )(func)


# Example usage:
# @retry_database_operation
# def create_patient(patient_data):
#     # Database operation that might fail
#     pass

# @retry_async_database_operation
# async def async_create_patient(patient_data):
#     # Async database operation that might fail
#     pass
