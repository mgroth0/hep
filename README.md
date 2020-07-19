Installation
-
1. git clone --recurse-submodules https://github.com/mgroth0/hep
1. install [miniconda](https://docs.conda.io/en/latest/miniconda.html)
1. `conda update conda`
1. `conda create --name hep --file requirements.txt` (requirements.txt is currently not working, TODO)
1. might need to separately `conda install -c mgroth0 mlib-mgroth0`-- When updating, use `conda install --file requirements.txt;`
1. `conda activate hep`


Usage
-
- ./hep
- 


Configuration
-


Testing
-
todo

Development
-
- TODO: have separate development and user modes. Developer mode has PYTHONPATH link to mlib and instructions for resolving and developing in ide in parallel. User mode has mlib as normal dependency. might need to use `conda uninstall mlib-mgroth0 --force`. Also in these public readmes or reqs.txt I have to require a specific mlib version
- ./hep build


Credits
-
Isaac, Brain Modulation Lab