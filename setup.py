from setuptools import setup


def get_version():
    with open('VERSION') as v:
        return v.read()


setup(name='aiobernhard',
      description='An async bernhard client',
      version=get_version(),
      packages=['aiobernhard'],
      url='https://github.com/thebenwaters/aio-bernhard',
      author='Ben Waers',
      author_email='bsawyerwaters@gmail.com',
      install_requires=['protobuf'],
      clasifiers=[
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6"
      ]

)
