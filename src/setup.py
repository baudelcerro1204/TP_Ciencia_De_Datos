from setuptools import setup, find_packages

setup(
    name="songrecommender",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.95.0,<1.0.0",
        "uvicorn>=0.23.0,<1.0.0",
        "spotipy>=2.23.0,<3.0.0",
        "pandas>=2.0.0,<3.0.0",
        "scikit-learn>=1.2.0,<2.0.0",
        "pydantic>=2.0.0,<3.0.0",          
        "pydantic-settings>=2.11.0,<3.0.0", 
        "python-dotenv>=0.21.0,<2.0.0",
    ],
)
