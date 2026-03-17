import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import time
import serial
from . import lss
from . import lss_const as lssc

class NodoBrazo(Node):

    def __init__(self):
        super().__init__('nodo_brazo')
        self.subscriber = self.create_subscription(String, 'brazo_cmd', self.callback, 10)
        self.publisher = self.create_publisher(String, 'respuestas_brazo', 10)

        self.respuesta = String()
        CST_LSS_Port = "/dev/ttyUSB0"
        CST_LSS_Baud = lssc.LSS_DefaultBaud

        # Create and open a serial port
        lss.initBus(CST_LSS_Port, CST_LSS_Baud)

        #Config motores
        self.motor1 = lss.LSS(1)
        self.motor1.setMaxSpeedRPM(6)
        self.motor2 = lss.LSS(2)
        self.motor2.setMaxSpeedRPM(5)
        self.motor3 = lss.LSS(3)
        self.motor3.setMaxSpeedRPM(5)
        self.motor4 = lss.LSS(4)
        self.motor4.setMaxSpeedRPM(5)
        self.motor5 = lss.LSS(5)
        self.motor5.setMaxSpeedRPM(4)

        motors = [self.motor5, self.motor4, self.motor3, self.motor2, self.motor1]
        for motor in motors:
            motor.hold()
            time.sleep(0.1)
        self.get_logger().info('Brazo listo\n\n')
        self.respuesta.data = 'Brazo listo\n'
        self.publisher.publish(self.respuesta)
        self.theta1=121
        self.theta2=0
        self.theta3=153
	
    def callback(self, msg):
        command = msg.data
        self.get_logger().info('Comando recibido: %s' % command)
        # Lógica para ejecutar acciones en función del comando recibido
        if command == 'x':  # Brazo_en_posicion_inicial
            self.Brazo_en_posicion_inicial()
        elif command == 'c':  # Apuntar_brazo
            self.Apuntar()
        elif command == 'v':  # Abrir_garra
            self.Abrir_garra()
        elif command == 'b':  # Agarrar_brazo
            self.Agarrar()
        elif command == 'n':  # Cerrar_garra
            self.Cerrar_garra()
        elif command == 'm':  # Guardar_objeto
            self.Guardar_objeto()
        elif command == ',':  # Secuencia completa
            self.Secuencia_completa()
        elif command == 'X':  # Vaciar_canasta
            self.Vaciar_canasta()
        elif command == '.':  # Colocar Brazo en 0
            self.Test()
        else:
            self.get_logger().info('Se recibió un comando inválido\n')
            self.respuesta.data = 'Se recibió un comando inválido\n'
            self.publisher.publish(self.respuesta)

        self.get_logger().info('Brazo listo para recibir otro comando\n')
        self.respuesta.data = 'Brazo listo para recibir otro comando\n'
        self.publisher.publish(self.respuesta)
        

    def Brazo_en_posicion_inicial(self):
        self.get_logger().info('Colocando Brazo en posición inicial...\n')
        self.respuesta.data = 'Brazo en posición inicial\n'
        self.publisher.publish(self.respuesta)
        
        #Color morado
        self.motor1.setColorLED(6)
        self.motor1.move(0)
        time.sleep(1)
        self.motor2.setColorLED(6)
        self.motor2.move(450)
        time.sleep(1)
        self.motor3.setColorLED(6)
        self.motor3.move(1100)
        time.sleep(1)
        self.motor4.setColorLED(6)
        self.motor4.move(-900)
        time.sleep(1)
        self.motor5.setColorLED(6)
        self.motor5.move(0)
        time.sleep(1)

        self.get_logger().info('Brazo Listo\n')
        self.respuesta.data = 'Brazo Listo\n'
        self.publisher.publish(self.respuesta)

    def Apuntar(self):
        self.get_logger().info('Bajando brazo\n')
        self.respuesta.data = 'Brazo bajado\n'
        self.publisher.publish(self.respuesta)
        
        #Color azul
        self.motor1.setColorLED(3)
        #self.motor1.move(0)
        #time.sleep(1)
        self.motor2.setColorLED(3)
        self.motor2.move(650)
        time.sleep(1)
        self.motor3.setColorLED(3)
        self.motor3.move(950)
        self.motor4.setColorLED(3)
        self.motor4.move(0)
        self.motor5.setColorLED(0)
        #self.motor5.move(-40)
        #time.sleep(1)

        self.get_logger().info('Brazo bajado\n')
        self.respuesta.data = 'Brazo bajado\n'
        self.publisher.publish(self.respuesta)
        
    def Abrir_garra(self):
        self.get_logger().info('Abriendo garra\n')
        self.respuesta.data = 'Garra abierta\n'
        self.publisher.publish(self.respuesta)
	
	#Color azul
        self.motor1.setColorLED(0)
        #self.motor1.move(0)
	#time.sleep(1)
        self.motor2.setColorLED(0)
        #self.motor2.move(-500)
        #time.sleep(1)
        self.motor3.setColorLED(0)
        #self.motor3.move(480)
        #time.sleep(1)
        self.motor4.setColorLED(0)
        #self.motor4.move(-900)
        #time.sleep(1)
        self.motor5.setColorLED(0)
        self.motor5.move(-400)
        time.sleep(1)
	
        self.get_logger().info('Garra abierta\n')
        self.respuesta.data = 'Garra abierta\n'
        self.publisher.publish(self.respuesta)
    
    def Agarrar(self):
        self.get_logger().info('Bajando brazo\n')
        self.respuesta.data = 'Brazo abajo\n'
        self.publisher.publish(self.respuesta)
	
	#Color amarillo
        self.motor1.setColorLED(0)
        #self.motor1.move(0)
        #time.sleep(1)
        self.motor3.setColorLED(0)
        self.motor3.move(950) #200 a -200
        #time.sleep(1)
        self.motor4.setColorLED(0)
        self.motor4.move(0) #-450 a 600
        time.sleep(1)
        self.motor5.setColorLED(0)
        #self.motor5.move(-400)
        #time.sleep(1)
        self.motor2.setColorLED(0)
        self.motor2.move(790) #-700 a -500
        #time.sleep(1)
        
        self.get_logger().info('Brazo extendido\n')
        self.respuesta.data = 'Brazo extendido\n'
        self.publisher.publish(self.respuesta)
        
    def Cerrar_garra(self):
        self.get_logger().info('Cerrando garra\n')
        self.respuesta.data = f'Cerrando garra\n'
        self.publisher.publish(self.respuesta)
        
        #Velocidad establecida para agarre (no tocar)
        self.motor5.setMaxSpeedRPM(4)
        
        #Color cyan
        self.motor1.setColorLED(0)
        #self.motor1.move(0)
        #time.sleep(1)
        self.motor2.setColorLED(0)
        #self.motor2.move(-470)
        #time.sleep(1)
        self.motor3.setColorLED(0)
        #self.motor3.move(0)
        #time.sleep(1)
        self.motor4.setColorLED(0)
        #self.motor4.move(-700)
        #time.sleep(1)
        self.motor5.setColorLED(0)
        self.motor5.move(-40)
        time.sleep(1)
        
        self.get_logger().info('Esperando...\n')
        self.respuesta.data = f'Esperando...\n'
        self.publisher.publish(self.respuesta)
        
        cuenta = 0
        cuenta2 = 0
        
        while True:
            cuenta = cuenta + 1
            corriente = self.motor5.getCurrent()
            corriente_str = str(corriente)
            if corriente_str != 'None':
                corriente_int = int(corriente_str,10)
                cuenta2 = cuenta2 + 1
                if corriente_int > 140:
                    cuenta = 0
                    self.motor5.hold()
                    self.get_logger().info('Objeto agarrado\n')
                    self.respuesta.data = f'Objeto agarrado\n'       
                    self.publisher.publish(self.respuesta)
                    break
                if cuenta2 > 500:
                    self.motor5.reset()
                    self.get_logger().info('Objeto no agarrado\n')
                    self.respuesta.data = f'Objeto no agarrado\n'
                    self.publisher.publish(self.respuesta)
                    cuenta2 = 0
                    break
            else:
                if cuenta > 500:
                    self.motor5.reset()
                    self.get_logger().info('Error con la garra\n')
                    self.respuesta.data = f'Error con la garra\n'
                    self.publisher.publish(self.respuesta)
                    break
    
    def Guardar_objeto(self):
        self.get_logger().info('Moviendo brazo a posición de guardado\n')
        self.respuesta.data = 'Brazo en posición de guardado\n'
        self.publisher.publish(self.respuesta)
	
	#Color magenta
        self.motor1.setColorLED(0)
        self.motor1.move(0)
        time.sleep(1)
        self.motor2.setColorLED(0)
        self.motor2.move(-300)
        time.sleep(1)
        self.motor3.setColorLED(0)
        self.motor3.move(-600)
        time.sleep(1)
        self.motor4.setColorLED(0)
        self.motor4.move(-900)
        time.sleep(1)
        self.motor5.setColorLED(0)
        #self.motor5.move(-40)
        #time.sleep(1)

        self.get_logger().info('Brazo en posición de guardado\n')
        self.respuesta.data = 'Brazo en posición de guardado\n'
        self.publisher.publish(self.respuesta)
        
    def Vaciar_canasta(self):
    	self.get_logger().info('Vaciando canasta...\n')
    	self.respuesta.data = 'Vaciando canasta...\n'
    	self.publisher.publish(self.respuesta)
    	
    	#Velocidad establecida para agarre (no tocar)
    	self.motor5.setMaxSpeedRPM(4)
    	
    	#Velocidad establecida para giro (no tocar)
    	self.motor1.setMaxSpeedRPM(6)
    	
    	# Color blanco
    	self.motor5.setColorLED(7)
    	self.motor5.move(-600)
    	time.sleep(3)
    	
    	self.motor1.setColorLED(7)
    	self.motor1.move(400)
    	time.sleep(3)
    	
    	self.motor2.setColorLED(7)
    	self.motor2.move(-1200)
    	time.sleep(1)
    	
    	self.motor3.setColorLED(7)
    	self.motor3.move(-1000)
    	time.sleep(1)
    	
    	self.motor4.setColorLED(7)
    	self.motor4.move(-1100)
    	time.sleep(1)
    	
    	self.motor5.setColorLED(7)
    	self.motor5.move(-30)
    	time.sleep(2)
    	
    	self.motor1.setColorLED(7)
    	self.motor1.move(-135) #cambio de 0 a -400 (depende si caen piedras)
    	time.sleep(2)
    	
    	self.motor1.setColorLED(7)
    	self.motor1.move(400)
    	time.sleep(2)
    	
    	self.motor5.setColorLED(7)
    	self.motor5.move(-600)
    	time.sleep(2)
    	
    	self.motor1.setColorLED(7)
    	self.motor1.move(0)
    	time.sleep(2)
    	
    	self.get_logger().info('Canasta vacía\n')
    	self.respuesta.data = 'Canasta vacía\n'
    	self.publisher.publish(self.respuesta)
    	
    def Test(self):
        self.get_logger().info('Colocando Brazo en ceros\n')
        self.respuesta.data = 'Brazo en ceros\n'
        self.publisher.publish(self.respuesta)
	
	#Color negro
        self.motor1.setColorLED(0)
        self.motor1.move(0)
        time.sleep(1)
        self.motor2.setColorLED(0)
        self.motor2.move(0)
        time.sleep(1)
        self.motor3.setColorLED(0)
        self.motor3.move(0)
        time.sleep(1)
        self.motor4.setColorLED(0)
        self.motor4.move(0)
        time.sleep(1)
        self.motor5.setColorLED(0)
        self.motor5.move(0)
        time.sleep(1)

        self.get_logger().info('Brazo en ceros\n')
        self.respuesta.data = 'Brazo en ceros\n'
        self.publisher.publish(self.respuesta)
        
    def Secuencia_completa(self):
        self.get_logger().info('Ejecutando secuencia completa\n')
        self.motor5.move(0)
        time.sleep(1)
        self.Apuntar()
        time.sleep(1)
        self.Abrir_garra()
        time.sleep(1)
        self.Agarrar()
        time.sleep(2)
        self.Cerrar_garra()
        time.sleep(2)
        self.Guardar_objeto()
        time.sleep(1)
        self.Abrir_garra()
        time.sleep(1)
        self.Brazo_en_posicion_inicial()

        self.get_logger().info('Secuencia completa ejecutada\n')
        self.respuesta.data = 'Secuencia completa ejecutada\n'
        self.publisher.publish(self.respuesta)

def main(args=None):
    rclpy.init(args=args)
    nodo = NodoBrazo()
    rclpy.spin(nodo)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

	
