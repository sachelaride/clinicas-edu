from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.metrics import dp
from kivy.app import App # Import App

# Import the theme manager
from app.core.theme_manager import theme_manager

Builder.load_string("""
<ThemeSettingsScreen>:
    theme_spinner: theme_spinner
    icon_style_spinner: icon_style_spinner
    font_size_spinner: font_size_spinner
    
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: dp(10)
            canvas.before:
                Color:
                    rgba: 0.2, 0.6, 0.8, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Label:
                text: '⚙️ Configurações'
                font_size: '24sp'
                color: 1, 1, 1, 1
                size_hint_x: 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size
            
            Button:
                text: '❌ Voltar'
                size_hint_x: None
                width: dp(100)
                background_color: 0.1, 0.7, 0.5, 1
                on_press: app.root.current = 'clinic_menu'
        
        # Main Content
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(20)
                spacing: dp(15)
                
                # Theme Selection
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(120)
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.9, 0.9, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    padding: dp(15)
                    
                    Label:
                        text: '⚙️ Tema'
                        font_size: '18sp'
                        color: 0.1, 0.1, 0.1, 1
                        size_hint_y: None
                        height: dp(30)
                        halign: 'left'
                        text_size: self.size
                    
                    Spinner:
                        id: theme_spinner
                        text: 'Selecione um tema'
                        values: ['Padrão', 'Escuro', 'Médico', 'Moderno']
                        size_hint_y: None
                        height: dp(40)
                        background_color: 0.1, 0.7, 0.5, 1
                        on_text: root.on_theme_changed(self.text)
                
                # Icon Style
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(120)
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.9, 0.9, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    padding: dp(15)
                    
                    Label:
                        text: '⚙️ Estilo de Ícones'
                        font_size: '18sp'
                        color: 0.1, 0.1, 0.1, 1
                        size_hint_y: None
                        height: dp(30)
                        halign: 'left'
                        text_size: self.size
                    
                    Spinner:
                        id: icon_style_spinner
                        text: 'Material'
                        values: ['Material', 'Médico', 'Moderno']
                        size_hint_y: None
                        height: dp(40)
                        background_color: 0.1, 0.7, 0.5, 1
                        on_text: root.on_icon_style_changed(self.text)
                
                # Font Size
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(120)
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.9, 0.9, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    padding: dp(15)
                    
                    Label:
                        text: '⚙️ Tamanho da Fonte'
                        font_size: '18sp'
                        color: 0.1, 0.1, 0.1, 1
                        size_hint_y: None
                        height: dp(30)
                        halign: 'left'
                        text_size: self.size
                    
                    Spinner:
                        id: font_size_spinner
                        text: '14'
                        values: ['12', '14', '16', '18', '20']
                        size_hint_y: None
                        height: dp(40)
                        background_color: 0.1, 0.7, 0.5, 1
                        on_text: root.on_font_size_changed(self.text)
                
                # Actions
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(50)
                    spacing: dp(10)
                    
                    Button:
                        text: '💾 Salvar Tema'
                        background_color: 0.2, 0.8, 0.2, 1
                        on_press: root.save_custom_theme()
                    
                    Button:
                        text: '❌ Resetar'
                        background_color: 1.0, 0.6, 0.0, 1
                        on_press: root.reset_theme()
                    
                    Button:
                        text: '📤 Exportar'
                        background_color: 0.1, 0.7, 0.5, 1
                        on_press: root.export_theme()
""")

class ThemeSettingsScreen(Screen):
    theme_spinner = ObjectProperty(None)
    icon_style_spinner = ObjectProperty(None)
    font_size_spinner = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_theme_data = {}
        self.color_picker_popup = None
    
    def on_enter(self, *args):
        """Chamado quando a tela é exibida"""
        self.load_current_theme_settings()
    
    def load_current_theme_settings(self):
        """Carrega as configurações do tema atual"""
        current_theme = theme_manager.get_current_theme()
        self.current_theme_data = current_theme.copy()
        
        # Atualiza os controles
        self.theme_spinner.text = current_theme.get('name', 'Padrão')
        self.icon_style_spinner.text = current_theme.get('icon_style', 'material').title()
        self.font_size_spinner.text = str(current_theme.get('font_size', 14))
    
    def on_theme_changed(self, theme_name):
        """Chamado quando o tema é alterado"""
        # Encontra o ID do tema pelo nome
        theme_id = None
        for theme in theme_manager.get_theme_list():
            if theme['name'] == theme_name:
                theme_id = theme['id']
                break
        
        if theme_id:
            theme_manager.set_theme(theme_id)
            self.load_current_theme_settings()
            # Force UI refresh on ClinicMenuScreen
            app = App.get_running_app()
            if app and app.root and 'clinic_menu' in app.root.screen_names:
                app.root.get_screen('clinic_menu').apply_theme_to_ui()
    
    def on_icon_style_changed(self, style_name):
        """Chamado quando o estilo de ícones é alterado"""
        style_map = {
            'Material': 'material',
            'Médico': 'medical',
            'Moderno': 'modern'
        }
        
        icon_style = style_map.get(style_name, 'material')
        self.current_theme_data['icon_style'] = icon_style
        theme_manager.apply_current_theme_to_api() # Apply changes immediately
        # Force UI refresh on ClinicMenuScreen
        app = App.get_running_app()
        if app and app.root and 'clinic_menu' in app.root.screen_names:
            app.root.get_screen('clinic_menu').apply_theme_to_ui()
    
    def on_font_size_changed(self, font_size):
        """Chamado quando o tamanho da fonte é alterado"""
        self.current_theme_data['font_size'] = int(font_size)
        theme_manager.apply_current_theme_to_api() # Apply changes immediately
        # Force UI refresh on ClinicMenuScreen
        app = App.get_running_app()
        if app and app.root and 'clinic_menu' in app.root.screen_names:
            app.root.get_screen('clinic_menu').apply_theme_to_ui()
    
    def save_custom_theme(self):
        """Salva o tema customizado"""
        theme_name = f"Tema Personalizado {len(theme_manager.get_theme_list()) + 1}"
        
        # Cria um novo tema customizado
        theme_id = theme_manager.create_custom_theme(
            name=theme_name,
            colors=self.current_theme_data,
            border_radius=self.current_theme_data.get('border_radius', 8),
            font_size=self.current_theme_data.get('font_size', 14),
            icon_style=self.current_theme_data.get('icon_style', 'material')
        )
        
        # Define como tema atual
        theme_manager.set_theme(theme_id)
        
        # Atualiza a lista de temas
        self.theme_spinner.values = [theme['name'] for theme in theme_manager.get_theme_list()]
        self.theme_spinner.text = theme_name
        # Force UI refresh on ClinicMenuScreen
        app = App.get_running_app()
        if app and app.root and 'clinic_menu' in app.root.screen_names:
            app.root.get_screen('clinic_menu').apply_theme_to_ui()
    
    def reset_theme(self):
        """Reseta para o tema padrão"""
        theme_manager.set_theme('default')
        self.load_current_theme_settings()
        # Force UI refresh on ClinicMenuScreen
        app = App.get_running_app()
        if app and app.root and 'clinic_menu' in app.root.screen_names:
            app.root.get_screen('clinic_menu').apply_theme_to_ui()
    
    def export_theme(self):
        """Exporta o tema atual"""
        print("Exportando tema...")