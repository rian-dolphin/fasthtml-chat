from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="fh-chat",
    version="0.3.1",
    packages=find_packages(),
    description="A package for chat functionality in FastHTML.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/rian-dolphin/fasthtml-chat",
    install_requires=[
        "python-fasthtml >= 0.4.4",
    ],
    extras_require={
        "dev": ["twine"],
    },
    python_requires=">=3.8",
    author="Rian Dolphin",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
