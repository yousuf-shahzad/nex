from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nex-mc",
    version="0.1.0",
    author="Yousuf Shahzad",
    author_email="contact@yousuf.sh",
    description="a command-line tool for managing Minecraft servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yousuf-shahzad/nex",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "rich>=10.0.0",
        "pydantic>=1.8.0",
        "tqdm>=4.60.0",
    ],
    entry_points={
        "console_scripts": [
            "nex=nex.cli:main",
        ],
    },
)