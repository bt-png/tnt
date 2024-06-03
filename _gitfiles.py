import streamlit as st
from github import Github
from github import Auth
from github import InputGitTreeElement


def connect() -> object:
    auth = Auth.Token(st.secrets['gittoken'])
    return Github(auth=auth)


def disconnect(_g):
    _g.close()


def repo(_g, name) -> object:
    return _g.get_user().get_repo(name)


def exists(_repo, _filename) -> bool:
    contents = _repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(_repo.get_contents(file_content.path))
        else:
            if file_content == _filename:
                return True
    return False


def update(repo, filename, message, content):
    contents = repo.get_contents(filename, ref="test")
    repo.delete_file(contents.path, "remove test", contents.sha, branch="test")
    push(repo, filename, message, content)


def push(_repo, _filename, _message, _content):
    #return_val = repo.create_file(path="current_input.csv", message="api commit", content=bit, branch="main")
    try:
        return_val = _repo.create_file(
            path=_filename,
            message=_message,
            content=_content,
            branch="main"
            )
        return True
    except Exception:
        False

    

def commit(filename, message, content) -> None:
    _g = connect()
    _repo = repo(_g, 'tnt')
    #content = bit = uploaded_file.getvalue()
    if exists(_repo, filename):
        success = update(_repo, filename, message, content)
    else:
        success = push(_repo, filename, message, content)
    disconnect(_g)
    st.write(success)


#stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

#for repo in g.get_user().get_repos():
#    st.write(repo.name)
    # repo name

#st.write(repo.name)
#commit_message = 'python commit'
#master_ref = repo.get_git_ref('heads/main')
#master_sha = master_ref.object.sha
#base_tree = repo.get_git_tree(master_sha)

#element_list = list()
#element = (InputGitTreeElement('Current_input.csv', '100644', 'blob', uploaded_file))
#element_list.append(element)

#tree = repo.create_git_tree(element_list, base_tree)
#parent = repo.get_git_commit(master_sha)
#commit = repo.create_git_commit(commit_message, tree, [parent])
#master_ref.edit(commit.sha)
    
