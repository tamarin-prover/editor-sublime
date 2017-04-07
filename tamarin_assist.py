import sublime
import sublime_plugin
import json
import sys
import os
import platform
import time
from subprocess import Popen, PIPE
from queue import Queue, Empty
from threading import Thread
import traceback
import time


LOCAL = '/usr/local/bin:/usr/local/sbin'
SYNTAX_FILE = 'Packages/TamarinAssist/Syntaxes/spthy.sublime-syntax'
VERSION = "0.0.1"

os.environ['PATH'] += ':'
os.environ['PATH'] += LOCAL

io_q = Queue()


def stream_watcher(identifier, stream):

    for line in stream:
        io_q.put((identifier, line))

    if not stream.closed:
        stream.close()


def settings_get(name, default=None):
    plugin_settings = sublime.load_settings('TamarinAssist.sublime-settings')
    project_settings = None
    if sublime.active_window() and sublime.active_window().active_view():
        project_settings = sublime.active_window().active_view().settings()

    if project_settings is None:
        project_settings = {}

    setting = project_settings.get(name, plugin_settings.get(name, default))
    return setting


def printer(self):

    while True:
        try:
            # Block for 1 second.
            item = io_q.get(True, 1)
        except Empty:
            # No output in either streams for a second. Are we done?
            if proc.poll() is not None:
                break
        else:
            identifier, line = item
            if line:
                self.output_view.run_command('tamarin_insert_text', {
                        "txt": line.decode("utf-8"),
                        "scroll_to_end": True,
                    })
                self.output_view.set_read_only(True)
                if not self.output_view.window():
                    sublime.status_message("Tamarin: cancelled")
                    process.kill()
                self.output_view.set_read_only(False)
            else:
                break


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


class TamarinCommand(sublime_plugin.WindowCommand):
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
            tamarin = find_bin("tamarin_bin_dir", "tamarin-prover")
            sapic = find_bin("sapic_bin_dir", "sapic")
            cmd = tamarin + " --prove " + spthy
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)

            Thread(target=stream_watcher, name='stdout-watcher', args=('STDOUT', proc.stdout)).start()
            Thread(target=stream_watcher, name='stderr-watcher', args=('STDERR', proc.stderr)).start()

            print_sublime_tamarin(self)
            self.output_view.set_read_only(False)
            self.output_view.run_command('tamarin_insert_text', {
                "txt": "$ %s \n\n" % cmd,
                "scroll_to_end": True,
            })

            Thread(target=printer(self), name='printer').start()

        self.window.focus_view(self.output_view)
        self.output_view.set_syntax_file(SYNTAX_FILE)
        sublime.set_timeout_async(prove, 0)


class TamarinCheckCommand(sublime_plugin.WindowCommand):
    """ Runs tamarin-prover --parse-only with the active script
        to see if the syntax of spthy file is correct. If errors
        or guardness issues are found, will highlight in the
        script tab window.
    """
    def is_enabled(self):
        return is_tamarin_view(self.window.active_view())

    def run(self):
        view = self.window.active_view()
        if view is None:
            return
        self.output_view = self.window.new_file()
        self.output_view.set_name("Tamarin Typecheck")
        self.output_view.set_scratch(True)
        self.output_view.set_read_only(True)
        self._runner(get_spthy_file(view))

    def _runner(self, spthy):
        def typecheck():
            tamarin = find_bin("tamarin_bin_dir", "tamarin-prover")
            sapic = find_bin("sapic_bin_dir", "sapic")
            cmd = tamarin + " --parse-only " + spthy
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)

            Thread(target=stream_watcher, name='stdout-watcher', args=('STDOUT', proc.stdout)).start()
            Thread(target=stream_watcher, name='stderr-watcher', args=('STDERR', proc.stderr)).start()

            print_sublime_tamarin(self)
            self.output_view.set_read_only(False)
            self.output_view.run_command('tamarin_insert_text', {
                "txt": "$ %s \n\n" % cmd,
                "scroll_to_end": True,
            })

            Thread(target=printer(self), name='printer').start()

        self.window.focus_view(self.output_view)
        self.output_view.set_syntax_file(SYNTAX_FILE)
        sublime.set_timeout_async(typecheck, 0)


def print_sublime_tamarin(self):

    MESSAGE = "TamarinAssist v" + VERSION

    self.output_view.set_read_only(False)
    self.output_view.run_command('tamarin_insert_text', {
        "txt": "%s \n\n" % MESSAGE,
        "scroll_to_end": True,
    })


def find_bin(name, binary):
    def is_exe(binpath):
        return os.path.isfile(binpath) and os.access(binpath, os.X_OK)

    search_paths = []
    setting_path = settings_get(name, None)
    if setting_path is not None:
        search_paths.append(setting_path)

    if is_mac():
        search_paths += os.getenv("PATH").split(os.pathsep)
        search_paths += ["~/.local/bin/"]
    elif is_linux():
        search_paths += os.getenv("PATH").split(os.pathsep)
        search_paths += ["~/.local/bin/"]

    for path in search_paths:
        path = path.strip('"')
        exe_file = os.path.join(os.path.expanduser(path), binary)
        if is_exe(exe_file):
            return exe_file

    raise Exception("Cannot find %s executable in %s. Set %s"
        \
                    % (binary, search_paths, name))
