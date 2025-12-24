from setuptools import setup, find_packages

setup(
    name="netui-gtk",
    version="1.0.0",
    description="Network Interface Management GUI",
    author="Samy Abdellatif",
    license="MIT",
    packages=find_packages(),
    py_modules=["netui", "manual_config"],
    # We rely on system packages (python3-gi, etc.) to minimize size
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)