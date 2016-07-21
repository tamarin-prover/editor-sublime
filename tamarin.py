import sublime
import sublime_plugin
import json
import os
import platform
import time
import subprocess


LOCAL = '/usr/local/bin:/usr/local/sbin'

os.environ['PATH'] += ':'
os.environ['PATH'] += LOCAL


def settings_get(name, default=None):
    plugin_settings = sublime.load_settings('Tamarin.sublime-settings')
    project_settings = None
    if sublime.active_window() and sublime.active_window().active_view():
        project_settings = sublime.active_window().active_view().settings()

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


class TamarinInsertTextCommand(sublime_plugin.TextCommand):
    """ A helper command to insert text at the end of a buffer.
    """
    def run(self, edit, txt, scroll_to_end):
        self.view.insert(edit, self.view.size(), txt)
        self.view.show(self.view.size())


class TamarinProveCommand(sublime_plugin.WindowCommand):
    """ Runs tamarin-prover --prove with the active script
    """
    def is_enabled(self):
        return is_tamarin_view(self.window.active_view())

    def run(self):
        view = self.window.active_view()
        if view is None:
            return
        self.output_view = self.window.new_file()
        self.output_view.set_name("Tamarin Proof")
        self.output_view.set_scratch(True)
        self.output_view.set_read_only(True)
        self._runner(get_spthy_file(view))

    def _runner(self, spthy):
        def prove():
            tamarin = find_tamarin_bin("tamarin-prover")
            cmd = tamarin + " --prove " + spthy
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

            while True:
                line = process.stdout.readline()
                if line:
                    self.output_view.set_read_only(False)
                    self.output_view.run_command('tamarin_insert_text', {
                            "txt": line.decode("utf-8"),
                            "scroll_to_end": True,
                        })
                    self.output_view.set_read_only(True)
                    if not self.output_view.window():
                        sublime.status_message("Tamarin: cancelled")
                        process.kill()
                    self.output_view.set_read_only(False)
                    # process.communicate()
                else:
                    break
        self.window.focus_view(self.output_view)
        sublime.set_timeout_async(prove, 0)


class TamarinProveInteractiveCommand(sublime_plugin.WindowCommand):
    """ Runs tamarin-prover --prove with the active script
    """
    def is_enabled(self):
        return is_tamarin_view(self.window.active_view())

    def run(self):
        sublime.status_message("DEVELOPMENT")


def find_tamarin_bin(binary):
    def is_exe(binpath):
        return os.path.isfile(binpath) and os.access(binpath, os.X_OK)

    search_paths = []
    setting_path = settings_get("tamarin_bin_dir", None)
    if setting_path is not None:
        search_paths.append(setting_path)

    if is_mac():
        search_paths += os.getenv("PATH").split(os.pathsep)
        search_paths += ["~/.local/bin/"]
    elif is_windows():
        binary += ".exe"
        search_paths += []
    elif is_linux():
        search_paths += os.getenv("PATH").split(os.pathsep)
        search_paths += ["~/.local/bin/"]

    for path in search_paths:
        path = path.strip('"')
        exe_file = os.path.join(os.path.expanduser(path), binary)
        if is_exe(exe_file):
            return exe_file

    raise Exception("Cannot find %s executable in %s. Set tamarin_bin_dir."
        \
                    % (binary, search_paths))
