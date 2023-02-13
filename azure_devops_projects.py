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


# config.load_config()


def az_pipelines_mutate():
    update_type = "pool"
    update_key = "vmImage"
    update_value = "ubuntu-20.03"

    filepath = "azure-pipelines.yml"
    token = ""
    git = Github(token)  # authenticating with token
    repo = git.get_repo("VinayTalla20/yaml")  # provide the repository name with username

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
            "vinaytalla20@gmail.com"
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


# az_pipelines_mutate()


def az_pipelines_mutate_test(organization, update_type, update_value, update_key, id, projectname):
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
                "vinaytalla20@gmail.com"
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

        organization_url = f"https://dev.azure.com/{organization}/"
        credentials = BasicAuthentication('', personal_access_token)
        pipelines_id = []
        pipeline_client = PipelinesClient(base_url=organization_url, creds=credentials)
        pipeline_data = pipeline_client.list_pipelines(project=projectname)
        # pipeline_info = pipeline_client.get_pipeline(pipeline_id=id, project=projectname)
        for pipeline in pipeline_data:
            print(pipeline)
            id = pipeline.id
            pipelines_id.append(id)
            print(pipelines_id)
        print(pipelines_id)

        x = 0
        while x < len(pipelines_id):
            pipeline_info = pipeline_client.get_pipeline(pipeline_id=pipelines_id[i], project=projectname)
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
                    "vinaytalla20@gmail.com"
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


az_pipelines_mutate_test(organization="vinaytalla20", update_type="pool", update_key="vmImage",
                         update_value="windows-2023", projectname="SampleProjects", id=1)