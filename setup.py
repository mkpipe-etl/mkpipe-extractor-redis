from setuptools import setup, find_packages

setup(
    name='mkpipe-extractor-redis',
    version='1.0.0',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=['mkpipe', 'redis'],
    include_package_data=True,
    entry_points={
        'mkpipe.extractors': [
            'redis = mkpipe_extractor_redis:RedisExtractor',
        ],
    },
    description='Redis extractor for mkpipe.',
    author='Metin Karakus',
    author_email='metin_karakus@yahoo.com',
    python_requires='>=3.9',
)
