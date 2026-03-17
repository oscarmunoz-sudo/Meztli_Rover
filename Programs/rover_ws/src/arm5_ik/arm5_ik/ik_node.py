import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState


class IKNode(Node):
    def __init__(self):
        super().__init__('arm5_ik_node')

        # ====== IO ROS ======
        self.sub = self.create_subscription(Point, '/ik_target', self.target_cb, 10)

        # Publica comandos para el driver (hardware)
        self.cmd_pub = self.create_publisher(JointState, '/arm5/joint_commands', 10)

        # Publica "estado" para RViz/robot_state_publisher (simulación/visualización)
        self.js_pub = self.create_publisher(JointState, '/joint_states', 10)

        # ====== Parámetros del robot (igual que el xacro) ======
        self.L1 = 0.10
        self.L2 = 0.10
        self.L3 = 0.10
        self.L4 = 0.10
        self.L5 = 0.08

        # ====== Movimiento suave ======
        self.rate_hz = 30.0
        self.max_step_rad = 0.06  # ~3.4° por ciclo @30Hz => ~100°/s aprox (ajusta a gusto)

        # Target (lo que queremos alcanzar) y estado actual (lo que vamos publicando)
        self.target_q = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.current_q = [0.0, 0.0, 0.0, 0.0, 0.0]

        self.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']

        self.timer = self.create_timer(1.0 / self.rate_hz, self.update)

        self.get_logger().info('IK node listo. Publica Point en /ik_target (m)')

    def clamp(self, v, vmin, vmax):
        return max(vmin, min(vmax, v))

    def step_towards(self, current, target, max_step):
        diff = target - current
        if abs(diff) <= max_step:
            return target
        return current + max_step * (1.0 if diff > 0.0 else -1.0)

    def solve_ik(self, x, y, z):
        """
        IK simple tipo 2R en el plano + yaw base.
        Devuelve [q1..q5] en radianes.
        """
        # yaw base
        q1 = math.atan2(y, x)

        # Proyección al plano radial
        r = math.sqrt(x * x + y * y)
        z_eff = z - self.L1

        # 2R equivalente para demo
        a = self.L2 + self.L3
        b = self.L4 + self.L5
        d = math.sqrt(r * r + z_eff * z_eff)

        # Saturación alcanzabilidad
        max_reach = a + b
        min_reach = abs(a - b)
        if d > max_reach:
            d = max_reach - 1e-6
        if d < min_reach:
            d = min_reach + 1e-6

        c3 = self.clamp((d * d - a * a - b * b) / (2.0 * a * b), -1.0, 1.0)
        q3 = math.acos(c3)

        phi = math.atan2(z_eff, r)
        psi = math.atan2(b * math.sin(q3), a + b * math.cos(q3))
        q2 = phi - psi

        # "muñeca" simple
        q4 = -(q2 + q3)
        q5 = 0.0

        # (Opcional) clamping a límites si quieres (según tu URDF)
        # q2 = self.clamp(q2, -1.57, 1.57) etc.

        return [q1, q2, q3, q4, q5]

    def target_cb(self, msg: Point):
        # Calcula un nuevo objetivo articular
        self.target_q = self.solve_ik(msg.x, msg.y, msg.z)

    def publish_jointstate(self, positions, publisher):
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = self.joint_names
        js.position = positions
        publisher.publish(js)

    def update(self):
        # Movimiento suave: avanzar current_q hacia target_q
        for i in range(5):
            self.current_q[i] = self.step_towards(self.current_q[i], self.target_q[i], self.max_step_rad)

        # 1) Publica comandos para el driver
        self.publish_jointstate(self.current_q, self.cmd_pub)

        # 2) Publica joint_states para RViz (mismo valor por ahora)
        self.publish_jointstate(self.current_q, self.js_pub)


def main():
    rclpy.init()
    node = IKNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
