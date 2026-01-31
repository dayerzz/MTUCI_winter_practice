from ultralytics import YOLO
import torch

def main():
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))
    else:
        print("WARNING: GPU not detected, training will be on CPU")

    DATA_YAML = "data.yaml"
    MODEL_NAME = "yolo26n.pt"

    model = YOLO(MODEL_NAME)

    model.train(
        data=DATA_YAML,
        epochs=100,
        imgsz=640,
        batch=16,
        device=0,
        workers=8,
        project="runs/detect",
        name="letter_A_train",
        pretrained=True
    )

    print("\nОбучение завершено.")
    print("Лучшие веса:")
    print("detect/letter_A_train/weights/best.pt")

if __name__ == "__main__":
    main()
