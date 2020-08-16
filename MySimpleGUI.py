"""
MySimpleGUI

See https://github.com/salabim/MySimpleGUI/blob/master/README.md for details
"""
import sys
from pathlib import Path

version = __version__ = "1.1.0"


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

class CodeList(list):
    def add(self, spec, indent=0):
        if isinstance(spec, str):
            lines = spec.splitlines()
        else:
            lines = spec
        if indent == 0:                 
            self.extend(lines)
        else:
            indentstr= " " * indent
            for line in lines:
                self.append(indentstr + line)

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

code = CodeList()
while lines.peek().startswith("#!"):
    code.add(next(lines))

code.add("""\

# This is {name}.py patched by MySimpleGUI version {version}
# Patches (c)2020  Ruud van der Ham, salabim.org

""".format(version = version, name=name))

for line in lines:
    if "def Read(self, timeout=None, timeout_key=TIMEOUT_KEY, close=False):" in line:  # adds attributes to Read
        indent = line_to_indent(line)
        code.add("""\
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
        raise AttributeError(e) from None""", indent = indent)
            
        

        code.add(line)
        while not lines.peek().strip().startswith("results = "):
            code.add(next(lines))
        line = next(lines)
        code.add(line)
        indent = line_to_indent(line)
        code.add("""\
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
""", indent=indent)

    elif line == "class Multiline(Element):":
        code.add(line)
        while not lines.peek().strip().startswith("self."):
            code.add(next(lines))
        indent = line_to_indent(lines.peek())
        code.add("""\
self._closed = False
self.write_fg = None
self.write_bg = None""", indent=indent)

    elif "def write(self, txt):" in line:

        indent = line_to_indent(line)
        while line_to_indent(lines.peek()) > indent:  # remove original write method
            next(lines)

        code.add("""\
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
    return not self._closed""", indent = indent)

    elif "element.TKText.insert(1.0, element.DefaultText)" in line:
        code.add(
            line.replace("element.TKText.insert(1.0, element.DefaultText)", "print(element.DefaultText, file=element)")
        )

    elif line.startswith("def SetOptions("):  # generates extra function to get/set globals
        names = {}
        code.add(line)
        while line_to_indent(lines.peek()) > 0:
            line = next(lines)
            code.add(line)
            left, *right = line.split(" = ")
            if "#" not in line and "." not in line and line.startswith("        ") and right:
                names[left.strip()] = right[0]
        names["RAISE_ERRORS"] = "raise_errors"
        for name in sorted(names, key=lambda x: names[x]):
            alias = names[name]
            code.add("""\
def {alias}(value):
    global {name}
    if value is not None:
        {name} = value
    return {name}""".format(name=name, alias=alias))

    elif line.startswith("def PopupError("):  # changes PopupError behaviour to raise exception
        indent = line_to_indent(line)

        code.add(line)
        while ":" not in lines.peek():  # read till final :
            code.add(next(lines))
        code.add(next(lines))
        
        code.add("""
trace_details = traceback.format_stack()
if (trace_details[-1].split(",")[0] == trace_details[-2].split(",")[0]) and RAISE_ERRORS:
    raise RuntimeError("\\n".join(args))""", indent=indent+4)

    elif line == "import sys":  # add some required modules
        code.add("""\
import keyword
import collections
import io
import sys""")

    elif line.startswith("version = "):  # check compatibilty of PySimpleGUI version (at patch time)
        code.add(line)
        exec(line)
        this_pysimplegui_version = version.split()[0]
        minimal_pysimplegui_version = "4.27.4"
        this_pysimplegui_version_tuple = tuple(map(int, this_pysimplegui_version.split(".")))
        minimal_pysimplegui_version_tuple = tuple(map(int, minimal_pysimplegui_version.split(".")))

        if this_pysimplegui_version_tuple < minimal_pysimplegui_version_tuple:
            raise NotImplementedError(
                "MySimpleGUI requires " + name + " >= "
                + minimal_pysimplegui_version
                + ", not "
                + this_pysimplegui_version
            )
        del version
        del this_pysimplegui_version
        del minimal_pysimplegui_version

    elif line.strip() in ("except:", "except Exception as e:"):  # exception handler insertion
        indent = line_to_indent(line)
        code.add("except Exception as e:", indent=indent)
        buffered_lines = []
        while line_to_indent(lines.peek()) > indent:
            buffered_lines.append(next(lines))
        requires_raise = False
        for line in buffered_lines:
            if line.strip().startswith("pass") or line.strip().startswith("return") or line.strip().startswith("break"):
                requires_raise = False
                break
            if line.strip().startswith("print("):
                requires_raise = True
        if requires_raise:
            code.add("""\
if RAISE_ERRORS:
    save_stdout = sys.stdout
    sys.stdout = io.StringIO()""", indent=indent+4)
            code.add(buffered_lines)

            code.add("""\

if RAISE_ERRORS:
    captured = sys.stdout.getvalue()
    sys.stdout = save_stdout
    if captured:
        raise type(e)(str(e) + '\\n' + captured) from None""", indent=indent+4)
        else:
            code.add(buffered_lines)

    elif "SUPPRESS_ERROR_POPUPS = False" in line:  # set global RAISE_ERRORS
        code.add(line)
        indent = line_to_indent(line)
        code.add("RAISE_ERRORS = True", indent=indent)

    elif "ix = random.randint(0, len(lf_values) - 1)" in line:  # no more random theme selection, but exception
        indent = line_to_indent(line)
        code.add("raise ValueError(index + ' not a valid theme')", indent=indent)
        while line_to_indent(lines.peek()) >= indent:
            next(lines)

    elif line.startswith("if __name__ == "):  # no more PySimpleGUI startup screen
        break

    else:
        code.add(line)


del lines
del splitlines
del line_to_indent
del peekable


if False:
    filename = name + "_patched.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(code))
        
exec("\n".join(code))

if __name__ == "__main__":
    filename = name + "_patched.py"
    if PopupYesNo("Would you like to save the patched version to " + filename) == "Yes":
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(code))
        Popup("saved to " + str(Path(filename).resolve()), title="saved")
