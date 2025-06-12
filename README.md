# Drowsiness Detection
This is repo for holding the code for the drowsiness detection project on on Toyota Motor Indonesia at Capabilty Center Division Department. The drowsiness use Mediapipe pipeline framework to detect the pose estimation and act approtiately according to that

<p align="center">
  <img width="79%"src="docs/images/Drowsiness_Detection.gif">
</p>

## Project Tech Stack 
This project use several Tech Stack, but most of them are using Python. As you an see, this project is a Real-Time face recognition to detect a drowsiness of an user that was captured by the camera. If running on Windows, it will use the default webcam current OS have, or if in linux, it will always -- always be in mind will be run on Raspberry Pi, especially in Raspberry Pi 5 with Raspberry Pi Camera as the video stream source. The project tech stack is mostly divided into 3 main core, the computer vision, the deep learning model, and the backend.

Perhaps some of you will ask, why not just using OpenCV windows to see the result of the calculation? Well, I plan to run this on a headless GUI OS, so making it run using OpenCV windows will be quite useless (this is to save resources when running on Low-Spec hardware).

1. Mediapipe
2. OpenCV
3. FastAPI

### Model
The model we are using to detect the pose estimation is [Mediapipe](https://github.com/google-ai-edge/mediapipe). It's easy to use, and cross-compatible and run pretty fast on x64 platfrom.

### Computer Vision
For the computer vision manipulation, we are using your old friend OpenCV. Really no question asked for this

### Backend
At first, I want to expose the API using C# ASP .NET platform. But it seems that doing this will just make more work, that's why I decided used [FastAPI](https://fastapi.tiangolo.com/) where it was already in the same environment as the Model and Computer Vision libraries. But maybe some of you will ask who already familiar with Flask, why not Flask or any other stuff? Well it's not like I hate flask, but I was searching a framework that already have OpenAPI built into them and FastAPI already meet that requirements.


## Project Structure
The app structure is as follows: the entry point of the app is `main.py`. The src folder contains the main application code, not really adhering to the Clean arhictecture, but more like following the more OOP Design to ensure the modularity and the shared-responsibilities that I want.

```
drowsiness-detection/
├── src/
│   ├── enum
│   ├── services
│   ├── ....
├── test/
```

As this project is still under development, I can say that this structure can be contested for change to be more flexible, as I really don't have experience building in a Python environment, and I don't really find a good project in github that really adheres OOP in Python, this will do for now.

## Installing Environment 
To run this project, we will use a virtual environment to manage our project dependencies. I think that most easiest way to installing python packages in secluded environment is using the Python own official, virtual environment. To do this, first you must have to install python first. The app is using this spesification

1. Python 3.11 version
2. Mediapipe 0.10.21 version

So for python, you can search for their installer [here](https://www.python.org/downloads/release/python-3119/) and install them. If you have installed them, we can start the virtual environment creation. Of course you can try to install another python version, but keep in mind, I made this project in 3.11 so it can be more stable rather the new python version and currently if using Hailo AI Accelerator, most of their compiler and program running max on Python 3.11 version, so it is recommended that you use Python 3.11 version both on Windows and Linux just for best practices. And another also, to connect and use the Raspberry Pi Camera on the Raspberry Pi, we are using the `picamera2` package, where it can for now be installed using `apt`, and by default that package came and installed in the Python 3.11.2 . If you decided to use another python version, do mind that the `requirements.txt` that I have prepared for you will be conflict, you can one-by-one install the package that I list on that `requirements.txt` and if you running them on Linux especially on the Raspberry Pi, it will really pain in the ass to set it to be working for the Camera. I will explain how you can set up the environment in both Windows and Linux for the Raspberry Pi, but keep in mind Windows version, this code probably will favor more on the Linux side, but it's a good idea to be able to run this on Windows as-well. So, before doing the environement set-up, please kindly clone this repo 

### Preparing environment on Windows
First go do the work directory. 
```bash
cd drowsiness-detection
```

Then after that, if your Python base already in 3.11 version, we can directly create our virtual environment under `drowsiness-detection/venv` with the following command
```bash
python -m venv venv
```

But if your machine have multiple python version, you can do this
```bash
py -3.11 -m venv venv
```


You will see now a folder named `venv` will be created in your work directory. Now that we have a virtual environment been created, we now need to activate it.

```bash
.\venv\Scripts\activate
```

You can see the virtual environment has been activated by seeing the (venv) in your terminal. After you activate the virtual environment, you can add packages to it using `pip`. You can also create a description of your dependencies using `pip`. In this repo, I have made it the packages that required in order to run this app, so simply just install them with this following command

```bash
pip install -r requirements.txt
```

To verify that the packages is installed, run following and see if there is packages that not have been installed
```bash
pip list
```

Then the setup for windows are finish and we can start running our app!

To return to normal system settings, use the deactivate command.
```bash
deactivate
```

I have make a script to automate this preparation. Run the following script to automate the installation process or double click the script located on the `scripts\setup_env_windows.bat`
```bash
cd scripts\
.\setup_env_windows.bat
```

### Preparing Environment on Linux
Currently, what I mean for preparing environment on linux is I meant in Raspberry Pi OS, because there are some package and especially hardware (like camera) are really depends on Raspberry Pi repository package. For running this on Linux Raspberry Pi, the steps are similar when we set up on Windows.

But, before preparing the environment to run our project. Kindly read this [guide](docs/preparing-rpi5.md) first to set up your Raspberry Pi first. 

Now, if you have do what guide above tells you, we can continue setting up our environment. First, go to the work directory after clone the repository. 
```bash
cd drowsiness-detection
```

And then we go, if your machine from start doesn't use the spesific Python version needed. You can make sure of the Python version active by this command
```bash
python3 --version
```

Then, because we decided to make this project inside the Virtual Environment using the Python Virtual Environment, this is a crucial step so the venv can recognize our Pi Camera. This issue has been reported [here](https://forums.raspberrypi.com/viewtopic.php?t=361758), where because the camera library are installed using `apt` not thorugh pip, we can easily access this library from inside our virtual environment. Conda also suffer the biggest from all of this than any other environment package. So, we gonna make this using a simple virtual environment. First make sure to install this package first from the apt package

```bash
sudo apt install -y python3-libcamera libcamera-dev
```

Then create the virtual environment using `system-site-packages` tag

```bash
python3 -m venv --system-site-packages venv
```

The `--system-site-packages` is really important one, as this will allow us to use package that installed by root system through `apt` in our virtual environment.

You will see now a folder named `venv` will be created in your work directory. Now that we have a virtual environment been created, we now need to activate it.

```bash
source venv\bin\activate
```

After that, you can see the virtual environment has been activated by seeing the (venv) in your terminal. After you activate the virtual environment, you can add packages to it using `pip`. You can also create a description of your dependencies using `pip`. In this repo, I have made it the packages that required in order to run this app, so simply just install them with this following command

```bash
pip install -r requirements-linux.txt
```

In linux, we will run the FastAPI using uvicorn and this will not install automatically when we install the FastAPI pip packages. So we can just do this'

```bash
pip install "uvicorn[standard]"
```

Then the setup for linux are finish and we can start running our app!

To return to normal system settings, use the deactivate command.
```bash
deactivate
```

Now, congrats you have finish the setup for Raspberry Pi OS System. But actually, I have also make a script to automate this preparation. Run the following script to automate the installation process located on the `scripts\setup_env_raspberry.sh`
```bash
chmod +x scripts/setup_env_raspberry.sh
./scripts/setup_env_raspberry.sh
```

## How to Migrate Database
For building the database, this project is using SQlite, where to build the entity and schemas, we are using [SQLModel](https://sqlmodel.tiangolo.com/) for interacting to the database where it was based on the [SQLAlchemy](https://www.sqlalchemy.org/). I choose this because it was perfect combination that combine with SQLAchemy and also the pydantic model of FastAPI was using. The entity can be seen on the `src/domain/entity`. For migrations, we are using [Alembic](https://alembic.sqlalchemy.org/en/latest/). This two is the tools that we are going to use for connecting to the database we building.

First, we already build the configuration, but if not yet being done or don't see `alembic.ini`, please init them by simply type this
```bash
alembic init alembic
```

To generate the migrations, we can simply on the terminal
```bash
alembic revision --autogenerate -m "migrations"
```

And to apply the migrations, we can type this on terminal
```bash
alembic upgrade head
```

in the code of `main.py`, I already add function to dynamically at the runtime on the startyp to apply migrations to the database if there's any changes. So what you can do is, if you want to add something to the databse, just make sure to do the migrations, then commit that, and then run them for your convinience. 

## How to Run The App
The app is using FastAPI to control the data of the stream. And to run this, it's quite simple if you follow the setup up environment correctly. We will use uvicorn, An ASGI web server for Python. First, make sure you are in the virtual environment first, and after that simply type this on terminal on the root directory

```bash
uvicorn main:app
```

To enable hot-reload, use this
```bash
uvicorn main:app --reload
```

The server will run and there will be logs like this one
```prolog
INFO:     Started server process [4060]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

To see the API documentation, just go to the http://127.0.0.1:8000/docs

## How to run the lints
I hope you read this, to make sure that this project is clean, as really Python never enforce any typing rules whatsoever, I really want this code project to have the same rules as other, that's why lints are used. This project use [Ruff](https://docs.astral.sh/ruff/) for the linters, and it really easy to use them. The rules can be found in the `.ruff.toml`.

So before commiting your changes, make sure to run this to check any not really recommended way to write the code
```bash
ruff check .
```

If you only want check certain file, you can do that by simply put the specific file name
```bash
ruff check your-file-name-path.py
```

If you want ruff to automatically fix that error types, you can also do this
```bash
ruff check . --fix
```
All of this can be found [here](https://docs.astral.sh/ruff/tutorial/), so feel free to play around with it.

## Possible Development
1. Currently, we are using Mediapipe to get the face mesh and other facial landmarks. To detect driver drowsiness, we rely on metrics like the Eye Aspect Ratio (EAR) and Mouth Aspect Ratio (MAR) for detecting eye closure and yawning. However, this approach is largely Rule-Based Detection and lacks the adaptability and robustness of more AI-driven methods. One possible improvement is to integrate <b>YOLO</b> (You Only Look Once), a fast and efficient object detection algorithm, to detect drowsiness-related features in real-time. For example, you can train a custom YOLO model to detect specific states such as: Closed Eyes, Yawning Mouth, and the Making Phone Call
2. Like I said, currently the Making Phone Call in my opinion is really ridicilous, as the state we can call them is when if the distance of the left or right wrist to the left or right ear is below the threshold, then that's 'Making a Phone Call'. But it's really ridicilious, as this can be false positive case if the driver just lift their hand really close to their ear.
3. Use the Hailo AI Kit software stack to increase the detection time by offloading the calculation to the AI Kit
4. Implement a Threaded Architecture for splitting the many feature calculation to increase the detection time by splitting the burden of the calculation. Say that when there are three detection feature, feature A, feature B, and feature C, rather running them as sequencial, we can separate their process in different thread to save more time.


## Authors
1. Muhammad Juniarto 
2. Batch 1 Members of CC Department


## Project Reference
1. https://www.hackster.io/AlbertaBeef/accelerating-the-mediapipe-models-on-raspberry-pi-5-ai-kit-1698fe
