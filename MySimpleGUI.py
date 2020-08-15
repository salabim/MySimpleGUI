"""
MySimpleGUI

See https://github.com/salabim/MySimpleGUI/blob/master/README.md for details
"""
import sys
from pathlib import Path

mysimplegui_version = "1.1.0"


class peekable:
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.peek_values = []

    def peek(self):
        if not self.peek_values:
            self.peek_values.append(next(self.iterator))
        return self.peek_values[0]

    def __iter__(self):
        return self

    def __next__(self):
        if self.peek_values:
            return self.peek_values.pop()
        else:
            return next(self.iterator)


def splitlines(s):
    return s.splitlines()


def line_to_indent(line):
    indent = 0
    for i, c in enumerate(line):
        if c == " ":
            indent += 1
        else:
            if c == "#":
                return float("inf")
            return indent
    return float("inf")


name = "PySimpleGUI"
for path in sys.path:
    source = Path(path) / (name + ".py")
    if source.is_file():
        break
    source = Path(path) / name / (name + ".py")
    if source.is_file():
        break
else:
    raise ImportError(name + ".py" + " not found")


with open(source, "r", encoding="utf-8") as f:
    lines = peekable(f.read().splitlines())

code = []
while lines.peek().startswith("#!"):
    code.append(next(lines))

code.append("")
code.append("# This is PySimpleGUI.py patched by MySimpleGUI version " + mysimplegui_version)
code.append("# Patches (c)2020  Ruud van der Ham, salabim.org")
code.append("")

for line in lines:
    if line == "    def Read(self, timeout=None, timeout_key=TIMEOUT_KEY, close=False):":  # adds attributes to Read
        code.extend(
            splitlines(
                """
    @staticmethod
    def lookup(d, key):
        try:
            return d[key]
        except KeyError:
            pass
        if isinstance(key, str):
            for prefix in ("key", "k"):
                if key.startswith(prefix):
                    try:
                        return d[int(key[len(prefix) :])]
                    except (ValueError, KeyError):
                        pass
            matches = []
            for name in d.keys():
                if isinstance(name, str):
                    norm_name = name
                    norm_name = norm_name.replace(WRITE_ONLY_KEY, "")
                    norm_name = norm_name.replace(TIMEOUT_KEY, "")
                    if not name or name[0].isdigit() or keyword.iskeyword(name):
                        norm_name = "_" + norm_name
                    norm_name = "".join(ch if ("A"[:i] + ch).isidentifier() else "_" for i, ch in enumerate(norm_name))
                    if norm_name == key:
                        matches.append(name)
            if len(matches) == 1:
                return d[matches[0]]
            if len(matches) > 1:
                raise KeyError("multiple matches for key " + repr(key) + " : " + repr(matches))
        raise KeyError(key)

    def __getitem__(self, key):
        return Window.lookup(self.AllKeysDict, key)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e) from None

"""
            )
        )

        code.append(line)
        while not lines.peek().strip().startswith("results = "):
            code.append(next(lines))
        code.append(next(lines))

        code.extend(
            splitlines(
                """
        class AttributeDict(collections.UserDict):
            def __getitem__(self, key):
                return Window.lookup(self.data, key)

            def __getattr__(self, key):
                try:
                    return self[key]
                except KeyError as e:
                    raise AttributeError(e) from None

        events, values = results
        if values is not None:
            if isinstance(values, list):
                values = {i: v for i, v in enumerate(values)}
            values = AttributeDict(values)
        results = events, values
        """
            )
        )

    elif line == "class Multiline(Element):":
        code.append(line)
        while not lines.peek().strip().startswith("self."):
            code.append(next(lines))
        code.extend(
            splitlines(
                """
        self._closed = False
        self.write_fg = None
        self.write_bg = None
        """
            )
        )

    elif line == "    def write(self, txt):":
        indent = line_to_indent(line)
        while line_to_indent(lines.peek()) > indent:  # remove original write method
            next(lines)

        code.extend(
            splitlines(
                """
    class AttributeDict(collections.UserDict):
        def __getitem__(self, key):
            return self.data[key]

        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError as e:
                raise AttributeError(e) from None

    global ansi
    codes = (
        ("reset", "\x1b[0m", "default", "ondefault"),
        ("black", "\x1b[30m", "black", None),
        ("red", "\x1b[31m", "red", None),
        ("green", "\x1b[32m", "green", None),
        ("yellow", "\x1b[33m", "yellow", None),
        ("blue", "\x1b[34m", "blue", None),
        ("magenta", "\x1b[35m", "magenta", None),
        ("cyan", "\x1b[36m", "cyan", None),
        ("white", "\x1b[37m", "white", None),
        ("default", "\x1b[39m", "default", None),
        ("onblack", "\x1b[40m", None, "black"),
        ("onred", "\x1b[41m", None, "red"),
        ("ongreen", "\x1b[42m", None, "green"),
        ("onyellow", "\x1b[43m", None, "yellow"),
        ("onblue", "\x1b[44m", None, "blue"),
        ("onmagenta", "\x1b[45m", None, "magenta"),
        ("oncyan", "\x1b[46m", None, "cyan"),
        ("onwhite", "\x1b[47m", None, "white"),
        ("ondefault", "\x1b[49m", None, "ondefault"),
    )
    code_fg = {}
    code_bg = {}

    ansi = AttributeDict()

    for name, code, fg, bg in codes:
        code_fg[code] = fg
        code_bg[code] = bg
        ansi[name] = code

    def write(self, s):
        self._check_closed()
        while s:
            for i, c in enumerate(s):
                if c == "\x1b":
                    for code in Multiline.code_bg:
                        if s[i:].startswith(code):
                            break
                    else:
                        continue
                    _print_to_element(
                        self, s[:i], sep="", end="", text_color=self.write_fg, background_color=self.write_bg
                    )
                    s = s[i + len(code) :]
                    if Multiline.code_fg[code] is not None:
                        if Multiline.code_fg[code] == "default":
                            self.write_fg = None
                        else:
                            self.write_fg = Multiline.code_fg[code]
                    if Multiline.code_bg[code] is not None:
                        if Multiline.code_bg[code] == "ondefault":
                            self.write_bg = None
                        else:
                            self.write_bg = Multiline.code_bg[code]
                    break
            else:
                _print_to_element(self, s, sep="", end="", text_color=self.write_fg, background_color=self.write_bg)
                s = ""

    def flush(self):
        self._check_closed()

    def close(self):
        self._closed = True

    def _check_closed(self):
        if self._closed:
            raise ValueError("I/O operation on closed file")

    def writable(self):
        return not self._closed

"""
            )
        )
    elif "element.TKText.insert(1.0, element.DefaultText)" in line:
        code.append(
            line.replace("element.TKText.insert(1.0, element.DefaultText)", "print(element.DefaultText, file=element)")
        )

    elif line.startswith("def SetOptions("):  # generates extra function to get/set globals
        names = {}
        code.append(line)
        while line_to_indent(lines.peek()) > 0:
            line = next(lines)
            code.append(line)
            left, *right = line.split(" = ")
            if "#" not in line and "." not in line and line.startswith("        ") and right:
                names[left.strip()] = right[0]
        names["RAISE_ERRORS"] = "raise_errors"
        for name in sorted(names, key=lambda x: names[x]):
            alias = names[name]
            code.append("def {alias}(value):".format(alias=alias))
            code.append("    global {name}".format(name=name))
            code.append("    if value is not None:")
            code.append("        {name} = value".format(name=name))
            code.append("    return {name}".format(name=name))

    elif line.startswith("def PopupError("):  # changes PopupError behaviour to raise exception
        code.append(line)

        while ":" not in lines.peek():  # read till final :
            code.append(next(lines))
        code.append(next(lines))

        code.extend(
            splitlines(
                """
    trace_details = traceback.format_stack()
    if (trace_details[-1].split(",")[0] == trace_details[-2].split(",")[0]) and RAISE_ERRORS:
        raise RuntimeError("\\n".join(args))
    """
            )
        )

    elif line == "import sys":  # add some required modules
        code.append(line)
        code.append("import keyword")
        code.append("import collections")
        code.append("import io")

    elif line.startswith("version = "):  # check compatibilty of PySimpleGUI version (at patch time)
        code.append(line)
        exec(line)
        this_pysimplegui_version = version.split()[0]
        minimal_pysimplegui_version = "4.27.4"
        this_pysimplegui_version_tuple = tuple(map(int, this_pysimplegui_version.split(".")))
        minimal_pysimplegui_version_tuple = tuple(map(int, minimal_pysimplegui_version.split(".")))

        if this_pysimplegui_version_tuple < minimal_pysimplegui_version_tuple:
            raise NotImplementedError(
                "MySimpleGUI requires PySimpleGUI >= "
                + minimal_pysimplegui_version
                + ", not "
                + this_pysimplegui_version
            )
        del version
        del this_pysimplegui_version
        del minimal_pysimplegui_version

    elif line.strip() in ("except:", "except Exception as e:"):  # exception handler insertion
        indent = line_to_indent(line)
        indentstr = " " * indent
        code.append(indentstr + "except Exception as e:")
        buffered_lines = []
        while line_to_indent(lines.peek()) > indent:
            buffered_lines.append(next(lines))
        if any((line+" dummy").split()[0] in ("pass", "return", "break") for line in buffered_lines):  # bodies with pass, return and break will not be affected
            code.extend(buffered_lines)
        else:
            code.append(indentstr + "    if RAISE_ERRORS:")
            code.append(indentstr + "        save_stdout = sys.stdout")
            code.append(indentstr + "        sys.stdout = io.StringIO()")
            code.extend(buffered_lines)
            code.append(indentstr + "    if RAISE_ERRORS:")
            code.append(indentstr + "        captured = sys.stdout.getvalue()")
            code.append(indentstr + "        sys.stdout = save_stdout")
            code.append(indentstr + "        if captured:")
            code.append(indentstr + "            raise type(e)(str(e) + '\\n' + captured) from None")

    elif "SUPPRESS_ERROR_POPUPS = False" in line:  # set global RAISE_ERRORS
        code.append(line)
        indent = line_to_indent(line)
        indentstr = indent * " "
        code.append(indentstr + "RAISE_ERRORS = True")

    elif "ix = random.randint(0, len(lf_values) - 1)" in line:  # no more random theme selection, but exception
        indent = line_to_indent(line)
        indentstr = indent * " "
        code.append((indentstr + "raise ValueError(index + ' not a valid theme')"))
        while line_to_indent(lines.peek()) >= indent:
            next(lines)

    elif line.startswith("if __name__ == "):  # no more PySimpleGUI startup screen
        break

    else:
        code.append(line)


del lines
del splitlines
del line_to_indent
del peekable

exec("\n".join(code))

if __name__ == "__main__":
    filename = "PySimpleGUI_patched.py"
    if PopupYesNo("Would you like to save the patched version to " + filename) == "Yes":
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(code))
        Popup("saved to " + str(Path(filename).resolve()), title="saved")
