# MySimpleGUI
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

    But there's more: if a key contains `sg.WRITE_ONLY_KEY` or `sg.TIMEOUT_KEY`, the key can be also accessed without
    these constants. So if we had defined `sg.Text("ab", key="zipcode" + sg.WRITE_ONLY_KEY)`,
    we can get the values as
        values["zipcode" + sg.WRITE_ONLY_KEY]
        values["zipcode"]
        values.zipcode

    And finally, there is normalization, which means that a given key is translated according to the following rules
    - if it is the null string, starts with a digit or is a keyword, a _ is added at the front
    - if there are any characters that are not acceptable in an identiefier, these are replaced by _
    So `sg.Text("ab", key="name-address(zipcode)")`,
    can also be accessed as `values.name_address_zipcode_` or (less useful) `values["name_address_zipcode"]`

    In the example above, I used values. But all the same functionality applies to a window lookup as well!
    So instead of `window["result"]`, we may also write `window.result`. And instead of `window["--result--"]` we can write
    `window.__result__`, although I don't see the point of using a key like "--result--", but the developer of
    PySimpleGUI seems to prefer that over "result".

    Note that the above functionality is only provided if the key is a string or a number.

    When used as `window[key]`, an ordinary a KeyError will be raised if a key cannot be found.
    So goodbye to the error popups with incomplete traceback information (IMHO).
    It also doesn't do any automatic replacement with the *closest* key. If that functionality is what you want you
    can still use `sg.FindElement`. But, I wouldn't recommend that ...

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
    
    ```
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
    ```

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
