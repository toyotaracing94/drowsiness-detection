from threading import Lock


class FrameBuffer:
    def __init__(self):
        self.raw_frame = None
        self.processed_frame = None
        self.lock = Lock()

    def update_raw(self, frame):
        """Update the raw frame."""
        with self.lock:
            self.raw_frame = frame

    def get_raw(self):
        """Get the raw frame."""
        with self.lock:
            return self.raw_frame

    def update_processed(self, frame):
        """Update the processed frame."""
        with self.lock:
            self.processed_frame = frame

    def get_processed(self):
        """Get the processed frame."""
        with self.lock:
            return self.processed_frame