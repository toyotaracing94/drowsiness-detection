## How to setup the Service Management on Linux using Systemd

In this documentation, we will use Systemd to manage and auto-run our service, in this case the drowsiness detection python service automatically to be run during the startup. But first, to use systemd, we must ensure that the program we want to start has an associated service unit file. In this case, I have build the associated service unit file to auto-run the drowsiness service.

First make sure that the code is located correctly on the path that we set on the `drowsines.service`, in this case I decided to put them on the `/opt` folder.

After that, make sure that the script that will be run by the unit service can be accessed as a bash program by this command

```bash
chmod +x scripts/start.sh
```

After making sure the script to run our program is in executable format, we can start register our service. This is achieved by storing our unit service file in the `/etc/systemd/system`

```bash
cd drowsiness-detection
sudo cp .services/drowsiness.service /etc/systemd/system
```

After we move our custom unit service file, we need to reload the systemd manager configuration
```bash
sudo systemctl daemon-reload
```

After that we can try to start the service by simply this
```bash
sudo systemctl start drowsiness.service
```

If nothing goes wrong, you can see wether the service is successfully run by simply check like this
```bash
sudo systemctl status drowsiness.service
```

You will see something like this for successfull service launch
```prolog
● drowsiness.service - Drowsiness Detection FastAPI Service
     Loaded: loaded (/etc/systemd/system/drowsiness.service; enabled; preset: enabled)
     Active: active (running) since Wed 2025-06-11 13:59:16 WIB; 40min ago
   Main PID: 717 (uvicorn)
      Tasks: 36 (limit: 9585)
        CPU: 44.620s
     CGroup: /system.slice/drowsiness.service
             └─717 /opt/drowsiness-detection/venv/bin/python3 /opt/drowsiness-detection/venv/bin/uvicorn main:app --host 0.0.0.0

Jun 11 13:59:22 drivesafepi start.sh[717]: INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Jun 11 13:59:22 drivesafepi start.sh[717]: Error in cpuinfo: prctl(PR_SVE_GET_VL) failed
Jun 11 13:59:22 drivesafepi start.sh[717]: INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
Jun 11 13:59:22 drivesafepi start.sh[717]: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
```

Now to enable them to start at the startup, we can set them again using systemd
```bash
sudo systemctl enable drowsiness.service
```

You can see this is working as above where the left side of preset is enable rather disable. See [here](https://access.redhat.com/sites/default/files/attachments/12052018_systemd_6.pdf) for more details of the command using systemd or this [guide](https://www.simplified.guide/linux/automatically-run-program-on-startup) to start service using other than systemd.