import os


def ursula_package_path(project, version):
    package_name_format = "openstack-%(version)s" % locals()
    path = os.path.join("/opt/bbc", package_name_format, project)
    return path
    

class FilterModule(object):
    ''' ursula utility filters '''

    def filters(self):
        return {
            'ursula_package_path': ursula_package_path
        }
