import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gmn",
    version="0.0.10",
    author="Nicole Eichert",
    author_email="n.eichert@googlemail.com",
    description="A network visualization of the relationships in Greek mythology.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NicoleEic/Brain_and_Code/tree/master/network",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "networkx",
        "numpy",
        "pandas",
        "requests",
        "matplotlib",
        "beautifulsoup4",
        "pillow",
    ],
    entry_points={
        'console_scripts': ['gmn = gmn.gmn:main']
    }
)