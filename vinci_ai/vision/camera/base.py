from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class CameraProvider(ABC):
    @abstractmethod
    def capture(self, filename: str | None = None) -> Path:
        """
        Capture one image and return the saved image path.
        """
        raise NotImplementedError

    def open(self) -> None:
        """Open the camera for continuous frame capture."""
        raise NotImplementedError(
            f"{type(self).__name__} does not support continuous capture."
        )

    def close(self) -> None:
        """Release the camera if continuous capture is active."""
        return None

    def read_frame(self) -> Any:
        """Read one frame from an open video stream."""
        raise NotImplementedError(
            f"{type(self).__name__} does not support video frames."
        )

    @property
    def supports_video(self) -> bool:
        """Whether this provider supports continuous video frames."""
        return False

    def __enter__(self) -> CameraProvider:
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()