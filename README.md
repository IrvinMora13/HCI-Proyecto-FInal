# Detección de Gestos y Control de Estado usando OpenCV, Mediapipe y PyQt5

## Descripción del Proyecto

Esta aplicación combina visión por computadora y una interfaz gráfica para detectar gestos manuales con la cámara, visualizar la detección en tiempo real y controlar el estado de un sistema (Bloqueado/Desbloqueado). Además, muestra actualizaciones del estado en un chat implementado con PyQt5.

## Tecnologías Utilizadas

- **Python**: Lenguaje principal.
- **OpenCV**: Para captura de video y procesamiento de imágenes.
- **Mediapipe**: Para detección y seguimiento de manos.
- **PyQt5**: Para la interfaz gráfica del usuario (GUI).
- **Python Event Bus**: Para la comunicación de eventos entre componentes.

## Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalados los siguientes paquetes y herramientas:

1. **Python 3.8 o superior**.
2. **Bibliotecas necesarias**:
   - OpenCV
   - Mediapipe
   - PyQt5
   - Python Event Bus

### Instalación de dependencias

Ejecuta el siguiente comando en tu terminal para instalar las dependencias:

```bash
pip install opencv-python mediapipe PyQt5 python-event-bus
```

### Estructura del Proyecto
main_program: Realiza la detección de gestos y controla el estado del sistema.
Ui_MainWindow: Clase para la interfaz gráfica con PyQt5.
update_status: Función de callback para actualizar mensajes en la interfaz gráfica usando el Event Bus.
Flujo principal: Ejecuta el hilo de detección de gestos junto con la interfaz gráfica.

#### Uso de la aplicación:
La ventana principal muestra un feed en tiempo real de la cámara.
Usa el gesto con la letra "P" (formado al unir el dedo índice y el pulgar) para activar o confirmar cambios.
Haz clic en el botón verde/rojo para cambiar el estado entre "Bloqueado" y "Desbloqueado".
La GUI muestra el estado actual y sus cambios.

## Explicación Técnica
### Detección de Gestos
Mediapipe Hands: Detecta landmarks en las manos y calcula las coordenadas del índice y el pulgar.
Criterio de detección: Si el índice y el pulgar están lo suficientemente cerca, se considera que forman la letra "P".
Confirmación de gesto: Si el gesto persiste por al menos 5 segundos, se confirma y activa la interacción.

### Interacción con la UI
Control del estado: Al hacer clic en el botón de la ventana y si el gesto está confirmado, se alterna entre los estados.
Feedback visual:
Botón: Verde para "Desbloqueado", rojo para "Bloqueado".
LED: Indica el estado actual del sistema.

## Integración con PyQt5
Ventana principal: Interfaz simple con un área de chat que muestra actualizaciones del estado del sistema.
Event Bus: Maneja la comunicación entre el sistema de detección de gestos y la interfaz gráfica.
