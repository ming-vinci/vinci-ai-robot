from __future__ import annotations

import time
from pathlib import Path

import cv2
from numpy.typing import NDArray

from vinci_ai.vision.camera.base import CameraProvider


class USBCameraProvider(CameraProvider):
    """USB UVC camera provider using OpenCV and Video4Linux2."""

    def __init__(
        self,
        output_dir: str = "data/images",
        device: int | str = "/dev/video0",
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
        warmup_frames: int = 5,
        jpeg_quality: int = 90,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.device = self._normalize_device(device)
        self.width = width
        self.height = height
        self.fps = fps
        self.warmup_frames = warmup_frames
        self.jpeg_quality = jpeg_quality

        self._capture: cv2.VideoCapture | None = None

    @staticmethod
    def _normalize_device(device: int | str) -> int | str:
        if isinstance(device, int):
            return device

        normalized = device.strip()

        if normalized.isdigit():
            return int(normalized)

        return normalized

    def open(self) -> None:
        if self._capture is not None and self._capture.isOpened():
            return

        self._capture = cv2.VideoCapture(
            self.device,
            cv2.CAP_V4L2,
        )

        self._capture.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"MJPG"),
        )

        if not self._capture.isOpened():
            self._capture.release()
            self._capture = None

            raise RuntimeError(
                f"Could not open USB camera device: {self.device}"
            )

        self._capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width,
        )
        self._capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height,
        )
        self._capture.set(
            cv2.CAP_PROP_FPS,
            self.fps,
        )

        for _ in range(max(0, self.warmup_frames)):
            self._capture.read()

        print(f"USB camera opened: {self.device}")

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def read_frame(self) -> NDArray:
        if self._capture is None or not self._capture.isOpened():
            self.open()

        if self._capture is None:
            raise RuntimeError("USB camera is not available.")

        success, frame = self._capture.read()

        if not success or frame is None:
            raise RuntimeError(
                f"Could not read a frame from USB camera: {self.device}"
            )

        return frame

    def capture(self, filename: str | None = None) -> Path:
        try:
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"

            output_path = self.output_dir / filename

            frame = self.read_frame()

            saved = cv2.imwrite(
                str(output_path),
                frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    self.jpeg_quality,
                ],
            )

            if not saved or not output_path.exists():
                raise RuntimeError(
                    f"Could not save USB camera image: {output_path}"
                )

            return output_path

        finally:
            self.close()