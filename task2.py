"""Task 2. Rate Limiter based on the Sliding Window algorithm.

Limits how often users can send chat messages: within a window of
window_size seconds no more than max_requests messages are allowed.
"""

import random
import time
from collections import deque
from typing import Dict


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        # per-user queue of timestamps of their messages
        self.user_windows: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Drop expired timestamps from the user's window.

        If the window becomes empty after cleanup, remove the user record.
        """
        window = self.user_windows.get(user_id)
        if window is None:
            return
        while window and current_time - window[0] >= self.window_size:
            window.popleft()
        if not window:
            del self.user_windows[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """Whether the user may send a message in the current window."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        window = self.user_windows.get(user_id)
        if window is None:                       # first message / window cleared
            return True
        return len(window) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """Record a message if allowed. Returns True/False."""
        current_time = time.time()
        if not self.can_send_message(user_id):
            return False
        self.user_windows.setdefault(user_id, deque()).append(current_time)
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        """Seconds to wait until the next message is allowed."""
        current_time = time.time()
        window = self.user_windows.get(user_id)
        if window is None or len(window) < self.max_requests:
            return 0.0
        # window is full — wait until the oldest message leaves it
        wait = self.window_size - (current_time - window[0])
        return max(0.0, wait)


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------
def test_rate_limiter():
    # Create a rate limiter: 10-second window, 1 message
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Simulate a stream of messages from users (sequential IDs from 1 to 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Simulate different users (IDs from 1 to 5)
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Random delay from 0.1 to 1 second
        time.sleep(random.uniform(0.1, 1.0))

    # Wait for the window to clear
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Random delay from 0.1 to 1 second
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
