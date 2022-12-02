# Nanopore Adsorption Experiment

## Launching the virtual experiment

First you need to import the virtual experiment in your ST4SD registry [from the global ST4SD registry](https://pages.github.com/st4sd/overview/using-the-virtual-experiments-registry-ui). You will then be able to start the parameterised package `nanopore-adsorption-experiment` in your private ST4SD registry (see [example notebook](nanopore-adsorption-experiment.ipynb)).

## Using custom database of CIF files

You may download the CIF files of your choosing to a PVC inside your OpenShift cluster (below we use the name `nanopore-database-pvc`), mount it as a volume and ask the virtual experiment instance to use the contents of the PVC as the contents of the `nanopore-database` application-dependency. You will also need to remove the line related to `nanopore-database` from the `manifest.yaml` to enable the use of the PVC.

```Python
file_names = [""]
payload = {
  "volumes": [{
        "type": {"persistentVolumeClaim": "nanopore-database-pvc"},
        "applicationDependency": "nanopore-database"
    }],
  # other fields
}
rest_uid = api.api_experiment_start("nanopore-adsorption-experiment", payload)
```

**Note**: The [example notebook](nanopore-adsorption-experiment.ipynb) shows a full example.
