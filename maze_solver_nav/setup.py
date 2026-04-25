from setuptools import find_packages, setup

package_name = 'maze_solver_nav'

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
    maintainer='aries',
    maintainer_email='aries@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'pledge_solver = maze_solver_nav.pledge_solver:main',
        'e_stop = maze_solver_nav.e_stop:main',
        'vision_alert = maze_solver_nav.vision_alert:main',
    ],
},
)
