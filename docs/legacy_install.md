# Legacy Installation and Usage of EMHASS - Using a Python Virtual Environment

> [!NOTE]
> This is the legacy method of installing EMHASS, and requires an understanding of your underlying operating system's command line and Python 3.


## Installing using a Python virtual environment

1. With this method you install a Python virtual environment.
For this you will need `virtualenv`, install it using:
```bash
sudo apt install python3-virtualenv
```
2. Create and activate the virtual environment:
```bash
virtualenv -p /usr/bin/python3 emhassenv
cd emhassenv
source bin/activate
```
3. Install using the distribution files:
```bash
python3 -m pip install emhass
```
4. Clone this repository to obtain the example configuration files.
In this example the repository is cloned to:
```
/home/user/emhass
```
This will be the root path containing the required yaml configuration files (`config_emhass.yaml` and `secrets_emhass.yaml`) and the required folders (a `data` folder to store the optimizations results and a `scripts` folder containing the bash scripts described below).


## Upgrading a Python virtual environment
To upgrade EMHASS you can use:
```bash
python3 -m pip install --upgrade emhass
```

## Using a Python virtual environment

To run EMHASS, use the `emhass` command followed by the these arguments:
- `--action`: Set the desired action when running EMHASS, options are: `perfect-optim`, `dayahead-optim`, `naive-mpc-optim`, `publish-data`, `forecast-model-fit`, `forecast-model-predict` and `forecast-model-tune`.
- `--config`: Define the path to the config.yaml file (include the yaml filename).
- `--params`: Configuration parameters as JSON.
- `--runtimeparams`: Data passed at runtime. This can be used to pass your own forecast data to EMHASS.
- `--costfun`: Select the type of cost function [optional], options are: `cost`, `self-consumption`, `profit` (default).
- `--log2file`: Define if EMHASS should log to a file or not [optional], options are: `True` or `False` (default)
- `--debug`: Define if EMHASS should operate in debugging mode [optional], options are: `True` or `False` (default)
- `--version`: Provides the current version of EMHASS.

For example, the following line command can be used to perform a day-ahead optimization task, using the self-consumption cost function:
```bash
emhass --action 'dayahead-optim' --config '/home/user/emhass/config_emhass.yaml' --costfun 'self-consumption'
```
Before you being running any commands you will need to modify the `config_emhass.yaml` and `secrets_emhass.yaml` files. These files should be updated to reflect your own system, following the instructions in the [documentation](https://emhass.readthedocs.io/en/latest/config.html).