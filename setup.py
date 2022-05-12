from setuptools import find_packages, setup

setup(
    name="powerflex-logging-utilities",
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=False,
    install_requires=[
        # TODO add > req
        "aiodebug",
        "python-json-logger",
    ],
    extras_require={
        "pydantic": ["pydantic"],
        "nats": ["nats-py"],
    },
)
