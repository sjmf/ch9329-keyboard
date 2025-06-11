from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kvm-serial",
    version="1.3.0",
    description="Python package for interfacing with CH9329 KVM devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Samantha Finnigan",
    author_email="1038320+sjmf@users.noreply.github.com",
    packages=find_packages(include=["kvm_serial", "kvm_serial.*"]),
    install_requires=[
        "pyserial>=3.5",
        "pyusb>=1.3.1",
        "pynput>=1.8.1",
        "opencv-python>=4.11.0.0",
        "screeninfo>=0.6.7",
    ],
    python_requires=">=3.10",
    url="https://github.com/sjmf/kvm-serial",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    app=["kvm_serial/kvm.py"],
    setup_requires=["py2app"],
)

# Build and Release with:
# python3 -m build 
# python3 -m twine upload --repository testpypi dist/*
