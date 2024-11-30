from setuptools import setup, find_packages


setup(
    name='dddhns',
    version='0.0.3',
    packages=find_packages(exclude='test'),
    install_requires=['jsonschema', 'lxml', 'pandas>=2', 
                      'specialsauce>=0.0.3a2'],
)