# DSP-Intervention

A Humanitarian Military Intervention Analysis and Dashboard Project. 

### Run application
Select environment, then run the following command from the project **root** directory:

```sh
$ python Dashboard/app.py
```

### Requirements
The dashboard is developed to run on the latest version of python (3.9 at time of writing). To install the required dependencies, there's two options.

#### Manual installation
Manually install the following dependencies:

```
- dash
- jupyter
- matplotlib
- pandas
- scipy
- wbdata
```

#### Installation via conda requirements yml
A conda requirements file is included in the root dir. Creating the environment from the file is easily done by executing:
```sh
$ conda create -n <environment-name> --file dependencies.yml
```

Note that one of the dependencies, wbdata, is not available through conda. Install manually using:

```sh
$ pip3 install wbdata
```


