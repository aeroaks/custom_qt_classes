#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
custom_qt_widgets

used as base class for configurable basic GUIs that interact with the Database.

Author: Akshay Verma
Date: 02-2017

""""

import os
import sys
import json
import logging
from time import gmtime
from time import strftime
from time import monotonic

from PyQt4 import QtGui
from PyQt4 import QtCore


# base widget class with groupbox #############################################
class DBWidget(QtGui.QWidget):
    """Class to make widgets used in EP GUIS

    Contains Groupbox with title methods, and layout to add items
    """
    def __init__(self, parent=None, name='dbicon'):
        super().__init__(parent)
        self.name = name
        self.setObjectName(self.name)
        self.vbox = QtGui.QVBoxLayout(self)
        self.box_layout = QtGui.QHBoxLayout()

        # add groupbox to widget
        self.init_groupbox()

    def init_groupbox(self):
        """Lineedit with groupbox used to display field name"""
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

        self.input_box = QtGui.QGroupBox()
        self.input_box.setLayout(self.box_layout)

        self.vbox.addWidget(self.input_box)

    def add_item_to_box(self, item):
        # add widget inside groupbox

        self.box_layout.addWidget(item)

    def increase_font(self, qt_item, font_size):
        font = qt_item.font()
        font.setPointSize(font_size)
        qt_item.setFont(font)
        return qt_item

    def update_title(self, lbl='UserInput', font_size=14, clear=True):
        # control title and font size of the groupbox; field reference name
        if clear:
            self.input_box.setTitle('')
        if lbl.endswith(' *'):
            self.input_box.setStyleSheet('QGroupBox::title {color: red;}')
        else:
            self.input_box.setStyleSheet('QGroupBox::title {color: black;}')
        lbl = self.input_box.title() + lbl

        self.input_box.setTitle(lbl)
        self.input_box = self.increase_font(self.input_box, font_size)


class DBExtendedLabel(QtGui.QLabel):
    """Class to make clickable label

    """
    clicked = QtCore.pyqtSignal()
    scroll = QtCore.pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()

    def wheelEvent(self, ev):
        self.scroll.emit(ev.delta())


class DBButtonGroup(QtGui.QButtonGroup):

    def __init__(self, parent):
        super().__init__(parent)

    def buttonClickedId(self, index):
        return self.id(index)


class DBIcon(QtGui.QWidget):
    """Class to display all the relevant icons

    - icons are placed in the same folder.
    - class can inherited sevral times
    """

    def __init__(self, parent=None, name='dbicon', set_icon='ok', set_state='rgb(166, 206, 227)'):
        super().__init__(parent)
        self.name = name
        self.setObjectName(self.name)
        self.vbox = QtGui.QVBoxLayout(self)

        self.set_icon = set_icon
        self.set_state = set_state
        self.icons = {
            'ok': '..\images\ok-32.png',
            'add': '..\images\plus-32.png',
            'qr': '..\images\qrcode-32.png'
        }

        self.init_icon()

    def init_icon(self):
        """Lineedit with groupbox used to display field name"""

        self.icon_label = DBExtendedLabel(self)
        self.icon_label.setStyleSheet("background-color: {}".format(self.set_state))
        self.icon_pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      self.icons[self.set_icon]))
        self.icon_label.setPixmap(self.icon_pixmap)
        self.icon_label.setMaximumHeight(self.icon_pixmap.width())
        self.icon_label.setMaximumWidth(self.icon_pixmap.height())
        # hides the background color of label
        # self.icon_label.setMask(self.icon_pixmap.mask())
        self.vbox.addWidget(self.icon_label)

    def set_icon_state(self, state_txt='rgb(166, 206, 227)'):
        self.set_state = state_txt
        self.icon_label.setStyleSheet("background-color : " + self.set_state)

        # def set_icon_scaling(self, scale=(30,30)):
        #     self.icon_pixmap.scaled(QtCore.QSize(scale[0], scale[1]), QtCore.Qt.KeepAspectRatio)


# Testing class ###############################################################
class MainUI(QtGui.QWidget):
    BUTTON_IMAGE = 'ok-32.png'

    def __init__(self, *args):
        super().__init__(*args)
        self.resize(350, 140)
        self.initButton()
        self.ImageButton.clicked.connect(self.buttonClicked)
        self.ImageButton.scroll.connect(self.wheelScrolled)

    def initButton(self):
        self.ImageButton = DBExtendedLabel(self)
        self.ImageButton.move(0, 0)
        print(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                              'ok-32.png'))
        self.ImageButton.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                              'ok-32.png')))
        self.ImageButton.setScaledContents(True)

    def buttonClicked(self):
        print('Button Clicked')

    def wheelScrolled(self, scrollAmount):
        scrollAmount /= 10
        self.ImageButton.resize(self.width() + scrollAmount, self.height() + scrollAmount)
        self.resize(self.ImageButton.size())


# groupbox contained input widgets #############################################
class DBComboBox(DBWidget):
    """Combobox to show list of items from the database column

    - items is the list of (modified, if needed) strings to show to the user
    - raw_items is is the ORM query result as a list of records.
    This is used to get connected information with the shown item.

    """

    currentTextChanged = QtCore.pyqtSignal(str)
    itemsAdded = QtCore.pyqtSignal()

    def __init__(self, parent=None, name='dbwidget'):
        super().__init__(parent)
        self.name = name
        self.setObjectName(self.name)

        self.items = []
        self.raw_items = []
        self.init_combobox()

    def init_combobox(self):
        """combobox with groupbox used to display field name"""
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(5)

        self.input_values = QtGui.QComboBox(self)
        self.input_values.setEditable(True)
        self.input_values.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.input_values.lineEdit().setReadOnly(True)
        self.input_values.setEditable(False)
        self.input_values.setSizePolicy(sizePolicy)
        self.input_values.currentIndexChanged.connect(self._currentIndexChanged)

        self.add_item_to_box(self.input_values)

    def set_focus_policy(self, policy_txt):
        # sets default focus to the widget, if enabled in settings
        if policy_txt.lower() == 'no':
            self.input_values.setFocusPolicy(QtCore.Qt.NoFocus)
        elif policy_txt.lower() == 'strong':
            self.input_values.setFocusPolicy(QtCore.Qt.StrongFocus)
        elif policy_txt.lower() == 'click':
            self.input_values.setFocusPolicy(QtCore.Qt.ClickFocus)
        elif policy_txt.lower() == 'tab':
            self.input_values.setFocusPolicy(QtCore.Qt.ClickFocus)

    def add_items(self, items, raw_items, font_size=12):
        # items are list of items (strings to display)
        # raw_items are database response with all the relevant data
        self.input_values.clear()
        self.items = items
        if raw_items:
            self.raw_items = raw_items
        self.input_values.addItems(items)
        self.itemsAdded.emit()
        self.input_values = self.increase_font(self.input_values, font_size)
        # self.input_values.resize(self.input_values.sizeHint())

    def setReadOnly(self, state=False):
        # Make the input field read only
        self.input_values.setEditable(state)

    def set_text(self, txt):
        # set txt programmatically
        full_input_txt = [item_txt for item_txt in self.items if txt.lower() in item_txt.lower()]
        if len(full_input_txt) > 0:
            txt_index = self.input_values.findText(full_input_txt[0])
            if txt_index != -1:
                self.input_values.setCurrentIndex(txt_index)
                return True

        return False


    def _currentIndexChanged(self):
        self.currentTextChanged.emit(self.input_values.currentText())

    def current_value(self):
        # get current value of text
        return self.input_values.currentText()

    def clear_text(self):
        # makes the first item in list as selected
        # can be used when "" is in the items as first item
        self.input_values.setCurrentIndex(0)

    def clear_text_and_set_focus(self):
        self.input_values.setCurrentIndex(0)
        self.input_values.setFocus()


class DBLineEdit(DBWidget):
    """LineEdit to show text item from the database column

    - items is the string to show to the user
    - can be set as readonly

    """

    def __init__(self, parent=None, name='dbwidget'):
        super().__init__(parent)
        self.name = name
        self.setObjectName(self.name)

        self.init_line()

    def init_line(self):
        """Lineedit with groupbox used to display field name"""
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(5)

        self.input_values = QtGui.QLineEdit(self)
        self.input_values.setSizePolicy(sizePolicy)
        self.input_values.setAlignment(QtCore.Qt.AlignHCenter)

        self.add_item_to_box(self.input_values)

    def set_focus_policy(self, policy_txt):
        # sets default focus to the widget, if enabled in settings
        if policy_txt.lower() == 'no':
            self.input_values.setFocusPolicy(QtCore.Qt.NoFocus)
        elif policy_txt.lower() == 'strong':
            self.input_values.setFocusPolicy(QtCore.Qt.StrongFocus)
        elif policy_txt.lower() == 'click':
            self.input_values.setFocusPolicy(QtCore.Qt.ClickFocus)
        elif policy_txt.lower() == 'tab':
            self.input_values.setFocusPolicy(QtCore.Qt.ClickFocus)

    def setReadOnly(self, state=False):
        # Make the input field read only
        self.input_values.setReadOnly(state)

    def current_value(self):
        # get current value of text
        return self.input_values.text()

    def set_text(self, msg, font_size=11):
        self.input_values = self.increase_font(self.input_values, font_size)
        self.input_values.setText(msg)

    def clear_text(self):
        self.input_values.clear()

    def clear_text_and_set_focus(self):
        self.input_values.clear()
        self.input_values.setFocus()


class DBTextEdit(DBWidget):
    """TextEdit to show text item from the database column

    - items is the string to show to the user
    - can be set as readonly
    - used for multiline text

    """

    def __init__(self, parent=None, name='dbwidget'):
        super().__init__(parent)
        self.name = name
        self.setObjectName(self.name)

        self.init_text()

    def init_text(self):
        """Lineedit with groupbox used to display field name"""

        self.input_values = QtGui.QTextEdit(self)

        self.add_item_to_box(self.input_values)

    def set_focus_policy(self, policy_txt):
        # sets default focus to the widget, if enabled in settings
        if policy_txt.lower() == 'no':
            self.input_values.setFocusPolicy(QtCore.Qt.NoFocus)
        elif policy_txt.lower() == 'strong':
            self.input_values.setFocusPolicy(QtCore.Qt.StrongFocus)
        elif policy_txt.lower() == 'click':
            self.input_values.setFocusPolicy(QtCore.Qt.ClickFocus)
        elif policy_txt.lower() == 'tab':
            self.input_values.setFocusPolicy(QtCore.Qt.ClickFocus)

    def setReadOnly(self, state=False):
        # Make the input field read only
        self.input_values.setReadOnly(state)

    def current_value(self):
        # get current value of text
        return self.input_values.toPlainText()

    def set_text(self, msg, font_size=11):
        self.input_values = self.increase_font(self.input_values, font_size)
        self.input_values.setText(msg)

    def clear_text(self):
        self.input_values.setText('')

    def clear_text_and_set_focus(self):
        self.input_values.clear()
        self.input_values.setFocus()


class DBLabel(DBWidget):
    """Label to show readonly text from the database column

    - items is the string to show to the user

    """

    def __init__(self, parent=None, name='dbwidget'):
        super().__init__(parent)
        self.name = name
        self.setObjectName(self.name)

        self.init_label()

    def init_label(self):
        """Lineedit with groupbox used to display field name"""
        self.input_values = DBExtendedLabel(self)
        self.input_values.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)

        self.add_item_to_box(self.input_values)

    def set_focus_policy(self, policy_txt):
        # sets default focus to the widget, if enabled in settings
        if policy_txt.lower() == 'no':
            self.input_values.setFocusPolicy(QtCore.Qt.NoFocus)
        elif policy_txt.lower() == 'strong':
            self.input_values.setFocusPolicy(QtCore.Qt.StrongFocus)
        elif policy_txt.lower() == 'click':
            self.input_values.setFocusPolicy(QtCore.Qt.ClickFocus)
        elif policy_txt.lower() == 'tab':
            self.input_values.setFocusPolicy(QtCore.Qt.ClickFocus)

    def current_value(self):
        # get current value of text
        return self.input_values.text()

    def set_center_alignment(self):
        self.input_values.setAlignment(QtCore.Qt.AlignHCenter)

    def update_text(self, msg, font_size=11, clear=True):
        if clear:
            self.input_values.setText('')
        msg = self.input_values.text() + msg
        self.input_values.setText(msg)
        self.input_values = self.increase_font(self.input_values, font_size)
        self.input_values.setWordWrap(True)

    def clear_text(self):
        self.input_values.setText('')

    def clear_text_and_set_focus(self):
        self.input_values.setText('')
        self.input_values.setFocus()


class DBTable(DBWidget):
    """Table widget

    - used to list of data
    - right click menu to delete rows from the model
    """

    def __init__(self, parent=None, name='dbtable'):
        super().__init__(parent)
        self.name = name
        self.setObjectName(self.name)

        self.raw_data = {}
        self.valid_rows = []
        self.data_validity = True
        self.data_model = QtGui.QStandardItemModel()

        self.init_table()

    def init_table(self):
        # setup table
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)

        self.data_table = QtGui.QTableView(self)
        self.data_table.setAutoScroll(True)
        self.data_table.setModel(self.data_model)
        self.data_table.setSizePolicy(sizePolicy)
        self.data_table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.data_table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.data_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.data_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.data_table.customContextMenuRequested.connect(self.right_click_menu)
        # self.data_table.dataChanged.connect(self.result_table.resizeColumnsToContents)

        self.add_item_to_box(self.data_table)

    def set_focus_policy(self, policy_txt):
        # sets default focus to the widget, if enabled in settings
        if policy_txt.lower() == 'no':
            self.data_table.setFocusPolicy(QtCore.Qt.NoFocus)
        elif policy_txt.lower() == 'strong':
            self.data_table.setFocusPolicy(QtCore.Qt.StrongFocus)
        elif policy_txt.lower() == 'click':
            self.data_table.setFocusPolicy(QtCore.Qt.ClickFocus)
        elif policy_txt.lower() == 'tab':
            self.data_table.setFocusPolicy(QtCore.Qt.ClickFocus)

    def reset_table(self):
        """clear data for the next session
        """
        self.data_model.clear()

    def clear_text(self):
        # clear data only for results model
        self.data_model.removeRows(0, self.data_model.rowCount())

    def clear_text_and_set_focus(self):
        self.data_model.removeRows(0, self.data_model.rowCount())
        self.data_model.setFocus()

    def resize_widget_to_contents(self):
        self.resize(self.size().width(),
                    3 * self.data_model.rowCount() * self.data_table.rowHeight(0))

    def set_table_headers(self, header_list, hide=None):
        # list of strings for header
        self.data_model.setHorizontalHeaderLabels(header_list)
        if hide:
            for col in hide.split(','):
                self.data_table.hideColumn(int(col))
        # fill the widget
        self.data_table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def set_table_data(self, table_data):
        # add data to the table view
        # table_data is list(rows) of list(data)
        # table_data['headers'] : list
        # table_data['data'] : list
        if 'header' in table_data:
            self.set_table_headers(table_data['header'])

        if 'data' in table_data:
            for row in table_data['data']:
                self.add_single_row(row)

        self.resize_table_view()

    def add_single_row(self, row_list, raw_data=None):

        # check if osa already in the list
        item_exists = self.data_model.findItems(row_list[0], column=0)

        result_model_row = []
        for i in row_list:
            item = QtGui.QStandardItem(str(i))
            result_model_row.append(item)

        if len(item_exists) == 0:
            # append row to the end
            self.data_model.appendRow(result_model_row)

        elif len(item_exists) > 0:
            # delete existing row
            self.data_model.removeRow(item_exists[0].row())
            # update row
            self.data_model.appendRow(result_model_row)

        self.data_model.dataChanged.emit(QtGui.QStandardItem('').index(),
                                         QtGui.QStandardItem('').index())

    def resize_table_view(self):
        # fit table to contents and stretch last column

        self.data_table.resizeColumnsToContents()
        self.data_table.resizeRowsToContents()
        # self.resize_widget_to_contents()

        self.data_table.horizontalHeader().setStretchLastSection(True)

    def get_selected_row_name(self, col=0):

        current_index = self.data_table.selectionModel().currentIndex()

        return self.data_model.item(current_index.row(), col).text()

    def remove_row(self):
        # remove selected row from the table
        # QModelIndex currentIndex = ui->tableView->selectionModel()->currentIndex();
        # model->removeRow(currentIndex.row());
        current_index = self.data_table.selectionModel().currentIndex()

        if current_index.row() in self.valid_rows:
            self.valid_rows.remove(current_index.row())

        self.data_model.removeRow(current_index.row())

    def check_valid_data(self, col=None, valid_value=[]):
        # check all data whether it is valid or not.
        self.data_validity = True
        for r in range(self.data_model.rowCount()):
            row_validity = self.check_valid_data_row(r, col, valid_value=valid_value)

            if row_validity:
                # valid rows are added to a list for reference
                self.valid_rows.append(r)
                self.valid_rows = list(set(self.valid_rows))
            else:
                # invalid rows set widget validity flag to false and the respective row colour becomes red
                self.data_validity = False
                self.update_row_color(r, 'red')

        return self.data_validity

    def check_valid_data_row(self, row=None, col=None, valid_value=[]):
        # check valid row and highlight as red if invalid
        # validity values are in the hidden column
        # valid values are passed from the worker

        if int(self.data_model.item(row, col).text()) in valid_value:
            is_valid = True
        else:
            is_valid = False

        return is_valid

    def update_row_color(self, row, clr_txt):
        # change colour of all items in the row

        for c in range(self.data_model.columnCount()):
            self.data_model.item(row, c).setBackground(QtGui.QBrush(QtGui.QColor(clr_txt)))

    def get_valid_row_column_data(self, col):
        # for valid rows, get the value of the hidden column
        valid_column_data = []
        if self.data_validity:
            for row in self.valid_rows:
                if self.data_model.item(row, col):
                    valid_column_data.append(int(self.data_model.item(row, col).text()))

        return valid_column_data

    def row_count(self):
        # table data row count
        return self.data_model.rowCount()

    def right_click_menu(self, point):
        # right click menu to allow deletion of rows
        remove_action = QtGui.QAction('Remove selected row', self)
        remove_action.triggered.connect(self.remove_row)

        menu = QtGui.QMenu(self)
        menu.addAction(remove_action)
        menu.popup(self.data_table.viewport().mapToGlobal(point))
