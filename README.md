# DSP-Intervention

A Humanitarian Military Intervention Analysis and Dashboard Project

### Run
Select environment, then run the following command from the project **root** directory:

```sh
$ python Dashboard/app.py
```

### Requirements
The dashboard is developed to run on the latest version of python (3.9 at time of writing). The dependencies include:

```
- dash
- jupyter
- matplotlib
- pandas
- scipy
- wbdata
```

A conda requirements file is included in the root dir. Creating the environment from the file is easily done by executing:

```sh
$ conda create -n <environment-name> --file dependencies.yml
```

Note that one of the dependencies, wbdata, is not available through conda. Install manually using:

```sh
$ pip3 install wbdata
```


