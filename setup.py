
from setuptools import setup

# Parse the version from the poster module.
with open('cloud_bot/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue


setup(name='cloud_bot',
      version=version,
      python_requires='>=3',
      description=u"do the job",
      long_description=u"do my job",
      author=u"Vincent Sarago",
      author_email='contact@remotepixel.ca',
      license='BSD',
      packages=['cloud_bot'],
      include_package_data=True,
      install_requires=[
        'rio_tiler',
        'tweepy',
        'click'
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': [
            'cloud_bot = cloud_bot.cli.cli:create'
          ]
      })
