import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements(fname):
    return [line.strip()
            for line in open(os.path.join(os.path.dirname(__file__), fname))]


setup(
    name="tofawiki",
    version="0.0.2",  # Update in tofawiki/__init__.py
    author="Amir Sarabadani",
    author_email="ladsgroup@gmail.com",
    description="A service to bring articles easily",
    license="MIT",
    url="https://github.com/Ladsgroup/tofawiki",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'tofawiki=tofawiki.tofawiki:main',
        ],
    },
    long_description=read('README.md'),
    install_requires=requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
    ]
)
