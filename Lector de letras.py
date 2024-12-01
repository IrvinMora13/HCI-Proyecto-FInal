import threading
import cv2
import mediapipe as mp
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from python_event_bus import EventBus
import sys


event_bus = EventBus()

@event_bus.on("update_status")
def update_status(status,ui):
    ui.updateMessage(status)


def main_program():
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
        nonlocal estado_actual
        estado_actual = "Bloqueado" if estado_actual == "Desbloqueado" else "Desbloqueado"
        event_bus.call("update_status", estado_actual,ui)


    def click_boton(event, x, y, flags, param):
        nonlocal letra_confirmada
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
                break

            # Procesar imagen
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            # Renderizar imagen
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

            # Dibujar UI
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



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Creacion de la ventana
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Label Name
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(0, 0, 131, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        # Lista de mensajes
        self.messageBox = QtWidgets.QTextEdit(self.centralwidget)
        self.messageBox.setGeometry(QtCore.QRect(420, 60, 361, 511))
        self.messageBox.setObjectName("messageBox")
        self.messageBox.setReadOnly(True)

        # Label de Chat
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(420, 40, 47, 13))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        # Main Windows
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Qt Chat"))
        self.label_2.setText(_translate("MainWindow", "Chat"))
        
    def updateMessage(self, statusMessage):
        self.messageBox.append(f"Estatus del proceso {statusMessage}")

if __name__ == "__main__":
    program_thread = threading.Thread(target=main_program)

    program_thread.start()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

