import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from gpiozero import Servo

# Define el pin GPIO utilizado para controlar el servo
SERVO_PIN = 13

# Define la posición central del servo
CENTRAL_POSITION = 1

class ServoController(Node):

    def __init__(self):
        super().__init__('servo_controller')
        self.publisher_ = self.create_publisher(String, 'respuestas_brazo', 10)
        self.subscription = self.create_subscription(
            String,
            'brazo_cmd',
            self.cmd_callback,
            10)
        self.servo = Servo(SERVO_PIN)

    def cmd_callback(self, msg):
        cmd = msg.data
        if cmd == 'i':
            self.servo.min()
            time.sleep(100)
            self.publish_state('initial')
        elif cmd == 'p':
            self.servo.max()
            time.sleep(100)
            self.publish_state('vision')

    def publish_state(self, state):
        msg = String()
        msg.data = state
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    servo_controller = ServoController()
    rclpy.spin(servo_controller)
    servo_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

