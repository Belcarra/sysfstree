
from setuptools import setup


def main():

    setup(
        name='pigadgetinfo',
        packages=['pigadgetinfo'],
        package_dir={'': 'src'},
        version=open('VERSION.txt').read().strip(),
        author='Stuart Lynne',
        author_email='stuart.lynne@gmail.com',
        url='http://github.com/stuartlynne/pigadgetinfo',
        download_url='http://github.com/stuartlynne/pigadgetinfo.git',
        license='MIT',
        keywords=['configfs','sysfs', 'pi', 'usb', 'gadget'],
        description='pigadgetinfo displayes gadget usb information from the ConfigFS and SysFS',
        entry_points={ 'console_scripts': [ 'pigadgetinfo = pigadgetinfo:main', ], },
        install_requires=["argparse", "time", "fnmatch", "magic"],
        classifiers=[
            "Programming Language :: Python",
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Operating System :: POSIX",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            'Topic :: System :: Logging',
            'Topic :: Text Processing',
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: System :: System Shells",
            "Topic :: System :: Systems Administration",
        ],
        long_description=open('README.md').read(),
    )


if __name__ == '__main__':
    main()
