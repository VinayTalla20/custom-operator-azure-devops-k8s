import kubernetes
from github import Github, InputGitAuthor
from kubernetes import config, client
import os
import yaml
import kopf
import json
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.pipelines.pipelines_client import PipelinesClient

config.load_config()

global resource_name
global resource_kind

pipeline_name = []
pipeline_id = []
project_name = []
project_visibility = []
project_created = []

personal_access_token = ""

def az_devops_projects(organization):
    organization_url = f"https://dev.azure.com/{organization}/"
    credentials = BasicAuthentication('', personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)

    core_client = connection.clients.get_core_client()

    get_projects_response = core_client.get_projects()

    for projects in get_projects_response.value:
        global project_name
        global project_visibility
        global project_created
        project = projects.name
        project_name.append(project)
        project_v = projects.visibility
        project_visibility.append(project_v)
        project_c = projects.last_update_time
        project_created.append(project_c)

def az_devops_pipelines(organization, projectname):
    organization_url = f"https://dev.azure.com/{organization}/"
    credentials = BasicAuthentication('', personal_access_token)
    pipeline_client = PipelinesClient(base_url=organization_url, creds=credentials)

    pipeline_data = pipeline_client.list_pipelines(project=projectname)

    for pipeline in pipeline_data:
        global pipeline_name
        global pipeline_id
        id = pipeline.id
        name = pipeline.name
        pipeline_name.append(name)
        pipeline_id.append(id)

def az_pipelines_mutate(organization, update_type, update_value, update_key, id, projectname):
    if id != 0:
        print("Modifying specific pipeline")
        organization_url = f"https://dev.azure.com/{organization}/"
        credentials = BasicAuthentication('', personal_access_token)
        pipeline_client = PipelinesClient(base_url=organization_url, creds=credentials)
        pipeline_info = pipeline_client.get_pipeline(pipeline_id=id, project=projectname)
        file_path = pipeline_info.configuration.additional_properties["path"]
        repo_name = pipeline_info.configuration.additional_properties["repository"]["fullName"]

        filepath = file_path
        token = ""
        git = Github(token)  # authenticating with token
        repo = git.get_repo(f"{repo_name}")  # provide the repository name with username

        file_data = repo.get_contents(path=filepath,
                                      ref="master")  # Getting file from the specific branch using the path or file name

        yaml_data = yaml.load(file_data.decoded_content.decode("utf-8"), Loader=yaml.SafeLoader)

        if update_type == "repositories":
            yaml_data["resources"][update_type][0][update_key] = update_value
            yaml_data = yaml.dump(yaml_data, sort_keys=False)

        elif update_type == "variables":

            yaml_values = yaml_data[update_type]

            i = 0
            while i < len(yaml_values):

                if yaml_values[i + 1]["name"] == update_key:
                    yaml_values[i + 1]["value"] = update_value
                    break
                i += 1

            yaml_values = yaml.dump(yaml_data, sort_keys=False)
            yaml_data = yaml_values

        elif update_type == "pool":
            print(yaml_data)
            yaml_data[update_type][update_key] = update_value
            yaml_data = yaml.dump(yaml_data, sort_keys=False)
            print(yaml_data)

        def push(path, message, content, branch, update=False):
            author = InputGitAuthor(
                "VinayTalla20",
                "@gmail.com"
            )
            source = repo.get_branch("master")
            repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source.commit.sha)  # create new branch for master
            if update:
                contents = repo.get_contents(path, ref=branch)
                repo.update_file(contents.path, message, content, contents.sha, branch=branch,
                                 author=author)  # add, commit and push branch
            else:
                repo.create_file(path, message, content, branch=branch, author=author)

        push(filepath, "Updating azure-pipeline yaml", yaml_data, f"{update_type}-{update_value}", update=True)

    else:
        print("modifying all pipelines")
        organization_url = f"https://dev.azure.com/{organization}/"
        credentials = BasicAuthentication('', personal_access_token)
        pipelines_id = []
        pipeline_client = PipelinesClient(base_url=organization_url, creds=credentials)
        pipeline_data = pipeline_client.list_pipelines(project=projectname)
        for pipeline in pipeline_data:
            print(pipeline)
            id = pipeline.id
            pipelines_id.append(id)
            print(pipelines_id)
        print(pipelines_id)

        x = 0
        while x < len(pipelines_id):
            pipeline_info = pipeline_client.get_pipeline(pipeline_id=pipelines_id[x], project=projectname)
            file_path = pipeline_info.configuration.additional_properties["path"]
            repo_name = pipeline_info.configuration.additional_properties["repository"]["fullName"]
            filepath = file_path
            token = ""
            git = Github(token)  # authenticating with token
            repo = git.get_repo(f"{repo_name}")  # provide the repository name with username

            file_data = repo.get_contents(path=filepath,
                                          ref="master")  # Getting file from the specific branch using the path or file name

            yaml_data = yaml.load(file_data.decoded_content.decode("utf-8"), Loader=yaml.SafeLoader)

            if update_type == "repositories":
                yaml_data["resources"][update_type][0][update_key] = update_value
                yaml_data = yaml.dump(yaml_data, sort_keys=False)

            elif update_type == "variables":

                yaml_values = yaml_data[update_type]

                i = 0
                while i < len(yaml_values):

                    if yaml_values[i + 1]["name"] == update_key:
                        yaml_values[i + 1]["value"] = update_value
                        break
                    i += 1

                yaml_values = yaml.dump(yaml_data, sort_keys=False)
                yaml_data = yaml_values

            elif update_type == "pool":
                print(yaml_data)
                yaml_data[update_type][update_key] = update_value
                yaml_data = yaml.dump(yaml_data, sort_keys=False)
                print(yaml_data)

            def push(path, message, content, branch, update=False):
                author = InputGitAuthor(
                    "VinayTalla20",
                    "@gmail.com"
                )
                source = repo.get_branch("master")
                repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source.commit.sha)  # create new branch for master
                if update:
                    contents = repo.get_contents(path, ref=branch)
                    repo.update_file(contents.path, message, content, contents.sha, branch=branch,
                                     author=author)  # add, commit and push branch
                else:
                    repo.create_file(path, message, content, branch=branch, author=author)

            push(filepath, "Updating azure-pipeline yaml", yaml_data, f"{update_type}-{update_value}-{x}", update=True)
            x += 1

@kopf.on.create('projects')
def crd_create(spec, **kwargs):
    resource_name = kwargs['body']['metadata']['name']
    print("Invoking organization name")
    organization = kwargs['body']['spec']['organizationName']

    az_devops_projects(organization)
    manifest_projects = yaml.safe_load(f"""
                                apiVersion: devops.azure.com/v1alpha1
                                kind: Project
                                metadata: 
                                  name: {resource_name}
                                spec:
                                  organizationName: {organization}
                                  projects: {len(project_name)}
                                          """)

    patch_parent = kubernetes.client.CustomObjectsApi()
    patch_resource_parent = patch_parent.patch_cluster_custom_object(group="devops.azure.com", name=resource_name,
                                                                     version="v1alpha1", plural="projects",
                                                                     body=manifest_projects)
    print(patch_resource_parent)

    i = 0
    while i < len(project_name):
        manifest_projectlist = yaml.safe_load(f"""
                            apiVersion: devops.azure.com/v1alpha1
                            kind: ListProject
                            metadata: 
                              name: {resource_name}-{i}
                            spec:
                              organizationName: {organization}
                              projectName: {project_name[i]}
                              projectVisibility: {project_visibility[i]}
                              projectCreated: {project_created[i]}
                                      """)
        i += 1
        print(manifest_projectlist)
        crd_create = kubernetes.client.CustomObjectsApi()
        resource_patch = crd_create.create_cluster_custom_object(group="devops.azure.com",
                                                                 version="v1alpha1", plural="listprojects",
                                                                 body=manifest_projectlist)
        print("Successfully patched Resources with required fields")

@kopf.on.create('pipelines')
def crd_pipeline_create(spec, **kwargs):
    resource_name = kwargs['body']['metadata']['name']
    projectname = kwargs['body']['spec']['projectName']
    organization = kwargs['body']['spec']['organizationName']

    az_devops_pipelines(organization, projectname)
    i = 0
    while i < len(pipeline_name):
        manifest_pipelines = yaml.safe_load(f"""
                                    apiVersion: devops.azure.com/v1alpha1
                                    kind: ListPipeline
                                    metadata: 
                                      name: {resource_name}-{i}
                                    spec:
                                      organizationName: {organization}
                                      projectName: {projectname}
                                      pipelineName: {pipeline_name[i]}
                                      pipelineId: {pipeline_id[i]}
                                              """)
        i += 1
        create_child = kubernetes.client.CustomObjectsApi()
        create_resource_child = create_child.create_cluster_custom_object(group="devops.azure.com", version="v1alpha1",
                                                                          plural="listpipelines",
                                                                          body=manifest_pipelines)
        print(create_resource_child)

@kopf.on.create('mutatepipelines')
def mutator_pipeline(spec, **kwargs):
    update_type = kwargs['body']['spec']['updateType']
    update_key = kwargs['body']['spec']['updateKey']
    update_value = kwargs['body']['spec']['updateValue']
    organization = kwargs['body']['spec']['organizationName']
    id = kwargs['body']['spec']['pipelineId']
    projectname = kwargs['body']['spec']['projectName']

    az_pipelines_mutate(organization, update_type, update_value, update_key, id, projectname)