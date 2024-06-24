from setuptools import setup

APP = ['SKUMaker.py']
DATA_FILES = [('templates', ['templates/PC_Spec_template.pdf', 'templates/Generic_spec_template.pdf'])]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PyQt5'],
    'includes': ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    'excludes': [
        'PyQt5.QtDesigner', 'PyQt5.QtNetwork', 'PyQt5.QtOpenGL', 'PyQt5.QtScript', 
        'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtXml',
        'tkinter', 'unittest', 'email', 'html', 'http', 'xml',
        'pydoc', 'doctest', 'argparse', 'datetime', 'zipfile',
        'urllib', 'encodings', 'distutils', 'asyncio'
    ],
    'plist': {
        'CFBundleName': 'SKUMaker',
        'CFBundleDisplayName': 'SKU Maker',
        'CFBundleGetInfoString': "Making SKUs",
        'CFBundleIdentifier': "com.cityewaste.SKUMaker",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHumanReadableCopyright': u"Copyright © 2023, CityeWaste, All Rights Reserved"
    },
    'arch': 'universal2',
    'optimize': 2,
}

setup(
    name='SKUMaker',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

