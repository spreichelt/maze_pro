# Maze Pro <!-- omit in toc -->
A game experience designed for use in teaching programming concepts from basic programming to training AI's, an advanced path finding algorithms.

## Table of Contents <!-- omit in toc -->
- [Getting started](#getting-started)
        - [Using Pipenv (preferred)](#using-pipenv-preferred)
        - [Using the dockerfile](#using-the-dockerfile)
        - [Using install.sh](#using-installsh)
## Getting started

### Using Pipenv (preferred)
- Install python (macOS)

        brew install python

- Install python (Ubuntu)
 
        apt-get update && add-apt-repository ppa:deadsnakes/ppa
        apt-get update && apt-get install python3.7
        apt-get update && apt-get install python3-pip


- Install pipenv using pip:

        python3.7 -m pip install pipenv

- Install required dependencies using the included Pipfile. Navigate to the projects root directory and:

        pipenv install

- To load the environment use:

        pipenv shell

You are now good to go! Run the project demo with:

        python maze_pro.py

Alternatively without first loading the pipenv you can run from your base shell using:

        pipenv run python maze_pro.py

### Using the dockerfile
**Note running a GUI from a dockerimage is incredibly slow**

- Navigate to the root of the project directory
- `docker build --rm -f Dockerfile -t maze_pro:latest .`
- Allow docker to access the host X11 display
+ Linux:
        *`docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix \ -e DISPLAY=unix$DISPLAY ple /bin/bash`

    + MacOS
        * install [Xquartz](https://www.xquartz.org/)
        * Open Xquartz, navigate to prefrences > security and check both boxes
        * Restart Xquartz
        * In terminal:
        * `xhost + 127.0.0.1`
        * `docker run -e DISPLAY=docker.for.mac.localhost:0 jess/firefox`

- Run the pygame demo
    + `docker run -t maze_pro python3.7 maze_pro.py`

### Using install.sh
**Tested using Ubuntu 16.04**

- Navigate to the root of the project directory
- execute the install sh from command line: `sudo ./install.sh`
- Run the pygame demo:
    + python3.7 maze_pro.py



