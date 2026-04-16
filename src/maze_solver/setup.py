import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'maze_solver'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # THESE ARE THE MAGIC LINES:
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vishal',
    maintainer_email='your_email@todo.todo',
    description='MAR Project Maze Solver using Pledge Algorithm',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pledge_node = maze_solver.pledge_node:main'
        ],
    },
)