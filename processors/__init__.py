import os

# Automatically set the __all__ variable with all
# the available plugins.

processor_dir = "processors"

__all__ = []
for filename in os.listdir(processor_dir):
    filename = processor_dir + "/" + filename
    if os.path.isfile(filename):
        basename = os.path.basename(filename)
        base, extension = os.path.splitext(basename)
        if extension == ".py" and not basename.startswith("_"):
            __all__.append(base)
