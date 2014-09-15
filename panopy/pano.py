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

def process_arg(key, value):
    global basename

    if key == 'o' or key == 'output':
        value = re.sub(r'%', basename, value)
    if value is None:
        return ['-{longkey}{key}'.format(longkey='-' if len(key) > 1 else '', key=key)]
    elif isinstance(value, basestring):
        value = os.path.expanduser(value)
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

    # check if we have a template name in here, else quit
    if len(args) > 1:
        template_name = args[1]
        args = args[2:]
    else:
        sys.exit('No template named')

    #print(args)

    (basefolder, basefile) = os.path.split(args[0])
    basefolder = '.' if basefolder == '' else basefolder
    basename = os.path.splitext(basefile)[0]
    #print(basename)

    # load templates
    with open(os.path.expanduser(os.path.join(DEFAULT_PATH))) as fin:
        templates = yaml.load_all(fin)
        templates = [x for x in templates if x is not None]

    # merge the templates together
    all_templates = dict()
    for template in templates:
        all_templates.update(template)

    # start with default template
    template = update_template(dict(), DEFAULT_TEMPLATE)
    #template = all_templates[DEFAULT_TEMPLATE] if '__default__' in all_templates else dict()

    # get template
    template = update_template(template, template_name, [DEFAULT_TEMPLATE])
    #if template_name not in all_templates:
        #sys.exit('Template ' + template_name + ' not found in configuration')
    #else:
        ## load inherits settings
        #pretemp = all_templates[template_name]
        #if KW_INHERIT in pretemp:
            #if pretemp[KW_INHERIT] not in 
        #template = all_templates[template_name]

    if debug:
        print(template)

    pandoc_args = [arg for (k,v) in template.iteritems() for arg in process_arg(k,v)]

    if debug:
        print(pandoc_args)

    call(['pandoc'] + pandoc_args + [basefile] + args[1:], cwd=basefolder)
    
if __name__ == '__main__':
    main()

