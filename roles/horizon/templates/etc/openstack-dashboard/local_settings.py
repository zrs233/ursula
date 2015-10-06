import os

from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import exceptions

DEBUG = False
TEMPLATE_DEBUG = DEBUG

COMPRESS_OFFLINE = True

ALLOWED_HOSTS = ['*']

# Set SSL proxy settings:
# For Django 1.4+ pass this header from the proxy after terminating the SSL,
# and don't forget to strip it from the client's request.
# For more information see:
# https://docs.djangoproject.com/en/1.4/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# If Horizon is being served through SSL, then uncomment the following two
# settings to better secure the cookies from security exploits
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Overrides for OpenStack API versions. Use this setting to force the
# OpenStack dashboard to use a specfic API version for a given service API.
# NOTE: The version should be formatted as it appears in the URL for the
# service API. For example, The identity service APIs have inconsistent
# use of the decimal point, so valid options would be "2.0" or "3".
OPENSTACK_API_VERSIONS = {
{% if horizon.keystone_api_version == 3 -%}
    "identity": 3,
{% else %}
#     "identity": 3,
{% endif %}
    "volume": 2
}

# Set this to True if running on multi-domain model. When this is enabled, it
# will require user to enter the Domain name in addition to username for login.
# OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = False

# Overrides the default domain used when running on single-domain model
# with Keystone V3. All entities will be created in the default domain.
# OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'

# Default OpenStack Dashboard configuration.
HORIZON_CONFIG = {
    'dashboards': ('project', 'admin', 'settings',),
    'default_dashboard': 'project',
    'user_home': 'openstack_dashboard.views.get_user_home',
    'ajax_queue_limit': 10,
    'auto_fade_alerts': {
        'delay': 3000,
        'fade_duration': 1500,
        'types': ['alert-success', 'alert-info']
    },
    'help_url': "http://docs.openstack.org",
    'exceptions': {'recoverable': exceptions.RECOVERABLE,
                   'not_found': exceptions.NOT_FOUND,
                   'unauthorized': exceptions.UNAUTHORIZED},
}

# Specify a regular expression to validate user passwords.
# HORIZON_CONFIG["password_validator"] = {
#     "regex": '.*',
#     "help_text": _("Your password does not meet the requirements.")
# }

# Disable simplified floating IP address management for deployments with
# multiple floating IP pools or complex network requirements.
# HORIZON_CONFIG["simple_ip_management"] = False

# Turn off browser autocompletion for the login form if so desired.
# HORIZON_CONFIG["password_autocomplete"] = "off"

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

# Set custom secret key:
# You can either set it to a specific value or you can let horizion generate a
# default secret key that is unique on this machine, e.i. regardless of the
# amount of Python WSGI workers (if used behind Apache+mod_wsgi): However, there
# may be situations where you would want to set this explicitly, e.g. when
# multiple dashboard instances are distributed on different machines (usually
# behind a load-balancer). Either you have to make sure that a session gets all
# requests routed to the same dashboard instance or you set the same SECRET_KEY
# for all of them.
from horizon.utils import secret_key
SECRET_KEY = "{{ secrets.horizon_secret_key }}"

{% macro memcached_hosts() -%}
{% for host in groups['controller'] -%}
   {% if loop.last -%}
'{{ hostvars[host][primary_interface]['ipv4']['address'] }}:{{ memcached.port }}'
   {%- else -%}
'{{ hostvars[host][primary_interface]['ipv4']['address'] }}:{{ memcached.port }}',
   {%- endif -%}
{% endfor -%}
{% endmacro -%}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND' : 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION' : [
            {{ memcached_hosts() }}
        ]
    }
}

# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Or send them to /dev/null
#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Configure these for your outgoing email host
# EMAIL_HOST = 'smtp.my-company.com'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = 'djangomail'
# EMAIL_HOST_PASSWORD = 'top-secret!'

# For multiple regions uncomment this configuration, and add (endpoint, title).
# AVAILABLE_REGIONS = [
#     ('http://cluster1.example.com:5000/v2.0', 'cluster1'),
#     ('http://cluster2.example.com:5000/v2.0', 'cluster2'),
# ]
{% if horizon.keystone_api_version == 3 -%}
AVAILABLE_REGIONS = [
     ('https://{{ endpoints.main }}:5001/v3', 'RegionOne'),
]
{% endif -%}

OPENSTACK_HOST = "{{ endpoints.main }}"
OPENSTACK_KEYSTONE_URL = "https://%s:5001/v{{horizon.keystone_api_version}}" % OPENSTACK_HOST
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "service"
SESSION_TIMEOUT = {{ horizon.session_timeout }}


# Disable SSL certificate checks (useful for self-signed certificates):
OPENSTACK_SSL_NO_VERIFY = True

# The OPENSTACK_KEYSTONE_BACKEND settings can be used to identify the
# capabilities of the auth backend for Keystone.
# If Keystone has been configured to use LDAP as the auth backend then set
# can_edit_user to False and name to 'ldap'.
#
# TODO(tres): Remove these once Keystone has an API to identify auth backend.
OPENSTACK_KEYSTONE_BACKEND = {
    'name': 'native',
    'can_edit_user': True,
    'can_edit_project': True,
    'can_edit_domain': True
}

OPENSTACK_HYPERVISOR_FEATURES = {
    'can_set_mount_point': False,
}

# The OPENSTACK_QUANTUM_NETWORK settings can be used to enable optional
# services provided by quantum.  Currently only the load balancer service
# is available.
OPENSTACK_NEUTRON_NETWORK = {
    'enable_lb': False,
    'enable_quotas': True
}

# OPENSTACK_ENDPOINT_TYPE specifies the endpoint type to use for the endpoints
# in the Keystone service catalog. Use this setting when Horizon is running
# external to the OpenStack environment. The default is 'internalURL'.
#OPENSTACK_ENDPOINT_TYPE = "publicURL"

# The number of objects (Swift containers/objects or images) to display
# on a single page before providing a paging element (a "more" link)
# to paginate results.
API_RESULT_LIMIT = 1000
API_RESULT_PAGE_SIZE = 20

# The timezone of the server. This should correspond with the timezone
# of your entire OpenStack installation, and hopefully be in UTC.
TIME_ZONE = "UTC"


# The Horizon Policy Enforcement engine uses these values to load per service
# policy rule files. The content of these files should match the files the
# OpenStack services are using to determine role based access control in the
# target installation.

# Map of local copy of service policy files
POLICY_FILES = {
    'identity': '/etc/keystone/policy.json',
    'compute': '/etc/nova/policy.json',
    'volume': '/etc/cinder/policy.json',
    'image': '/etc/glance/policy.json',
    'orchestration': '/etc/heat/policy.json',
    'network': '/etc/neutron/policy.json',
    'telemetry': '/etc/ceilometer/policy.json',
}

LOGGING = {
    'version': 1,
    # When set to True this will disable all logging except
    # for loggers specified in this configuration dictionary. Note that
    # if nothing is specified here and disable_existing_loggers is True,
    # django.db.backends will still log unless it is disabled explicitly.
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            # Set the level to "DEBUG" for verbose output logging.
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # Logging from django.db.backends is VERY verbose, send to null
        # by default.
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
        },
        'requests': {
            'handlers': ['null'],
            'propagate': False,
        },
        'horizon': {
            'handlers': ['console'],
            'propagate': False,
        },
        'openstack_dashboard': {
            'handlers': ['console'],
            'propagate': False,
        },
        'novaclient': {
            'handlers': ['console'],
            'propagate': False,
        },
        'cinderclient': {
            'handlers': ['console'],
            'propagate': False,
        },
        'keystoneclient': {
            'handlers': ['console'],
            'propagate': False,
        },
        'glanceclient': {
            'handlers': ['console'],
            'propagate': False,
        },
        'nose.plugins.manager': {
            'handlers': ['console'],
            'propagate': False,
        }
    }
}

from openstack_dashboard.settings import STATICFILES_DIRS, STATIC_ROOT
{% if openstack_install_method == 'package' %}
STATIC_ROOT='/opt/bbc/openstack-{{ openstack_package_version }}/horizon/static'
{% else %}
STATIC_ROOT='/opt/stack/horizon/static'
{% endif %}
STATICFILES_DIRS.append(('/etc/openstack-dashboard/static'))
