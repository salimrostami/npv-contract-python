from project import Project
from contract import contracts
from builder_enpv import builder_enpv
from owner_enpv import owner_enpv


def set_owner_threshold(project: Project, distribution):
    if contracts:
        project.owner_threshold = owner_enpv(
            project, contracts[0], distribution
        ) - builder_enpv(project, contracts[0], distribution)
    else:
        raise ValueError("No contracts have been created.")
