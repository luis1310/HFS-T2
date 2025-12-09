"""Setup para instalar tesis3 como paquete"""
from setuptools import setup, find_packages

setup(
    name="tesis3",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24.0',
        'matplotlib>=3.7.0',
        'pandas>=2.0.0',
        'seaborn>=0.12.0',
        'pyyaml>=6.0',
        'tqdm>=4.65.0',
        'pytest>=7.4.0',
        'pytest-cov>=4.1.0',
    ],
)
