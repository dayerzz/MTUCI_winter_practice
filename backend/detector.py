import cv2
import numpy as np
from ultralytics import YOLO

MODEL_A = "models/letter_A.pt"
MODEL_SEG = "models/yolo26n-seg.pt"
SEG_THRESHOLD = 0.1

model_A = YOLO(MODEL_A)
model_seg = YOLO(MODEL_SEG)


def run_detection(image_path: str):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    motorcycles = []

    res_A = model_A(img, conf=0.3)[0]
    if res_A.boxes is None or len(res_A.boxes) == 0:
        return {
            "violation": False,
            "message": "Буква A не найдена",
            "motorcycle_bbox": None,
            "motorcycles": []
        }

    ax1, ay1, ax2, ay2 = res_A.boxes.xyxy[0].cpu().numpy().astype(int)
    a_cx = (ax1 + ax2) // 2
    a_cy = (ay1 + ay2) // 2

    rx1 = max(a_cx - 320, 0)
    rx2 = min(a_cx + 320, w)
    ry1 = max(ay1 - 40, 0)
    ry2 = min(ay2 + 200, h)

    roi = img[ry1:ry2, rx1:rx2]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, white = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(white, 50, 150)

    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=20
    )

    if lines is None:
        return {
            "violation": False,
            "message": "Граница полосы не найдена",
            "motorcycle_bbox": None,
            "motorcycles": []
        }

    best_line = None
    best_dist = 1e9

    for l in lines:
        x1, y1, x2, y2 = l[0]
        gx1, gy1 = x1 + rx1, y1 + ry1
        gx2, gy2 = x2 + rx1, y2 + ry1

        if max(gy1, gy2) < ay1 or min(gy1, gy2) > ay2:
            continue

        if gx2 < ax1:
            dist = ax1 - max(gx1, gx2)
        elif gx1 > ax2:
            dist = min(gx1, gx2) - ax2
        else:
            continue

        if dist < best_dist:
            best_dist = dist
            best_line = (gx1, gy1, gx2, gy2)

    if best_line is None:
        return {
            "violation": False,
            "message": "Граница полосы не найдена",
            "motorcycle_bbox": None,
            "motorcycles": []
        }

    lx1, ly1, lx2, ly2 = best_line

    def side_of_line(px, py):
        return (px - lx1) * (ly2 - ly1) - (py - ly1) * (lx2 - lx1)

    a_side = side_of_line(a_cx, a_cy)

    res = model_seg(img, conf=0.3)[0]

    if res.masks is None:
        return {
            "violation": False,
            "message": "Мотоциклы не найдены",
            "motorcycle_bbox": None,
            "motorcycles": []
        }

    for i, (box, cls) in enumerate(zip(res.boxes.xyxy, res.boxes.cls)):
        if int(cls) != 3:
            continue

        mx1, my1, mx2, my2 = box.cpu().numpy().astype(int)
        poly = res.masks.xy[i]

        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [poly.astype(np.int32)], 1)

        ys, xs = np.where(mask == 1)
        if len(xs) == 0:
            continue

        same = 0
        for x, y in zip(xs, ys):
            m_side = side_of_line(x, y)
            if (
                m_side == 0 or
                (m_side > 0 and a_side > 0) or
                (m_side < 0 and a_side < 0)
            ):
                same += 1

        ratio = same / len(xs)
        is_violation = ratio >= SEG_THRESHOLD

        motorcycles.append({
            "violation": is_violation,
            "bbox": {
                "x": mx1 / w,
                "y": my1 / h,
                "w": (mx2 - mx1) / w,
                "h": (my2 - my1) / h
            }
        })

    violation = any(m["violation"] for m in motorcycles)

    return {
        "violation": violation,
        "message": (
            "Мотоцикл движется по полосе ОТ"
            if violation else
            "Нарушений не обнаружено"
        ),
        "motorcycle_bbox": motorcycles[0]["bbox"] if motorcycles else None,
        "motorcycles": motorcycles
    }