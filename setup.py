# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["pDESy", "pDESy.model"]

package_data = {"": ["*"]}

install_requires = [
    "matplotlib>=3.2.1,<4.0.0",
    "networkx>=2.4,<3.0",
    "numpy>=1.18.4,<2.0.0",
    "plotly>=4.7.1,<5.0.0",
    "pytest-cov>=2.9.0,<3.0.0",
    "typing>=3.7.4,<4.0.0",
    "uuid>=1.30,<2.0",
]

setup_kwargs = {
    "name": "pdesy",
    "version": "0.2.1",
    "description": "pDESy: Discrete Event Simulation of Python",
    "long_description": "# pDESy: Discrete-Event Simulator in Python\n\n![test](https://github.com/mitsuyukiLab/pDESy/workflows/test/badge.svg)\n\n## What is it?\n\n**pDESy** is a Python package of Discrete-Event Simulator (DES). It aims to be the fundamental high-level building block for doing practical, real world engineering project management by using DES and other DES modeling tools. **pDESy** has only the function of discrete-event simulation, does not include the function of visual modeling.\n\n\n## Where to get it\nThe source code is currently hosted on GitHub at: [https://github.com/mitsuyukiLab/pDESy](https://github.com/mitsuyukiLab/pDESy)\n\nBinary installers for the latest released version will be available at the Python package index. Now, please install pDESy as following.\n\n```\npip install git+ssh://git@github.com/mitsuyukiLab/pDESy.git\n```\n\n## License\n[MIT](https://github.com/mitsuyukiLab/pDESy/blob/master/LICENSE)\n\n## Documentation\nComming soon.. This version is not stable...\n\n## Background\n**pDESy** is developed by a part of next generation DES tool of **[pDES](https://github.com/mitsuyukiLab/pDES)**.\n\n## Contribution\n1. Fork it ( http://github.com/mitsuyukiLab/pDESy/fork )\n2. Create your feature branch (git checkout -b my-new-feature)\n3. Commit your changes (git commit -am 'Add some feature')\n4. Push to the branch (git push origin my-new-feature)\n5. Create new Pull Request\n\nIf you want to join this project as a researcher, please contact [me](https://github.com/taiga4112).",
    "author": "Taiga MITSUYUKI",
    "author_email": "mitsuyuki-taiga-my@ynu.ac.jp",
    "maintainer": "Taiga MITSUYUKI",
    "maintainer_email": "mitsuyuki-taiga-my@ynu.ac.jp",
    "url": "https://github.com/mitsuyukiLab/pDESy",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.6.9,<4.0",
}


setup(**setup_kwargs)
