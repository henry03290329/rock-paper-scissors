import cv2
import mediapipe as mp
import time
import os

# ====================================================
# 摄像头选择
# ====================================================
print("选择摄像头: 输入 'pc' 使用电脑摄像头, 输入 'phone' 使用手机摄像头 (Iriun)")
choice = input("请输入 pc 或 phone: ").strip().lower()

cap = None
if choice == 'pc':
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开电脑摄像头，尝试手机摄像头...")
        choice = 'phone'

if choice == 'phone':
    for idx in [1, 2]:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f"已连接手机摄像头 (索引 {idx})")
                break
            else:
                cap.release()
    else:
        print("手机摄像头连接失败！请检查 Iriun 是否正在运行。")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无可用摄像头，退出。")
            exit()

if cap is None or not cap.isOpened():
    print("无法打开任何摄像头，程序退出。")
    exit()

# ====================================================
# 加载表情包图片（如果存在）
# ====================================================
emoji = {}
emoji_files = {
    "Rock": "rock.png",
    "Scissors": "scissors.png",
    "Paper": "paper.png"
}
emoji_loaded = True
for gesture, filename in emoji_files.items():
    if os.path.exists(filename):
        img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        if img is not None:
            emoji[gesture] = img
        else:
            emoji_loaded = False
            break
    else:
        emoji_loaded = False
        break

if not emoji_loaded:
    print("⚠️ 未找到表情包图片，将使用几何图形代替。")

PROCESS_WIDTH = 640
PROCESS_HEIGHT = 480

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

STABLE_FRAMES = 2
last_gesture = None
gesture_count = 0
result_shown = False
result_start_time = 0
computer_gesture = None
middle_finger_shown = False
middle_finger_start_time = 0

def get_hand_gesture(hand_landmarks):
    fingers = []
    if hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y:
        fingers.append(1)
    else:
        fingers.append(0)
    tips = [8, 12, 16, 20]
    pip_joints = [6, 10, 14, 18]
    for tip, pip in zip(tips, pip_joints):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)
    total_fingers = sum(fingers[1:])
    if fingers[2] == 1 and total_fingers == 1:
        return "MiddleFinger"
    if fingers[1] == 1 and fingers[2] == 1 and total_fingers == 2:
        return "Scissors"
    elif total_fingers == 4:
        return "Paper"
    elif total_fingers == 0:
        return "Rock"
    else:
        return None

def get_winning_gesture(user_gesture):
    if user_gesture == "Rock":
        return "Paper"
    elif user_gesture == "Scissors":
        return "Rock"
    elif user_gesture == "Paper":
        return "Scissors"
    return None

def draw_computer_gesture(frame, gesture):
    h, w = frame.shape[:2]
    base_x = w - 180
    base_y = 50
    overlay = frame.copy()
    cv2.rectangle(overlay, (base_x - 20, base_y - 30), (w - 20, base_y + 150), (50, 50, 50), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    if emoji_loaded and gesture in emoji:
        img = emoji[gesture]
        img_resized = cv2.resize(img, (100, 100))
        x_offset = base_x + 20
        y_offset = base_y - 10
        if img_resized.shape[2] == 4:
            bgr = img_resized[:, :, :3]
            alpha = img_resized[:, :, 3] / 255.0
            roi = frame[y_offset:y_offset+100, x_offset:x_offset+100]
            if roi.shape[0] < 100 or roi.shape[1] < 100:
                frame[y_offset:y_offset+100, x_offset:x_offset+100] = bgr[:roi.shape[0], :roi.shape[1]]
            else:
                for c in range(3):
                    roi[:, :, c] = (1. - alpha) * roi[:, :, c] + alpha * bgr[:, :, c]
                frame[y_offset:y_offset+100, x_offset:x_offset+100] = roi
        else:
            frame[y_offset:y_offset+100, x_offset:x_offset+100] = img_resized
    else:
        if gesture == "Rock":
            cv2.circle(frame, (base_x + 60, base_y + 60), 40, (0, 0, 255), -1)
            cv2.putText(frame, "ROCK", (base_x + 10, base_y + 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        elif gesture == "Scissors":
            cv2.line(frame, (base_x + 40, base_y + 80), (base_x + 40, base_y + 20), (255, 255, 0), 8)
            cv2.line(frame, (base_x + 70, base_y + 80), (base_x + 70, base_y + 20), (255, 255, 0), 8)
            cv2.circle(frame, (base_x + 40, base_y + 20), 6, (255, 255, 0), -1)
            cv2.circle(frame, (base_x + 70, base_y + 20), 6, (255, 255, 0), -1)
            cv2.putText(frame, "SCISSORS", (base_x + 5, base_y + 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        elif gesture == "Paper":
            for i in range(5):
                x = base_x + 10 + i * 22
                cv2.line(frame, (x, base_y + 80), (x, base_y + 20), (0, 255, 0), 6)
                cv2.circle(frame, (x, base_y + 20), 5, (0, 255, 0), -1)
            cv2.putText(frame, "PAPER", (base_x + 15, base_y + 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

def draw_middle_finger_warning(frame):
    h, w = frame.shape[:2]
    text = "Are you fucking stupid !!!"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2          # 缩小字体
    thickness = 2             # 减小粗细
    color = (0, 0, 255)
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    overlay = frame.copy()
    box_x1 = int(w/2 - text_width/2) - 30
    box_y1 = int(h/2 - text_height/2) - 30
    box_x2 = int(w/2 + text_width/2) + 30
    box_y2 = int(h/2 + text_height/2) + 30
    cv2.rectangle(overlay, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    text_x = int(w/2 - text_width/2)
    text_y = int(h/2 + text_height/2)
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

print("极速模式启动！按 'q' 键退出。\n竖中指试试看……")

while True:
    ret, frame = cap.read()
    if not ret:
        print("摄像头连接中断。")
        break
    frame = cv2.resize(frame, (PROCESS_WIDTH, PROCESS_HEIGHT))
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    user_gesture = None
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            gesture = get_hand_gesture(hand_landmarks)
            if gesture:
                user_gesture = gesture
                break
    if user_gesture == "MiddleFinger":
        middle_finger_shown = True
        middle_finger_start_time = time.time()
        result_shown = False
        computer_gesture = None
        last_gesture = None
        gesture_count = 0
    elif user_gesture and user_gesture in ["Rock", "Scissors", "Paper"]:
        if user_gesture == last_gesture:
            gesture_count += 1
        else:
            last_gesture = user_gesture
            gesture_count = 1
        if gesture_count >= STABLE_FRAMES:
            comp_gesture = get_winning_gesture(user_gesture)
            computer_gesture = comp_gesture
            result_shown = True
            result_start_time = time.time()
            last_gesture = None
            gesture_count = 0
    else:
        last_gesture = None
        gesture_count = 0
    if result_shown:
        if time.time() - result_start_time < 1.0:
            if computer_gesture:
                draw_computer_gesture(frame, computer_gesture)
        else:
            result_shown = False
            computer_gesture = None
    if middle_finger_shown:
        if time.time() - middle_finger_start_time < 2.0:
            draw_middle_finger_warning(frame)
        else:
            middle_finger_shown = False
    cv2.imshow("Rock Paper Scissors (I always win)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()