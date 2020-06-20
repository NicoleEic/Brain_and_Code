import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gmn",
    version="0.0.1",
    author="Nicole Eichert",
    author_email="n.eichert@googlemail.com",
    description="A network visualization the relationships in Greek mythology.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NicoleEic/Brain_and_Code/tree/master/network",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "networkx",
        "numpy",
        "pandas",
        "requests",
        "tkinter",
        "webbrowser",
        "matplotlib",
        "bs4",
        "PIL",
    ],
    entry_points={
        'console_scripts': [
            'gmn = gmn:main',
        ],
        'gui_scripts': [
            'gmn = gmn:main',
        ]
    }
)