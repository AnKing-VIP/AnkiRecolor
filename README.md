# Development
## Setup
After cloning the project, run the following command
```bash
git submodule update --init --recursive
```
The command installs [ankiaddonconfig](https://github.com/BlueGreenMagick/ankiaddonconfig/) as a git submodule.

To update icons_rc.py file after changes to [icons.qrc](src/addon/AnKing/icons.qrc), run the following command, then edit the file to add `-> None` type hint.
```bash
pyrcc5 ./src/addon/AnKing/icons.qrc -o ./src/addon/icons_rc.py
```

## Tests & Formatting
This project uses [mypy](https://github.com/python/mypy) type checking for Python, and [standardjs](https://github.com/standard/standard) for formatting Javascript.

```
python -m mypy .
npx standard --fix
```

You will need to install the following python packages to run mypy: 
```
python -m pip install aqt PyQt5-stubs mypy
```

This project doesn't use a strict python formatter. Even so, please make it look pretty enough :)

# Building ankiaddon file
After cloning the repo, go into the repo directory and run the following command to install the git submodule [ankiaddonconfig](https://github.com/BlueGreenMagick/ankiaddonconfig/)
```
git submodule update --init src/addon/ankiaddonconfig
```
After installing the git submodule, run the following command to create an `recolor.ankiaddon` file
```
cd src/addon ; zip -r ../../recolor.ankiaddon * ; cd ../../
```