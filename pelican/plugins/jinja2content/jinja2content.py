"""
jinja2content.py
----------------

Pelican plugin that processes Markdown files as jinja templates.

"""

import os
from tempfile import NamedTemporaryFile

from jinja2 import ChoiceLoader, Environment, FileSystemLoader

from pelican import signals
from pelican.readers import HTMLReader, MarkdownReader, RstReader
from pelican.utils import pelican_open


class JinjaContentMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # will look first in 'JINJA2CONTENT_TEMPLATES', by default the
        # content root path, then in the theme's templates
        local_dirs = self.settings.get("JINJA2CONTENT_TEMPLATES", ["."])
        local_dirs = [
            os.path.join(self.settings["PATH"], folder) for folder in local_dirs
        ]
        theme_dir = os.path.join(self.settings["THEME"], "templates")

        loaders = [FileSystemLoader(_dir) for _dir in local_dirs + [theme_dir]]
        if "JINJA_ENVIRONMENT" in self.settings:  # pelican 3.7
            jinja_environment = self.settings["JINJA_ENVIRONMENT"]
        else:
            jinja_environment = {
                "trim_blocks": True,
                "lstrip_blocks": True,
                "extensions": self.settings["JINJA_EXTENSIONS"],
            }
        self.env = Environment(loader=ChoiceLoader(loaders), **jinja_environment)
        if "JINJA_FILTERS" in self.settings:
            self.env.filters.update(self.settings["JINJA_FILTERS"])
        if "JINJA_GLOBALS" in self.settings:
            self.env.globals.update(self.settings["JINJA_GLOBALS"])
        if "JINJA_TEST" in self.settings:
            self.env.tests.update(self.settings["JINJA_TESTS"])

    def read(self, source_path):
        with pelican_open(source_path) as text:
            text = self.env.from_string(text).render()

        with NamedTemporaryFile(delete=False) as f:
            f.write(text.encode())
            f.close()
            content, metadata = super().read(f.name)
            os.unlink(f.name)
            return content, metadata


class JinjaMarkdownReader(JinjaContentMixin, MarkdownReader):
    pass


class JinjaRstReader(JinjaContentMixin, RstReader):
    pass


class JinjaHTMLReader(JinjaContentMixin, HTMLReader):
    pass


def add_reader(readers):
    for Reader in [JinjaMarkdownReader, JinjaRstReader, JinjaHTMLReader]:
        for ext in Reader.file_extensions:
            readers.reader_classes[ext] = Reader


def register():
    signals.readers_init.connect(add_reader)
