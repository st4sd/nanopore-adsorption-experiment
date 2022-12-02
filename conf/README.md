# Usage of the `MakeGrid` component

The user is responsible for deciding whether the `MonteCarlo` component will be preceded by the `MakeGrid` component.
It may or may not be advantageous to use this feature, so use with caution.

## Monte Carlo simulation with energy grids

```YAML
  - stage: 1
    name: MakeGrid
    command:
      environment: raspa
      executable: make_grid.sh
      arguments: -c '%(gasComposition)s' -n stage0.GetNanoporeName:output_P1_EQeq -o .
    references:
      - stage0.GetNanoporeName:output
      - stage0.ChargeEquilibration/eqeq_cif.tgz:copy
    resourceManager:
      kubernetes:
        image: quay.io/st4sd/community-applications/raspa-source-mdlab:latest
        cpuUnitsPerCore: 1
    resourceRequest:
      memory: '%(raspa_memory)s'
    workflowAttributes:
      shutdownOn:
      - Killed
      - KnownIssue

  - stage: 2
    name: MonteCarlo
    command:
      environment: raspa
      executable: monte_carlo.sh
      arguments: -g -n stage0.GetNanoporeName:output_P1_EQeq -p '%(externalPressure_Pa)s' -t '%(externalTemperature_K)s' -c '%(gasComposition)s' -o .
    references:
      - stage0.GetNanoporeName:output
      - stage0.ChargeEquilibration/eqeq_cif.tgz:copy
      - stage1.MakeGrid/grids.tgz:copy
    resourceManager:
      kubernetes:
        image: quay.io/st4sd/community-applications/raspa-source-mdlab:latest
        cpuUnitsPerCore: 1
    resourceRequest:
      memory: '%(raspa_memory)s'
    workflowAttributes:
      shutdownOn:
      - Killed
      - KnownIssue
```

## Monte Carlo simulations without energy grids

```YAML
  - stage: 2
    name: MonteCarlo
    command:
      environment: raspa
      executable: monte_carlo.sh
      arguments: -n stage0.GetNanoporeName:output_P1_EQeq -p '%(externalPressure_Pa)s' -t '%(externalTemperature_K)s' -c '%(gasComposition)s' -o .
    references:
      - stage0.GetNanoporeName:output
      - stage0.ChargeEquilibration/eqeq_cif.tgz:copy
    resourceManager:
      kubernetes:
        image: quay.io/st4sd/community-applications/raspa-source-mdlab:latest
        cpuUnitsPerCore: 1
    resourceRequest:
      memory: '%(raspa_memory)s'
    workflowAttributes:
      shutdownOn:
      - Killed
      - KnownIssue
```
