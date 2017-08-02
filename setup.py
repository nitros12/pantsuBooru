from setuptools import setup

version = __import__("pantsuBooru").__version__


setup(name="PantsuBooru",
      version=version,
      description="Booru wew",
      long_description="A bad booru service",
      url="https://github.com/nitros12/pantsuBooru",
      author="Ben Simms",
      author_email="ben@bensimms.moe",
      license="BSD",
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Framework :: AsyncIO",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 3.6"
      ],
      keywords="Booru",
      packages=[
          "pantsuBooru"
      ])
