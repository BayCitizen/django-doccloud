from setuptools import setup

setup(
    name='django-doccloud',
    version='0.1',
    description='Provides a reusable document app which interfaces with DocumentCloud',
    author='Bay Citizen',
    author_email='info@baycitizen.org',
    url='http://github.com/BayCitizen/django-doccloud/',
    packages=[
        'doccloud',
    ],

    install_requires=[
        'python-documentcloud',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
