## Conda basics

* Verify conda is installed, check version number

`conda info`

* Update conda to the current version

`conda update conda`

* Install a package included in Anaconda

`conda install PACKAGENAME`

* Update any installed program

`conda update PACKAGENAME`

* Command line help

`COMMANDNAME --help`
`conda install --help`

## Using environments
* Create a new environment named py35, install Python 3.5

`conda create --name py35 python=3.5`

* Get a list of all my environments, active environment is shown with *

`conda env list`

* Make exact copy of an environment

`conda create --clone py35 --name py35-2`

* List all packages and versions installed in active environment

`conda list`

* List the history of each change to the current environment

`conda list --revisions`

* Restore environment to a previous revision

`conda install --revision 2`

* Save environment to a text file

`conda list > requirements.txt`

`conda list --explicit > bio-env.txt`

* Delete an environment and everything in it

`conda env remove --name bio-env`

* Deactivate the current environment

`source deactivate`

* Create environment from a text file

`conda env create --file bio-env.txt`

* Stack commands: create a new environment, name it bio-env and install the biopython package

`conda create --name bio-env biopython`

## Finding conda packages
* Use conda to search for a package

`conda search PACKAGENAME`

* See list of all packages in Anaconda
`https://docs.anaconda.com/anaconda/packages/pkg-docs`

## Installing and updating packages
* Install a new package (Jupyter Notebook) in the active environment

`conda install jupyter`

* Run an installed package (Jupyter Notebook)
`jupyter-notebook`

* Install a new package (toolz) in a different environment (bio-env)
`conda install --name bio-env toolz`

* Update a package in the current environment
`conda update scikit-learn`

* Install a package (boltons) from a specific channel (conda-forge)

`conda install --channel conda-forge boltons`

* Install a package directly from PyPI into the current active pip install boltons environment using pip

`pip install boltons`

* Remove one or more packages (toolz, boltons) from a specific environment (bio-env)

`conda remove --name bio-env toolz boltons`

* Clean up unused packages

`conda clean -t`

## Managing multiple versions of Python
* Install different version of Python in a new environment named py34
`conda create --name py34 python=3.4`

* Switch to the new environment that has a different version of Python

`source activate py34`

* Show the locations of all versions of Python that are currently in the path
NOTE: The first version of Python in the list will be executed.

`which -a python`

* Show version information for the current active Python

`python --version`
