from setuptools import setup, find_packages

setup(
    name="ashare_mcp",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastmcp>=0.1.0",
        "pandas",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "ashare-mcp=ashare_mcp.__main__:main",
        ],
    },
    description="Ashare stock data as MCP service",
    author="Rusian Huu",
    author_email="hu_bo_cheng@qq.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
