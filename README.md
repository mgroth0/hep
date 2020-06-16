Installation
-

1. `git clone --recurse-submodules https://github.com/mgroth0/hep`

1. install [miniconda](https://docs.conda.io/en/latest/miniconda.html)

2. `conda update conda`

3. `conda create --name hep --file requirements.txt`

<!--4. ; pip install -r reqs_pip.txt-->
-- When updating, use `conda install --file requirements.txt`
<!--; pip install -r reqs_pip.txt-->

5. `conda activate hep`

Basic Usage
-

- `./hep`

Configuration
-

(todo)

Development
- 

- use `conda list -e > requirements.txt; sed -i '' '/pypi/d' requirements.txt` to store dependencies.
<!--- There are also a couple of pip dependencies manually written in reqs_pip.txt, since these cannot be found through conda-->

Credits
-

- Isaac, Brain Modulation Lab
