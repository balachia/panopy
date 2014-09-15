import yaml
import os.path
import sys
import re
from subprocess import call

DEFAULT_PATH = '~/.pandoc/panopy.templates'

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


def main():
    global basename

    # check if we have a template name in here, else quit
    args = sys.argv
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
        #print(template)
        all_templates.update(template)

    # get template
    if template_name not in all_templates:
        sys.exit('Template ' + template_name + ' not found in configuration')
    else:
        template = all_templates[template_name]

    #print(template)

    #pandoc_args = ['pandoc']
    #for (k,v) in template.iteritems()
    pandoc_args = [arg for (k,v) in template.iteritems() for arg in process_arg(k,v)]
    #print(pandoc_args)

    call(['pandoc'] + pandoc_args + [basefile] + args[1:], cwd=basefolder)
    
if __name__ == '__main__':
    main()

