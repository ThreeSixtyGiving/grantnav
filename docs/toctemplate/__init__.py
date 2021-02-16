def _get_local_toctree(builder, docname, collapse=True, **kwds):
    if 'includehidden' not in kwds:
        kwds['includehidden'] = False
    toctree = builder.env.get_toctree_for(docname, builder, collapse, **kwds)
    return toctree


def html_page_context(app, pagename, templatename, context, doctree):
    try:
        context['get_toctree'] = lambda **kw: _get_local_toctree(app.builder, pagename, **kw)
        # Toctree(app.builder.env).get_toc_for(app.builder.env.config.master_doc, app.builder)
    except KeyError:
        pass


def setup(app):
    app.connect('html-page-context', html_page_context)
