import json
import os
from typing import Dict, List, Any
from pathlib import Path
import api # Import the api module

class ThemeManager:
    def __init__(self):
        self.themes_dir = Path("themes")
        self.themes_dir.mkdir(exist_ok=True)
        self.current_theme = "modern_medical"
        self.custom_colors = {}
        self.load_themes()
        self.apply_current_theme_to_api() # Apply theme on initialization
    
    def load_themes(self):
        """Carrega todos os temas disponíveis"""
        self.available_themes = {
            "default": {
                "name": "Padrão",
                "primary_color": [0.2, 0.6, 0.8, 1],
                "secondary_color": [0.9, 0.9, 0.9, 1],
                "accent_color": [0.1, 0.7, 0.5, 1],
                "background_color": [0.95, 0.95, 0.95, 1],
                "text_color": [0.1, 0.1, 0.1, 1],
                "success_color": [0.2, 0.8, 0.2, 1],
                "warning_color": [1.0, 0.6, 0.0, 1],
                "error_color": [0.8, 0.2, 0.2, 1],
                "border_radius": 8,
                "font_size": 14,
                "icon_style": "material"
            },
            "dark": {
                "name": "Escuro",
                "primary_color": [0.1, 0.1, 0.2, 1],
                "secondary_color": [0.2, 0.2, 0.3, 1],
                "accent_color": [0.0, 0.7, 0.8, 1],
                "background_color": [0.05, 0.05, 0.1, 1],
                "text_color": [0.9, 0.9, 0.9, 1],
                "success_color": [0.2, 0.8, 0.2, 1],
                "warning_color": [1.0, 0.6, 0.0, 1],
                "error_color": [0.8, 0.2, 0.2, 1],
                "border_radius": 8,
                "font_size": 14,
                "icon_style": "material"
            },
            "medical": {
                "name": "Médico",
                "primary_color": [0.0, 0.4, 0.6, 1],
                "secondary_color": [0.9, 0.95, 1.0, 1],
                "accent_color": [0.0, 0.6, 0.4, 1],
                "background_color": [0.98, 0.98, 1.0, 1],
                "text_color": [0.1, 0.1, 0.2, 1],
                "success_color": [0.0, 0.6, 0.3, 1],
                "warning_color": [1.0, 0.5, 0.0, 1],
                "error_color": [0.8, 0.1, 0.1, 1],
                "border_radius": 6,
                "font_size": 14,
                "icon_style": "medical"
            },
            "modern": {
                "name": "Moderno",
                "primary_color": [0.6, 0.2, 0.8, 1],
                "secondary_color": [0.95, 0.95, 0.95, 1],
                "accent_color": [1.0, 0.4, 0.6, 1],
                "background_color": [1.0, 1.0, 1.0, 1],
                "text_color": [0.1, 0.1, 0.1, 1],
                "success_color": [0.2, 0.8, 0.4, 1],
                "warning_color": [1.0, 0.7, 0.0, 1],
                "error_color": [0.9, 0.2, 0.3, 1],
                "border_radius": 12,
                "font_size": 16,
                "icon_style": "modern"
            },
            "modern_medical": {
                "name": "Médico Moderno",
                "primary_color": [0.0, 0.47, 0.84, 1],
                "secondary_color": [0.96, 0.97, 0.98, 1],
                "accent_color": [0.0, 0.73, 0.83, 1],
                "background_color": [1.0, 1.0, 1.0, 1],
                "text_color": [0.13, 0.13, 0.13, 1],
                "success_color": [0.0, 0.69, 0.31, 1],
                "warning_color": [1.0, 0.76, 0.03, 1],
                "error_color": [0.96, 0.26, 0.21, 1],
                "border_radius": 12,
                "font_size": 16,
                "icon_style": "medical"
            },
            "dark_medical": {
                "name": "Médico Escuro",
                "primary_color": [0.0, 0.47, 0.84, 1],
                "secondary_color": [0.18, 0.20, 0.25, 1],
                "accent_color": [0.0, 0.73, 0.83, 1],
                "background_color": [0.11, 0.11, 0.13, 1],
                "text_color": [0.95, 0.95, 0.95, 1],
                "success_color": [0.0, 0.69, 0.31, 1],
                "warning_color": [1.0, 0.76, 0.03, 1],
                "error_color": [0.96, 0.26, 0.21, 1],
                "border_radius": 12,
                "font_size": 16,
                "icon_style": "medical"
            },
            "soft_green": {
                "name": "Verde Suave",
                "primary_color": [0.0, 0.59, 0.53, 1],
                "secondary_color": [0.94, 0.97, 0.96, 1],
                "accent_color": [0.0, 0.77, 0.64, 1],
                "background_color": [0.99, 1.0, 0.99, 1],
                "text_color": [0.13, 0.13, 0.13, 1],
                "success_color": [0.0, 0.69, 0.31, 1],
                "warning_color": [1.0, 0.76, 0.03, 1],
                "error_color": [0.96, 0.26, 0.21, 1],
                "border_radius": 10,
                "font_size": 16,
                "icon_style": "medical"
            }
        }
        
        # Carrega temas customizados se existirem
        self.load_custom_themes()
    
    def load_custom_themes(self):
        """Carrega temas customizados salvos"""
        custom_file = self.themes_dir / "custom_themes.json"
        modern_file = self.themes_dir / "modern_medical_theme.json"
        
        # Carrega temas customizados antigos
        if custom_file.exists():
            try:
                with open(custom_file, 'r', encoding='utf-8') as f:
                    custom_themes = json.load(f)
                    self.available_themes.update(custom_themes)
            except Exception as e:
                print(f"Erro ao carregar temas customizados: {e}")
        
        # Carrega novos temas médicos modernos
        if modern_file.exists():
            try:
                with open(modern_file, 'r', encoding='utf-8') as f:
                    modern_themes = json.load(f)
                    self.available_themes.update(modern_themes)
            except Exception as e:
                print(f"Erro ao carregar temas médicos modernos: {e}")
    
    def save_custom_themes(self):
        """Salva temas customizados"""
        custom_file = self.themes_dir / "custom_themes.json"
        custom_themes = {k: v for k, v in self.available_themes.items() 
                        if k not in ["default", "dark", "medical", "modern", "modern_medical", "dark_medical", "soft_green"]}
        
        try:
            with open(custom_file, 'w', encoding='utf-8') as f:
                json.dump(custom_themes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar temas customizados: {e}")
    
    def get_current_theme(self) -> Dict[str, Any]:
        """Retorna o tema atual"""
        return self.available_themes.get(self.current_theme, self.available_themes["modern_medical"])
    
    def set_theme(self, theme_name: str):
        """Define o tema atual e aplica suas propriedades"""
        if theme_name in self.available_themes:
            self.current_theme = theme_name
            self.apply_current_theme_to_api()
            return True
        return False
    
    def apply_current_theme_to_api(self):
        """Aplica as propriedades do tema atual às variáveis globais em api.py"""
        current_theme_data = self.get_current_theme()
        api.global_primary_color = current_theme_data.get('primary_color', api.global_primary_color)
        api.global_secondary_color = current_theme_data.get('secondary_color', api.global_secondary_color)
        api.global_accent_color = current_theme_data.get('accent_color', api.global_accent_color)
        api.global_background_color = current_theme_data.get('background_color', api.global_background_color)
        api.global_text_color = current_theme_data.get('text_color', api.global_text_color)
        api.global_success_color = current_theme_data.get('success_color', api.global_success_color)
        api.global_warning_color = current_theme_data.get('warning_color', api.global_warning_color)
        api.global_error_color = current_theme_data.get('error_color', api.global_error_color)
        api.global_border_radius = current_theme_data.get('border_radius', api.global_border_radius)
        api.global_font_size = current_theme_data.get('font_size', api.global_font_size)
        api.global_icon_style = current_theme_data.get('icon_style', api.global_icon_style)
        print(f"[DEBUG] Tema aplicado: {self.current_theme}. Cor primária: {api.global_primary_color}, Tamanho da fonte: {api.global_font_size}")

    def create_custom_theme(self, name: str, colors: Dict[str, List[float]], 
                           border_radius: int = 8, font_size: int = 14, 
                           icon_style: str = "material"):
        """Cria um tema customizado"""
        theme_id = f"custom_{name.lower().replace(' ', '_')}"
        
        self.available_themes[theme_id] = {
            "name": name,
            "primary_color": colors.get("primary", [0.2, 0.6, 0.8, 1]),
            "secondary_color": colors.get("secondary", [0.9, 0.9, 0.9, 1]),
            "accent_color": colors.get("accent", [0.1, 0.7, 0.5, 1]),
            "background_color": colors.get("background", [0.95, 0.95, 0.95, 1]),
            "text_color": colors.get("text", [0.1, 0.1, 0.1, 1]),
            "success_color": colors.get("success", [0.2, 0.8, 0.2, 1]),
            "warning_color": [1.0, 0.6, 0.0, 1],
            "error_color": [0.8, 0.2, 0.2, 1],
            "border_radius": border_radius,
            "font_size": font_size,
            "icon_style": icon_style
        }
        
        self.save_custom_themes()
        return theme_id
    
    def get_icon_set(self, icon_style: str = None) -> Dict[str, str]:
        """Retorna o conjunto de ícones baseado no estilo"""
        if icon_style is None:
            icon_style = self.get_current_theme().get("icon_style", "material")
        
        icon_sets = {
            "material": {
                "user": "👤",
                "clinic": "🏥",
                "patient": "👨‍⚕️",
                "calendar": "📅",
                "document": "📄",
                "payment": "💰",
                "inventory": "📦",
                "settings": "⚙️",
                "reports": "📊",
                "treatment": "💊",
                "add": "➕",
                "edit": "✏️",
                "delete": "🗑️",
                "save": "💾",
                "search": "🔍",
                "filter": "🔧",
                "export": "📤",
                "import": "📥",
                "print": "🖨️",
                "email": "📧",
                "phone": "📞",
                "location": "📍",
                "time": "⏰",
                "check": "✅",
                "close": "❌",
                "warning": "⚠️",
                "info": "ℹ️",
                "help": "❓"
            },
            "medical": {
                "user": "👨‍⚕️",
                "clinic": "🏥",
                "patient": "🩺",
                "calendar": "📋",
                "document": "📋",
                "payment": "💳",
                "inventory": "💊",
                "settings": "🔬",
                "reports": "📈",
                "treatment": "🩹",
                "add": "➕",
                "edit": "✏️",
                "delete": "🗑️",
                "save": "💾",
                "search": "🔍",
                "filter": "🔧",
                "export": "📤",
                "import": "📥",
                "print": "🖨️",
                "email": "📧",
                "phone": "📞",
                "location": "📍",
                "time": "⏰",
                "check": "✅",
                "close": "❌",
                "warning": "⚠️",
                "info": "ℹ️",
                "help": "❓"
            },
            "modern": {
                "user": "👤",
                "clinic": "🏢",
                "patient": "👥",
                "calendar": "📅",
                "document": "📄",
                "payment": "💵",
                "inventory": "📦",
                "settings": "⚙️",
                "reports": "📊",
                "treatment": "🎯",
                "add": "➕",
                "edit": "✏️",
                "delete": "🗑️",
                "save": "💾",
                "search": "🔍",
                "filter": "🔧",
                "export": "📤",
                "import": "📥",
                "print": "🖨️",
                "email": "📧",
                "phone": "📞",
                "location": "📍",
                "time": "⏰",
                "check": "✅",
                "close": "❌",
                "warning": "⚠️",
                "info": "ℹ️",
                "help": "❓"
            }
        }
        
        return icon_sets.get(icon_style, icon_sets["material"])
    
    def get_theme_list(self) -> List[Dict[str, str]]:
        """Retorna lista de temas disponíveis"""
        return [
            {"id": theme_id, "name": theme_data["name"]}
            for theme_id, theme_data in self.available_themes.items()
        ]

# Instância global do gerenciador de temas
theme_manager = ThemeManager()