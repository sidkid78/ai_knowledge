from setuptools import setup, find_packages

setup(
    name="ukg",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "openai",
        "pytest",
        "pytest-asyncio"
    ]
) 