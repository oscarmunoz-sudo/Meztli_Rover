import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from pynput import keyboard

class TecladoNodo(Node):

    def __init__(self):
        super().__init__('teclado_nodo')
        self.publisher = self.create_publisher(String, 'motores_cmd', 10)

        def on_key_press(key):
            try:
                tecla = key.char
                msg = String()
                msg.data = tecla
                self.publisher.publish(msg)
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_key_press)
        listener.start()

def main(args=None):
    rclpy.init(args=args)
    nodo = TecladoNodo()
    rclpy.spin(nodo)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
