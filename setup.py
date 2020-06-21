from setuptools import setup, find_packages


setup(
    name='nice-bot',
    version='0.1',
    packages=find_packages(),
    package_data={'bot': ['resources/*']},
    url='https://github.com/cuiqui/nice-bot',
    license='MIT',
    author='Juan Schandin',
    author_email='juan.schandin@filo.uba.ar',
    description='Discord niceness tracker bot',
    entry_points={
        'console_scripts': [
            'nicebot = bot.service:main'
        ]
    },
    classifiers=(
        'Private :: Do not Upload'
    )
)
