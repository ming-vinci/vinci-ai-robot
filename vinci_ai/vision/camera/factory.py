from vinci_ai.config.settings import CAMERA_PROVIDER, USB_CAMERA_INDEX
from vinci_ai.vision.camera.base import CameraProvider


def create_camera_provider() -> CameraProvider:
    provider = CAMERA_PROVIDER.lower().strip()

    if provider in {"raspberry_pi", "pi"}:
        from vinci_ai.vision.camera.raspberry_pi_provider import (
            RaspberryPiCameraProvider,
        )

        return RaspberryPiCameraProvider()

    if provider in {"usb"}:
        from vinci_ai.vision.camera.usb_provider import (
            USBCameraProvider,
        )

        return USBCameraProvider(
            device=USB_CAMERA_INDEX,
        )

    raise ValueError(
        f"Unsupported camera provider: {CAMERA_PROVIDER}"
    )