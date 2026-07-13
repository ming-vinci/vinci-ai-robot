from __future__ import annotations

import subprocess
import time
from pathlib import Path


class RaspberryPiCamera:
    """Capture still images using Raspberry Pi Camera Module 3."""

    def __init__(
        self,
        output_dir: str = "data/images",
        width: int = 1280,
        height: int = 720,
        timeout_ms: int = 800,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.width = width
        self.height = height
        self.timeout_ms = timeout_ms

    def capture(self, filename: str | None = None) -> str:
        """
        Capture one JPEG image and return its path.

        Uses rpicam-still, which has already been tested successfully
        with the Raspberry Pi Camera Module 3.
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"

        output_path = self.output_dir / filename

        command = [
            "rpicam-still",
            "--nopreview",
            "--timeout",
            str(self.timeout_ms),
            "--width",
            str(self.width),
            "--height",
            str(self.height),
            "--quality",
            "90",
            "--output",
            str(output_path),
        ]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "rpicam-still was not found. "
                "Install Raspberry Pi camera applications first."
            ) from exc
        except subprocess.CalledProcessError as exc:
            error_message = exc.stderr.strip() or exc.stdout.strip()
            raise RuntimeError(
                f"Camera capture failed: {error_message}"
            ) from exc

        if not output_path.exists():
            raise RuntimeError(
                f"Camera command completed, but no image was created: "
                f"{output_path}"
            )

        return str(output_path)