from setuptools import find_packages, setup

package_name = 'arm5_lss_driver'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='oscaribe',
    maintainer_email='oscaribe@todo.todo',
    description='LSS driver for 5DOF arm',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'lss_driver = arm5_lss_driver.lss_driver_node:main',
        ],
    },
)
