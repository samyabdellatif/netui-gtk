from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="netui-gtk",
    version="1.0.0",
    description="Network Interface Management GUI for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Samy Abdellatif",
    author_email="",
    url="https://github.com/samyabdellatif/netui-gtk",
    license="MIT",
    packages=find_packages(),
    py_modules=["netui", "manual_config", "advanced_config", "config", "__main__"],
    # We rely on system packages (python3-gi, etc.) to minimize size
    install_requires=[],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "netui-gtk=__main__:main",
        ],
    },
    data_files=[
        ("share/applications", ["netui-gtk.desktop"]),
        ("share/polkit-1/actions", ["com.github.netui-gtk.policy"]),
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: GTK",
    ],
    keywords="network interface gtk gui linux dhcp ip configuration",
)