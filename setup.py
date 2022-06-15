#  Copyright (c) 2022 , IRIS-HEP
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# setuptools loads some plugins necessary for use here.
from setuptools import find_packages  # noqa: F401
from distutils.core import setup
import sys
import os

# Use the readme as the long description.
with open("README.md", "r") as fh:
    long_description = fh.read()

if sys.version_info[0] < 3:
    raise NotImplementedError("Do not support version 2 of python")

extra_test_packages = []

version = os.getenv("servicex_version")
if version is None:
    version = "0.1a1"
else:
    version = version.split("/")[-1]

setup(
    name="servicex_code_gen_lib",
    version=version,
    packages=["servicex_codegen"],
    scripts=[],
    description="Library for creating ServiceX Code Generators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ben Galewsky (IRIS-HEP/NCSA/University of Illinois)",
    author_email="bengal1@illinois.edu",
    maintainer="Ben Galewsky (IRIS-HEP/NCSA/University of Illinois)",
    maintainer_email="bengal1@illinois.edu",
    url="https://github.com/ssl-hep/ServiceX_Code_Generator_lib",
    license="BSD",
    python_requires=">=3.7, <3.11",
    test_suite="tests",
    install_requires=[
        "Flask==1.1.2",
        "Flask-RESTful==0.3.8",
        "Flask-WTF==0.14.3",
        # Incompatibility between flask and the latest itsdangerous
        "itsdangerous==2.0.1",
        # Avoid import error in Flask
        "werkzeug==2.0.3",
        "jinja2==3.0.3"

    ],
    extras_require={
        "test": [
            "pytest>=3.9",
            "pytest-mock",
            "pytest-cov",
            "coverage",
            "flake8",
            "codecov",
            "autopep8",
            "twine",
            "black",
        ]
        + extra_test_packages,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        # "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    platforms="Any",
)
