from os.path import dirname, join

from setuptools import find_packages, setup


def read(name, **kwargs):
    with open(
        join(dirname(__file__), name), encoding=kwargs.get("encoding", "utf8")
    ) as openfile:
        return openfile.read()


setup(
    name="powerflex-logging-utilities",
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=True,
    version=read("src/powerflex_logging_utilities/VERSION").strip(),
    package_data={"powerflex_logging_utilities": ["VERSION"]},
    include_package_data=True,
    license="MIT License",
    description="Helpful code for logging in Python",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/edf-re/powerflex_logging_utilities_py",
    project_urls={
        "Issue Tracker": "https://github.com/edf-re/powerflex_logging_utilities_py/issues",
    },
    keywords=["NATS", "NATS request", "aiodebug", "async", "JSON logging"],
    # Only 3.8+
    python_requires=">2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*",
    install_requires=[
        # TODO add > req
        "aiodebug",
        "python-json-logger",
    ],
    extras_require={
        "pydantic": ["pydantic"],
        "nats-and-pydantic": ["nats-py", "pydantic"],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
)
