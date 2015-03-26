from setuptools import setup

__version__ = "0.2.3"

with open('README.rst') as file:
    readme_text = file.read()

setup(name='panopy',
      version=__version__,
      description='Pandoc wrapper with templates',
      long_description=readme_text,
      url='https://github.com/balachia/panopy',
      author='Tony Vashevko ',
      author_email='avashevko@gmail.com',
      license='LICENSE.txt',
      packages=['panopy'],
      install_requires=['PyYAML'],
      include_package_data=True,
      keywords=['pandoc'],
      entry_points = {
          'console_scripts': [
              'panopy = panopy.pano:main'
          ]
        },
      zip_safe=False)
