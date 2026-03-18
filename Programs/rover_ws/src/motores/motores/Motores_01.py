
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from Phidget22.Phidget import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.Encoder import *
import time

class NodoMotores(Node):
    def __init__(self):
        super().__init__('nodo_motores')
        self.publisher_ = self.create_publisher(String, 'motores_cmd', 10)
        self.subscription_ = self.create_subscription(String, 'motores_cmd', self.callback, 10)

        self.dcMotorD = DCMotor()
        self.dcMotorI = DCMotor()
        self.encoderD = Encoder()
        self.encoderI = Encoder()

        self.dcMotorD.setDeviceSerialNumber(469351) #derecho
        self.dcMotorI.setDeviceSerialNumber(476416) #izquierdo
        self.encoderD.setDeviceSerialNumber(469351) #derecho
        self.encoderI.setDeviceSerialNumber(476416) #izquierdo

        self.dcMotorD.openWaitForAttachment(5000)
        self.dcMotorI.openWaitForAttachment(5000)
        self.encoderD.openWaitForAttachment(5000)
        self.encoderI.openWaitForAttachment(5000)

        self.vel = 0.7 #0.5 avanza y no se estanca, 0.75 sube poendientes, 1.00 maxima potencia relativa

        self.get_logger().info('Iniciado\n')

    def callback(self, msg):
        command = msg.data
        self.get_logger().info('Comando recibido: %s' % command)

        if command == 'Alto' or command == 'z':
            self.Alto()
        elif command == 'Adelante' or command == 'w':
            self.Adelante()
        elif command == 'Atras' or command == 's':
            self.Atras()
        elif command == 'Giro_izq' or command == 'a':
            self.Giro_izq()
        elif command == 'Giro_der' or command == 'd':
            self.Giro_der()
        elif command == 'Apagar' or command == 'q': 
            self.Alto()
            self.dcMotorI.close()
            self.dcMotorD.close()
        elif command == 'Encender' or command == 'e':
            self.dcMotorD = DCMotor()
            self.dcMotorI = DCMotor()
        else:
            self.Alto()

        self.leer_encoders()

    def Alto(self):
        self.dcMotorD.setTargetVelocity(0.0)
        self.dcMotorI.setTargetVelocity(0.0)
        print("Rover detenido\n")

    def Adelante(self):
        self.dcMotorD.setTargetVelocity(-self.vel)
        self.dcMotorI.setTargetVelocity(self.vel)  
        print("Movimiento hacia adelante\n")

    def Atras(self):
        self.dcMotorD.setTargetVelocity(self.vel)
        self.dcMotorI.setTargetVelocity(-self.vel) 
        print("Movimiento hacia atras\n")

    def Giro_izq(self):
        self.dcMotorD.setTargetVelocity(-self.vel)
        self.dcMotorI.setTargetVelocity(-self.vel)
        print("Giro a la derecha\n") 

    def Giro_der(self):
        self.dcMotorD.setTargetVelocity(self.vel)
        self.dcMotorI.setTargetVelocity(self.vel)
        print("Giro a la izquierda\n") 

    def leer_encoders(self):
        posD = self.encoderD.getPosition()
        posI = self.encoderI.getPosition()
        print("Posición Encoder Derecho: %f" % posD)
        print("Posición Encoder Izquierdo: %f" % posI)

def main(args=None):
    rclpy.init(args=args)
    nodo = NodoMotores()
    rclpy.spin(nodo)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()


