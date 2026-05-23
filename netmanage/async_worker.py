"""
Async worker for running network operations in a background thread.
Prevents GUI freezing during blocking network calls.
"""
import threading
import logging
from gi.repository import GLib

logger = logging.getLogger(__name__)


class AsyncWorker:
    """Runs blocking operations in a background thread and calls back on the GTK main thread."""

    @staticmethod
    def run_async(target_func, callback, on_error=None, *args, **kwargs):
        """
        Run a blocking function in a background thread.

        Args:
            target_func: The blocking function to run
            callback: Called on GTK main thread with (success, result) on completion
            on_error: Called on GTK main thread with exception info on failure
            *args, **kwargs: Passed to target_func
        """
        def worker():
            try:
                result = target_func(*args, **kwargs)
                # Schedule callback on GTK main thread
                GLib.idle_add(callback, True, result)
            except Exception as e:
                logger.error(f"Async worker error: {e}")
                if on_error:
                    GLib.idle_add(on_error, e)
                else:
                    GLib.idle_add(callback, False, str(e))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread