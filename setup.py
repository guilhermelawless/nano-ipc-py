from setuptools import setup
setup(
    name='nano_ipc',
    version='0.2.0',
    description='An IPC client for the Nano currency',
    url='https://github.com/guilhermelawless/nano-ipc-py',
    author='Guilherme Lawless',
    author_email='guilherme@nano.org',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License',
        'Programming Language :: Python :: 3',
    ],
    keywords='development',
    packages=['nano_ipc'],
    package_dir={'nano_ipc': 'src/nano_ipc'},
    python_requires='>=3.5',
    project_urls={
        'Nano': 'https://nano.org',
        'Source': 'https://github.com/guilhermelawless/nano-ipc-py',
    },
)
