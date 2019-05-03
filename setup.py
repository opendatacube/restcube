from setuptools import setup, find_packages

setup(
    name='restcube',
    version='0.1.0',
    description="Datacube REST Services",
    author="Open Data Cube",
    author_email='earth.observation@ga.gov.au',
    packages=find_packages(),
    include_package_data=True,
    license="Apache Software License 2.0",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ]
)