from setuptools import setup, find_packages

setup(
    name="p115nano302",
    version="0.0.9",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "jinja2",
        "aiofiles",
        "python-multipart",
        "orjson",
        "rich>=13.7.0",
        "p115nano302>=0.0.9"
    ],
) 