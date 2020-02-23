# Jinja2Content Plugin for Pelican

[![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/jinja2content/build)](https://github.com/pelican-plugins/jinja2content/actions) [![PyPI Version](https://img.shields.io/pypi/v/pelican-jinja2content)](https://pypi.org/project/pelican-jinja2content/)

This plugin allows the use of Jinja2 directives inside your Pelican articles and pages.

In this approach, your content is *first* rendered by the Jinja template engine. The result is then passed to the normal Pelican reader as usual. There are two consequences for usage. First, this means the Pelican context and Jinja variables [usually visible](http://docs.getpelican.com/en/stable/themes.html#templates-and-variables) to your article or page template are _not_ available at rendering time. Second, it means that if any of your input content could be parsed as Jinja directives, they will be rendered as such. This is unlikely to happen accidentally, but it’s good to be aware of.

All input that needs Pelican variables such as `article`, `category`, etc., should be put inside your *theme’s* templating. As such, the main use of this plugin is to automatically generate parts of your articles or pages.

Markdown, reStructured Text, and HTML input are all supported. Note that by enabling this plugin, all input files of these file types will be pre-processed with the Jinja renderer. It is not currently supported to selectively enable or disable `jinja2content` for only some of these input sources.


Example
-------

One usage is to embed repetitive HTML in Markdown articles. Since Markdown doesn’t allow customization of layout, if anything more sophisticated than just displaying an image is necessary, one is forced to embed HTML in Markdown articles (i.e. hard-code `<div>` tags and then select them from the theme’s CSS). However, with `jinja2content`, one can do the following:

File `my-cool-article.md`
```
# My cool title

My cool content.

{% from 'img_desc.html' import img_desc %}
{{ img_desc("/images/my-cool-image.png",
    "This is a cool tooltip",
    "This is a very cool image.") }}
```

Where file `img_desc.html` contains:
```
{% macro img_desc(src, title='', desc='') -%}
<div class="img-desc">
  <p><img src="{{ src }}" title="{{ title }}"></p>
  {% if desc %}
  <p><em>{{ desc }}</em></p>
  {% endif %}
</div>
{%- endmacro %}
```

The result will be:
```
# My cool title

My cool content.

<div class="img-desc">
  <p><img src="/images/my-cool-image.png" title="This is a cool tooltip"></p>
  <p><em>This is a very cool image.</em></p>
</div>
```

After this, the Markdown will be rendered into HTML and only then the theme’s templates will be applied.

In this way, Markdown articles have more control over the content that is passed to the theme’s `article.html` template, without the need to pollute the Markdown with HTML. Another added benefit is that now `img_desc` is reusable across articles.

Note that templates rendered with `jinja2content` can contain Markdown as well as HTML, since they are added before the Markdown content is converted to HTML.


Installation
------------

This plugin can be installed via:

    pip install pelican-jinja2content


Configuration
-------------

This plugin accepts the setting `JINJA2CONTENT_TEMPLATES` which should be set to a list of paths relative to `PATH` (the main content directory, usually `"content"`). `jinja2content` will look for templates inside these directories, in order. If they are not found in any, the theme’s templates folder is used.


Extending
---------

This plugin is structured such that it should be quite easy to extend readers for other file types to also render Jinja template logic. It should be sufficient to create a new reader class that inherits from the `JinjaContentMixin` and then your desired reader class. See class definitions in the source for examples.


Contributing
------------

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.


Acknowledgements
----------------

- Original implementation by @joachimneu and re-worked by @Leonardo.
- Updated to support reST and HTML input by @micahjsmith.
- Converted to new plugin format by @justinmayer.
- Replaces [pelican-jinj2content](https://github.com/joachimneu/pelican-jinja2content/tree/f73ef9b1ef1ee1f56c80757b4190b53f8cd607d1), which had become unmaintained.


[existing issues]: https://github.com/pelican-plugins/jinja2content/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html
