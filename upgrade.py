import sys


package_name = 'TamarinAssist'


def plugin_loaded():
    from package_control import events

    if events.install(package_name):
        print('Installed %s!' % events.install(package_name))
    elif events.post_upgrade(package_name):
        print('Upgraded to %s!' % events.post_upgrade(package_name))


def plugin_unloaded():
    from package_control import events

    if events.pre_upgrade(package_name):
        print('Upgrading from %s!' % events.pre_upgrade(package_name))
    elif events.remove(package_name):
        print('Removing %s!' % events.remove(package_name))