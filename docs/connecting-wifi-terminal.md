## Connect Raspberry Pi to Wi-Fi Using `nmcli`

This guide shows how to connect your Raspberry Pi to a Wi-Fi network from the terminal using `nmcli`, the command-line interface for NetworkManager. It's ideal for headless setups or minimal installations.

## Connect to Wi-Fi
We can see list Available Networks and search our network by this one

```bash
nmcli device wifi list
```

This will show a list of nearby Wi-Fi networks, like this
```prolog
SSID             MODE   CHAN  RATE       SIGNAL  BARS  SECURITY
MyWiFiNetwork    Infra  6     54 Mbit/s  70      ▂▄▆_   WPA2
OpenNetwork      Infra  1     54 Mbit/s  60      ▂▄▆_   --
```

And let's say that I want to connect to this `MyWiFiNetwork`, we can use again nmcli to connect to that using this command
```bash
nmcli device wifi connect "MyWiFiNetwork" password "YourWiFiPassword"
```

If the connection is successfull, you can check wether it's connected or not like this or simply just try ping google.com
```bash
nmcli connection show --active
```

You should see output similar to:
```prolog
NAME           UUID                                  TYPE      DEVICE
MyWiFiNetwork  12345678-1234-5678-1234-123456789abc  wifi      wlan0
```

With this, you have successfully connect to the WiFi you want. Often, Wi-Fi connections managed by NetworkManager usually reconnect automatically, where you can see the list of network you connected on the `wpa_suppliant.conf`, but you can force this by using this command instead above
```bash
nmcli connection modify "MyWiFiNetwork" connection.autoconnect yes
```
