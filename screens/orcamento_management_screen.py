from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty
from kivy.clock import mainthread, Clock
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.metrics import dp
import asyncio
import httpx
from datetime import datetime, timedelta
import json

# Import the api module and theme manager
import api
from app.core.theme_manager import theme_manager

Builder.load_string("""
#:import api api

<OrcamentoCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(140)
    padding: dp(10)
    spacing: dp(5)
    canvas.before:
        Color:
            rgba: 0.9, 0.9, 0.9, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(30)
        
        Label:
            text: f"Orçamento #{root.orcamento_data.get('numero_orcamento', 'N/A')}"
            font_size: '16sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.4
            halign: 'left'
            text_size: self.size
        
        Label:
            text: root.orcamento_data.get('data_orcamento', 'N/A')[:10]
            font_size: '14sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.3
            halign: 'center'
            text_size: self.size
        
        Label:
            text: root.orcamento_data.get('status', 'N/A').title()
            font_size: '14sp'
            color: root.get_status_color()
            size_hint_x: 0.3
            halign: 'center'
            text_size: self.size
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(25)
        
        Label:
            text: f"Paciente: {root.orcamento_data.get('paciente_nome', 'N/A')}"
            font_size: '12sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.6
            halign: 'left'
            text_size: self.size
        
        Label:
            text: f"R$ {root.orcamento_data.get('valor_final', '0.00')}"
            font_size: '14sp'
            color: 0.2, 0.8, 0.2, 1
            size_hint_x: 0.4
            halign: 'right'
            text_size: self.size
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(25)
        
        Label:
            text: f"Acadêmico: {root.orcamento_data.get('academico_nome', 'N/A')}"
            font_size: '12sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
        
        Label:
            text: f"Validade: {root.orcamento_data.get('data_validade', 'N/A')[:10] if root.orcamento_data.get('data_validade') else 'N/A'}"
            font_size: '12sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(30)
        
        Button:
            text: '✏️ Editar'
            size_hint_x: 0.25
            background_color: 0.1, 0.7, 0.5, 1
            on_press: root.edit_orcamento()
        
        Button:
            text: '✅ Aprovar'
            size_hint_x: 0.25
            background_color: 0.2, 0.8, 0.2, 1
            on_press: root.approve_orcamento()
        
        Button:
            text: '❌ Rejeitar'
            size_hint_x: 0.25
            background_color: 1.0, 0.6, 0.0, 1
            on_press: root.reject_orcamento()
        
        Button:
            text: '💰 Converter'
            size_hint_x: 0.25
            background_color: 0.2, 0.6, 0.8, 1
            on_press: root.convert_orcamento()

<OrcamentoForm>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(500)
    padding: dp(20)
    spacing: dp(10)
    
    Label:
        text: '💰 Novo Orçamento'
        font_size: '20sp'
        color: 0.1, 0.1, 0.1, 1
        size_hint_y: None
        height: dp(30)
    
    GridLayout:
        cols: 2
        spacing: dp(10)
        size_hint_y: None
        height: dp(400)
        
        Label:
            text: 'Paciente:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        Spinner:
            id: paciente_spinner
            text: 'Selecione o paciente'
            values: []
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Responsável:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        Spinner:
            id: responsavel_spinner
            text: 'Selecione o responsável'
            values: []
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Acadêmico:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        Spinner:
            id: academico_spinner
            text: 'Selecione o acadêmico'
            values: []
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Data Validade:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        TextInput:
            id: data_validade_input
            hint_text: 'YYYY-MM-DD'
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Desconto (%):'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        TextInput:
            id: desconto_percentual_input
            hint_text: '0.00'
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Forma Pagamento:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        Spinner:
            id: forma_pagamento_spinner
            text: 'Selecione a forma'
            values: ['Dinheiro', 'Cartão de Crédito', 'Cartão de Débito', 'PIX', 'Transferência']
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Observações:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        TextInput:
            id: observacoes_input
            hint_text: 'Observações do orçamento'
            size_hint_y: None
            height: dp(30)
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(40)
        spacing: dp(10)
        
        Button:
            text: '➕ Adicionar Item'
            background_color: 0.1, 0.7, 0.5, 1
            on_press: root.add_item()
        
        Button:
            text: '💾 Salvar'
            background_color: 0.2, 0.8, 0.2, 1
            on_press: root.save_orcamento()
        
        Button:
            text: '❌ Cancelar'
            background_color: 0.8, 0.2, 0.2, 1
            on_press: root.cancel_form()

<OrcamentoManagementScreen>:
    orcamentos_list: orcamentos_list
    
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
                text: '💰 Gestão de Orçamentos'
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
        BoxLayout:
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(10)
            
            # Filters and Actions
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(50)
                spacing: dp(10)
                
                Button:
                    text: '➕ Novo Orçamento'
                    background_color: 0.2, 0.8, 0.2, 1
                    on_press: root.show_new_orcamento_form()
                
                Spinner:
                    id: status_filter
                    text: 'Todos os Status'
                    values: ['Todos os Status', 'Rascunho', 'Enviado', 'Aprovado', 'Rejeitado', 'Convertido', 'Cancelado']
                    size_hint_x: None
                    width: dp(150)
                    on_text: root.filter_orcamentos()
                
                Spinner:
                    id: paciente_filter
                    text: 'Todos os Pacientes'
                    values: ['Todos os Pacientes']
                    size_hint_x: None
                    width: dp(150)
                    on_text: root.filter_orcamentos()
                
                Button:
                    text: '🔍 Buscar'
                    background_color: 0.1, 0.7, 0.5, 1
                    on_press: root.show_search_form()
                
                Button:
                    text: '📤 Relatório'
                    background_color: 0.1, 0.7, 0.5, 1
                    on_press: root.generate_report()
            
            # Orcamentos List
            ScrollView:
                GridLayout:
                    id: orcamentos_list
                    cols: 1
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height
""")

class OrcamentoCard(BoxLayout):
    def __init__(self, orcamento_data, **kwargs):
        super().__init__(**kwargs)
        self.orcamento_data = orcamento_data
    
    def get_status_color(self):
        """Retorna a cor baseada no status do orçamento"""
        status_colors = {
            'rascunho': [0.1, 0.1, 0.1, 1],
            'enviado': [0.2, 0.6, 0.8, 1],
            'aprovado': [0.2, 0.8, 0.2, 1],
            'rejeitado': [0.8, 0.2, 0.2, 1],
            'convertido': [0.1, 0.7, 0.5, 1],
            'cancelado': [1.0, 0.6, 0.0, 1]
        }
        return status_colors.get(self.orcamento_data.get('status', 'rascunho'), 
                               [0.1, 0.1, 0.1, 1])
    
    def edit_orcamento(self):
        """Edita o orçamento"""
        print(f"Editando orçamento: {self.orcamento_data.get('id')}")
    
    def approve_orcamento(self):
        """Aprova o orçamento"""
        print(f"Aprovando orçamento: {self.orcamento_data.get('id')}")
    
    def reject_orcamento(self):
        """Rejeita o orçamento"""
        print(f"Rejeitando orçamento: {self.orcamento_data.get('id')}")
    
    def convert_orcamento(self):
        """Converte o orçamento em tratamento"""
        print(f"Convertendo orçamento: {self.orcamento_data.get('id')}")

class OrcamentoForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None
    
    def add_item(self):
        """Adiciona item ao orçamento"""
        # Implementar adição de item
        print("Adicionando item...")
    
    def save_orcamento(self):
        """Salva o orçamento"""
        # Implementar salvamento
        print("Salvando orçamento...")
        if self.popup:
            self.popup.dismiss()
    
    def cancel_form(self):
        """Cancela o formulário"""
        if self.popup:
            self.popup.dismiss()

class OrcamentoManagementScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orcamentos = []
        self.filtered_orcamentos = []
    
    def on_enter(self, *args):
        """Chamado quando a tela é exibida"""
        self.load_orcamentos()
        self.load_filters()
    
    def load_orcamentos(self):
        """Carrega os orçamentos"""
        # Implementar carregamento via API
        self.orcamentos = [
            {
                'id': '1',
                'numero_orcamento': 'ORC001',
                'paciente_nome': 'João Silva',
                'academico_nome': 'Dr. Maria Santos',
                'data_orcamento': '2024-01-15 09:00:00',
                'data_validade': '2024-02-15 09:00:00',
                'status': 'enviado',
                'valor_final': '1500.00'
            },
            {
                'id': '2',
                'numero_orcamento': 'ORC002',
                'paciente_nome': 'Ana Costa',
                'academico_nome': 'Dr. Pedro Lima',
                'data_orcamento': '2024-01-14 10:30:00',
                'data_validade': '2024-02-14 10:30:00',
                'status': 'aprovado',
                'valor_final': '2300.00'
            }
        ]
        self.filtered_orcamentos = self.orcamentos.copy()
        self.update_orcamentos_display()
    
    def update_orcamentos_display(self):
        """Atualiza a exibição dos orçamentos"""
        self.orcamentos_list.clear_widgets()
        
        if not self.filtered_orcamentos:
            no_orcamentos = Label(
                text='Nenhum orçamento encontrado.',
                color=[0.1, 0.1, 0.1, 1],
                size_hint_y=None,
                height=dp(50)
            )
            self.orcamentos_list.add_widget(no_orcamentos)
            return
        
        for orcamento in self.filtered_orcamentos:
            card = OrcamentoCard(orcamento)
            self.orcamentos_list.add_widget(card)
    
    def load_filters(self):
        """Carrega os filtros disponíveis"""
        # Implementar carregamento de filtros via API
        pass
    
    def filter_orcamentos(self):
        """Filtra os orçamentos"""
        status_filter = self.ids.status_filter.text
        paciente_filter = self.ids.paciente_filter.text
        
        self.filtered_orcamentos = self.orcamentos.copy()
        
        if status_filter != 'Todos os Status':
            self.filtered_orcamentos = [
                orc for orc in self.filtered_orcamentos
                if orc.get('status') == status_filter.lower()
            ]
        
        if paciente_filter != 'Todos os Pacientes':
            self.filtered_orcamentos = [
                orc for orc in self.filtered_orcamentos
                if orc.get('paciente_nome') == paciente_filter
            ]
        
        self.update_orcamentos_display()
    
    def show_new_orcamento_form(self):
        """Mostra o formulário de novo orçamento"""
        form = OrcamentoForm()
        
        popup = Popup(
            title='➕ Novo Orçamento',
            content=form,
            size_hint=(0.9, 0.9)
        )
        
        form.popup = popup
        popup.open()
    
    def show_search_form(self):
        """Mostra o formulário de busca"""
        # Implementar busca avançada
        print("Mostrando busca avançada...")
    
    def generate_report(self):
        """Gera relatório de orçamentos"""
        # Implementar geração de relatório
        print("Gerando relatório...")
