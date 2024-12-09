# Run nanopore-adsorption-experiment using the Docker backend of ST4SD

## Prerequisites

1. A recent version of python 3 - [python 3.7+](https://www.python.org/downloads/)
2. The [docker](https://docs.docker.com/get-docker/) container runtime
3. The [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) command-line utility

## Instructions

You can try out the experiment on your laptop by:

1. creating a python virtual environment, activating it, and installing the python module `st4sd-runtime-core[deploy]`
2. cloning this repository
3. launching the experiment

For example:

```bash
#!/usr/bin/env sh

# Download virtual experiment
git clone https://github.com/st4sd/nanopore-adsorption-experiment.git
cd nanopore-adsorption-experiment

# Setup ST4SD runtime-core
python3 -m venv --copies venv
. venv/bin/activate
python3 -m pip install "st4sd-runtime-core[deploy]"

# Run Experiment
cat <<EOF >cif_files.dat
CoRE2019/GUJVOX_clean
EOF

numberOfNanopores=$(cat cif_files.dat | wc -l)

cat <<EOF >variables.yaml
global:
  numberOfNanopores: ${numberOfNanopores}
  raspa_memory: 2Gi
  externalTemperature_K: 298
  externalPressure_Pa: 1000,2000,5001,10000,20000,50000,100000
  gasComposition: '{"CO2":1.0}'
EOF

time elaunch.py --platform docker -i cif_files.dat -a variables.yaml \
    --manifest manifest.yaml conf/flowir_adsorption.yaml

# See outputs of experiment
output_dir=$(ls -td flowir_package*.instance | head -1)
ls -lth ${output_dir}
cat "${output_dir}/output/properties.csv"
```
