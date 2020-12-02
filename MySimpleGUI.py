#   __  __         ____   _                    _         ____  _   _  ___
#  |  \/  | _   _ / ___| (_) _ __ ___   _ __  | |  ___  / ___|| | | ||_ _|
#  | |\/| || | | |\___ \ | || '_ ` _ \ | '_ \ | | / _ \| |  _ | | | | | |
#  | |  | || |_| | ___) || || | | | | || |_) || ||  __/| |_| || |_| | | |
#  |_|  |_| \__, ||____/ |_||_| |_| |_|| .__/ |_| \___| \____| \___/ |___|
#           |___/                      |_|
#
# See https://github.com/salabim/MySimpleGUI/blob/master/README.md for details

import sys
from pathlib import Path
import os
import collections
import datetime

pysimplegui_name = "PySimpleGUI"
pysimplegui_patched_name = pysimplegui_name + "_patched"
__version__ = "1.1.16"


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


registered_patches = collections.defaultdict(int)
registered_patches[37] = 0


def register_patch(n):
    registered_patches[n] += 1


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
            if spec == "":
                lines = [""]
            else:
                lines = spec.splitlines()
        else:
            lines = spec

        indentstr = " " * indent
        for line in lines:
            self.append(indentstr + line.replace("\x1b", "\\x1b"))


for path in sys.path:
    pysimplegui_path = Path(path) / (pysimplegui_name + ".py")
    if pysimplegui_path.is_file():
        break
    pysimplegui_path = Path(path) / pysimplegui_name / (pysimplegui_name + ".py")
    if pysimplegui_path.is_file():
        break
else:
    raise ImportError(pysimplegui_name + ".py" + " not found")

mysimplegui_path = Path(__file__)

pysimplegui_patched_path = mysimplegui_path.parent / (pysimplegui_patched_name + ".py")

patch_info = "# patch info "
stat = os.stat(pysimplegui_path)
patch_info += "{st_mtime:16.3f}{st_size:8d}".format(st_mtime=stat.st_mtime, st_size=stat.st_size)
stat = os.stat(mysimplegui_path)
patch_info += "#{st_mtime:16.3f}{st_size:8d}".format(st_mtime=stat.st_mtime, st_size=stat.st_size)

pysimplegui_patched_match = False
if pysimplegui_patched_path.is_file():
    try:
        with open(pysimplegui_patched_path, "rb") as f:
            f.seek(-len(patch_info), os.SEEK_END)
            read_patch_info = f.read().decode("utf-8")
            if read_patch_info == patch_info:
                pysimplegui_patched_match = True
    except OSError:
        pass

if not pysimplegui_patched_match:
    with open(pysimplegui_path, "r", encoding="utf-8") as f:
        lines = peekable(f.read().splitlines())

    code = CodeList()
    while lines.peek().startswith("#!"):
        code.add(next(lines))

    code.add(
        """\
# This is {pysimplegui_name}.py patched by MySimpleGUI version {version}
# Patches (c)2020  Ruud van der Ham, salabim.org

""".format(
            version=__version__, pysimplegui_name=pysimplegui_name
        )
    )

    this_class = "?"
    for line in lines:
        if "is True" in line and line.strip()[0] != ":":
            s = line.split("is True", 1)[0]
            s1 = s.split()[-1]
            if s1 + " is True" not in line:
                register_patch(37)
            line = line.replace(s1 + " is True", "bool(" + s1 + ")")

        if "is False" in line and line.strip()[0] != ":":
            s = line.split("is False", 1)[0]
            s1 = s.split()[-1]
            if s1 + " is False" not in line:
                register_patch(37)
            line = line.replace(s1 + " is False", "(not " + s1 + " and " + s1 + " is not None)")

        if line.startswith("class "):
            parts = line.split()
            if len(parts) > 1:
                this_class = parts[1].split("(")[0].replace(":", "").strip()

        if line.strip().startswith("self.config_count = 0"):
            register_patch(0)
            code.add(line)
            indent = line_to_indent(line)
            code.add(
                """\
self.internal = Window.Internal(self)""",
                indent=indent,
            )

        elif "def Read(self, timeout=None, timeout_key=TIMEOUT_KEY, close=False):" in line:  # adds attributes to Read
            register_patch(1)
            indent = line_to_indent(line)
            code.add(
                """\
@staticmethod
def _lookup(d, key):
    try:
        return d[key]
    except KeyError:
        pass
    if isinstance(key, str):
        for prefix in ("key", "k", "_"):
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

def type_name(self):
    return "Window  id: " + str(id(self))

def __repr__(self):
    result = [self.type_name()]
    if not hasattr(self, "taken"):
        self.taken = True
        for k in sorted(self.__dict__.keys(), key=str.upper):
            v = self.__dict__[k]
            if v not in (None, (None,None)):
                if k in ("ParentContainer", "ParentForm"):
                    if hasattr(v, "type_name"):
                        result.append("    " + k + " = " + v.type_name())
                    else:
                        result.append("    " + k + " = " + repr(v))
                else:
                    if k not in ("AllKeysDict"):
                        if k == "WindowIcon":
                            v = str(v)[:80] + "..."
                        if isinstance(v, list):
                            v  = list_repr(v)
                        l = repr(v).split("\\n")
                        result.append("    " + k + " = " + l[0])
                        for x in l[1:]:
                            result.append("    " + x)

        for k, v in self.AllKeysDict.items():
            result.append("    [" + repr(k) + "] = " + v.type_name())
        del self.taken
    return "\\n".join(result)

class Internal:
    def __init__(self, window):
        self._window = window
    def __getattr__(self, v):
        return super(Window, self._window).__getattribute__(v)

def __getattribute__(self, key):
    if key in super().__getattribute__("AllKeysDict"):
        trace_details = traceback.format_stack()
        if trace_details[-1].split(",")[0] != trace_details[-2].split(",")[0]: # internal or external?
            return self[key]
    return super().__getattribute__(key)

def __getattr__(self, key):
    try:
        return self[key]
    except KeyError as e:
        raise AttributeError(e) from None
""",
                indent=indent,
            )

            code.add(line)
            while not lines.peek().strip().startswith("return results"):
                code.add(next(lines))
            line = next(lines)
            indent = line_to_indent(line)
            code.add(
                """\
class AttributeDict(collections.UserDict):
    def __getitem__(self, key):
        return Window._lookup(self.data, key)

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
""",
                indent=indent,
            )
            code.add(line)  # the original return result line

        elif line.strip().startswith("def _RightClickMenuCallback(self, event):"):
            register_patch(2)
            indent = line_to_indent(line)
            code.add(
                """\
def type_name(self):
    type_name = self.Type
    type_name = type_name.replace("option menu","OptionMenu")
    type_name = type_name.replace("spind","Spin")
    type_name = type_name.replace("tabgroup","TabGroup")
    type_name = type_name.replace("menubar","Menu")
    type_name = type_name.replace("progressbar","ProgressBar")
    type_name = type_name.replace("statusbar","StatusBar")
    type_name = type_name.capitalize()
    return type_name + " id: " + str(id(self))

def __repr__(self):
    result = [self.type_name()]
    if not hasattr(self, "taken"):
        self.taken = True

        for k in sorted(self.__dict__.keys(), key=str.upper):
            v = self.__dict__[k]
            if v not in (None, (None,None)):
                if k in ("ParentContainer", "ParentForm"):
                    if hasattr(v, "type_name"):
                        result.append("    " + k + " = " + v.type_name())
                    else:
                        result.append("    " + k + " = " + repr(v))
                else:
                    if k != "Type":
                        if isinstance(v, list):
                            v  = list_repr(v)
                        l = repr(v).split("\\n")
                        result.append("    " + k + " = " + l[0])
                        for x in l[1:]:
                            result.append("    " + x)
        del self.taken
    return "\\n".join(result)
    

def freeze(self, enabled=True):
    if enabled:
        return Column([[self]], pad=(0,0))
    else:
        return self""",
                indent=indent,
            )

            code.add(line)
        elif line.startswith("class Element"):
            register_patch(3)
            code.add(
                """\
class list_repr(list):
    def type_name(self):
        return "list"

    def __repr__(self):
        result = [self.type_name()]
        for v in self:
            if isinstance(v, list):
                v  = list_repr(v)

            l = repr(v).split("\\n")
            for x in l:
                result.append("    " + x)
        return "\\n".join(result)"""
            )

            code.add(line)
        elif line.strip().startswith("return self.FindElement(key)"):  # this the original Window.__getitem__ contents:
            register_patch(4)
            code.add(line.replace("return self.FindElement(key)", "return Window._lookup(self.AllKeysDict, key)"))

        elif line.strip().startswith("if file_name"):
            register_patch(5)
            code.add(line.replace("file_name", "file_name or self is target_element"))

        elif line.strip() == "if folder_name:":
            register_patch(6)
            code.add(line.replace("folder_name", "True"))

        elif "target=target" in line:
            register_patch(7)
            code.add(line.replace("target=target", "target=target or key or k or button_text"))

        elif line.strip().startswith("if element.Type == ELEM_TYPE_INPUT_TEXT:"):
            register_patch(8)
            code.add(line)
            if lines.peek().strip().startswith("try:"):
                while True:
                    line = next(lines)
                    if line.strip().startswith("elif"):
                        break
                    code.add(line)
                indent = line_to_indent(line)
                code.add(
                    """\
elif element.Type == ELEM_TYPE_TEXT:
    value = element.TKStringVar.get()""",
                    indent=indent,
                )
                code.add(line)

        elif "ELEM_TYPE_SEPARATOR):" in line:
            register_patch(9)
            code.add(line.replace("ELEM_TYPE_SEPARATOR", "ELEM_TYPE_SEPARATOR, ELEM_TYPE_TEXT"))

        elif "element.Type != ELEM_TYPE_TEXT and \\" in line:
            register_patch(10)
            pass  # remove this condition

        elif "if element.Key in key_dict.keys():" in line:
            register_patch(11)
            #        code.add(line)
            indent = line_to_indent(line)
            code.add(
                """\
if element.Key == "AllKeysDictxx":
    raise KeyError('key "AllKeysDict" not allowed in layout')""",
                indent=indent,
            )

            while line_to_indent(lines.peek()) > indent:  # remove original code
                next(lines)

        elif "self.AllKeysDict = self._BuildKeyDictForWindow(self, self, dict)" in line:
            register_patch(34)
            indent = line_to_indent(line)
            code.add(line)
            code.add(
                """\
self.AllKeysDictnewdict = {}
for k, v in dict.items():
    if not(isinstance(k, tuple) and len(k) == 2 and k[0] == NONE_KEY):
        self.AllKeysDictnewdict[k] = v
for k, v in dict.items():
    if isinstance(k, tuple) and len(k) == 2 and k[0] == NONE_KEY:
        for i in itertools.count(1):
            if i not in self.AllKeysDictnewdict:
                k = i
                v.Key = i
                self.AllKeysDictnewdict[k] = v
                break""",
                indent=indent,
            )

        elif "element.Key = top_window.DictionaryKeyCounter" in line:
            register_patch(35)
            indent = line_to_indent(line)
            code.add("element.Key = (NONE_KEY, top_window.DictionaryKeyCounter)", indent=indent)

        elif line.startswith("COLOR_SYSTEM_DEFAULT = "):
            register_patch(36)
            code.add("NONE_KEY = object()")
            code.add(line)

        elif line == "class Multiline(Element):":
            register_patch(12)
            code.add(line)
            while not lines.peek().strip().startswith("self."):
                code.add(next(lines))
            indent = line_to_indent(lines.peek())
            code.add(
                """\
self._closed = False
self.write_fg = None
self.write_bg = None
self.write_font = None""",
                indent=indent,
            )

        elif "def write(self, txt):" in line and this_class == "Multiline":
            register_patch(13)

            indent = line_to_indent(line)
            while line_to_indent(lines.peek()) > indent:
                next(lines)

            code.add(
                """\
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
    ("font", "\x1b[font", None, None),
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
                        if s[i:].startswith("\x1b[font"):
                            parts = s[i:].split('|',1)
                            if len(parts) >1:
                                fontspec = parts[0][6:]
                                use = parts[0]+"|"
                                break
                        else:
                            use = code
                            break
                else:
                    continue
                _print_to_element(
                    self, s[:i], sep="", end="", text_color=self.write_fg, background_color=self.write_bg, font=self.write_font,
                )
                s = s[i + len(use) :]
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
                if code == "\x1b[0m":
                    self.write_font = None
                if code == "\x1b[font":
                    self.write_font = fontspec
                break
        else:
            _print_to_element(self, s, sep="", end="", text_color=self.write_fg, background_color=self.write_bg, font=self.write_font)
            s = ""

def flush(self):
    self._check_closed()

def close(self):
    self._closed = True

def _check_closed(self):
    if self._closed:
        raise ValueError("I/O operation on closed file")

def writable(self):
    return not self._closed""",
                indent=indent,
            )

        elif "element.TKText.insert(1.0, element.DefaultText)" in line:
            register_patch(14)
            code.add(
                line.replace(
                    "element.TKText.insert(1.0, element.DefaultText)", "print(element.DefaultText, file=element)"
                )
            )

        elif "background_color_for_value=background_color" in line:
            register_patch(15)
            code.add(
                line.replace(
                    "background_color_for_value=background_color",
                    "background_color_for_value=background_color, font_for_value=font",
                )
            )

        elif "background_color_for_value=None" in line:
            register_patch(16)
            code.add(
                line.replace("background_color_for_value=None", "background_color_for_value=None, font_for_value=None")
            )

        elif "if background_color_for_value is not None or text_color_for_value is not None:" in line:
            register_patch(17)
            code.add(line.replace(":", " or font_for_value is not None:"))

        elif "str(background_color_for_value)+')'" in line:
            register_patch(18)
            code.add(
                line.replace(
                    "str(background_color_for_value)+')'",
                    "str(background_color_for_value)+',' + str(font_for_value)+')'",
                )
            )

        elif "text_color=None, background_color=None" in line and line.strip().startswith(
            ("def Print", "def print", "def _print_to_element")
        ):
            register_patch(19)
            code.add(
                line.replace(
                    "text_color=None, background_color=None", "text_color=None, background_color=None, font=None"
                )
            )

        elif "text_color=text_color, background_color=background_color" in line and line.strip().startswith(
            "_print_to_element"
        ):
            register_patch(20)
            code.add(
                line.replace(
                    "text_color=text_color, background_color=background_color",
                    "text_color=text_color, background_color=background_color, font=font",
                )
            )

        elif "if background_color_for_value is not None:" in line:
            register_patch(21)
            indent = line_to_indent(line)
            code.add(
                """\
if font_for_value is not None:
    self.TKText.tag_configure(tag, font=font_for_value)""",
                indent=indent,
            )
            code.add(line)

        elif "if element.Key is not None:" in line:
            register_patch(22)
            code.add(
                line.replace(
                    "if element.Key is not None:",
                    "if element.Key is not None and isinstance(element.Key, collections.abc.Hashable):",
                )
            )

        elif line.strip().startswith("form.ReturnValuesDictionary[element.Key] = value"):
            register_patch(23)
            indent = line_to_indent(line)
            code.add(
                """\
if isinstance(element.Key, collections.abc.Hashable):
    form.ReturnValuesDictionary[element.Key] = value""",
                indent=indent,
            )

        elif line.startswith("def SetOptions("):  # generates extra function to get/set globals
            register_patch(24)
            names = {}
            code.add(line)
            while line_to_indent(lines.peek()) > 0:
                line = next(lines)
                code.add(line)
                left, *right = line.split(" = ")
                if "#" not in line and "." not in line and line.startswith("        ") and right:
                    names[left.strip()] = right[0]
            code.add(
                """\
class _TemporaryChange:
    def __init__(self, value, global_name, globals):
        self.globals=globals
        self.save_value = self.globals[global_name]
        self.global_name=global_name
        self.globals[global_name] = value
    def __enter__(self):
        return self.save_value
    def __exit__(self, *args):
        self.globals[self.global_name] = self.save_value
    def __call__(self):
        return self.globals[self.global_name]"""
            )

            names["RAISE_ERRORS"] = "raise_errors"
            for name in sorted(names, key=lambda x: names[x]):
                alias = names[name]
                code.add(
                    """\
def {alias}(value = None):
    global {name}
    if value is None:
        return {name}
    return _TemporaryChange(value, '{name}', globals())""".format(
                        name=name, alias=alias
                    )
                )

        elif line.startswith("def PopupError("):  # changes PopupError behaviour to raise exception
            register_patch(25)
            indent = line_to_indent(line)

            code.add(line)
            while ":" not in lines.peek():  # read till final :
                code.add(next(lines))
            code.add(next(lines))

            code.add(
                """
trace_details = traceback.format_stack()
if (trace_details[-1].split(",")[0] == trace_details[-2].split(",")[0]) and RAISE_ERRORS:
    raise RuntimeError("\\n".join(args))""",
                indent=indent + 4,
            )

        elif line == "import queue":  # add some required modules
            register_patch(26)
            code.add(line)
            code.add(
                """\
import keyword
import collections
import io"""
            )

        elif line.startswith("version = "):  # check compatibilty of PySimpleGUI version (at patch time)
            register_patch(27)
            code.add(line)
            save__version__ = __version__
            exec(line)
            __version__ = save__version__
            this_pysimplegui_version = version.split()[0]
            minimal_pysimplegui_version = "4.27.4"
            this_pysimplegui_version_tuple = tuple(map(int, this_pysimplegui_version.split(".")))
            minimal_pysimplegui_version_tuple = tuple(map(int, minimal_pysimplegui_version.split(".")))

            if this_pysimplegui_version_tuple < minimal_pysimplegui_version_tuple:
                raise NotImplementedError(
                    "MySimpleGUI requires "
                    + pysimplegui_name
                    + " >= "
                    + minimal_pysimplegui_version
                    + ", not "
                    + this_pysimplegui_version
                )
            del version
            del this_pysimplegui_version
            del minimal_pysimplegui_version

        elif line.strip() in ("except:", "except Exception as e:"):  # exception handler insertion
            indent = line_to_indent(line)
            exception_line = line
            buffered_lines = []
            while line_to_indent(lines.peek()) > indent:
                line = next(lines)
                if line.strip().startswith("warnings.warn"):
                    line = line.replace("warnings.warn", "print")
                buffered_lines.append(line)
            requires_raise = False
            for line in buffered_lines:
                if (
                    line.strip().startswith("pass")
                    or line.strip().startswith("return")
                    or line.strip().startswith("break")
                ):
                    requires_raise = False
                    break
                if line.strip().startswith("print("):
                    requires_raise = True
            if requires_raise:
                code.add("except Exception as e:", indent=indent)
                code.add(
                    """\
if RAISE_ERRORS:
    save_stdout = sys.stdout
    sys.stdout = io.StringIO()""",
                    indent=indent + 4,
                )
                code.add(buffered_lines)

                code.add(
                    """\
if RAISE_ERRORS:
    captured = sys.stdout.getvalue()
    sys.stdout = save_stdout
    if captured:
        raise type(e)(str(e) + '\\n' + captured) from None""",
                    indent=indent + 4,
                )
            else:
                code.add(exception_line)
                code.add(buffered_lines)

        #    elif line.strip().startswith("if key in settings.dict:"):
        #        indent = line_to_indent(line)
        #        while not lines.peek().strip().startswith("else:"):
        #            code.add(next(lines).strip(), indent=indent)
        #        while line_to_indent(next(lines)) == indent:
        #            next(lines)

        elif "SUPPRESS_ERROR_POPUPS = False" in line:  # set global RAISE_ERRORS
            register_patch(29)
            code.add(line)
            indent = line_to_indent(line)
            code.add("RAISE_ERRORS = True", indent=indent)

        elif "ix = random.randint(0, len(lf_values) - 1)" in line:  # no more random theme selection, but exception
            register_patch(30)
            indent = line_to_indent(line)
            code.add("raise ValueError(index + ' not a valid theme')", indent=indent)
            while line_to_indent(lines.peek()) >= indent:
                next(lines)

        elif line.strip().startswith("warnings.warn("):
            register_patch(31)
            if "popup" in lines.peek().lower() and "error" in lines.peek().lower():
                pass  # remove line
            else:
                line = line.replace("warnings.warn", "raise RuntimeError")
                line = line.replace(", UserWarning", "")
                code.add(line)

        elif "photo = tk.PhotoImage(file=element.Filename)" in line:
            register_patch(32)
            indent = line_to_indent(line)
            code.add(
                """\
try:
    import PIL
    from PIL import ImageTk
    from PIL import Image as PILImage
except ModuleNotFoundError:
    PIL = None
if isinstance(element.Filename, (str, Path)):
    if Path(element.Filename).is_file():
        if PIL:
            img = PILImage.open(element.Filename)
            photo = ImageTk.PhotoImage(img)
        else:
            if Path(element.Filename).suffix.lower() in (".gif", ".png"):
                photo = tk.PhotoImage(file=element.Filename)
            else:
                raise ValueError("file format not supported. Try installing PIL")
    else:
        if element.Filename == "":
            photo = tk.PhotoImage(file="")

        else:
            raise FileNotFoundError(element.Filename)
else:
    if PIL:
        photo = ImageTk.PhotoImage(element.Filename)
    else:
        raise ValueError("PIL image format not supported. Try installing PIL")
""",
                indent=indent,
            )

        elif "image = tk.PhotoImage(file=filename)" in line:
            register_patch(33)
            indent = line_to_indent(line)
            code.add(
                """\
try:
    import PIL
    from PIL import ImageTk
    from PIL import Image as PILImage
except ModuleNotFoundError:
    PIL = None
if isinstance(filename, (str, Path)):
    if Path(filename).is_file():
        if PIL:
            img = PILImage.open(filename)
            image = ImageTk.PhotoImage(img)
        else:
            if Path(filename).suffix.lower() in (".gif", ".png"):
                image = tk.PhotoImage(file=filename)
            else:
                raise ValueError("file format not supported. Try installing PIL")
    else:
        raise FileNotFoundError(filename)
else:
    if PIL:
        image = ImageTk.PhotoImage(filename)
    else:
        raise ValueError("PIL image format not supported. Try installing PIL")

""",
                indent=indent,
            )
        elif "__delitem__" in line:
            register_patch(35)
            code.add(line)
            indent = line_to_indent(line)
            while line_to_indent(lines.peek()) >= indent:
                code.add(next(lines))
            code.add(
                """\
def __getattr__(self, item):
    if item in self.dict:
        return self[item]
    else:
        return super().__getattr(item)

def __setattr__(self, item, value):
    trace_details = traceback.format_stack()
    if trace_details[-1].split(",")[0] == trace_details[-2].split(",")[0]: # internal or external?
        return super().__setattr__(item, value)
    else:
        self[item] = value

def __delattr__(self, item):
    del self[item]""",
                indent=indent,
            )

        elif line.strip() == "return self.update(*args, **kwargs)":
            register_patch(38)
            code.add("return self.get()", indent=line_to_indent(line))

        elif line.startswith("if __name__ == "):  # no more PySimpleGUI startup screen
            register_patch(36)
            break
        else:
            code.add(line)
    code.add(
        f"""\
class _Info:
    pass
pysimplegui = _Info()
pysimplegui.version = version
pysimplegui.__version__ = __version__

del _Info
version = __version__ = mysimplegui_version = "{__version__}\"""".format(
            __version__=__version__
        )
    )

    code.add(patch_info)

    to_be_registered_patches = {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 3,
        6: 1,
        7: 7,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1,
        15: 2,
        16: 1,
        17: 1,
        18: 1,
        19: 3,
        20: 1,
        21: 1,
        22: 6,
        23: 1,
        24: 1,
        25: 1,
        26: 1,
        27: 1,
        29: 1,
        30: 1,
        31: 9,
        32: 1,
        33: 2,
        34: 1,
        35: 2,
        36: 2,
        37: 0,
        38: 1,
    }
    if 35 in registered_patches:
        to_be_registered_patches[35] = registered_patches[35]  # ignore test for patch 35 as it may be 1 or 2
    mismatch = False
    for patch in to_be_registered_patches:
        if patch in registered_patches:
            if registered_patches[patch] != to_be_registered_patches[patch]:
                print(
                    "patch {patch} should be applied {tbr} times , but it {r} times".format(
                        patch=patch, tbr=to_be_registered_patches[patch], r=registered_patches[patch]
                    )
                )
                mismatch = True
        else:
            print(
                "patch {patch} should be applied {tbr} times, but is not registered at all".format(
                    patch=patch, tbr=to_be_registered_patches[patch]
                )
            )
            mismatch = True

    for patch in registered_patches:
        if patch not in to_be_registered_patches:
            print(
                "patch {patch} is applied {r} times, but is not in the to_be_registered dict at all".format(
                    patch=patch, r=registered_patches[patch]
                )
            )
            mismatch = True

    if mismatch:
        patches = {}
        for patch in sorted(registered_patches):
            patches[patch] = registered_patches[patch]
        print("Suggested mod:")
        print("to_be_registered_patches = {patches}".format(patches=patches))

    if mismatch:
        raise Warning("patches mismatch")

    with open(pysimplegui_patched_path, "w", encoding="utf-8") as f:
        f.write("\n".join(code))

sys.path.insert(0, str(mysimplegui_path.parent))
for var in list(vars().keys()):
    if var not in ("__name__", "pysimplegui_patched_path", "pysimplegui_patched_match", "sys"):
        del vars()[var]


from PySimpleGUI_patched import *
from PySimpleGUI_patched import __version__
sys.path.pop(0)

if __name__ == "__main__":
    if pysimplegui_patched_match:
        print(str(pysimplegui_patched_path) + " is up-to-date. Nothing written.")
    else:
        print(str(pysimplegui_patched_path) + " written successfully.")

del pysimplegui_patched_path
del pysimplegui_patched_match
