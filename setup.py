from distutils.core import setup

setup(name='updog',
        version='1.0',
        description='Network device configuration manager',
        author='Michael Sheinberg',
        url='https://github.com/msheiny/updog',
        author_email='m.sheiny@gmail.com',
        scripts=['bin/woof','bin/bark'],
        packages=['updog'],
        data_files=[('local/updog/vendors/',['vendors/cisco.ini',
                    'vendors/foundry.ini',
                    'vendors/extreme.ini'
                    ])
                    ],
        install_requires=[
            'pexpect>=3.1',
            'shell>=1.0.1',
            'nose'
            ],
        classifiers=[
            'Topic :: System :: Networking :: Monitoring',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
            'Programming Language :: Python',
            'Operating System :: POSIX :: Linux',
            'License :: OSI Approved :: MIT License'
            ]
        )
