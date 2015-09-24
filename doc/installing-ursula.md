OS-Specific Ursula Install Instructions
=======================================

Reference the main README.md for overall deployment instructions

# RHEL System Dependencies

The following packages are needed on Red Hat Enterprise Linux environments:

* python-pip
* python-devel
* python-virtualenvwrapper
* libxml2-devel
* libxslt-devel
* libffi-devel


# Differences on RHEL Environment Setup...

Slight difference on the virtualenvwrapper.sh sourcing path...
```bash
$ pip install virtualenvwrapper
$ mkvirtualenv --no-wheel ursula
$ source /usr/bin/virtualenvwrapper.sh

# And this for adding permanently into your .bashrc:
$ echo "source /usr/bin/virtualenvwrapper.sh" >> ~/.bashrc
```
