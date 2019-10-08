# Configuring git
* general settings (stored in $root/.git/.gitconfig)
```
git config --global user.name "Nicole Eichert"
git config --global user.email "nicole.eichert@psy.ox.ac.uk"
git config --global core.editor "atom -wl1"
git config --global color.ui true
```
* git aliases (example to type: git st)
```
git config --global alias.st "status"
```
* show which aliases I have defined
```
git config --get-regexp alias
```
* remove git alias
```
git config --global --unset alias.st
```
# Auto-completion and branch display on command line
```
cd ~
curl -OL https://github.com/git/git/raw/master/contrib/completion/git-completion.bash
curl -OL https://github.com/git/git/raw/master/contrib/completion/git-prompt.sh
mv ~/git-completion.bash ~/.git-completion.bash
mv ~/git-prompt.sh ~/.git-prompt.sh
```
* edit ~/.bash_profile
```
if [ -f ~/.git-completion.bash ]; then
  source ~/.git-completion.bash
fi
if [ -f ~/.git-prompt.sh ]; then
  source ~/.git-prompt.sh
fi
export PS1='\W$(__git_ps1 "(%s)") $ '
```

# Basic git commands
* using git help
```
git help
git help <command>
```
* initialize a git repository
```
cd $root
git init
```
* show staging environment and changes in working directory
```
git status
```
* show only changes in tracked files
```
git status -uno
```
* add a new file to tracking (and to staging immediately)
```
git add <new_file>
```
* add change in file to staging environment
```
git add <changed_file>
```
* add all changes (and removes) to staging environment
```
git add .
```
* remove file and add deletion to staging environment
```
git rm <file>
```
* move file
```
git mv <path/file> <new_path/file>
```
* rename file
```
git mv <filename> <new_filename>
```
* commit change to local repository
```
git commit -m "commit message"
```
* amend last commit with additional change in <file>
```
git add <file>
git commit --amend -m "commit message"
```
* change commit message
```
git commit --amend -m "new message"
```

# View commit log
* SHA-1 algorithm creates checksums (40-character hexadecimal string)
* default view:
```
git log
```
* short log info for the last 5 logs
```
git log --oneline -5
```
* search log for keyword in commit message
```
git log --grep="keyword"
```
* view log for branch (master, origin/master, HEAD, etc)
```
git log <branch>
```
* show the changes associated with a previous commit
```
git show <SHA>
git show HEAD
```
* show visualization of branch merges in log
```
git log --graph
```

# View differences
* show changes between working directory and the current master (where HEAD is pointing to)
```
# -HEAD +WD
git diff
git diff <file>
```
* show summary info on the changes
```
git diff --stat --summary
```
* show changes between staged environment and local repository
```
git diff --staged
```
* changes between specific commit and working directory
```
git diff <SHA>
```
* changes between 2 commits
```
git diff <SHA1>..<SHA2>
```
* changes between 2 branches
```
git diff master..new_branch
```
* changes between WD and local repository
```
git diff origin/master <file>
```

# Undoing changes
* if file modified and not staged, revert WD to local repository.  
(Note: use '--' to make clear that file and not branch is checked out)
```
git checkout -- <file>
```
* unstage changes, but keep change in WD
```
git reset HEAD <file>
```

* retrive earlier version of file.  
(i.e. get from local directory into staging environment)
```
git checkout 1x2c3c4v5b -- <file>
```
* commit to master
```
git commit -m "reverted to version from 1x2c3c4v5b"
```
* or unstage file and revert to version of local repository
```
git reset HEAD <file>
git checkout -- <file>
```
* do revert in one step. If complicated changes works like a merge
```
git revert <SHA>
```

# HEAD
* general
** tip of the current branch
** where is head pointing to is stored in
```
$root/.git/HEAD/
```
** HEAD is pointing to a commit stored in
$root/.git/refs/heads/master

* move HEAD
** only move HEAD, don't change WD or SD. Very similar to checkout, but not when on branch
```
git reset --soft
```
** move HEAD and change SD to local directory, but not WD
```
git reset --mixed
```
** move HEAD, change WD and SD: all changes that came after are lost, like travel back in time
```
git reset --hard
```

# Ignoring files
* create text file and edit
```
touch $root/.gitignore
atom $root/.gitignore
```
* globally ignore in every repository
```
git config --global core.excludesfile $root/.gitignore_global
```
* untrack file, but keep in WD and LD (will be deleted in RD)
```
git rm --cached <file>
```
* stop syncing file, but keep in WD and LD and RD
```
git update-index --assume-unchanged myfile
```
* untrack the whole content of a folder , but keep in WD and LD
```
git rm -r --cached <folderwithfiles>/
```
* make sure an empty folder is not ignored
```
touch $root/folder/.gitkeep
```
* delete untracked files (they are actually deleted)
```
git clean -f
```

# Branching
* tree-ish is:
** full SHA hash or partial SHA hash
** HEAD pointer
** branch reference
** ancestry (HEAD^, HEAD ^^ or HEAD~1, HEAD~2, etc.)

* show branches (currently checked out labelled with \*)
```
git branch
```
* make new branch
** creates new reference in .git/refs/heads/new_branch
```
git branch new_branch
```
* change to (checkout) new branch (updates working directory)
```
git checkout new_branch
```
* make new branch and checkout in one command
```
git checkout -b new_branch
```
* if conflicts in working directory and checked-out branch: error
** 1st option: discard current changes
```
git checkout -- <file>
```
** 2nd option: commit changes to current branch
```
git add <file>
git commit -m "commit message"
```
** 3rd option: stash changes
* rename branch
```
git branch -m <branchtitle> <new_branchtitle>
```
* delete branch
```
git checkout master
git branch -d <branch2delete>
```
* if commits have been made on <branch2delete>
```
git branch -D <branch2delete>
```
* show which branches are included in the current branch.  
i.e. all commits are included, i.e. the ancestors
```
git branch --merged
```

# Merging
```
git checkout master
git merge <branch>
```
* Fast-forward merge
** can be done if no commits have been made to master since branching
** i.e. if HEAD at current branch is in the ancestry of <branch>
** It will append the new commits on <branch> at the tip of the master branch
** No additional commit will be made

* True merge without conflicts
** if additional commit have been made on master and <branch>
** and git can solve the merge by an inbuilt strategy.
** editor prompts for changes in commit message.
** new commit for merge will be made

* merge conflict
** if master and <branch> have conflicting modifications in <file>
** error message pops up: CONFLICT (content): Merge conflict in <file>
** git marks the conflict inside a temporary version of <file>
```
<<<< HEAD
# content on HEAD Version
=======
# content on <brach>
>>>> <branch>
```
* Solutions mor merge conflicts:
** 1) abort merge to return to stage before merge attempts
```
git merge --abort
```
** 2) solve merge manually  
(edit temporary file, remove flags and save)
```
git add <file>
git commit -m "Merged branch manually"
```
* 3) use merge tool
```
git mergetool --tool
```

# Stashing
* save changes for example to prevent merge conflict when switching branches
* performs a git reset --hard in the background
```
git stash save "<stashMessage>"
```
* show stashed items  
format: stash@{0}: On <branch> <stashMessage>
```
git stash list
```
* show changes in stash like diff
```
git show -p stash@{0}
```
* retrieve stashed items
** will change working directory
** branch will be ignored
** works like a merge

* apply and leave copy of item in stash
```
git stash pop stash@{0}
```
* apply and remove from stash store
```
git stash apply
```
* remove stashed item
```
git stash drop stash@{0}
```
* remove all shashed items
```
git stash clear
```

# Remotes
* remote server:
** server version of repository
** gets updated by push
** can be fetched/pulled

* origin/master:
** current local repository
** mirrors remote server
** gets updated by git fetch
** like a normal branch, but can't be checked out

* master:
** local master branch
** updates to origin/master by merge

* add remote repository
** 'origin' is an alias and could be chosen to be a different name
```
git add remote origin <url>
```
* show remote branch
```
git remote
```
* show which remote for fetch and for push (could be different)
```
git remote -v
```
* remove remote
```
git remote rm origin
```
* get latest version of remote repository into local repository (updates origin/master)
```
git fetch
```
* update master with origin/master
```
git merge origin/master
```
* fetch and pull in one step
```
git pull
```
* checkout remote branch
```
git branch <remote_Branch> origin/<remote_Branch>
```
* delete remote branch from remote repository
```
git push origin :<remote_Branch>
or: git push origin --delete <remote_Branch>
```
* update remote server with my changes
```
git fetch
git merge origin/master
git push
```

* see which files changed remotely after fetch
```
git fetch && git diff @{u} --name-only
```

* specify the remote you want to push to if you have several
```
git push <my_origin>
```
* specify that pushed branch will be tracked
```
git push -u <branch>
```
