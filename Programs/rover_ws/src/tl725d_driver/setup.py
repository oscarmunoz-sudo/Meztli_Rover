from setuptools import find_packages, setup

package_name = 'tl725d_driver'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='oscaribe',
    maintainer_email='oscaribe@todo.todo',
    description='TL725D IMU driver for ROS2',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'tl725d_node = tl725d_driver.tl725d_node:main',
        ],
    },
)
