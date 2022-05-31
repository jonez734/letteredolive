== shell (bbs) ==
    * [ ] turn off tab-complete after a command has been entered. remove delims? (@since 20211211)
    * [ ] confirm no bash chars can be entered at the bbs prompt (@since 20211211) @security
    * [x] handle setarea() correctly (@since 20211211) (@done 20211214)
    * [ ] somehow remove requirement of bbsengine.initscreen() at each run through the while loop (@since 20211214)
    * [ ] import given module, call main(). does this keep it runnable from a shell (tcsh) prompt? (@since 20211214)
    * [ ] in 'socrates.addpost', how to call main() (aka initscreen()) if needed (@since 20211214)
    * [ ] if callback is 'socrates', import module and call socrates.main() (@since 20211214)
    * [ ] if callback is 'socrates.addpost', import module and call 'addpost' (@since 20211214)
    * [ ] in __main__, be sure to initscreen() (@since 20211214)
    * [ ] use 'cmd2' (@since 20220130)
       * [ ] cmd2 uses 'poutput' with very similar function to ttyio.echo()
    * [ ] change-sig in shell (@since 20220130)
    * https://github.com/python-cmd2/cmd2/issues/194
    * if point and buffer len are the same, increment idle timer
    * https://stackoverflow.com/questions/301134/how-to-import-a-module-given-its-name-as-string?rq=1
    * https://stackoverflow.com/questions/7719466/i-have-a-string-whose-content-is-a-function-name-how-to-refer-to-the-correspond
    * https://www.google.com/search?q=cmd2+disable+built-in+alias&oq=cmd2+disable+built-in+alias&aqs=chrome..69i57.10208j0j7&sourceid=chrome&ie=UTF-8
    * static command tables need a way to check access, do not show commands a member does not have access to ("engine", etc)
    * try to import cmd_<command> file based on PYTHONPATH
    * check for callable cmd_foo.cmd_foo()
    * check current environment for the command
      * exits
    * store engine.member.env(ironment) instead of 'currentroom'
    * __init__()
    * reset()
    * handle commands. search for _*.py
    * commands
      - if shellout, make sure all **kwargs are passed to system command (@since 20220428)
      - if prg (only runnable from bbs), call prg.buildargs() before call to parse_args()
        * in shell, banner --help should show --center, etc (@since 20220428)
    * banner
      - no database work
      - make sure database args are at least dropped silently
    * optimize. callback() vs bbs.runprg(), etc
    * (https://docs.python.org/3/library/importlib.html#importlib.abc.Loader.exec_module)[use exec_module instead of load_module]
    * https://www.educative.io/edpresso/what-is-argparse-parents-in-python
    * https://realpython.com/command-line-interfaces-python-argparse/#setting-the-name-of-the-attribute-to-be-added-to-the-object-once-parsed
    * https://stackoverflow.com/questions/7498595/python-argparse-add-argument-to-multiple-subparsers
    * [python3 argparse parent](https://www.google.com/search?q=python3+argparse+parent&sxsrf=ALiCzsYHYbOxowHOmBkVe5Y3lMuCSrQCRw%3A1651257900875&ei=LDJsYtCLNc23ggfR-4r4CQ&ved=0ahUKEwjQ0fSE97n3AhXNm-AKHdG9Ap8Q4dUDCA8&uact=5&oq=python3+argparse+parent&gs_lcp=Cgdnd3Mtd2l6EAMyBAgjECc6BwgAEEcQsAM6BwgjEK4CECc6BggAEBYQHjoFCAAQhgM6BQgAEIAEOgoIABCABBCHAhAUOggIABAWEAoQHjoECAAQDUoECEEYAEoECEYYAFDDDVi9ImDOI2gBcAF4AIABgwGIAaUQkgEENS4xNJgBAKABAcgBCMABAQ&sclient=gws-wiz)
- bbsengine5.runcallback(args, callback, **kwargs) (@since 20220501)
    * if `callback` is callable(), call it and return the result
    * if `callback` is a string, split it on ".". if there's only one element ("empyre"), that becomes the module name and use 'main' as funcname
    * if callback is still not callable, eval `callback` and check again
    * first try to call empyre.buildargs(), then try to call empyre.main()
- git@github.com:jonez734/letteredolive.git
- https://www.google.com/search?q=south+carolina+state+shell&sxsrf=ALiCzsYxibv8Kf5JjFz54lECes_DvkirIA%3A1651452162000&ei=ASlvYrvlPK--ggfbzbfYAg&ved=0ahUKEwj76erbyr_3AhUvn-AKHdvmDSsQ4dUDCA4&uact=5&oq=south+carolina+state+shell&gs_lcp=Cgdnd3Mtd2l6EAMyBQguEIAEMgYIABAWEB4yCAgAEBYQChAeMgYIABAWEB4yBQgAEIYDMgUIABCGAzIFCAAQhgMyBQgAEIYDOgcIABBHELADOgoIABBHELADEMkDOgQIIxAnOggIABCABBDJAzoFCAAQgAQ6CggAEIAEEIcCEBQ6CwguEIAEEMcBEK8BOgoILhCABBCHAhAUOggIABCABBCxAzoLCC4QgAQQsQMQgwE6DQguEIAEEIcCELEDEBQ6BQgAELEDOg4ILhCABBCxAxCDARDUAjoOCC4QgAQQxwEQrwEQ1AI6DQgAEIAEEIcCELEDEBQ6DggAEIAEELEDEIMBEMkDOgsILhCABBDHARCjAjoJCAAQyQMQFhAeSgQIQRgASgQIRhgAUJ4GWIcbYLwdaAJwAXgAgAHUAYgB9g-SAQYwLjE1LjGYAQCgAQHIAQjAAQE&sclient=gws-wiz
- https://stackoverflow.com/questions/24666197/argparse-combining-parent-parser-subparsers-and-default-values
- https://www.shellcheck.net/ -- linter for bash
- [ ] cache modules loaded by bbsengine5.runcallback()? (@since 20220404)
- https://stackoverflow.com/questions/17157162/compare-a-bash-string-literal-to-a-local-variable
- upon exit from runcallback() via EOF, return to the shell prompt? (@since 20220506)
- argumentparser.parse_args() accepts a string (@since 20220506)
- https://docs.python.org/3/library/multiprocessing.html?fbclid=IwAR1I33CNxFTZ3pyAamEIvU1Nt27AFajFxNCH-4JHbvIwUtCjUBivENLxD7s
- run empyre from tcsh with --debug, works correctly. run empyre from bbs with --debug, does not work correctly (@since 20220509)
- [x] running 'empyre --help' from the shell exits the shell (@since 20220509) (@done 20220510) trapped SystemExit @see https://stackoverflow.com/questions/58367375/can-i-prevent-argparse-from-exiting-if-the-user-specifies-h
- https://docs.python.org/3/library/argparse.html#exit-on-error
- [ ] bbsengine.setarea() has a diff areastack than empyre.bbsengine.setarea() (shell) (@since 20220513)
- [x] prompt does not show timezone - call time.tzset() (@since 20220515) (@done 20220516)
- [ ] add hard-coded commands to help and tab-complete (logout, lo, etc) (@since 20220516)
- [ ] aliases: banner -> banderole. add them to help (@since 20220516)
- [ ] handle SIGHUP (@since 20220516)
    * https://docs.python.org/3/library/faulthandler.html#module-faulthandler
    * https://docs.python.org/3/library/signal.html#signal.SIGHUP
    * https://docs.python.org/3/library/signal.html#signal.signal
- [ ] add accessprg() to most prgs, given an op and other details, return bool (@since 20220517)
- [ ] figure out why a module like figlet from bbs is not reloaded every time (@since 20220519)

== migrate to setuptools ==
- https://www.google.com/search?q=setuptools+not+copying+files&oq=setuptools+not+copying+files&aqs=chrome..69i57.6941j1j7&sourceid=chrome&ie=UTF-8
- https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html
- https://jwodder.github.io/kbits/posts/pypkg-mistakes/
- https://unix.stackexchange.com/questions/19317/can-less-retain-colored-output
