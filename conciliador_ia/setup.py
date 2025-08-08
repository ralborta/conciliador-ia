from setuptools import setup, find_packages

setup(
    name="conciliador_ia",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "python-dotenv",
        "pandas",
        "openpyxl",
        "pdfplumber"
    ],
)
