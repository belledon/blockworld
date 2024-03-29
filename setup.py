import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="blockworld",
    version="0.0.1",
    author="Mario Belledonne",
    author_email="mbelledonne@gmail.com",
    description="Precuderal block generation and simulation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages = ['blockworld'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
