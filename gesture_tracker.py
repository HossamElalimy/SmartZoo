import cv2
import mediapipe as mp
from dollarpy import Recognizer, Template, Point
import numpy as np
import dill
import os

TEMPLATE_FILE = "saved_gestures.pkl"
MATCH_THRESHOLD = 0.75

# Load raw data from file (each gesture: name + list of (x, y, stroke_id))
def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        try:
            with open(TEMPLATE_FILE, "rb") as f:
                raw_data = dill.load(f)
            templates = [Template(item['name'], [Point(x, y, sid) for x, y, sid in item['points']])
                         for item in raw_data]
            print("📂 Loaded saved gesture templates.")
            return templates, raw_data
        except Exception as e:
            print(f"❌ Error loading templates: {e}")
    print("📂 No saved gestures found. Starting fresh.")
    return [], []

# Save raw gesture data (not Template objects)
def save_templates(raw_data):
    try:
        with open(TEMPLATE_FILE, "wb") as f:
            dill.dump(raw_data, f)
        print("💾 Templates saved.")
    except Exception as e:
        print(f"❌ Error while saving: {e}")

def normalize_path(points):
    if not points:
        return []
    points_np = np.array(points)
    min_xy = np.min(points_np, axis=0)
    max_xy = np.max(points_np, axis=0)
    scale = max(max_xy - min_xy)
    if scale == 0:
        return [Point(p[0], p[1], 1) for p in points]
    normalized = [((p[0] - min_xy[0]) / scale, (p[1] - min_xy[1]) / scale) for p in points]
    return [Point(x, y, 1) for x, y in normalized]

# Setup
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

templates, raw_templates = load_templates()
recognizer = Recognizer(templates)

cap = cv2.VideoCapture(0)

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
    raw_path = []
    last_result = ""

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.flip(image, 1)
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        h, w, _ = image.shape
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x = int(hand_landmarks.landmark[8].x * w)
                y = int(hand_landmarks.landmark[8].y * h)
                raw_path.append((x, y))
                cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Draw red gesture path
        for i in range(1, len(raw_path)):
            cv2.line(image, raw_path[i - 1], raw_path[i], (0, 0, 255), 2)

        # Display info
        cv2.putText(image, f"Points: {len(raw_path)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 0), 2)
        cv2.putText(image, f"Match: {last_result}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(image, "C=Classify | S=Save | R=Reset | Esc=Quit", (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow('Gesture Tracker (with Save/Load)', image)
        key = cv2.waitKey(10)

        if key == ord('r'):
            raw_path.clear()
            last_result = "🧹 Reset"

        elif key == ord('s'):
            if len(raw_path) >= 10:
                name = input("Enter gesture name: ")
                norm_points = normalize_path(raw_path)
                template = Template(name, norm_points)
                templates.append(template)

                # Save as raw dict
                raw_templates.append({
                    "name": name,
                    "points": [(p.x, p.y, p.stroke_id) for p in norm_points]
                })
                save_templates(raw_templates)
                recognizer = Recognizer(templates)

                print(f"✅ Gesture saved: {name}")
                last_result = f"Saved: {name}"
                raw_path.clear()
            else:
                print("❗ Too few points to save gesture.")
                last_result = "❗ Too few points"

        elif key == ord('c'):
            if len(raw_path) >= 10:
                norm_points = normalize_path(raw_path)
                print(f"[DEBUG] Trying to classify {len(norm_points)} normalized points.")
                print(f"[DEBUG] Loaded {len(templates)} saved gesture templates.")
                try:
                    results = recognizer.recognize(norm_points)
                    valid_results = [r for r in results if hasattr(r, 'name') and hasattr(r, 'score')]
                    if valid_results:
                        print("🔍 Top Matches:")
                        for idx, r in enumerate(valid_results[:3]):
                            print(f"  {idx+1}. {r.name} (score: {r.score:.2f})")
                        best = valid_results[0]
                        if best.score >= MATCH_THRESHOLD:
                            last_result = f"{best.name} ({best.score:.2f})"
                            print(f"🎯 Match: {best.name} | Score: {best.score:.2f}")
                        else:
                            last_result = f"⚠️ Low score ({best.name}: {best.score:.2f})"
                            print(f"⚠️ Low score: {best.name} | {best.score:.2f}")
                    else:
                        last_result = "❌ No valid match"
                        print("❌ No valid match.")
                except Exception as e:
                    print(f"❌ Recognition error: {e}")
                    last_result = "❌ Error"
            else:
                print("✋ Not enough points to classify.")
                last_result = "❗ Too few points"

        elif key == 27:  # ESC
            break

cap.release()
cv2.destroyAllWindows()
