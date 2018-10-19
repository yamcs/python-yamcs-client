import io

import setuptools

with io.open('README.md', encoding='utf-8') as f:
    readme = f.read()

packages = [
    package for package in setuptools.find_packages()
    if package.startswith('yamcs')]

version = '1.1.4'

setuptools.setup(
    name='yamcs-cli',
    version=version,
    description='Yamcs Command-Line Tools',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/yamcs/yamcs-python',
    author='Space Applications Services',
    author_email='yamcs@spaceapplications.com',
    license='LGPL',
    packages=packages,
    namespace_packages=['yamcs', 'yamcs.cli'],
    entry_points={
        'console_scripts': [
            'yamcs = yamcs.cli.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    platforms='Posix; MacOS X; Windows',
    install_requires=[
        'six',
        'yamcs-client>=' + version,
    ],
    include_package_data=True,
    zip_safe=False,
)
