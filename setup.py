import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    install_requires = fh.read().splitlines()

setuptools.setup(
    name="craigslist-cli",
    version="0.1.1",
    author="Jerome de Leon",
    author_email="jpdeleon.bsap@gmail.com",
    description="craiglist via CLI",
    long_description=long_description,
    url="https://github.com/jpdeleon/craigslist",
    packages=setuptools.find_packages(exclude=["tests"]),
    # package_data={"craigslist": ["data/*"]},
    # include_package_data=True,
    scripts=["apartments.py", "posts.py"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
)
