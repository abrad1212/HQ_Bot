from setuptools import setup
from setuptools import find_packages

setup(name="HQBot",
      version="1.0.0",
      description="A HQ Trivia Bot",
      license="MIT",

      author="abrad1212",
      author_email="abrad12122@gmail.com",
      url="https://github.com/abrad1212/HQ_Bot",

      install_requires=[
          "beautifulsoup4",
          "lxml",
          "numpy",
          "opencv-contrib-python>=3.0.0"
          "Pillow",
          "pytesseract",
          "wikipedia"
      ],
      dependency_links=[
          "https://github.com/abenassi/Google-Search-API.git#egg=google-search-api"
      ],
      extras_require={
          'tests': ["pytest",
                    "pytest-pep8",
                    "pytest-cache",
                    "pytest-xdist",
                    "pytest-cov"]
      },

      include_package_data=True,

      entry_points={
          'console_scripts': [
              "answer-bot=hqbot.answerbot:main",
              "hq-bot=hqbot.answerbot:main",
              "hqbot=hqbot.answerbot:main"
          ]
      },
      packages=find_packages())
