from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf8') as f:
    readme = f.read()

with open('requirements.txt','r',encoding='utf8') as f:
    requirements = f.readlines()

version = __import__('island_backup').version


setup(
    name='island_backup',
    version=version,
    description="backup h.nimingban and kukuku.cc",
    long_description=readme,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',

    ],
    url='https://github.com/littlezz/island-backup',
    author='littlezz',
    author_email='zz.at.field@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests*',]),
    install_requires=requirements,
    tests_require=['pytest'],
    include_package_data=True,

    zip_safe=False,
    entry_points={
        'console_scripts': [
            'island_backup=island_backup.main:cli'
        ]
    },

)

