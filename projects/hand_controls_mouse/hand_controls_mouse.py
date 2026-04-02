import time
import cv2
import mediapipe as mp
import math
import pyautogui

# --- Inicializa o módulo MediaPipe Hands --- #
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# --- Inicializa o módulo MediaPipe Drawing para desenhar pontos de referência --- #
mp_drawing = mp.solutions.drawing_utils

# --- controle de tempo por gesto --- #
click_start_time = None
click_times = []
click_cooldown = 0.05
scroll_mode = False
freeze_cursor = False

screen_w, screen_h = pyautogui.size()
prev_screen_x, prev_screen_y = 0,0

# --- Abre um objeto de captura de vídeo (0 para a câmera padrão) --- #
# --- Caso tenha uma segunda câmera, use 1, e assim por diante --- #
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    # --- invertendo o video --- #
    frame = cv2.flip(frame, 1)

    # --- Converte o frame para o formato RGB --- #
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # --- Processa o frame para detectar as mãos --- #
    results = hands.process(frame_rgb)

    # Verifica se as mãos foram detectadas
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Desenha os pontos de referência no frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # --- Obtem o ponto de referência dos dedos(ponto do dedo) para controle do mouse --- #
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]

        fingers = [
            1 if hand_landmarks.landmark[tip].y<hand_landmarks.landmark[tip-2].y else 0
            for tip in [8,12,16,20]
        ]

        # --- Distância entre o polegar e o indicador --- #
        dist = math.hypot(thumb_tip.x-index_tip.x, thumb_tip.y-index_tip.y)
        click_times = []
        if dist < 0.06:
            if not freeze_cursor:
                freeze_cursor = True
                click_times.append(time.time())
                # --- Verificação de duplo clique --- #
                if len(click_times) >= 2 and click_times[-1] - click_times[-2] < 0.5:
                    pyautogui.doubleClick()
                    cv2.putText(frame, "Double Click", (10,50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 255), 2)
                    click_times=[]
                else:
                    pyautogui.click()
                    cv2.putText(frame, "Single Click", (10,50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 255, 0), 2)
        else:
            if freeze_cursor:
                time.sleep(0.1)
            freeze_cursor = False

        # --- Mover o cursor com o dedo indicador --- #
        if not freeze_cursor:
            screen_x= int(index_tip.x * screen_w)
            screen_y= int(index_tip.y * screen_h)
            pyautogui.moveTo(screen_x, screen_y, duration=0.05)
            prev_screen_x, prev_screen_y = screen_x, screen_y

    # --- Exibe o quadro com os pontos de referência das mãos --- #
    # --- Para ocultar a captura do vídeo, comente a linha abaixo --- #
    #cv2.imshow("Reconhecimento de Mãos", frame)
    # --- Variável para capturar a tecla pressionada --- #
    key = cv2.waitKey(10)
    # --- Sai quando a tecla 'esc' for pressionado --- #
    if key == 27:
        break

# --- Libera o objeto de captura de vídeo e  --- #
cap.release()
# --- Fecha as janelas do OpenCV --- #
cv2.destroyAllWindows()