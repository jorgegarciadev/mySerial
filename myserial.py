#!/usr/bin/env python
# coding: UTF-8


import datetime
import sys
import serial, threading, argparse, time

import urwid
from urwid import MetaSignals
from websocket import create_connection

FILE = '/dev/tty.usbmodem1411'
BAUDRATE = 9600
NEWLINE = ("CRLF", "LF", "CR")


class ExtendedListBox(urwid.ListBox):
    """
        Listbow widget with embeded autoscroll
    """

    __metaclass__ = urwid.MetaSignals


    def __init__(self, body):
        urwid.ListBox.__init__(self, body)
        self.auto_scroll = True


    def switch_body(self, body):
        if self.body:
            urwid.disconnect_signal(body, "modified", self._invalidate)

        self.body = body
        self._invalidate()

        urwid.connect_signal(body, "modified", self._invalidate)


    def keypress(self, size, key):
        urwid.ListBox.keypress(self, size, key)

        if key in ("page up", "page down"):
            # logging.debug("focus = %d, len = %d" % (self.get_focus()[1], len(self.body)))
            if self.get_focus()[1] == len(self.body)-1:
                self.auto_scroll = True
            else:
                self.auto_scroll = False
            # logging.debug("auto_scroll = %s" % (self.auto_scroll))


    def scroll_to_bottom(self):
        # logging.debug("current_focus = %s, len(self.body) = %d" % (self.get_focus()[1], len(self.body)))

        if self.auto_scroll:
            # at bottom -> scroll down
            self.set_focus(len(self.body)-1)



class MainWindow(object):

    __metaclass__ = MetaSignals
    signals = ["quit","keypress"]

    _palette = [
            ('divider','black','dark cyan', 'standout'),
            ('text','light gray', 'default'),
            ('bold_text', 'light gray', 'default', 'bold'),
            ("body", 'black', 'dark blue'),
            ("footer", 'black', 'dark blue'),
            ("header", "text"),
        ]

    for type, bg in (
            ("div_fg_", "dark cyan"),
            ("", "default")):
        for name, color in (
                ("red","dark red"),
                ("blue", "dark blue"),
                ("green", "dark green"),
                ("yellow", "yellow"),
                ("magenta", "dark magenta"),
                ("gray", "light gray"),
                ("white", "white"),
                ("black", "black")):
            _palette.append( (type + name, color, bg) )


    def __init__(self):
        self.shall_quit = False
        if parsed.ws:
            self.moo = create_connection(FILE)
            time.sleep(1)
            self.rec = threading.Thread(target=self.webSocketReceiver)
        elif parsed.wss:
            self.moo = create_connection(FILE, sslopt={"check_hostname": False})
            time.sleep(1)
            self.rec = threading.Thread(target=self.webSocketReceiver)
        else:
            self.moo = serial.serial_for_url(FILE, BAUDRATE)
            time.sleep(1)
            self.rec = threading.Thread(target=self.serialReciver)
        self.rec.daemon = True
        self.rec.on = True
        self.rec.start()


    def main(self):
        """ 
            Entry point to start UI 
        """

        self.ui = urwid.raw_display.Screen()
        self.ui.register_palette(self._palette)
        self.build_interface()
        self.ui.run_wrapper(self.run)

    def serialReciver(self):
        while self.rec.on:
            try:
                recv = self.moo.readline()
                if len(recv) > 0:
                    self.print_received_message(recv)
            except:
                pass
    def webSocketReceiver(self):
        while self.rec.on:
            try:
                recv = self.moo.recv()
                time.sleep(0.1)
                self.print_received_message(recv)
            except:
                pass

    def run(self):
        """ 
            Setup input handler, invalidate handler to
            automatically redraw the interface if needed.

            Start mainloop.
        """


        def input_cb(key):
            if self.shall_quit:
                raise urwid.ExitMainLoop
            self.keypress(self.size, key)

        self.size = self.ui.get_cols_rows()

        self.main_loop = urwid.MainLoop(
                self.context,
                screen=self.ui,
                handle_mouse=False,
                unhandled_input=input_cb,
            )

        def call_redraw(*x):
            self.draw_interface()
            invalidate.locked = False
            return True

        inv = urwid.canvas.CanvasCache.invalidate

        def invalidate (cls, *a, **k):
            inv(*a, **k)

            if not invalidate.locked:
                invalidate.locked = True
                self.main_loop.set_alarm_in(0, call_redraw)

        invalidate.locked = False
        urwid.canvas.CanvasCache.invalidate = classmethod(invalidate)

        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.quit()


    def quit(self, exit=True):
        """ 
            Stops the ui, exits the application (if exit=True)
        """
        urwid.emit_signal(self, "quit")

        self.shall_quit = True

        if exit:
            self.rec.on = False

            self.moo.close()
            sys.exit(0)


    def build_interface(self):
        """ 
            Call the widget methods to build the UI 
        """

        self.header = urwid.Text(" mySerial" + " " + FILE + " " + str(BAUDRATE) + " " + end)
        self.footer = urwid.Edit("> ")
        self.divider = urwid.Text("Initializing.")

        self.generic_output_walker = urwid.SimpleListWalker([])
        self.body = ExtendedListBox(
            self.generic_output_walker)


        self.header = urwid.AttrWrap(self.header, "divider")
        self.footer = urwid.AttrWrap(self.footer, "footer")
        self.divider = urwid.AttrWrap(self.divider, "divider")
        self.body = urwid.AttrWrap(self.body, "body")

        self.footer.set_wrap_mode("space")

        main_frame = urwid.Frame(self.body, 
                                header=self.header,
                                footer=self.divider)
        
        self.context = urwid.Frame(main_frame, footer=self.footer)

        self.divider.set_text(("divider",
                               (" Send command:")))

        self.context.set_focus("footer")


    def draw_interface(self):
        self.main_loop.draw_screen()


    def keypress(self, size, key):
        """ 
            Handle user inputs
        """

        urwid.emit_signal(self, "keypress", size, key)

        # scroll the top panel
        if key in ("page up","page down", "up", "down"):
            self.body.keypress (size, key)

        # resize the main windows
        elif key == "window resize":
            self.size = self.ui.get_cols_rows()

        elif key in ("ctrl d", 'ctrl c'):
            self.quit()

        elif key == "enter":
            # Parse data or (if parse failed)
            # send it to the current world
            text = self.footer.get_edit_text()

            self.footer.set_edit_text(" "*len(text))
            self.footer.set_edit_text("")


            if text.strip():
                self.print_sent_message(text)
                # self.print_received_message('Answer')
        elif key == 'esc':
            self.quit()

        else:
            self.context.keypress (size, key)

 
    def print_sent_message(self, text):
        """
            Print a received message
        """

        self.print_text('[%s][sent] - %s' % (self.get_time(), text))
        if parsed.ws:
            self.moo.send(text+nl)
        else:
            self.moo.write(text+nl)
 


    def print_received_message(self, text):
        text = text.strip()
        self.print_text('[%s][recv] - %s' % (self.get_time(), text))
        self.draw_interface()

        
    def print_text(self, text):
        """
            Print the given text in the _current_ window
            and scroll to the bottom. 
            You can pass a Text object or a string
        """

        walker = self.generic_output_walker

        if not isinstance(text, urwid.Text):
            text = urwid.Text(text)

        walker.append(text)

        self.body.scroll_to_bottom()


    def get_time(self):
        """
            Return formated current datetime
        """
        return datetime.datetime.now().strftime('%H:%M:%S')
        



if __name__ == "__main__":
    description = '''
    mySerial is an Urwid based serial monitor tool similar to the one included on 
    Arduino IDE and Stino. It's has been thought to be used via Secure Shell.

    '''
    epilog = 'Press ESC to exit the program. Use up, down page up and page down to scroll.'
    parser = argparse.ArgumentParser(description = description,
        epilog = epilog)
    parser.add_argument('port',
        action='store',
        help = "port, a number or a device name.",
        default = None
        )
    parser.add_argument('-b',
        action='store',
        dest='baudrate',
        help = "set baud rate, default 9600",
        default=9600
    )
    parser.add_argument('-cr',
        action='store_true',
        default = False,
        help = "do not send CR+LF, send CR only."
    )
    parser.add_argument('-lf',
        action='store_true',
        default = False,
        help = "do not send CR+LF, send LR only."
    )
    parser.add_argument('-nn',
        action='store_true',
        default = False,
        help = "do not add endline characters."
    )
    parser.add_argument('-s',
        action='store_true',
        default = False,
        help = "Connect to a raw socket. User should provide IP and port separated by ':'."
    )
    parser.add_argument('-ws',
        action='store_true',
        default = False,
        help = "Connect to a WebSocket. User should provide IP and port separated by ':'."
    )
    parser.add_argument('-wss',
        action='store_true',
        default = False,
        help = "Connect to a Secure WebSocket (ssl). User should provide IP and port separated by ':'."
    )

    # parser.add_argument('-qt'
    #     action = 'store_true',
    #     default = False,
    #     help = "Loads a QT based interface"
    # )

    parsed = parser.parse_args()

    if parsed.s:
        FILE = "socket://" + parsed.port
    elif parsed.ws:
        FILE = "ws://" + parsed.port
    elif parsed.wss:
        FILE = "wss://" + parsed.port
    else:    
        FILE = parsed.port
    BAUDRATE = parsed.baudrate

    if parsed.cr:
        nl = '\r'
        end = NEWLINE[2]
    elif parsed.lf:
        nl = '\n'
        end = NEWLINE[1]
    elif parsed.nn:
        nl = ''
        end = ''
    else:
        nl = '\r\n'
        end = NEWLINE[0]
    try:
        main_window = MainWindow()
        main_window.main()
    except Exception, e:
        print "\033[91mError:\033[0m %s\n" % e
        sys.exit(1)
