# isobar

isobar is a Python library for creating and manipulating musical patterns, designed for use in algorithmic composition, generative music and sonification. It makes it quick and easy to express complex musical ideas, and can send and receive events from various different sources: MIDI, OSC, SocketIO, and .mid files.

## Documentation

        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.

!!! tip "Installation in a virtual environment"

    The best way to make sure that you end up with the correct versions and
    without any incompatibility problems between packages it to use a **virtual
    environment**. Don't know what this is or how to set it up? We recommend
    to start by reading a [tutorial on virtual environments][6] for Python.

!!! warning "Installation on macOS"

    When you're running the pre-installed version of Python on macOS, `pip`
    tries to install packages in a folder for which your user might not have
    the adequate permissions. There are two possible solutions for this:

=== "Unix"

    ```
    docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
    ```

=== "Windows"

    ```
    docker run --rm -it -p 8000:8000 -v "%cd%":/docs squidfunk/mkdocs-material
    ```
