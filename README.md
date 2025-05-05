# Drowsiness Detection
This is repo for holding the code for the drowsiness detection project on on Toyota Motor Indonesia at Capabilty Center Division Department. The drowsiness use Mediapipe pipeline framework to detect the pose estimation and act approtiately according to that

<p align="center">
  <img width="79%"src="docs/images/Drowsiness_Detection.gif">
</p>

## Project Tech Stack 
This project use several Tech Stack, but most of them is using Python. As you an see, this project is a Real-Time face recognition to detect a drowsiness of an user that was captured by the camera. If running on Windows, it will use the default webcam current OS have, or if in linux, it will always -- always be in mind will be run on Raspberry Pi, especially in Raspberry Pi 5 with Raspberry Pi Camera with the video stream source. The project tech stack is mostly divided into 3 main core idea, the computer vision, the model, and the backend.

Perhaps some of you will ask, why not just using OpenCV windows to see the result of the calculation? Well, I plan to run this on a headless GUI OS, so making it run using OpenCV windows will be quite useless (this is to save resources when running on Low-Spec hardware).

1. Mediapipe
2. OpenCV
3. FastAPI

### Model
The model we are using to detect the pose estimation is [Mediapipe.](https://github.com/google-ai-edge/mediapipe). It's easy to use, and cross-compatible and run pretty fast on x64 platfrom.

### Computer Vision
For the computer vision manipulation, we are using your old friend OpenCV. Really no question asked for this

### Backend
At first, I want to expose the API using C# ASP .NET platform. But it semes that will make more work, that's why I used [FastAPI](https://fastapi.tiangolo.com/) where it was already in the same environment as the Model and Computer Vision. But maybe some of you will ask who already familiar with Flask, why not Flask or any other stuff? Well it's not like I hate flask, but I was searching a framework that already have OpenAPI built into them and FastAPI already meet that requirements.


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

As this project is still under development, I can say that this structure can be contested to be more flexible, as I really don't have experience building in a Python environment, and I don't really find a good project in github that really adheres OOP in Python, this will do for now.

## Installing Environment 
I think that installing python packages in secluded environment was simple can be used using the Python own official virtual environment. To do this, first you must have to install python first. This app using this spesification

1. Python 3.11 version
2. Mediapipe 0.10.21 version

So for python, you can search for their installer [here](https://www.python.org/downloads/release/python-31112/) and install them. If you have installed them, we can start the virtual environment creation. Of course you can try to install another python version, but keep in mind, I made this project in 3.11 so it can be more stable rather the new python version. I will explain how you can set up the environment in both Windows and Linux for the Raspberry Pi, but keep in mind Windows version, this code probably will favor more on the Linux side, but it's a good idea to be able to run this on Windows aswell. So, before doing the environement set-up, please kindly clone this repo 

### Installing environment through Virtual Env (Windows)
First go do the work directory. 
```bash
cd drowsiness-detection
```

Then after that, we can create our virtual environment under `drowsiness-detection/venv` with the following command
```bash
python -m venv venv
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

### Installing Environment through Virtual Env (Linux)
For running this on Linux Raspberry Pi, there steps is similar when we set up on Windows. First go do the work directory after clone the repository. 
```bash
cd drowsiness-detection
```

Then, because we decided to make this project inside the Virtual Environment using the Python Virtual Environment, this is a crucial step so the venv can recognize our Pi Camera. This issue has been reported [here](https://forums.raspberrypi.com/viewtopic.php?t=361758). Conda also suffer the biggest from all of this than any other environment package. So, we gonna make this using a simple virtual environment. First make sure to install the package first from the apt package

```bash
sudo apt install -y python3-libcamera
```

Then create the virtual environment using system-site-packages tag

```bash
python3 -m venv --system-site-packages venv
```

The `--system-site-packages` is really important one

You will see now a folder named `venv` will be created in your work directory. Now that we have a virtual environment been created, we now need to activate it.

```bash
source venv\bin\activate
```

Before installing the packages, first we have to make sure, as this will allow us to install other packages in the virtual environment, while using the system versions of packages such as libcamera.

After that, we can install the Python bindings of the libcamera by this instruction.

```bash
sudo apt install -y libcamera-dev
pip install rpi-libcamera
```

The detailed instruction for this spesific step can be found [here](https://github.com/raspberrypi/pylibcamera).

After that, you can see the virtual environment has been activated by seeing the (venv) in your terminal. After you activate the virtual environment, you can add packages to it using `pip`. You can also create a description of your dependencies using `pip`. In this repo, I have made it the packages that required in order to run this app, so simply just install them with this following command

```bash
pip install -r requirements.txt
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
1. Batch 1 Members of CC Department
2. Muhammad Juniarto 


