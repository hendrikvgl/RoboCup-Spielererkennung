"""Provides conversion from (at the time beeing) a subset of rst markup to urwid-markup

This module makes some misuse of the docutils library by extending the
docutils Writer class in a manner that was not intended by the docutils-makers.
Most specificly urwid-markup is a list of tuples of strings while a usual docutils
module would spit out a string alone.

The online-documentation for docutils sucks (2015 here). If you want to understand
what happens, I can only recommend you a look into the docutils sources.
"""

__docformat__ = 'reStructuredText'

import docutils.core
import logging
from docutils import writers, nodes


class HelpParser():
    def __init__(self, logger=None):
        if not logger:
            self.logger = logging.getLogger('record-gui')
        else:
            self.logger = logger
        self.writer = Writer()

    def parse(self, unparsed):
        doctree = docutils.core.publish_doctree(unparsed)
        urwid = self.writer.get_urwid(doctree)
        return urwid


class Writer(writers.Writer):

    supported = ('urwid',)
    """Formats this writer supports."""

    #This could be your settings:
    """
    settings_spec = (
        '"Docutils XML" Writer Options',
        None,
        (('Generate XML with newlines before and after tags.',
          ['--newlines'],
          {'action': 'store_true', 'validator': frontend.validate_boolean}),
         ('Generate XML with indents and newlines.',
          ['--indents'],
          {'action': 'store_true', 'validator': frontend.validate_boolean}),
         ('Omit the XML declaration.  Use with caution.',
          ['--no-xml-declaration'],
          {'dest': 'xml_declaration', 'default': 1, 'action': 'store_false',
           'validator': frontend.validate_boolean}),
         ('Omit the DOCTYPE declaration.',
          ['--no-doctype'],
          {'dest': 'doctype_declaration', 'default': 1,
           'action': 'store_false', 'validator': frontend.validate_boolean}),))

    settings_defaults = {'output_encoding_error_handler': 'xmlcharrefreplace'}
    """

    config_section = 'docutils_urwid writer'
    config_section_dependencies = ('writers',)

    output = None
    """Final translated form of `document`."""

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = UrwidTranslator

    def get_urwid(self, document):
        self.document = document
        self.translate()
        return self.output

    def translate(self):
        self.visitor = visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.output


class UrwidTranslator(nodes.GenericNodeVisitor):

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)

        # Reporter
        self.warn = self.document.reporter.warning
        self.error = self.document.reporter.error

        # Output
        self.output = []

        self.section_level = 0
        self.levels = {0: '#',
                       1: '*',
                       2: '=',
                       3: '-',
                       4: '^',
                       5: '"'}
    # generic visit and depart methods
    # --------------------------------

    def default_visit(self, node):
        """Default node visit method."""
        #self.output.append(('help_unparseable', node.astext()))
        self.output.append(('help_unparseable', node.__repr__() + '\n'))

    def default_departure(self, node):
        """Default node depart method."""
        pass

    # specific visit and depart methods
    # ---------------------------------
    def visit_Text(self, node):
        self.output.append(('help_default', node.astext()))

    def depart_Text(self, node):
        pass

    def visit_raw(self, node):
        self.output.append(('help_raw', node.astext()))
        raise nodes.SkipNode  # content already processed

    def visit_document(self, node):
        pass

    def visit_emphasis(self, node):
        self.output.append(('help_emphasis', node.astext()))
        raise nodes.SkipNode

    def depart_emphasis(self, node):
        pass

    def visit_title(self, node):
        text = node.astext()
        length = len(text)
        level = self.section_level
        if level not in self.levels:
            c = '~'
        else:
            c = self.levels[level]
        if level is 0:
            out = c * (length + 4) + "\n"
            out += '# ' + text + " #\n"
            out += c * (length + 4) + "\n\n"
        else:
            out = text + "\n" + c * length + "\n\n"

        self.output.append(('help_caption', out))
        raise nodes.SkipNode

    def depart_title(self, node):
        pass

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def visit_paragraph(self, node):
        pass

    def depart_paragraph(self, node):
        self.output.append("\n\n")

    def visit_literal(self, node):
        """ Do nothing
        """
        pass

    def depart_literal(self, node):
        """ Do nothing
        """
        pass
