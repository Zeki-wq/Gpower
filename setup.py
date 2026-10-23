from setuptools import setup, find_packages

setup(
    name="gpower-clone",
    version="1.3.0",
    description="Clean-room G*Power power-analysis engine, CLI, UI, MCP server, and AI agent",
    author="Zeki",
    packages=find_packages(),
    install_requires=[
        "scipy>=1.14.0",
        "numpy>=2.0.0",
        "mcp>=2.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
            "statsmodels>=0.14.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "gpower-clone=src.cli:main",
            "gpower-agent=src.agent:main",
            "gpower-mcp=src.mcp_server:run_stdio",
        ],
    },
    python_requires=">=3.10",
)
