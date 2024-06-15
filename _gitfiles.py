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


def update(_repo, _filename, _message, _content):
    #st.write('File Exists')
    contents = _repo.get_contents(_filename, ref="main")
    try:
        _repo.delete_file(contents.path, "remove api", contents.sha, branch="main")
        #_repo.update_file(contents.path, _message, _content, contents.sha, branch="test")
        return push(_repo, _filename, _message, _content)
    except Exception:
        return False
    return None
    #success = _repo.update_file(contents.path, _message, _content, contents.sha, branch="test")
    #success = push(_repo, _filename, _message, _content)
    return success


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
    #st.write('Trying to connect to GitHub')
    _g = connect()
    _repo = repo(_g, 'tnt')
    try:
        success = update(_repo, filename, message, content)
    except Exception:
        success = push(_repo, filename, message, content)
    #content = bit = uploaded_file.getvalue()
    #if exists(_repo, filename):
    #    st.write('File Exists')
    #    st.stop()
    #    success = update(_repo, filename, message, content)
    #else:
    #    st.write('File doesnt exist')
    #    success = push(_repo, filename, message, content)
    disconnect(_g)
    if success:
        st.success('Saved')
    else:
        st.warning('Something went wrong')


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
    
