# Try Python #
## An interactive Python tutorial running in the browser ##


An interactive [Python](http://www.python.org) interpreter that runs in the browser, using [Silverlight](http://silverlight.net/GetStarted/) and [IronPython](http://www.codeplex.com/IronPython).

You can see it running online at [www.trypython.org](http://www.trypython.org/).

It should also run under [Moonlight](http://go-mono.com/moonlight-beta/) for Linux (although bug reports to the Mono team and not me if it doesn't!).

As well as an interactive interpreter running in the browser it has a few pages from the [Python tutorial](http://docs.python.org/tutorial/).

The tutorial pages are automatically formatted for displaying in Silverlight using [rst2xaml](http://code.google.com/p/rst2xaml/).

The online interpreter has the following features:

  * Auto-resizes with the browser
  * Navigation bar through the tutorial pages at the top and bottom
  * Individual pages are bookmarkable and the URL fragment auto-updates when you change page
  * Mouse scroll wheel supported over the tutorial and console scroll viewers
  * Control-C interrupts the running code with a keyboard interrupt
  * File I/O works (the file type and open function) using local browser storage to store files
  * raw\_input and input work in the interpreter
  * Basic auto-indent and auto-dedent in the console
  * Console history, including multiline history
  * Syntax highlighting in the console
  * reset command to clear the console
  * Assign to sys.ps1 and sys.ps2 from the console

Not much of the Python standard library is included. I intend to expand the tutorial adding new modules as they are needed (the whole standard library is about 5mb and would make Try Python take much longer to load).

Some of the console history code was contributed by [Resolver Systems](http://www.resolversystems.com/).