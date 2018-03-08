

from setuptools import setup

setup(
    name='frame_controller',    # This is the name of your PyPI-package.
    version='0.1',                          # Update the version number for new releases
    description='The funniest joke in the world',
    url='https://github.com/apl-ocean-engineering/sensor-test-frame-controller',
    license='MIT',
    packages=['frame_controller'],
    install_requires=['grpcio'],
    extras_require={
        'dev': ['grpcio_tools']
    },
    scripts=['apps/framed', 'apps/framec']                  # The name of your scipt, and also the command you'll be using for calling it
)
