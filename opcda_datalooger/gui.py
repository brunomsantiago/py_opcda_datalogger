import sys
from PySide.QtGui import (QAbstractItemView,
                          QApplication,
                          QCheckBox,
                          QComboBox,
                          QDockWidget,
                          QHBoxLayout,
                          QGroupBox,
                          QLabel,
                          QLineEdit,
                          QListWidget,
                          QMainWindow,
                          QPushButton,
                          QRegExpValidator,
                          QTextEdit,
                          QVBoxLayout,
                          QWidget)
# from PySide.QtGui.QAbstractItemView import MultiSelection
from PySide.QtCore import QRegExp, Qt, QTimer
import opcda


class MainWindow(QMainWindow):
    def __init__(self, opc=None):
        super(MainWindow, self).__init__()

        self.opc = opc

        self.setWindowTitle('OPC DA Datalogger')

        self.layout = QHBoxLayout(self)

        self.configuration = Configuration(self, opc)
        self.configuration_dock = QDockWidget("Configuration", self)
        self.configuration_dock.setWidget(self.configuration)
        self.configuration_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.configuration_dock)

        self.logging_area = LoggingArea(self)
        self.logging_dock = QDockWidget("Logging", self)
        self.logging_dock.setWidget(self.logging_area)
        self.logging_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, self.logging_dock)

        self.setLayout(self.layout)
        self.resize(900, 600)

        self.logging_timer = QTimer(self)
        self.logging_timer.timeout.connect(self._loogging_callback)

    def _start_logging(self):
        self.tags = self.configuration.tag_selection.selected_tags()
        header, line = opcda.read(self.opc, self.tags)
        self.logging_area.te_logging.clear()
        self.logging_area.te_logging.append(header)
        self.logging_timer.start(500)

    def _loogging_callback(self):
        header, line = opcda.read(self.opc, self.tags)
        self.logging_area.te_logging.append(line)

    def _stop_logging(self):
        self.logging_timer.stop()


class Configuration(QWidget):
    def __init__(self, parent=None, opc=None):
        super(Configuration, self).__init__()
        self.layout = QVBoxLayout(self)

        # TagSelection() is inited before Server() but added later (inited)
        self.tag_selection = TagSelecion(self, opc)

        self.server = Server(self, opc, self.tag_selection)
        self.layout.addWidget(self.server)

        # TagSelection() is instanced before Server() but added later (added)
        self.layout.addWidget(self.tag_selection)

        self.read_options = ReadOptions(self)
        self.read_options.setEnabled(False)
        self.layout.addWidget(self.read_options)

        self.logging_options = LoggingOptions()
        self.logging_options.setEnabled(False)
        self.layout.addWidget(self.logging_options)

        self.setLayout(self.layout)


class Server(QGroupBox):
    def __init__(self, parent=None, opc=None, tag_selection=None):
        super(Server, self).__init__()

        self.opc = opc
        self.tag_selection = tag_selection

        self.setTitle('OPC Server Selection')

        self.layout = QHBoxLayout(self)

        self.button_refresh = QPushButton('Refresh', self)
        self.button_refresh.clicked.connect(self._refresh)
        self.layout.addWidget(self.button_refresh)

        self.combobox_server = QComboBox(self)
        self.layout.addWidget(self.combobox_server)

        self.button_connect = QPushButton('Conect', self)
        self.button_connect.clicked.connect(self._connect)
        self.layout.addWidget(self.button_connect)

        self.setLayout(self.layout)

        self._refresh()

    def _refresh(self):
        servers = opcda.servers(self.opc)
        self.combobox_server.clear()
        self.combobox_server.addItems(servers)

    def _connect(self):
        server = self.combobox_server.currentText()
        connected = opcda.connect(self.opc, server)
        if connected:
            if self.tag_selection:
                self.tag_selection._refresh()


class TagSelecion(QGroupBox):
    def __init__(self, parent=None, opc=None):
        super(TagSelecion, self).__init__()

        self.opc = opc

        self.setTitle('Tag Selection')

        self.layout = QVBoxLayout(self)

        self.button_refresh = QPushButton('Refresh', self)
        self.button_refresh.clicked.connect(self._refresh)
        self.layout.addWidget(self.button_refresh)

        self.button_all = QPushButton('Select All', self)
        self.button_all.clicked.connect(self._select_all)
        self.layout.addWidget(self.button_all)

        self.button_none = QPushButton('Select None', self)
        self.button_none.clicked.connect(self._select_none)
        self.layout.addWidget(self.button_none)

        self.hbox_pattern = QHBoxLayout(self)
        self.button_pattern = QPushButton('Toggle Pattern', self)
        self.button_pattern.clicked.connect(self._toggle_pattern)
        self._next_toggle = 'select'
        self.hbox_pattern.addWidget(self.button_pattern)
        self.le_pattern = QLineEdit(self)
        self.le_pattern.setPlaceholderText('Pattern')
        self.hbox_pattern.addWidget(self.le_pattern)
        self.layout.addLayout(self.hbox_pattern)

        self.label = QLabel('Select Tags', self)
        self.layout.addWidget(self.label)

        self.listw_tags = QListWidget(self)
        self.listw_tags.setSelectionMode(QAbstractItemView.MultiSelection)
        self.layout.addWidget(self.listw_tags)

        self.setLayout(self.layout)

    def selected_tags(self):
        return [item.text() for item in self.listw_tags.selectedItems()]

    def _refresh(self):
        self.tags_all = opcda.tags(self.opc)
        self.listw_tags.clear()
        self.listw_tags.addItems(self.tags_all)

    def _select_all(self):
        self.listw_tags.selectAll()

    def _select_none(self):
        self.listw_tags.clearSelection()

    def _toggle_pattern(self):
        toggle = self._next_toggle
        if toggle is 'select':
            self._next_toggle = 'deselect'
        elif toggle is 'deselect':
            self._next_toggle = 'select'
        pattern = self.le_pattern.text().lower()
        if len(pattern) is 0:
            matched_tags = []
        else:
            matched_tags = [tag for tag in self.tags_all if
                            pattern in tag.lower()]
        for tag in matched_tags:
            item = self.listw_tags.findItems(tag, Qt.MatchExactly)[0]
            if toggle is 'select':
                item.setSelected(True)
            elif toggle is 'deselect':
                item.setSelected(False)


class ReadOptions(QGroupBox):
    def __init__(self, parent=None):
        super(ReadOptions, self).__init__()

        self.setTitle('Reading Options')

        self.layout = QVBoxLayout(self)

        self.label_poolling_rate = QLabel('Pooling Rate (ms)', self)
        self.layout.addWidget(self.label_poolling_rate)

        self.le_poolling_rate = QLineEdit(self)
        self.le_poolling_rate.setText('200')
        regex = QRegExp('[0-9]+')
        validator = QRegExpValidator(regex)
        self.le_poolling_rate.setValidator(validator)
        self.layout.addWidget(self.le_poolling_rate)

        self.chbox_sync = QCheckBox("Synchronous read")
        self.layout.addWidget(self.chbox_sync)

        self.setLayout(self.layout)


class LoggingOptions(QGroupBox):
    def __init__(self, parent=None):
        super(LoggingOptions, self).__init__()

        self.setTitle('Logging Options')

        self.layout = QVBoxLayout(self)

        self.chbox_include_timestamps = QCheckBox('Include timestamps')
        self.layout.addWidget(self.chbox_include_timestamps)

        self.chbox_equal_lines = QCheckBox(("Ignore if timestamps and values "
                                            "don't change"))
        self.layout.addWidget(self.chbox_equal_lines)

        self.hbox_bad_quality = QHBoxLayout(self)
        self.label_bad_quality = QLabel(('Value to log if reading '
                                         'quality is bad'), self)
        self.hbox_bad_quality.addWidget(self.label_bad_quality)
        self.le_bad_quality = QLineEdit(self)
        self.le_bad_quality.setText('bad')
        regex = QRegExp('[a-zA-Z0-9]+')
        validator = QRegExpValidator(regex)
        self.le_bad_quality.setValidator(validator)
        self.hbox_bad_quality.addWidget(self.le_bad_quality)
        self.layout.addLayout(self.hbox_bad_quality)

        self.hbox_separator = QHBoxLayout(self)
        self.label_separator = QLabel('CSV separator', self)
        self.hbox_separator.addWidget(self.label_separator)
        self.le_separator = QLineEdit(self)
        self.le_separator.setText(';')
        self.hbox_separator.addWidget(self.le_separator)
        self.layout.addLayout(self.hbox_separator)

        self.chbox_print_exceptions = QCheckBox(('Print exceptions as '
                                                 'comment'))
        self.layout.addWidget(self.chbox_print_exceptions)

        self.hbox_comment_char = QHBoxLayout(self)
        self.label_comment_char = QLabel('Comment escape character', self)
        self.hbox_comment_char.addWidget(self.label_comment_char)
        self.le_comment_char = QLineEdit(self)
        self.le_comment_char.setText("'")
        self.hbox_comment_char.addWidget(self.le_comment_char)
        self.layout.addLayout(self.hbox_comment_char)

        self.setLayout(self.layout)


class LoggingArea(QWidget):
    def __init__(self, parent=None):
        super(LoggingArea, self).__init__()

        self.layout = QVBoxLayout(self)

        self.hbox_buttons_top = QHBoxLayout(self)
        self.button_start = QPushButton('Start Logging', self)
        self.button_start.clicked.connect(parent._start_logging)
        self.hbox_buttons_top.addWidget(self.button_start)
        self.button_stop = QPushButton('Stop Logging', self)
        self.button_stop.clicked.connect(parent._stop_logging)
        self.hbox_buttons_top.addWidget(self.button_stop)
        self.layout.addLayout(self.hbox_buttons_top)

        self.te_logging = QTextEdit(self)
        self.layout.addWidget(self.te_logging)

        self.hbox_buttons_bottom = QHBoxLayout(self)
        self.button_clear = QPushButton('Clear Data', self)
        self.button_clear.clicked.connect(self._clear_data)
        self.hbox_buttons_bottom.addWidget(self.button_clear)
        self.button_clipboard = QPushButton('Copy to Clipboard', self)
        self.button_clipboard.clicked.connect(self._copy_to_cliboard)
        self.hbox_buttons_bottom.addWidget(self.button_clipboard)
        self.button_file = QPushButton('Save to CSV', self)
        self.button_file.clicked.connect(self._save_to_csv)
        self.button_file.setEnabled(False)
        self.hbox_buttons_bottom.addWidget(self.button_file)
        self.layout.addLayout(self.hbox_buttons_bottom)

        self.setLayout(self.layout)

    def _clear_data(self):
        self.te_logging.clear()

    def _copy_to_cliboard(self):
        self.te_logging.selectAll()
        self.te_logging.copy()

    def _save_to_csv(self):
        print('Save to csv')


def main():
    app = QApplication(sys.argv)
    opc = opcda.start()
    main_window = MainWindow(opc)
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
