import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String

class NodoControlador(Node):

    def __init__(self):
        super().__init__('nodo_controlador')
        self.subscriber = self.create_subscription(String, 'respuestas_brazo', self.callback, 10)
        self.publisher = self.create_publisher(String, 'brazo_cmd', 10)

    def enviar_comando(self, command):
        msg = String()
        msg.data = str(command)
        self.publisher.publish(msg)
    
    def callback(self, msg):
        respuesta = msg.data
        print('Respuesta del brazo: %s' % respuesta)

def main(args=None):
    rclpy.init(args=args)
    nodo = NodoControlador()

    continuar = True
    # Enviar comandos al nodo del brazo
    rate = nodo.create_rate(1)  # 1 Hz
    while continuar:
        command = input("Ingrese el comando (entero o string): ")
        if command.lower() == 'exit':
            continuar = False
        else:
            nodo.enviar_comando(command)
            #rate.sleep()
    rclpy.spin(nodo)
    rclpy.shutdown()

if __name__ == '__main__':
    main()


