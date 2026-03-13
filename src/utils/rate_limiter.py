import logging
from collections import defaultdict
from time import time
from typing import Dict, List

logger = logging.getLogger("watchman")


class RateLimiter:
    """Simple token bucket rate limiter for command execution."""

    def __init__(self, max_calls: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Dict[int, List[float]] = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if user can make a call.

        Args:
            user_id: Telegram user ID

        Returns:
            True if allowed, False if rate limited
        """
        now = time()

        # Clean old calls outside time window
        self.calls[user_id] = [
            call_time
            for call_time in self.calls[user_id]
            if now - call_time < self.time_window
        ]

        # Check if under limit
        if len(self.calls[user_id]) < self.max_calls:
            self.calls[user_id].append(now)
            return True

        logger.warning(f"Rate limit exceeded for user {user_id}")
        return False

    def get_wait_time(self, user_id: int) -> int:
        """
        Get seconds until next call is allowed.

        Args:
            user_id: Telegram user ID

        Returns:
            Seconds to wait (0 if allowed now)
        """
        if not self.calls[user_id]:
            return 0

        oldest_call = self.calls[user_id][0]
        wait_time = int(self.time_window - (time() - oldest_call)) + 1
        return max(0, wait_time)

    def reset_user(self, user_id: int) -> None:
        """Reset rate limit for specific user."""
        if user_id in self.calls:
            del self.calls[user_id]

    def clear(self) -> None:
        """Clear all rate limit data."""
        self.calls.clear()
