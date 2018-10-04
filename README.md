editor-sublime
==============

Repository for text editor (sublime) syntax highlighting

*Please be aware that the plugin is still under active development and as such, several of the features are still implemented in a prototypical manner.*
*If you experience any problems or have any questions on running any parts of the plug-in please open an [issue on GitHub](https://github.com/tamarin-prover/editor-sublime/issues).

## Introduction

This is a [Sublime Text 3](https://www.sublimetext.com/3) plug-in which adds
support for [Tamarin] Security Protocol Theories (`spthy`):

+ Syntax Highlighting
+ Autocompltion (Snippets)
+ Run Tamarin functions within Sublime

See [Screenshots](docs/SCREENSHOTS.md) for how this plugin looks and works.

For the latest developments see the [Tamarin GitHub] page.

It also includes some useful commands, accessed via `CTRL + SHIFT + P` then
type "*Tamarin*" to see the options available.

## Features

- [X] Basic Syntaxes
- [X] Run Tamarin within Sublime
- [X] Snippets for Theory, Rule, Restriction and Lemma
- [X] Configure `SAPIC` path

## Under Development

- [ ] Add package to [PackageControl.io]
- [ ] Highlight Script errors in Editor
- [ ] Highlight Restriction / Lemma Guardedness issues in Editor

## Installation

### Manual

### OS X

```bash
$ git clone https://github.com/tamarin-prover/editor-sublime.git
$ ln -s `pwd`/editor-sublime ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/
```

### Linux

```bash
$ git clone https://github.com/tamarin-prover/editor-sublime.git
$ ln -s `pwd`/editor-sublime ~/.config/sublime-text-3/Packages/
```

### Windows

On Windows, you can use directory junctions instead of symlinks (symlinks require administrative rights; directory junctions don't):
```powershell
# Using PowerShell
PS> git clone https://github.com/tamarin-prover/editor-sublime.git
PS> cmd /c mklink /J "$env:APPDATA/Sublime Text 3/Packages/editor-sublime" (convert-path ./editor-sublime)
```

### Package Control

[PackageControl.io](https://packagecontrol.io/packages/) currently in development and hope to bring this installation method back very soon.

[Tamarin]:https://tamarin-prover.github.io/
[Tamarin GitHub]:https://github.com/tamarin-prover/tamarin-prover
[PackageControl.io]:https://packagecontrol.io/