import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

import serial
import math


PACKET_SIZE = 32


def bcd3_to_float(b1, b2, b3):

    negative = (b1 & 0x10) != 0
    hundreds = b1 & 0x0F

    tens = (b2 >> 4) & 0x0F
    units = b2 & 0x0F

    tenths = (b3 >> 4) & 0x0F
    hundredths = b3 & 0x0F

    value = (
        hundreds * 100 +
        tens * 10 +
        units +
        (tenths * 10 + hundredths) / 100.0
    )

    if negative:
        value = -value

    return value


def euler_to_quaternion(roll, pitch, yaw):

    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    qw = cr * cp * cy + sr * sp * sy

    return qx, qy, qz, qw


class TL725DNode(Node):

    def __init__(self):

        super().__init__('tl725d_node')

        self.publisher = self.create_publisher(Imu, '/imu/data', 10)

        self.ser = serial.Serial(
            '/dev/ttyACM0',
            115200,
            timeout=0.01
        )

        self.buffer = bytearray()

        self.timer = self.create_timer(0.002, self.read_serial)

        self.get_logger().info("TL725D node iniciado")

    def read_serial(self):

        data = self.ser.read(256)

        if data:
            self.buffer.extend(data)

        while len(self.buffer) >= PACKET_SIZE:

            if self.buffer[0] != 0x68:
                self.buffer.pop(0)
                continue

            packet = self.buffer[:PACKET_SIZE]

            checksum = sum(packet[1:31]) & 0xFF

            if checksum != packet[31]:
                self.buffer.pop(0)
                continue

            self.decode_packet(packet)

            del self.buffer[:PACKET_SIZE]

    def decode_packet(self, p):

        idx = 4

        roll = bcd3_to_float(p[idx],p[idx+1],p[idx+2]); idx+=3
        pitch = bcd3_to_float(p[idx],p[idx+1],p[idx+2]); idx+=3
        yaw = bcd3_to_float(p[idx],p[idx+1],p[idx+2]); idx+=3

        ax = bcd3_to_float(p[idx],p[idx+1],p[idx+2]); idx+=3
        ay = bcd3_to_float(p[idx],p[idx+1],p[idx+2]); idx+=3
        az = bcd3_to_float(p[idx],p[idx+1],p[idx+2]); idx+=3

        gx = bcd3_to_float(p[idx],p[idx+1],p[idx+2]); idx+=3
        gy = bcd3_to_float(p[idx],p[idx+1],p[idx+2]); idx+=3
        gz = bcd3_to_float(p[idx],p[idx+1],p[idx+2])

        # conversiones ROS

        roll = math.radians(roll)
        pitch = math.radians(pitch)
        yaw = math.radians(yaw)

        gx = math.radians(gx)
        gy = math.radians(gy)
        gz = math.radians(gz)

        ax *= 9.80665
        ay *= 9.80665
        az *= 9.80665

        qx,qy,qz,qw = euler_to_quaternion(roll,pitch,yaw)

        msg = Imu()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "imu_link"

        msg.orientation.x = qx
        msg.orientation.y = qy
        msg.orientation.z = qz
        msg.orientation.w = qw

        msg.angular_velocity.x = gx
        msg.angular_velocity.y = gy
        msg.angular_velocity.z = gz

        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az

        self.publisher.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = TL725DNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
