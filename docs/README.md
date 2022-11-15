# DOCS README

## Introduction
These are the documentation pages for grantnav.

Live deploy at https://help.grantnav.threesixtygiving.org

## Requirements
This application is built using python 3

## Installation
These instructions assume  instructions and requirements have been met for grantnav via the root README. To build and test documentation locally, run the following commands in sequence:

```sh
cd grantnav
python3 -m venv .ve
source .ve/bin/activate
pip install --upgrade pip
pip install -r requirements_docs.txt
cd docs
make html
```
