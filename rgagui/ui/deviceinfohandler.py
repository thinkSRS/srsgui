
import logging
from PyQt5.QtWidgets import QTabWidget, QWidget,  QTextBrowser, QHBoxLayout

logger = logging.getLogger(__name__)


class DeviceInfoHandler(object):
    def __init__(self, parent):
        if not (hasattr(parent, 'inst_dict') and
                hasattr(parent, 'deviceInfo') and
                hasattr(parent, 'deviceInfoTabWidget') and
                type(parent.inst_dict) == dict and
                type(parent.deviceInfo) == QTextBrowser and
                type(parent.deviceInfoTabWidget) == QTabWidget
                ):
            raise AttributeError('Parent does not have all attributes required')
        self.parent = parent
        self.tabWidget = self.parent.deviceInfoTabWidget
        self.tabs = []
        self.browsers = []
        self.names = []
        if self.tabWidget.count() != 1:
            raise AttributeError('deviceInfoTabWidget is expected to have one tab')
        self.tabs.append(self.tabWidget.currentWidget())
        self.browsers.append(parent.deviceInfo)
        self.names.append('N/A')

    def select_browser(self, name):
        """
        Set parent.deviceInfo browser to the tab associated with the name
        """
        if name not in self.names:
            logger.error("'inst '{}' is not registered with DeviceInfoHandler".format(name))
        else:
            i = self.names.index(name)
            self.parent.deviceInfo = self.browsers[i]
            self.tabWidget.setCurrentIndex(i)

    def update_tabs(self):
        """
        Update tabs in sync with inst_dict
        """
        inst_dict = self.parent.inst_dict
        if len(inst_dict) == 0:
            logger.error('No item in inst_dict')

        while self.tabWidget.count() > 0:
            self.remove_tab()
        for inst in inst_dict:
            self.add_tab(inst)

        self.tabWidget.setCurrentIndex(0)
        self.parent.deviceInfo = self.browsers[0]

    def add_tab(self, name):
        """
        Add a new tab at the end
        """
        tab_count = self.tabWidget.count()
        tab_list_length = len(self.tabs)
        if tab_list_length > tab_count:
            self.tabWidget.addTab(self.tabs[tab_count], name)
            self.names.append(name)
            logger.debug('Added a tab from tabs list')
        else:
            tab = QWidget()
            layout = QHBoxLayout(tab)
            browser = QTextBrowser(tab)
            layout.addWidget(browser)
            self.tabWidget.addTab(tab, name)
            self.tabs.append(tab)
            self.browsers.append(browser)
            self.names.append(name)
            logger.debug('Created a new tab')

    def remove_tab(self):
        """
        Remove the last tab
        """
        count = self.tabWidget.count()
        if count > 0:
            self.tabWidget.removeTab(count - 1)
            self.names.pop()
            logger.debug('Removed the last tab')
        else:
            logger.error('No tab to remove')

