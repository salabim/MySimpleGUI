"""
The  module MySimpleGUI is an add on for PySimpleGUI

It's not a fork but an addon that adds functionality and changes some functionality of PySimpleGUI.
This means that -in principle- future versions of PySimpleGUI will be supported.

Requirements: installed PySimpleGUI >= 4.27.4, Python >= 3.3

Why MySimpleGui?
I am a big fan of MySimpleGUI, but don't like all of its functionality and think that there are
some enhancements possible. I tried to convince the PySimpleGUI developer, but he doesn't want to
implement these for various reasons. The most obvious way is then to fork the package and modify
it. The disadvantage of this approach is that future versions of PySimpleGUI are not automatically
supported by MySimpleGUI.
Therefore, I choose another way: patching the original PySimpleGUI code at runtime. This is not a 100%
guarantee that future PySimpleGUI version will work, but the way it's done is pretty stable.

Usage: import MySimpleGUI as sg

This imports the whole PySimpleGUI package, with some added functionality:

-   Attribute notation to Window and the values parameter as returned from Window.read()

    So, if we specified sg.Input("      ", key="name"),
    we can retrieve the value via values["name"] as usual but now also as values.name !
    Of course, in order to be able to do that the key has to be a name that is accepted as an attribute.

    But, there are some handy automatic conversions provided. If a key is a number (which happens if
    you don't specify a key parameter), the key can be accessed as k<number> or key<number> or _<number>, e.g.
    the key 0 can be retrieved with the usual values[0], but also with values.k0, values.key0 or values._0.
    And even values["key0"], although this seems a bit too much.

    But there's more: if a key contains sg.WRITE_ONLY_KEY or sg.TIMEOUT_KEY, the key can be also accessed without
    these constants. So if we had defined sg.Text("ab", key="zipcode" + sg.WRITE_ONLY_KEY),
    we can get the values as
        values["zipcode" + sg.WRITE_ONLY_KEY]
        values["zipcode"]
        values.zipcode

    And finally, there is normalization, which means that a given key is translated according to the following rules
    - if it is the null string, starts with a digit or is a keyword, a _ is added at the front
    - if there are any characters that are not acceptable in an identiefier, these are replaced by _
    So sg.Text("ab", key="name-address(zipcode)"),
    can also be accessed as values.name_address_zipcode_ or (less useful) values["name_address_zipcode"]

    In the example above, I used values. But all the same functionality applies to a window lookup as well!
    So instead of window["result"], we may also write window.result. And instead of window["--result--"] we can write
    window.__result__, although I don't see the point of using a key like "--result__", but the developer of
    PySimpleGUI seems to prefer that over "result".

    Note that the above functionality is only provided if the key is a string or a number.

    When used as window[key], an ordinary a KeyError will be raised if a key cannot be found.
    So goodbye to the error popups with incomplete traceback information (IMHO).
    It also doesn't do any automatic replacement with the 'closest' key. If that functionality is what you want you
    can still use sg.FindElement. But, I wouldn't recommend that ...

-   Functions are provided to get/set the globals that can be normally only be defined with SetOptions:
        auto_size_buttons() to get/set DEFAULT_AUTOSIZE_BUTTONS
        auto_size_text() to get/set DEFAULT_AUTOSIZE_TEXT
        autoclose_time() to get/set DEFAULT_AUTOCLOSE_TIME
        background_color() to get/set DEFAULT_BACKGROUND_COLOR
        border_width() to get/set DEFAULT_BORDER_WIDTH
        button_color() to get/set DEFAULT_BUTTON_COLOR
        button_element_size() to get/set DEFAULT_BUTTON_ELEMENT_SIZE
        debug_win_size() to get/set DEFAULT_DEBUG_WINDOW_SIZE
        element_background_color() to get/set DEFAULT_ELEMENT_BACKGROUND_COLOR
        element_padding() to get/set DEFAULT_ELEMENT_PADDING
        element_size() to get/set DEFAULT_ELEMENT_SIZE
        element_text_color() to get/set DEFAULT_ELEMENT_TEXT_COLOR
        enable_treeview_869_patch() to get/set ENABLE_TREEVIEW_869_PATCH
        error_button_color() to get/set DEFAULT_ERROR_BUTTON_COLOR
        font() to get/set DEFAULT_FONT
        input_elements_background_color() to get/set DEFAULT_INPUT_ELEMENTS_COLOR
        input_text_color() to get/set DEFAULT_INPUT_TEXT_COLOR
        margins() to get/set DEFAULT_MARGINS
        message_box_line_width() to get/set MESSAGE_BOX_LINE_WIDTH
        progress_meter_border_depth() to get/set DEFAULT_PROGRESS_BAR_BORDER_WIDTH
        progress_meter_color() to get/set DEFAULT_PROGRESS_BAR_COLOR
        progress_meter_relief() to get/set DEFAULT_PROGRESS_BAR_RELIEF
        progress_meter_size() to get/set DEFAULT_PROGRESS_BAR_SIZE
        scrollbar_color() to get/set DEFAULT_SCROLLBAR_COLOR
        slider_border_width() to get/set DEFAULT_SLIDER_BORDER_WIDTH
        slider_orientation() to get/set DEFAULT_SLIDER_ORIENTATION
        slider_relief() to get/set DEFAULT_SLIDER_RELIEF
        suppress_error_popups() to get/set SUPPRESS_ERROR_POPUPS
        suppress_key_guessing() to get/set SUPPRESS_KEY_GUESSING
        suppress_raise_key_errors() to get/set SUPPRESS_RAISE_KEY_ERRORS
        text_color() to get/set DEFAULT_TEXT_COLOR
        text_element_background_color() to get/set DEFAULT_TEXT_ELEMENT_BACKGROUND_COLOR
        text_justification() to get/set DEFAULT_TEXT_JUSTIFICATION
        tooltip_font() to get/set TOOLTIP_FONT
        tooltip_time() to get/set DEFAULT_TOOLTIP_TIME
        ttk_theme() to get/set DEFAULT_TTK_THEME
        use_ttk_buttons() to get/set USE_TTK_BUTTONS
        window_location() to get/set DEFAULT_WINDOW_LOCATION

    This can be very handy when a global variable has to be set during a certain operation and reset to
    its original value afterwards, like
        org_suppress_key_guessing = suppress_key_guessing()
        suppress_key_guessing(True)
        window.find_element("Result").update(123)
        suppress_key_guessing(org_suppress_key_guessing)
    to make the find_element use key guessing, although I have no idea why someone would like that.

-   The functions ChangeLookAndFeel and theme will now generate a proper ValueError when an invalid theme is given.
    So no more crazy random themes with a printed out warning, that can be easily missed, and not traced to
    where it was called from.

-   A Multiline element can now be used as a file.
    That means, a user program can use the write function, but more importantly, can also use the print builtin, like
    print("This is a test", file=window.mymultiline)
    Multiline elements can be closed and flushed as ordinary files.
    That also opens the door to more Pythonic redirections of stdout and stderr.

-   More interesting is the support of ANSI colours, both for foreground and background colours.
    The escape sequences associated with the various colours can be used as such but also via the ansi dict like
    data structure. Available colors/commands are
    ansi["reset"]      or ansi.reset     or "\x1b[0m"
    ansi["black"}      or ansi.black     or "\x1b[30m"
    ansi["red"]        or ansi.red       or "\x1b[31m"
    ansi["green"]      or ansi.green     or "\x1b[32m"
    ansi["yellow"}     or ansi.yellow    or "\x1b[33m"
    ansi["blue"]       or ansi.blue      or "\x1b[34m"
    ansi["magenta"}    or ansi.magenta   or "\x1b[35m"
    ansi["cyan"]       or ansi.cyan      or "\x1b[36m"
    ansi["onwhite"]    or ansi.onwhite   or "\x1b[37m"
    ansi["ondefault"]  or ansi.ondefault or "\x1b[39m"
    ansi["onblack"}    or ansi.onblack   or "\x1b[40m"
    ansi["onred"]      or ansi.onred     or "\x1b[41m"
    ansi["ongreen"]    or ansi.ongreen   or "\x1b[42m"
    ansi["onyellow"}   or ansi.onyellow  or "\x1b[43m"
    ansi["onblue"]     or ansi.onblue    or "\x1b[44m"
    ansi["onmagenta"}  or ansi.onmagenta or "\x1b[45m"
    ansi["oncyan"]     or ansi.oncyan    or "\x1b[46m"
    ansi["onwhite"]    or ansi.onwhite   or "\x1b[47m"
    ansi["ondefault"]  or ansi.ondefault or "\x1b[49m"

    So, we can now do:
        from MySimpleGUI import ansi
        ...
        window = [[sg.Multiline, size=(80, 10), key="results"]]
        print(f"colour {ansi.red} red {ansi.onred}{ansi.white} red on white {ansi.reset}", file=window.results)
        print(f"still red on white {ansi.reset}{ansi.green} green", file=window.result)

-   ANSI colours are also supported in the initial contents of Multiline and PopupScrolled.

-   MySimpleGUI has its own standard startup popup, with just the option to save generated code.

-   The following patches make that a MySimpleGUI is less likely to have issues that
    are just presented to the user (even often without the line in the code where it was generated):

    *   PopupErrors generated within PySimpleGUI will now suppress the popup and raise a RuntimeError
        with the information that would normally be shown in the popup.
        Setting SUPPRESS_ERROR_POPUPS to True will now be (silently) ignored.

    *   MySimpleGUI tries to capture all exceptions where output is generated. If so, 
        the exception is actually raised along with the information that would normally be printed.
        This behaviour can be disabled with sg.raise_errors(False).


Changelog
=========
vs 1.1.0  2020-08-12
--------------------
Complete change of code. Instead of importing PySimpleGUI, the complete source code is now read from
PySimpleGUI and patched where required. This is a much more flexible approach that also allows for
future patches to be applied relatively easy.

SUPPRESS_ERROR_POPUPS is now always False, even if you try and set it.

Exception and PopupError handling included.

The generated code can be run as a separate (forked) package, if required.

vs 1.0.1  2020-08-06
--------------------
Renamed to MySimpleGUI

Added functionality:
- functions to get/set the global variables as used in SetOptions
- The function ChangeLookAndFeel or change_look_and_feel as well theme now raises a ValueError
  if a non existing theme is given
- MultiLine now supports ANSI colors and can be used as a file.


vs 1.0.0  2020-07-28
--------------------
Initial version called PySimpleGUI_attributes
"""
import sys
from pathlib import Path


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
    lines = f.read().splitlines()

iter_lines = iter(lines)
code = []
code.append("# This code is generated by MySimpleGUI")
code.append("# Patches (c)2020  Ruud van der Ham, salabim.org")

for line in iter_lines:
    if line == "    def Read(self, timeout=None, timeout_key=TIMEOUT_KEY, close=False):":
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

    def Read(self, timeout=None, timeout_key=TIMEOUT_KEY, close=False):
        class AttributeDict(collections.UserDict):
            def __getitem__(self, key):
                return Window.lookup(self.data, key)

            def __getattr__(self, key):
                try:
                    return self[key]
                except KeyError as e:
                    raise AttributeError(e) from None

        if not Window._read_call_from_debugger:
            _refresh_debugger()

        Window._root_running_mainloop = self.TKroot
        events, values = self._read(timeout=timeout, timeout_key=timeout_key)
        if values is not None:
            if isinstance(values, list):
                values = {i: v for i, v in enumerate(values)}
            values = AttributeDict(values)
        results = events, values

        if close:
            self.close()

        return results

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
        code.append("    def _(self, timeout=None, timeout_key=TIMEOUT_KEY, close=False):")
    elif line == "class Multiline(Element):":
        code.append(line)
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

    elif line == "        self.EnterSubmits = enter_submits":
        code.append(line)
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
        code.append("    def _(self, txt):")
    elif line.startswith("                    element.TKText.insert(1.0, element.DefaultText)"):
        code.append("                    print(element.DefaultText, file=element)")
    elif line.startswith("def SetOptions("):
        names = {}
        while True:
            code.append(line)
            left, *right = line.split(" = ")
            if "#" not in line and "." not in line and line.startswith("        ") and right:
                names[left.strip()] = right[0]
            names["RAISE_ERRORS"] = "raise_errors"
            line = next(iter_lines)
            if line.strip() and line[0] != " " and names:

                for name in sorted(names, key=lambda x: names[x]):
                    alias = names[name]
                    code.append("def {alias}(value):".format(alias=alias))
                    code.append("    global {name}".format(name=name))
                    code.append("    if value is not None:")
                    code.append("        {name} = value".format(name=name))
                    code.append("    return {name}".format(name=name))

                code.append(line)
                break
    elif line.startswith("def PopupError("):
        while True:
            code.append(line)
            if ":" in line:  # reached the end of the PopupError definition
                break
            line = next(iter_lines)

        code.extend(
            splitlines(
                """
    trace_details = traceback.format_stack()
    if trace_details[-1].split(",")[0] == trace_details[-2].split(",")[0]:
        raise RuntimeError("\\n".join(args))
    """
            )
        )
    elif line == "import sys":
        code.append(line)
        code.append("import keyword")
        code.append("import collections")
        code.append("import io")
    elif line.startswith("version = "):
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
    elif line.strip() in ("except:", "except Exception as e:"):
        indent = line_to_indent(line)
        indentstr = " " * indent
        code.append(indentstr + "except Exception as e:")
        buffered_lines = []
        while True:
            line = next(iter_lines)
            if line_to_indent(line) > indent:
                buffered_lines.append(line)
            else:
                break
        if any(l.strip() == "pass" for l in buffered_lines):
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
        code.append(line)
    elif "SUPPRESS_ERROR_POPUPS = False" in line:
        code.append(line)
        indent = line_to_indent(line)
        indentstr = indent * " "
        code.append(indentstr + "RAISE_ERRORS = True")

    elif "SUPPRESS_ERROR_POPUPS = suppress_error_popups" in line:
        code.append(line.replace("suppress_error_popups", "False"))

    elif line == "        ix = random.randint(0, len(lf_values) - 1)":
        code.append("        raise ValueError(index + ' not a valid theme')")
    elif line.startswith("if __name__ == "):  # no more PySimpleGUI startup screen
        break

    else:
        code.append(line)


del lines
del splitlines
del line_to_indent
    
if True:
    filename = "MySimpleGUI_generated.py"
    with open(filename, "w", encoding='utf-8') as f:
        f.write("\n".join(code))
exec("\n".join(code))
if __name__ == "__main__":
    filename = "MySimpleGUI_generated.py"
    if PopupYesNo("Would you like to save the patched version to " + filename) == "Yes":
        with open(filename, "w", encoding='utf-8') as f:
            f.write("\n".join(code))
        Popup("saved to " + str(Path(filename).resolve()), title="saved")
