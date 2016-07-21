import sublime
import sublime_plugin


def settings_get(name, default=None):
    plugin_settings = sublime.load_settings('tamarin.sublime-settings')
    project_settings = None
    if sublime.active_window() and sublime.active_window().active_view():
        project_settings = sublime.active_window().active_view().settings()
        .get("tamarin")

    if project_settings is None:
        project_settings = {}

    setting = project_settings.get(name, plugin_settings.get(name, default))
    return setting


def is_mac():
    return platform.system() == "Darwin"


def is_linux():
    return platform.system() == "Linux"


def is_windows():
    return platform.system() == "Windows"


def is_tamarin_view(view):
    """ True if the view has a spthy file loaded"""
    if view is None or view.file_name() is None:
        return False
    return 'spthy' in view.settings().get('syntax').lower()


def get_spthy_file(view):
        return view.file_name()


class TamarinRunProveCommand(sublime_plugin.WindowCommand):
    """ Runs tamarin --prove with the active
    """
    def is_enabled(self):
        return is_tamarin_view(self.window.active_view())

    def run(self):
        view = self.window.active_view()
        if view is None:
            return
        tamarin = find_tamarin_bin("tamarin-prover")
        subprocess.Popen([tamarin, '--prove', get_spthy_file(view)])


def find_tamarin_bin(binary):
    def is_exe(binpath):
        return os.path.isfile(binpath) and os.access(binpath, os.X_OK)

    search_paths = []
    setting_path = settings_get("tamarin_bin_dir", None)
    if setting_path is not None:
        search_paths.append(setting_path)

    if is_mac():
        search_paths += os.getenv("PATH").split(os.pathsep)
        search_paths += ["$HOME/.local/bin/"]
    elif is_windows():
        binary += ".exe"
        search_paths += []
    elif is_linux():
        search_paths += os.getenv("PATH").split(os.pathsep)
        search_paths += ["$HOME/.local/bin/"]

    for path in search_paths:
        path = path.strip('"')
        exe_file = os.path.join(os.path.expanduser(path), program)
        if is_exe(exe_file):
            return exe_file

    raise Exception("Cannot find %s executable in %s. Set tamarin_bin_dir."
        \
                    % (program, search_paths))
