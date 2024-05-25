### Method 3) Legacy method using a Python virtual environment

[!NOTE]
This is the legacy method of installing Home Assistant, and requires a moderate understanding of your underlying operating system and python.

With this method it is recommended you install on a Python virtual environment.
For this you will need `virtualenv`, install it using:
```bash
sudo apt install python3-virtualenv
```
Then create and activate the virtual environment:
```bash
virtualenv -p /usr/bin/python3 emhassenv
cd emhassenv
source bin/activate
```
Install using the distribution files:
```bash
python3 -m pip install emhass
```
Clone this repository to obtain the example configuration files.
We will suppose that this repository is cloned to:
```
/home/user/emhass
```
This will be the root path containing the yaml configuration files (`config_emhass.yaml` and `secrets_emhass.yaml`) and the different needed folders (a `data` folder to store the optimizations results and a `scripts` folder containing the bash scripts described further below).

To upgrade the installation in the future just use:
```bash
python3 -m pip install --upgrade emhass
```