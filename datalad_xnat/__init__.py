command_suite = (
    'XNAT server access support',
    [
#        (
#            'datalad_xnat.init',
#            'Init',
#            'xnat-init',
#            'xnat_init',
#        ),
#        (
#            'datalad_xnat.update',
#            'Update',
#            'xnat-update',
#            'xnat_update',
#        ),
    ]
)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
