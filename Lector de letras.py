import cv2
import mediapipe as mp
import time

def distancia_euclidiana(p1, p2):
    return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

def draw_bounding_box(image, hand_landmarks):
    image_height, image_width, _ = image.shape
    x_min, y_min = image_width, image_height
    x_max, y_max = 0, 0
    
    for landmark in hand_landmarks.landmark:
        x, y = int(landmark.x * image_width), int(landmark.y * image_height)
        x_min = min(x, x_min)
        y_min = min(y, y_min)
        x_max = max(x, x_max)
        y_max = max(y, y_max)
    
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

estado_actual = "Desbloqueado"
ultima_letra = None
inicio_letra_detectada = None
duracion_requerida = 5
letra_confirmada = False

boton_pos = (1200, 650)
boton_radio = 30
led_pos = (1300, 650)
led_radio = 15

def cambiar_estado():
    global estado_actual
    estado_actual = "Bloqueado" if estado_actual == "Desbloqueado" else "Desbloqueado"

def click_boton(event, x, y, flags, param):
    global letra_confirmada
    if event == cv2.EVENT_LBUTTONDOWN:
        if ((x - boton_pos[0]) ** 2 + (y - boton_pos[1]) ** 2) ** 0.5 <= boton_radio:
            if letra_confirmada:
                cambiar_estado()
                letra_confirmada = False

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

cv2.namedWindow('MediaPipe Hands')
cv2.setMouseCallback('MediaPipe Hands', click_boton)

with mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1) as hands:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        letra_detectada = None 

        image_height, image_width, _ = image.shape
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
                draw_bounding_box(image, hand_landmarks)

                index_finger_tip = (int(hand_landmarks.landmark[8].x * image_width),
                                    int(hand_landmarks.landmark[8].y * image_height))
                thumb_tip = (int(hand_landmarks.landmark[4].x * image_width),
                             int(hand_landmarks.landmark[4].y * image_height))

                if abs(index_finger_tip[1] - thumb_tip[1]) < 50:
                    letra_detectada = "P"
                    cv2.putText(image, 'P', (700, 150), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                3.0, (0, 0, 255), 6)

        tiempo_actual = time.time()
        
        if letra_detectada == "P":
            if letra_detectada == ultima_letra:
                if inicio_letra_detectada is None:
                    inicio_letra_detectada = tiempo_actual
                elif tiempo_actual - inicio_letra_detectada >= duracion_requerida:
                    letra_confirmada = True
            else:
                inicio_letra_detectada = tiempo_actual
        else:
            inicio_letra_detectada = None
            letra_confirmada = False

        ultima_letra = letra_detectada

        color_boton = (0, 255, 0) if estado_actual == "Desbloqueado" else (0, 0, 255)
        cv2.circle(image, boton_pos, boton_radio, color_boton, -1)
        cv2.putText(image, "BTN", (boton_pos[0] - 20, boton_pos[1] + 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        color_led = (0, 0, 255) if estado_actual == "Bloqueado" else (0, 255, 0)
        cv2.circle(image, led_pos, led_radio, color_led, -1)

        color_estado = (0, 0, 255) if estado_actual == "Bloqueado" else (0, 255, 0)
        cv2.putText(image, f"Estado: {estado_actual}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.5, color_estado, 3)

        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
