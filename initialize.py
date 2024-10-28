from project import Project
from contract import contracts
from builder_exact import builder_enpv
from owner_exact import owner_enpv


def set_owner_threshold(project: Project, distribution):
    if contracts:
        project.owner_threshold = owner_enpv(
            project, contracts[0], distribution
        ) - builder_enpv(project, contracts[0], distribution)
    else:
        raise ValueError("No contracts have been created.")
