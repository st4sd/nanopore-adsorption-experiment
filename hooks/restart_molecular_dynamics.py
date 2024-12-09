# SPDX-License-Identifier: Apache2.0
# © Copyright IBM Corp. 2023 All Rights Reserved

import os
import shutil


def Restart(workingDirectory, restarts, componentName, log, exitReason, exitCode):
    """
    This function is expected to examine the components workingDirectory, optionally make \
    modifications to it, and return a restart decision.

    Parameters
    ----------
    workingDirectory: str
        Directory containing simulation to be restarted
    restarts: int
        The number of times this function has been called for this component
    componentName: str
        The label the workflow engine uses to id this component
    log: logging.Logger
        A logger used to write output messages
    exitReason: str
        Defines why the program exited
    exitCode: int
        The exit-code returned by the program

    Returns
    -------
    string: One of the strings defined by experiment.codes.restartContexts that capture the hooks \
    decision
    """

    shutil.rmtree(os.path.join(workingDirectory, 'Restart'))
    shutil.rmtree(os.path.join(workingDirectory, 'Output'))
    shutil.rmtree(os.path.join(workingDirectory, 'CrashRestart'))
    shutil.rmtree(os.path.join(workingDirectory, 'MSDOrderN'))
    shutil.rmtree(os.path.join(workingDirectory, 'Movies'))
    shutil.rmtree(os.path.join(workingDirectory, 'VTK'))

    return 'RestartContextRestartPossible'
