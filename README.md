# MySimpleGUI
The  module MySimpleGUI is an addon for PySimpleGUI

It's not a fork but an addon that adds functionality and changes some functionality of PySimpleGUI.
This means that -in principle- future versions of PySimpleGUI will be supported.

Requirements: installed PySimpleGUI >= 4.27.4, Python >= 3.3

**Why MySimpleGUI**

I am a fan of PySimpleGUI, but don't like all of its functionality and think that there are
some enhancements possible.

The most obvious way is then to fork the package and modify
it. The disadvantage of this approach is that future versions of PySimpleGUI are not automatically
supported by MySimpleGUI.
Therefore, I choose another way: patching the original PySimpleGUI code at runtime. This is not a 100%
guarantee that future PySimpleGUI versions will work with MySimpleGUI, but the way it's done is pretty stable.

**Installation**

You can either install MySimpleGUI by downloading the file MySimpleGUI.py from 
    https://github.com/salabim/MySimpleGUI/

or from PyPI with
```
pip install MySimpleGUI
```
**Usage**

`import MySimpleGUI as sg`

**Functionality**

MySimpleGUI offers the whole PySimpleGUI functionality, with some added features and changes:

-   Attribute notation to Window and the values parameter as returned from `Window.read()`.

    So, if we specified `sg.Input("      ", key="name")`,
    we can retrieve the value via `values["name"]` as usual but now also as `values.name` !
    Of course, in order to be able to do that the key has to be a name that is accepted as an attribute.

    But, there are some handy automatic conversions provided. If a key is a number (which happens if
    you don't specify a key parameter), the key can be accessed as `k`*number* or `key`*number* or `_`*number*, e.g.
    the key `0` can be retrieved with the usual `values[0]`, but also with `values.k0`, `values.key0` or `values._0`.
    And even `values["key0"]`, although this seems a bit too much...

    But there's more: if a key contains `sg.WRITE_ONLY_KEY` or `sg.TIMEOUT_KEY`, the key can be also accessed without
    these constants. So if we had defined `sg.Text("ab", key="zipcode" + sg.WRITE_ONLY_KEY)`,
    we can get the values as
    
        values["zipcode" + sg.WRITE_ONLY_KEY]
        values["zipcode"]
        values.zipcode

    And finally, there is normalization, which means that a given key is translated according to the following rules
    - if it is the null string, starts with a digit or is a keyword, a _ is added at the front
    - if there are any characters that are not acceptable in an identifier, these are replaced by `_`.
    So `sg.Text("ab", key="name-address(zipcode)")`,
    can also be accessed as `values.name_address_zipcode_` or (less useful) `values["name_address_zipcode"]`

    In the example above, I used values. But all the same functionality applies to a window lookup as well!
    So instead of `window["result"]`, we may also write `window.result`. And instead of `window["--result--"]`
    as prefered in PySimpleGUI  we can write `window.__result__`, although I don't see the point of using a key like "--result--".

    Note that the above functionality is only provided if the key is a string or a number.

    When used as `window[key]`, an ordinary a KeyError will be raised if a key cannot be found.
    So goodbye to the error popups with incomplete traceback information (IMHO).
    It also doesn't do any automatic replacement with the *closest* key. If that functionality is what you want you
    can still use `sg.FindElement`. But, I wouldn't recommend that ...
    
    Just one example of MySimpleGUI's attribute approach.
    The PySimpleGUI documentation shows this recipe:
    
    ```
    import PySimpleGUI as sg

    sg.theme('BluePurple')

    layout = [[sg.Text('Your typed chars appear here:'), sg.Text(size=(15,1), key='-OUTPUT-')],
              [sg.Input(key='-IN-')],
              [sg.Button('Show'), sg.Button('Exit')]]

    window = sg.Window('Pattern 2B', layout)

    while True:  # Event Loop
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Show':
            # Update the "output" text element to be the value of "input" element
            window['-OUTPUT-'].update(values['-IN-'])

    window.close()   
    ```
    With MySimpleGUI you can do this as follows
    
    ```
    import MySimpleGUI as sg

    sg.theme('BluePurple')

    layout = [[sg.Text('Your typed chars appear here:'), sg.Text(size=(15,1), key='output')],
              [sg.Input(key='input')],
              [sg.Button('Show'), sg.Button('Exit')]]

    window = sg.Window('Pattern 2B', layout)

    while True:  # Event Loop
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
             break
        if event == 'Show':
            # Update the "output" text element to be the value of "input" element
            window.output.update(values.in)

    window.close()   
    ```    
-   In contrast to PySimpleGUI, window.read() wil also return the value of Text elements in values.

-   In contrast to PySimpleGUI, duplicate keys for elements are allowed. The element returned when using window[key] or values[key] will
be the last defined.

-   In MySimpleGUI, defined keys are never overridden, by elements that are defined without a given key/k (these are numbered 1, 2, ..., but will skip
any already defined key.

-   If a key is also used as an internal attribute of Window, e.g. modal, `window.modal` will return the element associated with "modal"
        
    If the internal attribute is required in that case use internal. So `window.internal.modal` will return the value of the internal attribute window.
        
    If an internal attribute of a window is not defined as a key of any element in that window,
    e.g. (under the assumption that 'saw_00' is not used as a key) `window.saw_00` and `window.internal.saw_00` will be equivalent.
        
    In practice however, internal will hardly ever have to be used.    
    
-   The functions ChangeLookAndFeel and theme will now generate a proper ValueError when an invalid theme is given.
    So no more random themes with a printed out warning, that can be easily missed, and not traced to
    where it was called from.

-   A Multiline element can now be used as a file.
    That means, a user program can use the write function, but more importantly, can also use the print builtin, like
    `print("This is a test", file=window.mymultiline)`
    Multiline elements can be closed and flushed as ordinary files.
    That also opens the door to more Pythonic redirections of stdout and stderr.

-   And Multiline files support of ANSI colours, both for foreground and background colours.
    The escape sequences associated with the various colours can be used as such but also via the ansi dict like
    data structure. Available colours/commands are
    
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
    ansi["font"]       or ansi.font      or "x\1b[font"
    ```

    So, we can now do:
    
        from MySimpleGUI import ansi
        ...
        window = [[sg.Multiline, size=(80, 10), key="results"]]
        print(f"colour {ansi.red} red {ansi.onred}{ansi.white} red on white {ansi.reset}", file=window.results)
        print(f"still red on white {ansi.reset}{ansi.green} green", file=window.result)

-   On top of the ANSI colors, A font can be specified in a similar way with ansi.font (or ansi["font"]).
It makes it possible to change fonts inline. The font should be
specified immediately following the ansi.font code and terminated by |. E.g
    
        from MySimpleGUI import ansi
        ...
        window = [[sg.Multiline, size=(80, 10), key="results"]]
        print(f"{ansi.font}courier 8|this is courier, 8 points{ansi.reset}this is not", file=window.results)  

-   ANSI colors/font are also supported as the initial contents of Multiline and PopupScrolled.

-   The following patches make that a MySimpleGUI is less likely to have issues that
    are just presented to the user (even often without the line in the code where it was generated):

    *   PopupErrors generated within PySimpleGUI will now suppress the popup and raise a RuntimeError
        with the information that would normally be shown in the popup.
        This behaviour can be disabled with `raise_errors(False)`

    *   MySimpleGUI tries to capture all exceptions where output is generated. If so, 
        the exception is actually raised along with the information that would normally be printed.
        
        For example if you have this code:
        ```
        DarkGrey8 = {'BACKGROUND': '#19232D',
              'TEXT': '#ffffff',
              'INPUT': '#32414B',
              'TEXT_INPUT': '#ffffff',
              'SCROLL': '#505F69',
              'BUTTON': ('#ffffff', '#32414B'),
              'PROGRESS': ('#505F69', '#32414B'),
              'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
              }

        sg.theme_add_new(DarkGrey8, DarkGrey8)
        ```
        PySimpleGUI will print a message
        `Exception during adding new theme unhashable type: 'dict` without any indication
        what kind of exception, where this error occurred and will just continue, so you might even miss it easily.
        
        On the other hand, MySimpleGUI will raise an exception and generate the following useful information about the why and where:
        ```
        Traceback (most recent call last):
        File "c:\Users\Ruud\Dropbox (Personal)\Apps\Python Ruud\misc\EuroPython\adder pysimplegui.py", line 26, in <module>
        sg.theme_add_new(DarkGrey8, DarkGrey8)
        File "<string>", line 15697, in theme_add_new
        TypeError: unhashable type: 'dict'
        Exception during adding new theme unhashable type: 'dict'
        ```
        This behaviour can be disabled with `sg.raise_errors(False)`.
        
-   All `warnings.warn` messages are either suppressed (when followed by a PopupError), or will raise a RuntimeError exception with the
    original message.

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
        
    The value of a global variable can be retrieved by calling the function without an argument, like

        current_message_box_line_with = sg.message_box_line_width()
    
    The value of a global variable can be set by calling the function with the new value as its argument, like

        sg.message_box_line_width(20)

    And it is possible to use the function with an argument as a context manager. In that case, the global variable
    will be restored after finishing the context manager:

        with sg.message_box_line_width(20):
            sg.Popup("Hey, this is much more narrow than usual!")
        sg.Popup("And now it's back to the usual 60 characters width, isn't it?")
        
    Some details:
    
    -   A function with a parameter like `sg.message_box_line_width(100)` returns a TemporaryChange object.
    -   When a value is set, the new value can also be retrived by calling the function, like `sg.message_box_line_width(100)()`
    -   The `as` parameter in the context manager will be set to the saved value, like
    
            with sg.message_box_line_width(20) as saved_message_box_line_width:
                print(saved_message_box_line_width)
                sg.Popup("Hey, this is much more narrow than usual!")
            sg.Popup("And now it's back to the usual 60 characters width, isn't it?")
            
-   MySimpleGUI adds a `font` parameter to Multiline()

-   MySimpleGUI add a `font_for_value` parameter to Multiline.update()
            
-   In contrast to PySimpleGUI, MySimpleGUI doesn't require the key parameter in element specifications to be hashable.
Please note that to access an item/attribute of a window of values, the key has to be hashable, still.

-   In contrast to PySimpleGUI, MySimpleGUI doesn't require the key parameter to be unique. 

-   Upon creation of an element in a layout, a `freeze()` method call can be added.

    If a froxen element is made invisible, the space keeps reserved and no changes in the positions of other element
    will occur when the element is made invisible. Example:
    
    ```
    import MySimpleGUI as sg

    layout = [  [sg.Text("<<"), sg.Button('Button1', key='button1').freeze(), sg.Button('Button2', key='button2').freeze(), sg.Text(">>")],
                [sg.Checkbox('Show Button1', default=True, enable_events=True, key="sb1"), sg.Checkbox('Show Button 2', default=True, enable_events=True, key="sb2")]]

    window = sg.Window('Window', layout)

    while True: 
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'sb1':
            window['button1'].update(visible=window.sb1.get())
        if event == 'sb2':
            window['button2'].update(visible=window.sb2.get())

    window.close()
    
    ```
-   In MySimpleGUI, anywhere where an explicit False or True is required as a parameter, that can now
be any falsy (apart from None) or any truthy value.

    So,
    
    ```
    window['button2'].update(visible=bool(window.sb2.get()))
    ```
    
    is equivalent to
    
    ```
    window['button2'].update(visible=window.sb2.get())
    ```

-   The `__call__` method of any element still calls the `update` method, but will now also return the current value. This
is useful to avoid using the `get` method:

    ```
        window['button2'].update(visible=window.sb2())`
    ```
    
    is equivalent to
    
    ```
        window['button2'].update(visible=window.sb2.get())`
    ```
    Notice that this is NOT equivalent to:
    
    ```
        window['button2'].update(visible=window.sb2.update())
    ```

-   MySimpleGUI also allows PIL images to be used in Image elements.
Also, when PIL is installed, other extensions than .png or .gif, e.g. .jpg can be used in Image elements.

    Image.DrawImage and Image.Update support PIL Images as well as other extension than just
.png or .gif if PIL is installed.

    Note that there's still no requirement to have PIL installled. But is highly recommended, though.
    
-   MySimpleGUI can print Elements, Columns and Windows in a nice format, which can be very useful for debugging and just getting to
know what My  SimpleGUI/PySimpleGUI does internally.
    For instance:
        
        Input id: 2069800000984        
            BackgroundColor = '#f0f3f7'
            BorderWidth = 1
            ChangeSubmits = False
            DefaultText = ''
            Disabled = False
            do_not_clear = True
            Focus = False
            Key = 'IN'
            pad_used = (0, 0)
            ParentContainer = Window  id: 2069800001432
            PasswordCharacter = ''
            Position = (1, 0)
            ReadOnly = False
            taken = True
            Tearoff = False
            TextColor = '#000000'
            UseReadonlyForDisable = True
            user_bind_dict = {}
            Visible = True
        
    The output will suppress all attributes that are None or (None, None) and will try and expand where possible.
            
-   
    
-  In PySimpleGUI the target in several Button functions (like FilesBrowse and FolderBrowse) defaults to the
(ThisRow, -1). When you want it to point to the button itself, you have to specify a target that is equal
to key, k or button_text. In order support the DRY (don't repeat yourself) principle, MySimpleGUI now automatically
points to 'itself' if the target parameter is the null string or None.

-   In contrast to PySimpleGUI, MySimpleGUI correctly returns the null string upon pressing
<Cancel> in FileBrowse, FilesBrowse and FolderBrowse, provided the target parameter points to 'itself' (see also bullet above).
    
-   The user settings can now be accessed also via attributes, provided the name is a valid attribute.
    So, now we can say
    ```
    settings.get("name")           setting["name"]             settings.name
    settings.set("name", "test")   settings["name"] = "test"   settings.name = "test"
    settings.delete_entry("name")  del settings["name]         del settings.name
    ```
    
-   Version

    `sg.version` will return the inherited PySimpleGUI version
    
    `sg.mysimplegui_version` will return the MySimpleGUI_version

-   Perfomance:
    Whenever a new version of PySimpleGUI or MySimpleGUI is detected. loading MySimpleGUI will take a bit longer 
    as a PySimpleGUI_patched file has to be written.
    
    Once the PySimpleGUI_patched is created, there will be no difference in perfomance.
    
-   If your run MySimpleGUI, a simple text confirmation will be printed.
