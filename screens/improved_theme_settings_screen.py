from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from app.core.theme_manager import theme_manager
import api

Builder.load_string("""
<ThemePreviewCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(200)
    padding: dp(15)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: root.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [root.border_radius]
        Color:
            rgba: root.border_color
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, root.border_radius
            width: 2 if root.is_selected else 1
    
    # Nome do tema
    Label:
        text: root.theme_name
        font_size: '18sp'
        bold: True
        color: root.text_color
        size_hint_y: None
        height: dp(30)
    
    # Preview das cores
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(40)
        spacing: dp(5)
        
        # Cor primária
        Widget:
            canvas.before:
                Color:
                    rgba: root.primary_color
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [6]
        
        # Cor secundária
        Widget:
            canvas.before:
                Color:
                    rgba: root.secondary_color
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [6]
        
        # Cor de destaque
        Widget:
            canvas.before:
                Color:
                    rgba: root.accent_color
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [6]
        
        # Cor de sucesso
        Widget:
            canvas.before:
                Color:
                    rgba: root.success_color
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [6]
    
    # Botões de exemplo
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(35)
        spacing: dp(5)
        
        Button:
            text: 'Primário'
            background_color: root.primary_color
            color: 1, 1, 1, 1
            font_size: '14sp'
        
        Button:
            text: 'Destaque'
            background_color: root.accent_color
            color: 1, 1, 1, 1
            font_size: '14sp'
        
        Button:
            text: 'Sucesso'
            background_color: root.success_color
            color: 1, 1, 1, 1
            font_size: '14sp'
    
    # Informações do tema
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(25)
        
        Label:
            text: f"Fonte: {root.font_size}px"
            font_size: '12sp'
            color: root.text_color
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
        
        Label:
            text: f"Estilo: {root.icon_style.title()}"
            font_size: '12sp'
            color: root.text_color
            size_hint_x: 0.5
            halign: 'right'
            text_size: self.size
    
    # Botão de seleção
    Button:
        text: '✓ Selecionado' if root.is_selected else 'Selecionar Tema'
        size_hint_y: None
        height: dp(40)
        background_color: root.success_color if root.is_selected else root.primary_color
        color: 1, 1, 1, 1
        font_size: '16sp'
        disabled: root.is_selected
        on_press: root.screen.select_theme(root.theme_id)

<ImprovedThemeSettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: dp(15)
            canvas.before:
                Color:
                    rgba: 0.0, 0.47, 0.84, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Button:
                text: '← Voltar'
                size_hint_x: None
                width: dp(100)
                background_color: 0, 0, 0, 0
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: app.root.current = 'clinic_menu'
            
            Label:
                text: 'Configurações de Tema'
                font_size: '24sp'
                color: 1, 1, 1, 1
                bold: True
            
            Button:
                text: '🎨 Criar Tema'
                size_hint_x: None
                width: dp(120)
                background_color: 0.0, 0.73, 0.83, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.create_custom_theme()
        
        # Informações do tema atual
        BoxLayout:
            size_hint_y: None
            height: dp(80)
            padding: dp(15)
            spacing: dp(15)
            canvas.before:
                Color:
                    rgba: 0.96, 0.97, 0.98, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.7
                
                Label:
                    text: f"Tema Atual: {root.current_theme_name}"
                    font_size: '18sp'
                    bold: True
                    color: 0.13, 0.13, 0.13, 1
                    size_hint_y: None
                    height: dp(25)
                    halign: 'left'
                    text_size: self.size
                
                Label:
                    text: "Personalize a aparência do sistema selecionando um dos temas disponíveis"
                    font_size: '14sp'
                    color: 0.5, 0.5, 0.5, 1
                    size_hint_y: None
                    height: dp(25)
                    halign: 'left'
                    text_size: self.size
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.3
                spacing: dp(10)
                
                Button:
                    text: '🔄 Atualizar'
                    background_color: 0.0, 0.47, 0.84, 1
                    color: 1, 1, 1, 1
                    font_size: '16sp'
                    on_press: root.refresh_themes()
                
                Button:
                    text: '💾 Salvar'
                    background_color: 0.0, 0.69, 0.31, 1
                    color: 1, 1, 1, 1
                    font_size: '16sp'
                    on_press: root.save_theme_preference()
        
        # Lista de temas
        ScrollView:
            id: themes_scroll
            
            GridLayout:
                id: themes_container
                cols: 3
                size_hint_y: None
                height: self.minimum_height
                padding: dp(15)
                spacing: dp(15)
"""
)

class ThemePreviewCard(BoxLayout):
    theme_id = StringProperty('')
    theme_name = StringProperty('')
    is_selected = ObjectProperty(False)
    screen = ObjectProperty(None)
    
    # Cores do tema
    primary_color = ListProperty([0.0, 0.47, 0.84, 1])
    secondary_color = ListProperty([0.96, 0.97, 0.98, 1])
    accent_color = ListProperty([0.0, 0.73, 0.83, 1])
    background_color = ListProperty([1.0, 1.0, 1.0, 1])
    text_color = ListProperty([0.13, 0.13, 0.13, 1])
    success_color = ListProperty([0.0, 0.69, 0.31, 1])
    border_color = ListProperty([0.9, 0.9, 0.9, 1])
    
    # Propriedades visuais
    border_radius = 12
    font_size = 16
    icon_style = 'medical'

class ImprovedThemeSettingsScreen(Screen):
    available_themes = ListProperty([])
    current_theme_name = StringProperty('Médico Moderno')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load_themes, 0.5)

    def load_themes(self, dt):
        """Carrega todos os temas disponíveis"""
        try:
            # Recarrega os temas do gerenciador
            theme_manager.load_themes()
            
            # Obtém a lista de temas
            themes_list = []
            for theme_id, theme_data in theme_manager.available_themes.items():
                themes_list.append({
                    'id': theme_id,
                    'name': theme_data.get('name', theme_id.title()),
                    'data': theme_data
                })
            
            self.available_themes = themes_list
            self.current_theme_name = theme_manager.get_current_theme().get('name', 'Tema Atual')
            self.update_themes_display()
            
        except Exception as e:
            print(f"Erro ao carregar temas: {e}")

    @mainthread
    def update_themes_display(self):
        """Atualiza a exibição dos temas"""
        container = self.ids.themes_container
        container.clear_widgets()
        
        if not self.available_themes:
            no_data_label = Label(
                text="Nenhum tema encontrado",
                font_size='18sp',
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=dp(100)
            )
            container.add_widget(no_data_label)
            return
        
        for theme_info in self.available_themes:
            theme_data = theme_info['data']
            is_current = theme_info['id'] == theme_manager.current_theme
            
            card = ThemePreviewCard(
                theme_id=theme_info['id'],
                theme_name=theme_info['name'],
                is_selected=is_current,
                screen=self,
                primary_color=theme_data.get('primary_color', [0.0, 0.47, 0.84, 1]),
                secondary_color=theme_data.get('secondary_color', [0.96, 0.97, 0.98, 1]),
                accent_color=theme_data.get('accent_color', [0.0, 0.73, 0.83, 1]),
                background_color=theme_data.get('background_color', [1.0, 1.0, 1.0, 1]),
                text_color=theme_data.get('text_color', [0.13, 0.13, 0.13, 1]),
                success_color=theme_data.get('success_color', [0.0, 0.69, 0.31, 1]),
                border_radius=theme_data.get('border_radius', 12),
                font_size=theme_data.get('font_size', 16),
                icon_style=theme_data.get('icon_style', 'medical')
            )
            
            # Define cor da borda baseada na seleção
            if is_current:
                card.border_color = theme_data.get('success_color', [0.0, 0.69, 0.31, 1])
            else:
                card.border_color = [0.9, 0.9, 0.9, 1]
            
            container.add_widget(card)

    def select_theme(self, theme_id):
        """Seleciona um tema"""
        try:
            success = theme_manager.set_theme(theme_id)
            if success:
                self.current_theme_name = theme_manager.get_current_theme().get('name', 'Tema Selecionado')
                self.update_themes_display()
                print(f"Tema '{theme_id}' selecionado com sucesso!")
            else:
                print(f"Erro ao selecionar tema '{theme_id}'")
        except Exception as e:
            print(f"Erro ao selecionar tema: {e}")

    def refresh_themes(self):
        """Atualiza a lista de temas"""
        self.load_themes(None)

    def save_theme_preference(self):
        """Salva a preferência de tema do usuário"""
        try:
            theme_manager.save_theme_preference(theme_manager.current_theme)
            print("Preferência de tema salva com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar preferência de tema: {e}")

    def create_custom_theme(self):
        """Abre o criador de temas customizados"""
        print("Funcionalidade de criação de tema customizado em desenvolvimento...")
        # Implementar popup para criação de tema customizado

    def apply_theme_to_app(self):
        """Aplica o tema atual a toda a aplicação"""
        try:
            # Força a aplicação do tema atual
            theme_manager.apply_current_theme_to_api()
            
            # Atualiza as cores globais
            current_theme = theme_manager.get_current_theme()
            
            # Aplica as cores aos elementos da interface atual
            self.apply_theme_to_screen(current_theme)
            
        except Exception as e:
            print(f"Erro ao aplicar tema: {e}")

    def apply_theme_to_screen(self, theme_data):
        """Aplica o tema à tela atual"""
        try:
            # Atualiza as cores dos elementos da tela
            # Isso pode ser expandido para aplicar o tema a todos os widgets
            pass
        except Exception as e:
            print(f"Erro ao aplicar tema à tela: {e}")

    def on_enter(self):
        """Chamado quando a tela é exibida"""
        super().on_enter()
        self.load_themes(None)

    def on_leave(self):
        """Chamado quando a tela é deixada"""
        super().on_leave()
        # Salva automaticamente a preferência ao sair da tela
        self.save_theme_preference()

