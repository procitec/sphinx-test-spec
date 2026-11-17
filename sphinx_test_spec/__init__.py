def setup(app):
    # Keep importing result-processing modules independent from Sphinx itself.
    # Sphinx imports this function when loading the extension and only then
    # needs the extension-specific modules.
    from .main import setup as setup_extension

    return setup_extension(app)
