from vinci_ai.vision.camera.factory import create_camera_provider


def main() -> None:
    camera = create_camera_provider()

    image_path = camera.capture()

    print(f"Image captured successfully: {image_path}")


if __name__ == "__main__":
    main()