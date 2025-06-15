import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon, QPixmap

class ClowBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuração inicial
        self.setWindowTitle("Clow Browser")
        self.setMinimumSize(1024, 768)
        
        # User Agent personalizado
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ClowBrowser/1.0"
        
        # Configuração das guias
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.setCentralWidget(self.tabs)
        
        # Inicialização
        self.init_ui()
        self.new_tab()
    
    def init_ui(self):
        """Configura toda a interface do usuário"""
        self.setup_navbar()
        self.setup_statusbar()
        self.apply_styles()
        self.setWindowIcon(self.load_icon("logo.png"))
    
    def load_icon(self, icon_name):
        """Carrega ícones da pasta base"""
        icon_path = os.path.join(os.path.dirname(__file__), icon_name)
        return QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
    
    def setup_navbar(self):
        """Cria a barra de navegação"""
        navbar = QToolBar("Barra de Ferramentas")
        self.addToolBar(navbar)
        
        # Botão Nova Guia
        new_tab_btn = QAction(self.load_icon("newtab.png"), "Nova Guia", self)
        new_tab_btn.triggered.connect(self.new_tab)
        navbar.addAction(new_tab_btn)
        
        # Ações de navegação
        nav_actions = [
            ("Voltar", "back.png", lambda: self.current_browser().back()),
            ("Avançar", "forward.png", lambda: self.current_browser().forward()),
            ("Recarregar", "reload.png", lambda: self.current_browser().reload()),
            ("Home", "home.png", self.navigate_home)
        ]
        
        for text, icon, slot in nav_actions:
            action = QAction(self.load_icon(icon), text, self)
            action.triggered.connect(slot)
            navbar.addAction(action)
        
        # Barra de URL
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Digite uma URL ou termo de pesquisa...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
    
    def setup_statusbar(self):
        """Configura a barra de status"""
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Pronto", 3000)
    
    def apply_styles(self):
        """Aplica o estilo CSS personalizado"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QToolBar {
                background-color: #2c3e50;
                padding: 4px;
                border-bottom: 1px solid #1a2a3a;
                spacing: 8px;
            }
            QToolButton {
                color: #ecf0f1;
                background-color: transparent;
                padding: 5px 8px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #34495e;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
                min-width: 400px;
                font-size: 14px;
            }
            QStatusBar {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 12px;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #34495e;
                color: white;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2c3e50;
                border-bottom: 2px solid #3498db;
            }
        """)
    
    def current_browser(self):
        """Retorna o navegador da guia atual"""
        return self.tabs.currentWidget()
    
    def new_tab(self, url=None):
        """Cria uma nova guia"""
        browser = QWebEngineView()
        
        # Configura o User Agent
        profile = browser.page().profile()
        profile.setHttpUserAgent(self.USER_AGENT)
        
        if not url:
            url = "https://www.google.com"
        
        browser.setUrl(QUrl(url))
        browser.urlChanged.connect(self.update_url)
        
        # Adiciona a nova guia
        index = self.tabs.addTab(browser, "Nova Guia")
        self.tabs.setCurrentIndex(index)
        
        # Configura o ícone da guia
        favicon = browser.page().icon()
        if not favicon.isNull():
            self.tabs.setTabIcon(index, favicon)
        
        # Atualiza o título quando a página carrega
        browser.titleChanged.connect(lambda title, browser=browser: 
            self.update_tab_title(browser, title))
        
        browser.iconChanged.connect(lambda icon, browser=browser: 
            self.update_tab_icon(browser, icon))
    
    def close_tab(self, index):
        """Fecha a guia especificada"""
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            widget.deleteLater()
            self.tabs.removeTab(index)
    
    def tab_changed(self, index):
        """Atualiza a UI quando a guia é alterada"""
        if index >= 0:
            browser = self.tabs.widget(index)
            if browser:
                self.update_url(browser.url())
    
    def update_tab_title(self, browser, title):
        """Atualiza o título da guia"""
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title[:15] + "..." if len(title) > 15 else title)
    
    def update_tab_icon(self, browser, icon):
        """Atualiza o ícone da guia"""
        index = self.tabs.indexOf(browser)
        if index != -1 and not icon.isNull():
            self.tabs.setTabIcon(index, icon)
    
    def navigate_home(self):
        """Navega para a página inicial"""
        self.current_browser().setUrl(QUrl("https://www.google.com"))
    
    def navigate_to_url(self):
        """Navega para a URL digitada"""
        url = self.url_bar.text().strip()
        
        if not url:
            return
            
        # Verifica se é um termo de pesquisa
        if ' ' in url or '.' not in url:
            url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
        elif not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        self.current_browser().setUrl(QUrl(url))
    
    def update_url(self, q):
        """Atualiza a barra de URL quando a página muda"""
        self.url_bar.setText(q.toString())
        self.status.showMessage(f"Carregando: {q.host()}", 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Configuração para alta DPI
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    browser = ClowBrowser()
    browser.show()
    sys.exit(app.exec_())