import os
from setuptools import setup

APP = ['SKUMaker.py']
DATA_FILES = [('templates', ['templates/PC_Spec_template.pdf', 'templates/Generic_spec_template.pdf'])]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5', 'fitz'],
    'includes': ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    'plist': {
        'CFBundleName': 'SKUMaker',
        'CFBundleDisplayName': 'SKU Maker',
        'CFBundleGetInfoString': "Making SKUs",
        'CFBundleIdentifier': "com.yourcompany.SKUMaker",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHumanReadableCopyright': u"Copyright © 2023, Your Company, All Rights Reserved"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
