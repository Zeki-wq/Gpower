from setuptools import setup, find_packages

setup(
    name="gpower-clone",
    version="1.0.0",
    description="Clean-room re-implementation of G*Power two-sample t-test power calculator",
    author="Zeki",
    packages=find_packages(),
    install_requires=[
        "scipy>=1.14.0",
        "numpy>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gpower-clone=src.cli:main",
        ],
    },
    python_requires=">=3.10",
)
