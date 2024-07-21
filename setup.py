from setuptools import find_packages, setup

setup(
    license_files=["LICENSE.txt"],
    name="my_package",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["flask", "sqlalchemy"],
    extras_require={
        "dev": ["pytest", "check-manifest"],
        "test": ["coverage"],
    },
    entry_points={
        "console_scripts": [
            "my_command=my_package.module:function",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
)
