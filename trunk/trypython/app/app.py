from __future__ import with_statement

import sys

# Handle infinite recursion gracefully
# CPython default is 1000 - but Firefox can't handle that deep
sys.setrecursionlimit(500)

from System import EventHandler, Math
from System.Windows import Application
from System.Windows import Point
from System.Windows.Browser import HtmlPage, HtmlEventArgs
from System.Windows.Controls import StackPanel, ComboBoxItem, UserControl
from System.Windows.Markup import XamlReader

from consoletextbox import ConsoleTextBox
from context import context
from printer import StatefulPrinter
from utils import invoke, _debug, SetInvokeRoot


root = Application.Current.LoadRootVisual(StackPanel(), "app.xaml")
SetInvokeRoot(root)

topCombobox = root.topComboBox
bottomCombobox = root.bottomComboBox
console_output = root.consoleOutput
prompt_panel = root.promptPanel
scroller = root.scroller
textbox_parent = root.consoleParent


def content_resized(sender, event):
    root.Width = width = max(Application.Current.Host.Content.ActualWidth - 25, 700)
    root.Height = height = max(Application.Current.Host.Content.ActualHeight - 25, 700)

    root.document.Width = int(width * 0.53)
    root.container.Height = height - 120
    root.scroller.Width = int(width * 0.44)

Application.Current.Host.Content.Resized += content_resized
content_resized(None, None)
    
# nicely format unhandled exceptions
def excepthook(sender, e):
    error = Application.Current.Environment.GetEngine('py').FormatException(e.ExceptionObject)
    HtmlPage.Document.debugging.innerHTML += error.replace('\n', '<br />')

Application.Current.UnhandledException += excepthook

@invoke
def focus_text_box(sender, event):
    #_debug('focus\n')
    HtmlPage.Plugin.Focus()
    console_textbox.Focus()


printer = StatefulPrinter(console_output, scroller)

console_textbox = ConsoleTextBox(scroller.Width - 75, printer, context, root.prompt)
textbox_parent.Child = console_textbox
console_textbox.reset()

console_output.GotFocus += focus_text_box
scroller.GotFocus += focus_text_box
root.container.GotFocus += focus_text_box


sys.stdout = console_textbox
sys.stderr = console_textbox

with open('list.txt') as handle:
    items = handle.readlines()

for combobox in topCombobox, bottomCombobox:
    for item in items:
        boxitem = ComboBoxItem()
        boxitem.Content = item
        boxitem.Height = 25
        combobox.Items.Add(boxitem)
    
def onChangeTop(sender, event):
    index = topCombobox.SelectedIndex
    bottomCombobox.SelectionChanged -= onChangeBottom
    bottomCombobox.SelectedIndex = index
    bottomCombobox.SelectionChanged += onChangeBottom
    changeDocument(index)
    
def onChangeBottom(sender, event):
    index = bottomCombobox.SelectedIndex
    topCombobox.SelectionChanged -= onChangeTop
    topCombobox.SelectedIndex = index
    topCombobox.SelectionChanged += onChangeTop
    changeDocument(index)

def changeDocument(index):
    page = ''
    if index > 0:
        page = 'page%s' % (index + 1)
    HtmlPage.Window.CurrentBookmark = page
    with open('docs/item%s.xaml' % (index+1)) as handle:
        xaml = handle.read().decode('utf-8')
    document = XamlReader.Load(xaml)
    root.document.Child.Content = document
    root.document.Child.ScrollToVerticalOffset(0)
    focus_text_box(None, None)

topCombobox.SelectionChanged += onChangeTop
bottomCombobox.SelectionChanged += onChangeBottom

page = 0
bookmark = HtmlPage.Window.CurrentBookmark.lower()
if bookmark.startswith('page'):
    try:
        page = int(bookmark[4:])
    except ValueError:
        pass
    else:
        page = min((page - 1), len(combobox.Items) - 1)
        page = max(page, 0)

def first(sender, event):
    topCombobox.SelectedIndex = 0
def last(sender, event):
    topCombobox.SelectedIndex = len(combobox.Items) - 1
def next(sender, event):
    current = combobox.SelectedIndex
    topCombobox.SelectedIndex = min(current + 1, len(combobox.Items) - 1)
def prev(sender, event):
    current = combobox.SelectedIndex
    topCombobox.SelectedIndex = max(current - 1, 0)
    
    
root.topFirst.Click += first
root.bottomFirst.Click += first
root.topLast.Click += last
root.bottomLast.Click += last
root.topNext.Click += next
root.bottomNext.Click += next
root.topPrev.Click += prev
root.bottomPrev.Click += prev
        
topCombobox.SelectedIndex = page
focus_text_box(None, None)


class MouseHandler(object):
    def __init__(self, scrollers):
        self.position = None
        self.scrollers = scrollers
    
    def on_mouse_move(self, sender, event):
        self.position = event.GetPosition(None)
    
    def on_mouse_wheel(self, sender, event):
        delta = 0
        e = event.EventObject
        if e.GetProperty("detail"):
            delta = e.GetProperty("detail")
        elif e.GetProperty("wheelDelta"):
            delta = -e.GetProperty("wheelDelta")
        delta = Math.Sign(delta) * 40
        
        for scroller in self.scrollers:
            if self.mouse_over(scroller):
                e.SetProperty('cancel', True)
                e.SetProperty('cancelBubble', True)
                e.SetProperty('returnValue', False)
                if e.GetProperty('preventDefault'):
                    e.Invoke('preventDefault')
                elif e.GetProperty('stopPropagation'):
                    e.Invoke('stopPropagation')
                scroller.ScrollToVerticalOffset(scroller.VerticalOffset + delta)
                return


    def mouse_over(self, scroller):
        minX, maxX, minY, maxY = self.get_element_coords(scroller)
        return ((minX <= self.position.X <= maxX) and
                (minY <= self.position.Y <= maxY))


    def get_element_coords(self, element):
        transform = element.TransformToVisual(root)
        topleft = transform.Transform(Point(0, 0))
        minX = topleft.X
        minY = topleft.Y
        maxX = minX + element.RenderSize.Width
        maxY = minY + element.RenderSize.Height
        return minX, maxX, minY, maxY

        
handler = MouseHandler([scroller, root.documentScroller])
root.MouseMove += handler.on_mouse_move
on_mouse_wheel = EventHandler[HtmlEventArgs](handler.on_mouse_wheel)
    
HtmlPage.Window.AttachEvent("DOMMouseScroll", on_mouse_wheel)
HtmlPage.Window.AttachEvent("onmousewheel", on_mouse_wheel)
HtmlPage.Document.AttachEvent("onmousewheel", on_mouse_wheel)

_debug('Started')