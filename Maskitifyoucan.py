import cv2
import mediapipe as mp
import time
import numpy as np
import os
import sys
import random
from PIL import Image, ImageDraw, ImageFont
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#NUHA SABER, GGJ 2026

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def draw_text(img, text, pos, size, color=(255, 255, 255)):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try:
        font = ImageFont.truetype("seguiemj.ttf", size)
    except:
        font = ImageFont.load_default()
    draw.text(pos, text, font=font, fill=color, embedded_color=True)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def overlay_transparent(background, overlay, x, y, size=None):
    if overlay is None: return background
    if size:
        overlay = cv2.resize(overlay, size)
    h, w, _ = overlay.shape
    if y + h > background.shape[0] or x + w > background.shape[1] or y < 0 or x < 0:
        return background
    if overlay.shape[2] < 4:
        overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2BGRA)
    alpha = overlay[:, :, 3] / 255.0
    for c in range(0, 3):
        background[y:y+h, x:x+w, c] = (alpha * overlay[:, :, c] +
                                      (1.0 - alpha) * background[y:y+h, x:x+w, c])
    return background

model_path = 'face_landmarker.task'
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    output_face_blendshapes=True,
    num_faces=1)
landmarker = vision.FaceLandmarker.create_from_options(options)

masks_images = {
    "Sad Mask": cv2.imread('sad.png', cv2.IMREAD_UNCHANGED),
    "Smile Mask": cv2.imread('smile.png', cv2.IMREAD_UNCHANGED),
    "Surprised Mask": cv2.imread('suprized.png', cv2.IMREAD_UNCHANGED),
   #python Maskitifyoucan.py "Angry Mask": cv2.imread('mad.png', cv2.IMREAD_UNCHANGED),
    "Smile Closed Eyes Mask": cv2.imread('smilecloseeyes.png', cv2.IMREAD_UNCHANGED),
    "One Eye Close Mask": cv2.imread('oneeyesclose.png', cv2.IMREAD_UNCHANGED)
}

calibration_frames = 0
max_calibration_frames = 40 
baseline_frown = 0.0
is_calibrated = False
game_state = "MENU"
score = 0
target_expr = ""
round_start_time = 0
countdown_start_time = 0 
round_duration = 5 
expressions_list = ["Smile Mask", "Sad Mask", "Surprised Mask", "Smile Closed Eyes Mask", "One Eye Close Mask"]

cap = None
btn_x, btn_y, btn_w, btn_h = 0, 0, 0, 0
mouse_x, mouse_y = 0, 0 
menu_bg = cv2.imread('main.png')
btn_img = cv2.imread('button.png', cv2.IMREAD_UNCHANGED)

def get_new_challenge():
    return random.choice(expressions_list)

def handle_mouse_clicks(event, x, y, flags, param):
    global game_state, score, countdown_start_time, cap, start_time, mouse_x, mouse_y
    mouse_x, mouse_y = x, y
    if event == cv2.EVENT_LBUTTONDOWN:
        if game_state == "MENU":
            if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                if cap is None:
                    cap = cv2.VideoCapture(0)
                start_time = time.time()
                score = 0
                game_state = "COUNTDOWN"
                countdown_start_time = time.time()

window_name = "MASK IT IF YOU CAN "
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_EXPANDED)
cv2.setWindowProperty(window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
cv2.resizeWindow(window_name, 960, 540)
cv2.setMouseCallback(window_name, handle_mouse_clicks)

start_time = time.time()

while True:
    if cap is not None:
        ret, frame = cap.read()
        if not ret: 
            cap.release()
            cap = None
            continue
        frame = cv2.flip(frame, 1)
    else:
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    h, w, _ = frame.shape
    scale = w / 1280.0
    overlay = frame.copy()

    if cap is not None:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        timestamp = int((time.time() - start_time) * 1000)
        result = landmarker.detect_for_video(mp_image, timestamp)
        
        current_expr = "Normal 😐"
        if result.face_landmarks and result.face_blendshapes:
            scores = {b.category_name: b.score for b in result.face_blendshapes[0]}
            lm = result.face_landmarks[0]
            current_frown = ((lm[61].y - lm[13].y) + (lm[291].y - lm[13].y)) / 2
            
            if not is_calibrated:
                baseline_frown += current_frown
                calibration_frames += 1
                current_expr = "Calibrating... ⏳"
                if calibration_frames >= max_calibration_frames:
                    baseline_frown /= max_calibration_frames; is_calibrated = True
            else:
                frown_diff = current_frown - baseline_frown
                dist_l = abs(lm[159].y - lm[145].y)
                dist_r = abs(lm[386].y - lm[374].y)
                smile_avg = (scores['mouthSmileLeft'] + scores['mouthSmileRight']) / 2
                eye_l_closed = scores['eyeBlinkLeft'] > 0.55 or dist_l < 0.014
                eye_r_closed = scores['eyeBlinkRight'] > 0.55 or dist_r < 0.014
                both_eyes_closed = eye_l_closed and eye_r_closed
                right_eye_only = eye_r_closed and not eye_l_closed

                if both_eyes_closed and smile_avg > 0.45: current_expr = "Smile Closed Eyes Mask"
                elif right_eye_only and smile_avg < 0.35: current_expr = "One Eye Close Mask"
                elif scores['jawOpen'] > 0.6 and smile_avg < 0.3: current_expr = "Surprised Mask"
               #3 elif scores['browDownLeft'] > 0.4 or scores['browDownRight'] > 0.4 and smile_avg < 0.3: current_expr = "Angry Mask"
                elif smile_avg > 0.55 and scores['jawOpen'] < 0.3: current_expr = "Smile Mask"
                elif frown_diff > 0.01 and smile_avg < 0.25: current_expr = "Sad Mask"
                else: current_expr = "Normal 😐"

    if game_state == "MENU":
        if menu_bg is not None:
            bg_display = cv2.resize(menu_bg, (w, h))
            frame = cv2.addWeighted(bg_display, 1.0, frame, 0.0, 0)
        base_w, base_h = int(w * 0.4), int(h * 0.3)
        base_x, base_y = int(w/2 - base_w/2), int(h * 0.62)
        is_hover = (base_x <= mouse_x <= base_x + base_w and base_y <= mouse_y <= base_y + base_h)
        btn_w, btn_h = (int(base_w * 1.1), int(base_h * 1.1)) if is_hover else (base_w, base_h)
        btn_x, btn_y = (int(w/2 - btn_w/2), int(base_y - (btn_h - base_h)/2)) if is_hover else (base_x, base_y)
        if btn_img is not None: frame = overlay_transparent(frame, btn_img, btn_x, btn_y, (btn_w, btn_h))

    elif game_state == "COUNTDOWN":
        count = 3 - int(time.time() - countdown_start_time)
        if count > 0: frame = draw_text(frame, str(count), (int(w*0.45), int(h*0.4)), int(150*scale), (0, 255, 255))
        else: game_state = "PLAYING"; round_start_time = time.time(); target_expr = get_new_challenge()

    elif game_state == "PLAYING":
        elapsed = time.time() - round_start_time
        remaining = max(0, round_duration - elapsed)
        hud_h = int(h * 0.15)
        cv2.rectangle(overlay, (0, 0), (w, hud_h), (30, 30, 30), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        if target_expr in masks_images:
            mask_to_show = masks_images[target_expr]
            if mask_to_show is not None:
                desired_h = int(h * 0.25); orig_h, orig_w = mask_to_show.shape[:2]
                aspect_ratio = orig_w / orig_h
                new_w = int(desired_h * aspect_ratio); new_h = desired_h
                frame = overlay_transparent(frame, mask_to_show, int(w*0.02), int(h*0.18), (new_w, new_h))
                frame = draw_text(frame, "Target: IMITATE THIS!", (int(w*0.05), int(hud_h*0.2)), int(35*scale), (0, 255, 255))
        frame = draw_text(frame, f"Score: {score}", (int(w*0.8), int(hud_h*0.2)), int(30*scale))
        bar_x1, bar_y = int(w*0.05), int(hud_h*0.8); bar_w_curr = int((remaining / round_duration) * int(w*0.9))
        cv2.rectangle(frame, (bar_x1, bar_y), (bar_x1 + bar_w_curr, bar_y + 10), (0, 255, 0), -1)
        if current_expr == target_expr:
            score += 10; target_expr = get_new_challenge(); round_start_time = time.time()
        if remaining <= 0: game_state = "GAMEOVER"

    elif game_state == "GAMEOVER":
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 50), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        frame = draw_text(frame, "TIME'S UP! 💥", (int(w*0.35), int(h*0.4)), int(60*scale))
        frame = draw_text(frame, f"Total Score: {score}", (int(w*0.4), int(h*0.55)), int(40*scale))
        frame = draw_text(frame, "Press R to Reset", (int(w*0.38), int(h*0.7)), int(25*scale))

    if game_state != "MENU":
        display_name = current_expr
        if current_expr == "Sad Mask": display_name = "Sad 😔"
        elif current_expr == "Smile Mask": display_name = "Smiling 😁"
        elif current_expr == "Surprised Mask": display_name = "Surprised 😲"
        elif current_expr == "Angry Mask": display_name = "Angry 😡"
        elif current_expr == "Smile Closed Eyes Mask": display_name = "Smiling & Blinking 😉"
        elif current_expr == "One Eye Close Mask": display_name = "Normal & Right Eye Closed 😉"
        frame = draw_text(frame, f"You: {display_name}", (int(w*0.05), int(h*0.9)), int(35*scale))

    cv2.imshow(window_name, frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  
        break
    elif key == ord('r') or key == ord('R'):
        game_state = "MENU"
        score = 0
        is_calibrated = False
        calibration_frames = 0
        baseline_frown = 0.0
        if cap is not None:
            cap.release()
            cap = None

if cap is not None: cap.release()
cv2.destroyAllWindows()