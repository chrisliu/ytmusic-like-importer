#!/bin/bash
isort *.py
black --line-length 80 *.py
