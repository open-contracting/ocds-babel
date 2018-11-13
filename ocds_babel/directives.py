from docutils.nodes import literal_block
from docutils.parsers.rst import Directive


class NullDirective(Directive):
    has_content = True

    def run(self):
        return [literal_block(self.block_text, language='eval_rst')]
