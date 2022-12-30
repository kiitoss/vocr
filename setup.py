from setuptools import setup

setup(
    name='vocr',
    version='1.0.0',
    install_requires=['argparse', 'os', 'sys', 'json', 'easyocr', 'Pillow', 'numpy', 'opencv-python', 'time', 'mss', 'screeninfo'],
    description='Video Optical Character Recognition',
    author='kiitoss',
    maintainer='kiitoss',
    license='MIT'
)
