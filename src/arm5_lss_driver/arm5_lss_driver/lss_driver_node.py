import math
import time

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState

from . import lss
from . import lss_const as lssc


class Arm5LSSDriver(Node):
    """
    Driver simple:
    - Sub: /arm5/joint_commands (JointState, rad)
    - Convierte a unidades LSS (0.1 deg)
    - Suaviza con rampa por ciclo
    - Publica /joint_states para RViz (estado estimado = comando actual)
    """

    def __init__(self):
        super().__init__('arm5_lss_driver')

        # ====== Params ======
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', int(lssc.LSS_DefaultBaud))
        self.declare_parameter('rate_hz', 30.0)

        # Suavizado: max delta por update (en grados)
        self.declare_parameter('max_step_deg', 3.0)

        # Invertir sentido si hiciera falta (1.0 o -1.0)
        self.declare_parameter('dir_joint1', 1.0)
        self.declare_parameter('dir_joint2', 1.0)
        self.declare_parameter('dir_joint3', 1.0)
        self.declare_parameter('dir_joint4', 1.0)
        self.declare_parameter('dir_joint5', 1.0)

        # Límite tool: 0..90 grados
        self.tool_min_deg = 0.0
        self.tool_max_deg = 90.0

        self.port = self.get_parameter('port').get_parameter_value().string_value
        self.baud = self.get_parameter('baud').get_parameter_value().integer_value
        self.rate_hz = self.get_parameter('rate_hz').get_parameter_value().double_value
        self.max_step_deg = self.get_parameter('max_step_deg').get_parameter_value().double_value

        self.dir = [
            float(self.get_parameter('dir_joint1').value),
            float(self.get_parameter('dir_joint2').value),
            float(self.get_parameter('dir_joint3').value),
            float(self.get_parameter('dir_joint4').value),
            float(self.get_parameter('dir_joint5').value),
        ]

        # ====== ROS IO ======
        self.sub = self.create_subscription(JointState, '/arm5/joint_commands', self.cmd_cb, 10)
        self.js_pub = self.create_publisher(JointState, '/joint_states', 10)

        # ====== LSS init ======
        lss.initBus(self.port, self.baud)

        self.motors = {
            'joint1': lss.LSS(1),
            'joint2': lss.LSS(2),
            'joint3': lss.LSS(3),
            'joint4': lss.LSS(4),
            'joint5': lss.LSS(5),
        }

        # Velocidades (RPM) - ajusta a tu gusto
        self.motors['joint1'].setMaxSpeedRPM(6)
        self.motors['joint2'].setMaxSpeedRPM(5)
        self.motors['joint3'].setMaxSpeedRPM(5)
        self.motors['joint4'].setMaxSpeedRPM(5)
        self.motors['joint5'].setMaxSpeedRPM(4)

        # Hold todos
        for name in ['joint5', 'joint4', 'joint3', 'joint2', 'joint1']:
            self.motors[name].hold()
            time.sleep(0.05)

        self.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']

        # Estado interno en grados (lo que vamos aplicando)
        self.current_deg = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.target_deg = [0.0, 0.0, 0.0, 0.0, 0.0]

        self.timer = self.create_timer(1.0 / self.rate_hz, self.update)

        self.get_logger().info(f'LSS Driver listo en {self.port} @ {self.baud}. Sub: /arm5/joint_commands')

    def clamp(self, v, vmin, vmax):
        return max(vmin, min(vmax, v))

    def step_towards(self, current, target, max_step):
        diff = target - current
        if abs(diff) <= max_step:
            return target
        return current + max_step * (1.0 if diff > 0.0 else -1.0)

    def rad_to_deg(self, rad):
        return rad * 180.0 / math.pi

    def deg_to_rad(self, deg):
        return deg * math.pi / 180.0

    def deg_to_lss_units(self, deg):
        # 0.1° por unidad
        return int(round(deg * 10.0))

    def cmd_cb(self, msg: JointState):
        # Convertimos el mensaje entrante a un diccionario name->pos(rad)
        name_to_pos = {}
        for i, n in enumerate(msg.name):
            if i < len(msg.position):
                name_to_pos[n] = msg.position[i]

        # Extraer joints en orden
        new_target_deg = []
        for idx, jn in enumerate(self.joint_names):
            rad = name_to_pos.get(jn, None)
            if rad is None:
                # si no viene, conservar target actual
                new_target_deg.append(self.target_deg[idx])
                continue

            deg = self.rad_to_deg(rad) * self.dir[idx]

            # Límite especial tool joint5: 0..90
            if jn == 'joint5':
                deg = self.clamp(deg, self.tool_min_deg, self.tool_max_deg)

            new_target_deg.append(deg)

        self.target_deg = new_target_deg

    def publish_joint_states(self):
        # Publica el estado estimado (current_deg) como JointState en radianes
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = self.joint_names

        # OJO: aquí quitamos la dirección (dir) para que RViz vea lo que “realmente”
        # corresponde a la convención del URDF. Como ya aplicamos dir al target,
        # current_deg ya está en el “sentido físico”. Para visualizar con el URDF
        # normalmente quieres la convención URDF, así que des-aplicamos dir.
        pos_rad = []
        for i, deg_phys in enumerate(self.current_deg):
            deg_urdf = deg_phys / self.dir[i] if self.dir[i] != 0 else deg_phys
            pos_rad.append(self.deg_to_rad(deg_urdf))

        js.position = pos_rad
        self.js_pub.publish(js)

    def update(self):
        # Rampa suave en grados
        for i in range(5):
            self.current_deg[i] = self.step_towards(self.current_deg[i], self.target_deg[i], self.max_step_deg)

        # Enviar a servos
        for i, jn in enumerate(self.joint_names):
            motor = self.motors[jn]
            units = self.deg_to_lss_units(self.current_deg[i])
            motor.move(units)

        # Publicar joint_states para RViz
        self.publish_joint_states()


def main():
    rclpy.init()
    node = Arm5LSSDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
