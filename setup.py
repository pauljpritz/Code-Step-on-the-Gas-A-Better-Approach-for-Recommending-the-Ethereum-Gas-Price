from setuptools import setup, find_packages


setup(
    name="ethpred",
    packages=find_packages(),
    scripts=["./bin/dummy", "./bin/prep_data", "./bin/run_prepped", "./bin/run_evaluation"],
    install_requires=[
        "matplotlib",
        "tqdm",
        "pandas",
        "pyyaml",
        "sortedcontainers",
        "scikit-learn",
    ],
)
