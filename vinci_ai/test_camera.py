from vinci_ai.vision.camera import RaspberryPiCamera


def main() -> None:
    camera = RaspberryPiCamera()

    print("Capturing image...")
    image_path = camera.capture("camera_test.jpg")

    print(f"Image saved successfully: {image_path}")


if __name__ == "__main__":
    main()