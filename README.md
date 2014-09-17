# pano.py

A workflow automation wrapper for [Pandoc](http://johnmacfarlane.net/pandoc/).

You've got `exciting.md` and want a pdf with LuaLaTeX, bibliography support?

```sh
panopy pdf exciting.md
```

Want a self-contained html with Bootstrap too?

```sh
panopy html exciting.md
```

Pandoc requires a large number of command-line arguments to generate any output
format. Typical solutions have been to use makefiles or YAML configurations to
specify what pandoc should do, along with pre/post-processors to clean up
pandoc's shortcomings. This can get messy.

`panopy`'s philosophy is to separate contents from workflow. Content should try
as hard as it can to be agnostic to its output format. Likewise, the file system
should segregate content from the tools needed to process it. Instead of
makefile and document-embedded output specifications, `panopy` uses global YAML
templates to specify workflows around any given input file, combined with
a global script to process it all. So you can write a single markdown file and
push it to whatever formats you need.

At the present moment, panopy is a barebones wrapper allowing for a series of
preprocessing commands, a pandoc command and a series of postprocessing
commands. I can't vouch for its ability to process multiple input files into
a single output. I also doubt that pandoc is fast enough to be an online
processor for multiple files.

## Similar

 -  [panzer](https://github.com/msprev/panzer) allows you to specify styles at
     the file level (YAML metadata), while `panopy` specifies a workflow at the
     command line. I made `panopy` because I wanted to keep my YAML clean and
     sort of tool agnostic.

 -  Makefiles: see e.g. [Kieran Healy's
     solution](http://kieranhealy.org/blog/archives/2014/01/23/plain-text/)
