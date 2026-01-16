import cv2 as cv
import mediapipe as mp
import math, time
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions

from visualization import draw_manual, print_RSP_result

## 필요한 함수 작성

# ===============================
# 가위/바위/보 판별 로직
# ===============================
WRIST = 0
FINGERS = {
    "index":  (6, 8),
    "middle": (10, 12),
    "ring":   (14, 16),
    "pinky":  (18, 20),
}

def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def classify_rps(landmarks):
    wrist = landmarks[WRIST]
    states = {}

    # 손가락 펴짐 여부 판단
    for name, (pip, tip) in FINGERS.items():
        states[name] = _dist(landmarks[tip], wrist) > _dist(landmarks[pip], wrist) * 1.05

    extended = sum(states.values())

    if extended <= 1:
        return 0      # Rock
    if extended == 4:
        return 1      # Paper
    if extended == 2 and states["index"] and states["middle"]:
        return 2      # Scissors
    return None


# ===============================
# MediaPipe 콜백 (실시간 결과 저장)
# ===============================
latest_result = None

def result_callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result


# ===============================
# 메인 실행부
# ===============================
if __name__ == "__main__":
    # 실행 로직
    
    MODEL_PATH = "hand_landmarker.task"

    # HandLandmarker 설정
    options = vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        result_callback=result_callback,
    )

    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv.flip(frame, 1)
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            # MediaPipe 입력
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            landmarker.detect_async(mp_image, int(time.time() * 1000))

            rps = None
            if latest_result and latest_result.hand_landmarks:
                landmarks = latest_result.hand_landmarks[0]
                rps = classify_rps(landmarks)
                frame = draw_manual(frame, latest_result)

            # 결과 출력
            frame = print_RSP_result(frame, rps)
            cv.imshow("RPS Game", frame)

            if cv.waitKey(1) == ord('q'):
                break

    cap.release()
    cv.destroyAllWindows()