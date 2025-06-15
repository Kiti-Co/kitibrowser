import sys
import os
from PyQt5.QtCore import Qt, QUrl, QSize, QUrlQuery
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit, 
                            QStatusBar, QAction, QVBoxLayout, QWidget, QHBoxLayout,
                            QTabWidget, QMenu, QLabel, QSizePolicy, QToolButton,
                            QProgressBar, QShortcut, QStyle)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        
        self._web_page = WebPage(self.profile, self)
        self.setPage(self._web_page)
        
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
        settings.setDefaultTextEncoding("utf-8")
        settings.setAttribute(QWebEngineSettings.AutoLoadIconsForPage, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        
        cache_path = os.path.join(os.path.expanduser("~"), ".cache", "clowbrowser")
        os.makedirs(cache_path, exist_ok=True)
        self.profile.setCachePath(cache_path)
        self.profile.setPersistentStoragePath(os.path.join(cache_path, "storage"))
        
        user_agent = self.page().profile().httpUserAgent()
        self.page().profile().setHttpUserAgent(user_agent)
        
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)
        
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        
        self.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        self.page().profile().setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        self.page().profile().setHttpCacheMaximumSize(1024 * 1024 * 500)
        
        desktop_user_agent = user_agent.replace('Mobile', '').replace('mobile', '')
        self.page().profile().setHttpUserAgent(desktop_user_agent)
        
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)
        
        self.page().profile().setHttpUserAgent(
            f"{desktop_user_agent} ClowBrowser/1.5"
        )
        
        self.page().profile().setPersistentStoragePath(
            os.path.join(os.path.expanduser("~"), ".cache", "clowbrowser", "storage")
        )
        
        self.loadStarted.connect(self._on_load_started)
        self.loadFinished.connect(self._on_load_finished)
        
        self.setStyleSheet("""
            QWebEngineView {
                background-color: white;
                color: black;
            }
        """)
        
    def _on_load_started(self):
        self.setZoomFactor(1.0)
        
    def _on_load_finished(self, ok):
        if ok:
            self.page().runJavaScript("window.scrollTo(0, 0);")
            self.update()

class WebPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
    def certificateError(self, certificateError):
        return True
        
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        level_names = {
            0: "INFO",
            1: "WARNING",
            2: "ERROR"
        }
        level_name = level_names.get(int(level), "UNKNOWN")
        print(f"JS {level_name}: {message} ({sourceID}:{lineNumber})")
        return super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)
        
    def createWindow(self, _type):
        browser = self.parent().parent()
        if browser and hasattr(browser, 'add_new_tab'):
            return browser.add_new_tab()
        return None

class ClowBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clow Browser")
        self.setMinimumSize(1280, 800)
        
        self.setup_shortcuts()
    
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.ElideRight)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #202124;
            }
            QTabBar::tab {
                background: #2d2e30;
                color: #e8eaed;
                padding: 8px 15px 8px 15px;
                margin: 0 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #3c4043;
                border-bottom: none;
                min-width: 100px;
                max-width: 200px;
            }
            QTabBar::tab:selected {
                background: #202124;
                border-bottom: 2px solid #8ab4f8;
                margin-bottom: -1px;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
                background: #2d2e30;
            }
            QTabBar::tab:hover {
                background: #3c4043;
            }
            QTabBar::close-button {
                subcontrol-position: right;
                width: 16px;
                height: 16px;
                margin: 0px 2px;
                border-radius: 8px;
                background: transparent;
            }
            QTabBar::close-button:hover {
                background: #5f6368;
            }
            QTabBar::close-button::pressed {
                background: #9aa0a6;
            }
            
            /* Estilo dos botões de rolagem de abas */
            QTabBar::scroller {
                width: 20px;
            }
            QTabBar QToolButton {
                background: #2d2e30;
                border: none;
                padding: 0px;
                margin: 0px;
                color: #e8eaed;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar QToolButton::right-arrow {
                image: none;
                text: "›";
            }
            QTabBar QToolButton::left-arrow {
                image: none;
                text: "‹";
            }
            QTabBar QToolButton:hover {
                background: #3c4043;
            }
            QTabBar QToolButton:pressed {
                background: #5f6368;
            }
        """)
        
        self.setCentralWidget(self.tabs)
        self.init_ui()
        self.apply_styles()
        
        self.add_new_tab()
        
    def setup_shortcuts(self):
        new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        new_tab_shortcut.activated.connect(self.add_new_tab)
        
        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(self.close_current_tab)
        
        reload_shortcut = QShortcut(QKeySequence("F5"), self)
        reload_shortcut.activated.connect(self.reload_current_tab)
        reload_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reload_shortcut.activated.connect(self.reload_current_tab)
        
        focus_url_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        focus_url_shortcut.activated.connect(self.focus_url_bar)
        focus_url_shortcut = QShortcut(QKeySequence("F6"), self)
        focus_url_shortcut.activated.connect(self.focus_url_bar)
        
    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)
            
    def reload_current_tab(self):
        browser = self.current_browser()
        if browser:
            browser.reload()
            
    def focus_url_bar(self):
        if hasattr(self, 'url_bar') and self.url_bar:
            self.url_bar.setFocus()
            self.url_bar.selectAll()
        
    def init_ui(self):
        self.setup_toolbar()
        self.setup_statusbar()
        
    def setup_toolbar(self):
        toolbar = QToolBar("Barra de Navegação")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #202124;
                border: none;
                border-bottom: 1px solid #3c4043;
                padding: 5px 10px;
                spacing: 5px;
            }
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton:hover {
                background: #3c4043;
            }
            QToolButton:pressed {
                background: #5f6368;
            }
            QToolButton:disabled {
                color: #5f6368;
            }
        """)
        self.addToolBar(toolbar)
        
        def create_tool_button(icon_name, tooltip, slot, shortcut=None):
            btn = QToolButton()
            btn.setToolTip(tooltip)
            btn.setIcon(self.style().standardIcon(icon_name))
            btn.clicked.connect(slot)
            if shortcut:
                btn.setShortcut(shortcut)
            return btn
        
        self.back_btn = create_tool_button(
            getattr(QStyle, 'SP_ArrowBack', None) or QStyle.SP_ArrowLeft,
            "Voltar (Alt+Esquerda)",
            self.navigate_back,
            "Alt+Left"
        )
        
        self.forward_btn = create_tool_button(
            getattr(QStyle, 'SP_ArrowForward', None) or QStyle.SP_ArrowRight,
            "Avançar (Alt+Direita)",
            self.navigate_forward,
            "Alt+Right"
        )
        
        self.reload_btn = create_tool_button(
            QStyle.SP_BrowserReload,
            "Recarregar (F5)",
            self.reload_page,
            "F5"
        )
        
        self.home_btn = create_tool_button(
            QStyle.SP_ComputerIcon,
            "Página inicial (Alt+Home)",
            self.navigate_home,
            "Alt+Home"
        )
        
        toolbar.addWidget(self.back_btn)
        toolbar.addWidget(self.forward_btn)
        toolbar.addWidget(self.reload_btn)
        toolbar.addWidget(self.home_btn)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Digite um endereço ou termo de busca...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                border: 1px solid #5f6368;
                border-radius: 20px;
                background: #2d2e30;
                color: #e8eaed;
                min-width: 400px;
                margin: 5px 10px;
                font-size: 13px;
                selection-background-color: #5f6368;
            }
            QLineEdit:focus {
                border: 2px solid #8ab4f8;
                background: #3c4043;
                padding: 7px 14px;
            }
        """)
        
        toolbar.addWidget(self.url_bar)
        
        new_tab_btn = QToolButton()
        new_tab_btn.setText("+")
        new_tab_btn.setToolTip("Nova aba (Ctrl+T)")
        new_tab_btn.setFixedSize(24, 24)
        new_tab_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: 1px solid #5f6368;
                border-radius: 12px;
                color: #e8eaed;
                font-size: 16px;
                font-weight: bold;
            }
            QToolButton:hover {
                background: #3c4043;
                border-color: #8ab4f8;
            }
            QToolButton:pressed {
                background: #5f6368;
            }
        """)
        new_tab_btn.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(new_tab_btn, Qt.TopRightCorner)
        
        self.menu_btn = QToolButton()
        self.menu_btn.setPopupMode(QToolButton.InstantPopup)
        self.menu_btn.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))
        self.menu_btn.setToolTip("Menu")
        self.menu_btn.setStyleSheet("""
            QToolButton::menu-indicator { width: 0px; }
        """)
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2e30;
                color: #e8eaed;
                border: 1px solid #5f6368;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 30px 5px 30px;
            }
            QMenu::item:selected {
                background-color: #3c4043;
            }
            QMenu::item:disabled {
                color: #5f6368;
            }
        """)
        
        new_tab_action = menu.addAction("Nova aba")
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.add_new_tab)
        
        new_window_action = menu.addAction("Nova janela")
        new_window_action.setShortcut("Ctrl+N")
        new_window_action.triggered.connect(self.new_window)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("Sair")
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        
        self.menu_btn.setMenu(menu)
        toolbar.addWidget(self.menu_btn)
        
        self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Atualiza o estado dos botões de navegação com base no histórico da aba atual"""
        browser = self.current_browser()
        if browser:
            self.back_btn.setEnabled(browser.history().canGoBack())
            self.forward_btn.setEnabled(browser.history().canGoForward())
            
    def update_tab_title(self, browser, title):
        """Atualiza o título da aba quando o título da página muda"""
        index = self.tabs.indexOf(browser)
        if index >= 0:
            if not title or title == "about:blank":
                self.tabs.setTabText(index, "Nova aba")
                self.tabs.setTabIcon(index, self.style().standardIcon(QStyle.SP_FileIcon))
            else:
                display_title = title[:25] + ("..." if len(title) > 25 else "")
                self.tabs.setTabText(index, display_title)
                
                icon = browser.icon()
                if icon.isNull():
                    icon = self.style().standardIcon(QStyle.SP_FileIcon)
                self.tabs.setTabIcon(index, icon)
                
                self.tabs.setTabToolTip(index, title)
    
    def setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(14)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        
        self.status.addPermanentWidget(self.progress_bar)
        
        self.status.showMessage("Pronto")
    
    def current_browser(self):
        return self.tabs.currentWidget()
    
    def add_new_tab(self, url=None):
        browser = BrowserTab()
        
        browser.urlChanged.connect(self.update_url)
        browser.loadProgress.connect(self.update_progress)
        browser.loadFinished.connect(self.page_loaded)
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(browser, title))
        
        browser.loadFinished.connect(lambda ok, browser=browser: self.handle_load_finished(ok, browser))
        
        i = self.tabs.addTab(browser, "Nova aba")
        self.tabs.setTabIcon(i, self.style().standardIcon(QStyle.SP_BrowserReload))
        self.tabs.setCurrentIndex(i)
        
        if url and isinstance(url, QUrl) and url.isValid():
            browser.setUrl(url)
        else:
            browser.setUrl(QUrl("https://www.google.com"))
            
        return browser
        
    def handle_load_finished(self, ok, browser):
        if not ok:
            error_html = """
            <html>
            <head>
                <style>
                    body {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        background-color: #202124;
                        color: #e8eaed;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        text-align: center;
                    }
                    .error-container {
                        max-width: 500px;
                        padding: 20px;
                    }
                    h1 {
                        color: #f28b82;
                        font-size: 24px;
                        margin-bottom: 16px;
                    }
                    p {
                        margin: 10px 0;
                        color: #9aa0a6;
                    }
                    a {
                        color: #8ab4f8;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1>Não foi possível carregar a página</h1>
                    <p>Verifique sua conexão com a internet e tente novamente.</p>
                    <p><a href="#" onclick="window.history.back(); return false;">Voltar</a> | 
                       <a href="#" onclick="window.location.reload(); return false;">Recarregar</a> | 
                       <a href="https://www.google.com">Ir para a página inicial</a></p>
                </div>
            </body>
            </html>
            """
            browser.setHtml(error_html, QUrl("about:error"))
    
    def close_tab(self, index):
        if self.tabs.count() < 2:
            return
            
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
            self.tabs.removeTab(index)
    
        self.url_bar.setCursorPosition(0)

    def tab_changed(self, index):
        if index >= 0:
            browser = self.tabs.widget(index)
            if browser:
                self.update_url(browser.url())
                self.update_navigation_buttons()
                title = browser.page().title()
                if title:
                    self.tabs.setTabText(index, title[:15] + ("..." if len(title) > 15 else ""))
    
    def update_url(self, url):
        """Atualiza a barra de endereço com a URL atual"""
        if isinstance(url, QUrl):
            display_url = url.toString()
            if display_url.startswith('https://'):
                display_url = display_url[8:]
            elif display_url.startswith('http://'):
                display_url = display_url[7:]
                
            if display_url.endswith('/'):
                display_url = display_url[:-1]
                
            self.url_bar.setText(display_url)
            self.url_bar.setCursorPosition(0)
    
    def update_progress(self, progress):
        if progress < 100:
            self.progress_bar.setValue(progress)
            self.progress_bar.setVisible(True)
        else:
            self.progress_bar.setVisible(False)
    
    def page_loaded(self, ok):
        if ok:
            self.status.showMessage("Página carregada", 2000)
        else:
            self.status.showMessage("Erro ao carregar a página", 3000)
            
        self.progress_bar.setVisible(False)
    
    def navigate_home(self):
        """Navega para a página inicial"""
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl("https://www.google.com"))
            
    def navigate_back(self):
        """Navega para a página anterior no histórico"""
        browser = self.current_browser()
        if browser and browser.history().canGoBack():
            browser.back()
            
    def navigate_forward(self):
        """Avança para a próxima página no histórico"""
        browser = self.current_browser()
        if browser and browser.history().canGoForward():
            browser.forward()
            
    def reload_page(self):
        """Recarrega a página atual"""
        browser = self.current_browser()
        if browser:
            browser.reload()
            
    def new_window(self):
        """Abre uma nova janela do navegador"""
        new_browser = ClowBrowser()
        new_browser.show()
            
    def navigate_to_url(self):
        url_text = self.url_bar.text().strip()
        
        if not url_text:
            return
            
        self.status.showMessage("Carregando...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        if ' ' in url_text or '.' not in url_text:
            url = QUrl("https://www.google.com/search")
            query = QUrlQuery()
            query.addQueryItem("q", url_text)
            url.setQuery(query)
        else:
            if not url_text.startswith(('http://', 'https://')):
                url_text = 'https://' + url_text
            url = QUrl(url_text)
            
            if not url.isValid():
                self.status.showMessage("URL inválida", 3000)
                return
        
        self.current_browser().setUrl(url)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #202124;
                color: #e8eaed;
            }
            QToolBar {
                background-color: #2d2e30;
                border: none;
                border-bottom: 1px solid #3c4043;
                padding: 6px 8px;
                spacing: 6px;
            }
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                color: #e8eaed;
            }
            QToolButton:hover {
                background-color: #3c4043;
            }
            QToolButton:pressed {
                background-color: #5f6368;
            }
            QLineEdit {
                background: #3c4043;
                border: 1px solid #5f6368;
                border-radius: 20px;
                padding: 8px 20px;
                font-size: 14px;
                color: #e8eaed;
                margin: 0 8px;
                min-width: 400px;
            }
            QLineEdit:focus {
                background: #3c4043;
                border: 2px solid #8ab4f8;
                padding: 7px 19px;
            }
            QTabBar::tab {
                background: #3c4043;
                border: 1px solid #5f6368;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 20px;
                margin-right: 2px;
                color: #e8eaed;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: #202124;
                border-bottom: 2px solid #8ab4f8;
                color: #8ab4f8;
            }
            QTabBar::tab:!selected:hover {
                background: #5f6368;
            }
            QTabBar::tab:first-child {
                margin-left: 5px;
            }
            QTabBar::close-button {
                image: url(close_icon.png);
                subcontrol-position: right;
                subcontrol-origin: padding;
                padding: 2px 4px;
            }
            QStatusBar {
                background-color: #202124;
                color: #9aa0a6;
                border-top: 1px solid #3c4043;
                font-size: 11px;
            }
            QProgressBar {
                border: 1px solid #5f6368;
                border-radius: 4px;
                text-align: center;
                background: #3c4043;
                min-width: 100px;
                max-width: 200px;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #8ab4f8;
                border-radius: 2px;
            }
            QMenu {
                background-color: #2d2e30;
                color: #e8eaed;
                border: 1px solid #3c4043;
                padding: 4px 0;
            }
            QMenu::item:selected {
                background-color: #3c4043;
            }
            QMenu::item:disabled {
                color: #5f6368;
            }
        """)

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    QApplication.setAttribute(Qt.AA_UseOpenGLES)
    
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu-rasterization --enable-accelerated-video-decode --enable-accelerated-video-encode --enable-webrtc-hw-decoding --enable-webrtc-hw-encoding --enable-features=WebRTCHWDecoding,WebRTCHWEncoding,WebRTCH265WithOpenH264FFmpeg,WebRtcHideLocalIpsWithMdns,WebRtcUseEchoCanceller3"
    
    if sys.platform == "win32":
        os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
        os.environ["QT_QUICK_BACKEND"] = "software"
        os.environ["QMLSCENE_DEVICE"] = "softwarecontext"
    
    if "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = ""
    


    flags_to_add = [
        "--enable-gpu-rasterization",
        "--enable-accelerated-2d-canvas",
        "--disable-gpu-compositing",
        "--disable-software-rasterizer",
        "--disable-gpu"
    ]
    
    for flag in flags_to_add:
        if flag not in os.environ["QTWEBENGINE_CHROMIUM_FLAGS"]:
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += f" {flag}"
    
    if sys.platform == "win32":
        os.environ["QT_QUICK_BACKEND"] = "software"
        os.environ["QMLSCENE_DEVICE"] = "softwarecontext"
    
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "clowbrowser")
    os.makedirs(cache_dir, exist_ok=True)
    
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    os.environ["QTWEBENGINE_DISABLE_WEB_SECURITY"] = "1"
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass
    
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor("#202124"))
    palette.setColor(QPalette.WindowText, QColor("#e8eaed"))
    palette.setColor(QPalette.Base, QColor("#2d2e30"))
    palette.setColor(QPalette.AlternateBase, QColor("#3c4043"))
    palette.setColor(QPalette.ToolTipBase, QColor("#202124"))
    palette.setColor(QPalette.ToolTipText, QColor("#e8eaed"))
    palette.setColor(QPalette.Text, QColor("#e8eaed"))
    palette.setColor(QPalette.Button, QColor("#3c4043"))
    palette.setColor(QPalette.ButtonText, QColor("#e8eaed"))
    palette.setColor(QPalette.BrightText, QColor("#8ab4f8"))
    palette.setColor(QPalette.Highlight, QColor("#8ab4f8"))
    palette.setColor(QPalette.HighlightedText, QColor("#202124"))
    palette.setColor(QPalette.Link, QColor("#8ab4f8"))
    palette.setColor(QPalette.LinkVisited, QColor("#c58af9"))
    app.setPalette(palette)
    
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    browser = ClowBrowser()
    browser.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()