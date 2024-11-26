import cv2
import mediapipe as mp
import time

def distancia_euclidiana(p1, p2):
    d = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return d

def draw_bounding_box(image, hand_landmarks):
    image_height, image_width, _ = image.shape
    x_min, y_min = image_width, image_height
    x_max, y_max = 0, 0
    
    for landmark in hand_landmarks.landmark:
        x, y = int(landmark.x * image_width), int(landmark.y * image_height)
        if x < x_min: x_min = x
        if y < y_min: y_min = y
        if x > x_max: x_max = x
        if y > y_max: y_max = y
    
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

estado_actual = "Desbloqueado"
ultima_letra = None
ultimo_cambio_estado = time.time() 

cap = cv2.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)

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
        if letra_detectada and letra_detectada == ultima_letra:
            if tiempo_actual - ultimo_cambio_estado >= 10:  
                estado_actual = "Bloqueado" if estado_actual == "Desbloqueado" else "Desbloqueado"
                ultimo_cambio_estado = tiempo_actual  

        ultima_letra = letra_detectada

        cv2.putText(image, f"Estado: {estado_actual}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.5, (255, 255, 255), 3)

        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
