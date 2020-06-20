Installation
-

1. `git clone --recurse-submodules https://github.com/mgroth0/hep`

2. install [miniconda](https://docs.conda.io/en/latest/miniconda.html)

3. `conda update conda`

4. `conda create --name hep --file requirements.txt`
-- When updating, use `conda install --file requirements.txt;pip install -r reqs_pip.txt`

5. `conda activate hep`
6. `pip install -r reqs_pip.txt`

Basic Usage
-

- `./hep`

Configuration
-

(todo)

Development
- 

- use `conda list -e > requirements.txt; sed -i '' '/pypi/d' requirements.txt` to store dependencies.
There are also a couple of pip dependencies manually written in reqs_pip.txt, since these cannot be found through conda

Credits
-

- Isaac, Brain Modulation Lab
