import gitlab
import json
import requests
import argparse
import warnings
from pkg_resources import parse_requirements
from packaging import version

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('-t','--token',help='Gitlab Access token')
parser.add_argument('-u','--url',help='Internal Gitlab URL')

args = parser.parse_args()
# GitLab access token
GITLAB_ACCESS_TOKEN = args.token

# NPM URL
NPM_URL = 'https://npmjs.com/package/{}'

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

        # Check if the project has any .js files in the repository
        has_js_files = any(file.get('name', '')== 'package.json' for file in repository_files)
        if not has_js_files:
            continue 
            
        # Check if package-lock.json exists in the repository files
        has_package_lock = any(file.get('name', '') == 'package-lock.json' for file in repository_files)
        if not has_package_lock:
            # Get the raw content of package.json
            try:
                package_json_file = next(file for file in repository_files if file.get('name') == 'package.json')
                file_content = gl.projects.get(project.id).files.get(file_path=package_json_file['path'], ref=default_branch).decode()
            except (StopIteration, gitlab.exceptions.GitlabGetError):
                print(f"Error retrieving package.json for project: {project.name}")
                continue

            # Parse the package.json content
            try:
                dependencies = {}
                json_fileContent = json.loads(file_content)
                for key,value in json_fileContent.items():
                    if key in ['dependencies', 'devDependencies', 'peerDependencies', 'bundledDependencies', 'optionalDependencies']:
                        dependencies.update(value)

                json.loads(file_content)['dependencies']
               # print(dependencies)
            except KeyError:
                print(f"No dependencies found in package.json for project: {project.name}")
                continue

            # Check each dependency against NPM
            for dependency, version in dependencies.items():
                #print(NPM_URL.format(dependency))
                response = requests.get(NPM_URL.format(dependency))
                #print(response.history)

                for r in response.history:
                    if r.status_code == 302:
                        print(f"Package not found on NPM: {dependency} (required by {project.name})")
                        break

        else:
            print(f"package-lock.json found for project: {project.name}. Skipping dependency check.")