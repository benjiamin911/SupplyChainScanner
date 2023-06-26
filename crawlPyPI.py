import gitlab
import json
import requests
import warnings
import argparse
from pkg_resources import parse_requirements
from packaging import version

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('-t','--token',help='Gitlab Access token')
parser.add_argument('-u','--url',help='Internal Gitlab URL')

args = parser.parse_args()
# GitLab access token
GITLAB_ACCESS_TOKEN = args.token

# PyPI URL
PYPI_URL = 'https://pypi.org/pypi/{}/json'

# Create a GitLab API client
gl = gitlab.Gitlab(args.url, private_token=GITLAB_ACCESS_TOKEN)

organizations = gl.groups.list(all=True)
for organization in organizations:
    print("organization:",organization.name)

    try:
        organization = gl.groups.get(organization.name)
    except gitlab.exceptions.GitlabGetError:
        continue

    # Get all projects in the organization
    projects = organization.projects.list(all=True)

    # Iterate over each project
    for project in projects:
        # Get the default branch of the project
        default_branch = project.default_branch
        #print(project)
        # Retrieve the repository files
        try:
            response = gl.projects.get(project.id).repository_tree(ref=default_branch, recursive=True)
            repository_files = response
        except gitlab.exceptions.GitlabGetError:
            print(f"Error retrieving repository tree for project: {project.name}")
            continue

        # Check if the project has any .py files in the repository
        has_python_files = any(file.get('name', '').endswith('.py') for file in repository_files)
        if not has_python_files:
            continue 
        # Check if requirements.txt exists in the repository files
        #print(repository_files)

        requirements_file=None
        for file in repository_files:
            if 'requirements.txt' in file.get('name'):
                requirements_file=file
                print(f"requirements.txt found for project: {project.name}")

        if requirements_file:
            # Retrieve the raw content of requirements.txt
            # Get the raw content of requirements.txt
            try:
                file_content = gl.projects.get(project.id).files.get(file_path=requirements_file['path'], ref=default_branch).decode()
            except gitlab.exceptions.GitlabGetError:
                print(f"Error retrieving requirements.txt for project: {project.name}")
                continue

            #print("requirements.txt Contents:\n",file_content.decode())
            #print(file_content.decode)
            #requirements = file_content.decode().strip().split('\n')
            try:
                requirements = list(parse_requirements(file_content.decode()))
            except:
                continue

            # Check each requirement against PyPI
            for requirement in requirements:
                package_name = requirement.name
                package_version = requirement.specifier

                response = requests.get(PYPI_URL.format(package_name))
                if response.status_code == 404:
                    print(f"Package not found on PyPI: NAME: {package_name}, VERSION:{package_version} (required by {project.name})")
                else:
                    data = response.json()
                    versions = data.get('releases').keys()

                    if package_version not in versions:
                        print(f"Version mismatch for package: {package_name} (required by {project.name})")
        else:
            print(f"requirements.txt not found for project: {project.name}")