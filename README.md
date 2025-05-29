# shell (bbs)
===
- [ ] gracefully handle `screen`
- [ ] dynamic command set
- [ ] turn off tab-complete after a command has been entered. remove delims? (@since 20211211)
- [ ] confirm no bash chars can be entered at the bbs prompt (@since 20211211) @security
- [x] handle setarea() correctly (@since 20211211) (@done 20211214)
- [ ] somehow remove requirement of bbsengine.initscreen() at each run through the while loop (@since 20211214)
- [ ] import given module, call main(). does this keep it runnable from a shell (tcsh) prompt? (@since 20211214)
- [ ] in 'socrates.addpost', how to call main() (aka initscreen()) if needed (@since 20211214)
- [ ] change-sig in shell (@since 20220130)
- [ ] store 'sysop mode' flag in session
- [x] if shellout, make sure all **kwargs are passed to system command (@since 20220428)
- [x] if prg (only runnable from bbs), call prg.buildargs() before call to parse_args()
- [x] in shell, banner --help should show --center, etc (@since 20220428)
- git@github.com:jonez734/letteredolive.git
- https://www.shellcheck.net/ -- linter for bash
- [ ] run empyre from tcsh with --debug, works correctly. run empyre from bbs with --debug, does not work correctly (@since 20220509)
- [x] running 'empyre --help' from the shell exits the shell (@since 20220509) (@done 20220510) trapped SystemExit @see https://stackoverflow.com/questions/58367375/can-i-prevent-argparse-from-exiting-if-the-user-specifies-h
- https://docs.python.org/3/library/argparse.html#exit-on-error
- [ ] handle SIGHUP (@since 20220516)
    * https://docs.python.org/3/library/faulthandler.html#module-faulthandler
    * https://docs.python.org/3/library/signal.html#signal.SIGHUP
    * https://docs.python.org/3/library/signal.html#signal.signal

=== migrate to setuptools ===
- [setuptools not copying files]](https://www.google.com/search?q=setuptools+not+copying+files&oq=setuptools+not+copying+files&aqs=chrome..69i57.6941j1j7&sourceid=chrome&ie=UTF-8)
- https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html
- https://jwodder.github.io/kbits/posts/pypkg-mistakes/
- https://unix.stackexchange.com/questions/19317/can-less-retain-colored-output

- (https://stackoverflow.com/questions/2059482/python-temporarily-modify-the-current-processs-environment)[python temporarily modify the current process environment]
- https://stackoverflow.com/questions/16472639/setting-up-idle-thread-signalling-thread
- https://stackoverflow.com/questions/16452517/controlling-ui-elements-in-wxpython-using-threading/16452674#16452674

Details:

Common name: Lettered olive

Scientific name: Oliva sayana

Appearance: Smooth, glossy, cylindrical shell with distinctive brownish markings that can look like letters or scribbles—hence the name.

Habitat: Sandy shores and shallow waters, particularly along the Atlantic and Gulf coasts of the U.S.

So yes, if you're referring to a glossy, patterned shell often found along the southeastern U.S. coast, “lettered olive” is indeed the correct term.
