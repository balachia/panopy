pano.py
=======

A workflow automation wrapper for
`Pandoc <http://johnmacfarlane.net/pandoc/>`__.

You’ve got ``exciting.md`` and want a pdf with LuaLaTeX, bibliography
support?

.. code:: sh

    panopy pdf exciting.md

Want a self-contained html with Bootstrap too?

.. code:: sh

    panopy html exciting.md

Installation
------------

.. code:: sh

    pip install panopy

Purpose
-------

Pandoc requires a large number of command-line arguments to generate any
output format. Typical solutions have been to use makefiles or YAML
configurations to specify what pandoc should do, along with
pre/post-processors to clean up pandoc’s shortcomings. This can get
messy.

``panopy``\ ’s philosophy is to separate contents from workflow. Content
should try as hard as it can to be agnostic to its output format.
Likewise, the file system should segregate content from the tools needed
to process it. Instead of makefile and document-embedded output
specifications, ``panopy`` uses global YAML templates to specify
workflows around any given input file, combined with a global script to
process it all. So you can write a single markdown file and push it to
whatever formats you need.

At the present moment, panopy is a barebones wrapper allowing for a
series of preprocessing commands, a pandoc command and a series of
postprocessing commands. I can’t vouch for its ability to process
multiple input files into a single output. I also doubt that pandoc is
fast enough to be an online processor for multiple files.

Usage
-----

Panopy looks for a default YAML template file in
~/.pandoc/panopy.templates. Currently there is no way to change this
location. A sample file might looks something like:

.. code:: yaml

    __default__:
        s:
        S:
        r: markdown+yaml_metadata_block

    latex:
        o: %.tex
        bibliography: ~/Documents/library.bib
        filter:
            - pandoc-citeproc

    pdf:
        __inherits__: latex
        o: %.pdf
        latex-engine: pdflatex

    fancypdf:
        __inherits__: pdf
        __pre__:
            - gpp -o %.gpp.md %.md
        __in__: %.gpp.md

The ``__default__`` template sets options ``-s`` (standalone), ``-S``
(smart), and ``-r markdown+yaml_metadata_block`` for all files. The
``latex`` template changes the default output format to tex and adds
pandoc’s bibliography processing filter. The ``pdf`` template inherits
all settings from ``latex`` but changes the output to pdf and sets the
latex engine. The ``fancypdf`` template updates ``pdf`` to preprocess
the input file with
`gpp <http://files.nothingisreal.com/software/gpp/gpp.html>`__ and
changes the input file to pass to pandoc.

Now just find your input file in the terminal and type:

.. code:: sh

    panopy fancypdf input.md

And if you use vim:

.. code:: vim

    :!panopy fancypdf %

\`\`\`

Panopy Keywords
~~~~~~~~~~~~~~~

Special templates:

-  ``__default__``: provides the default template that all others
   inherit from

Keywords in template:

-  ``%``: auto-replaced by base file name: ``panopy pdf infile.md`` with
   template option ``-o: %.pdf`` becomes ``-o infile.pdf``. Escape with
   ``\%``
-  ``__inherits__``: inherit from named template(s)
-  ``__in__``: specifies input file format
-  ``__pre__``: specifies commands to run before pandoc
-  ``__post__``: specifies commands to run after pandoc
-  ``__clear__``: specifies which inherited options to clear

Similar
-------

-  `panzer <https://github.com/msprev/panzer>`__ allows you to specify
   styles at the file level (YAML metadata), while ``panopy`` specifies
   a workflow at the command line. I made ``panopy`` because I wanted to
   keep my YAML clean and sort of tool agnostic.

-  Makefiles: see e.g. `Kieran Healy’s
   solution <http://kieranhealy.org/blog/archives/2014/01/23/plain-text/>`__
