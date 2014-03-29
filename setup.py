from distutils.core import setup

setup(name='updog',
        version='1.0',
        description='Network device configuration manager',
        author='Michael Sheinberg',
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
        )
