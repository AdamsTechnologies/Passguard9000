from setuptools import setup, find_packages

setup(
    name='Passguard9000',
    version='0.1.0',
    author='Jacob M. Adams',
    author_email='jakeadams@duck.com',
    description='A secure password management tool.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    license='',  # Or your chosen license
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'passguard.frontend.icons': ['*.png'],
    },
    install_requires=[
        'ttkbootstrap==1.10.1',
        'cryptography==44.0.0',
        # Add other dependencies
    ],
    entry_points={
        'gui_scripts': [
            'passguard=passguard.main:main',  # Assuming your main file is main.py with a main() function
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)