from __future__ import print_function
import yaml
import os.path
import sys
import re
from subprocess import call

DEFAULT_PATH = '~/.pandoc/panopy.templates'

all_templates = dict()

# keywords
DEFAULT_TEMPLATE = '__default__'
KW_INHERIT = '__inherits__'
KW_IN = '__in__'
KW_POST = '__post__'
KW_PRE = '__pre__'
KW_CLEAR = '__clear__'

def filename_replace(text):
    global basename
    return re.sub(r'(^|[^\\])%', basename, text)
    #return re.sub(r'%', basename, text)

def process_arg(key, value):
    #global basename

    # swap % for the global filename
    #if value is not None:
        #print(value)
        #value = filename_replace(value)
    #if key == 'o' or key == 'output':
        #value = re.sub(r'%', basename, value)
        #value = filename_replace(value)
    if value is None:
        return ['-{longkey}{key}'.format(longkey='-' if len(key) > 1 else '', key=key)]
    elif isinstance(value, basestring):
        value = os.path.expanduser(filename_replace(value))
        if len(key) > 1:
            return ['--{key}={value}'.format(key=key, value='"' + value + '"' if ' ' in value else value)]
        else:
            return ['-{key}'.format(key=key), '{value}'.format(value='"' + value + '"' if ' ' in value else value)]
    else: # it's a list?
        return [item for subval in value for item in process_arg(key, subval)]

def update_template(template, update_name, already_used=[]):
    global all_templates

    res = dict(template)

    # check for cycles
    if update_name in already_used:
        raise ValueError('Detected cycle while building template: ' + str(already_used + [update_name]))

    # load update template
    if update_name not in all_templates:
        raise ValueError('Could not find template "' + update_name + '" in configuration')
    else:
        pretemp = all_templates[update_name]

    # load with inherited characteristics if needed, then overwrite with local settings
    if KW_INHERIT in pretemp:
        res = update_template(res, pretemp[KW_INHERIT], already_used + [update_name])
        del pretemp[KW_INHERIT]
        res.update(pretemp)
    else:
        res.update(pretemp)

    return res


def main():
    global basename
    global all_templates

    # split arguments into panopy and pandoc args
    args = sys.argv
    panopy_args = [x for x in args if re.match('^---', x)]
    args = [x for x in args if not re.match('^---', x)]

    # panopy settings
    debug = '---debug' in panopy_args

    if debug:
        print(args, file=sys.stderr)

    # check if we have a template name in here, else quit
    if len(args) > 1:
        template_name = args[1]
        args = args[2:]
    else:
        sys.exit('No template named')

    # pull out base file name from first (non-template) argument
    # TODO: this is a hackish format...
    # TODO: let alone the total inability to deal with multiple input files
    if len(args) > 0:
        (basefolder, basefile) = os.path.split(args[0])
        basefolder = '.' if basefolder == '' else basefolder
        basename = os.path.splitext(basefile)[0]
    else:
        basefolder = '.'
        basefile = None
        basename = ''

    # load all templates, and merge together
    with open(os.path.expanduser(os.path.join(DEFAULT_PATH))) as fin:
        templates = yaml.load_all(fin)
        all_templates = dict()
        for x in templates:
            if x is not None:
                all_templates.update(x)
        #templates = [x for x in templates if x is not None]

    # merge the templates together
    #all_templates = dict()
    #for template in templates:
        #all_templates.update(template)

    ## build up current template
    # start with default template
    template = update_template(dict(), DEFAULT_TEMPLATE)

    # get named template
    template = update_template(template, template_name, [DEFAULT_TEMPLATE])
    if debug:
        print("TEMPLATE\n%s" % template)

    # clear any unwanted settings
    if KW_CLEAR in template:
        clears = template[KW_CLEAR]
        del template[KW_CLEAR]
        for clear in clears:
            if clear in template:
                del template[clear]

    # extract preprocessing commands
    if KW_PRE in template:
        preprocess = template[KW_PRE]
        del template[KW_PRE]
        preprocess = [[os.path.expanduser(filename_replace(item)) for item in x.split()] for x in preprocess]
    else:
        preprocess = None

    # extract postprocessing commands
    if KW_POST in template:
        postprocess = template[KW_POST]
        del template[KW_POST]
        postprocess = [[os.path.expanduser(filename_replace(item)) for item in x.split()] for x in postprocess]
    else:
        postprocess = None

    if debug and preprocess:
        print("PREPROCESSING COMMANDS:\n%s" % preprocess)
    if debug and postprocess:
        print("POSTPROCESSING COMMANDS:\n%s" % postprocess)

    # get input files
    if KW_IN not in template:
        infiles = [basefile]
    else:
        infiles = template[KW_IN]
        del template[KW_IN]
        if isinstance(infiles, basestring):
            infiles = [infiles]
        infiles = [os.path.expanduser(filename_replace(item)) for item in infiles]


    # build pandoc arguments list
    pandoc_args = [arg for (k,v) in template.iteritems() for arg in process_arg(k,v)]

    if debug:
        print("PANDOC ARGS:\n%s" % pandoc_args)

    # call preprocessing commands
    if preprocess:
        for pp_command in preprocess:
            call(pp_command, shell=True)

    # call the bugger
    # TODO: this is an awful hack for stdin/stdout piping
    if basefile is not None:
        call(['pandoc'] + pandoc_args + infiles + args[1:], cwd=basefolder)
    else:
        call(['pandoc'] + pandoc_args, cwd=basefolder)

    # call postprocessing commands
    if postprocess:
        for pp_command in postprocess:
            call(pp_command, shell=True)
    
if __name__ == '__main__':
    main()

