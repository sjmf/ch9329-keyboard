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
    install_requires=[],
    python_requires=">=3.6",
    url="https://github.com/sjmf/kvm-serial",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)