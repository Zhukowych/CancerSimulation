from setuptools import setup, find_packages

setup(
    name="cancer_simulation",
    version='0.7.2',
    packages=find_packages(),
    short_description="A simple cancer and chemotherapy simulation",
    long_description="""We implemented cancer development and chemotherapy impact simulation using
                   stochastic cellular automaton with Python. The main feature of implemented 
                   app is capability of simulating different treatment strategies under same-
                   type cancer behavior.""",
    url = "https://github.com/Zhukowych/CancerSimulation",
    install_requires = [
        'pygame==2.5.2',
        'pygame-chart==1.0.0',
        'numpy==1.26.3',
        'PyYAML==6.0.1'
    ],
    entry_points = {
        'console_scripts': [
            "csim = src:main"
        ]
    }
)