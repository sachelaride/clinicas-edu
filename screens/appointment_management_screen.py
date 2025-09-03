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
from kivy.uix.checkbox import CheckBox
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

<AppointmentCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(120)
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
            text: root.appointment_data.get('paciente_nome', 'N/A')
            font_size: '16sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.4
            halign: 'left'
            text_size: self.size
        
        Label:
            text: root.appointment_data.get('inicio', 'N/A')[:16]
            font_size: '14sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.3
            halign: 'center'
            text_size: self.size
        
        Label:
            text: root.appointment_data.get('status', 'N/A')
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
            text: f"Acadêmico: {root.appointment_data.get('academico_nome', 'N/A')}"
            font_size: '12sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
        
        Label:
            text: f"Serviço: {root.appointment_data.get('servico_nome', 'N/A')}"
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
            size_hint_x: 0.33
            background_color: 0.1, 0.7, 0.5, 1
            on_press: root.edit_appointment()
        
        Button:
            text: '✅ Iniciar'
            size_hint_x: 0.33
            background_color: 0.2, 0.8, 0.2, 1
            on_press: root.start_appointment()
        
        Button:
            text: '🗑️ Cancelar'
            size_hint_x: 0.33
            background_color: 0.8, 0.2, 0.2, 1
            on_press: root.cancel_appointment()

<AppointmentForm>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(400)
    padding: dp(20)
    spacing: dp(10)
    
    Label:
        text: '📅 Novo Agendamento'
        font_size: '20sp'
        color: 0.1, 0.1, 0.1, 1
        size_hint_y: None
        height: dp(30)
    
    GridLayout:
        cols: 2
        spacing: dp(10)
        size_hint_y: None
        height: dp(300)
        
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
            text: 'Serviço:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        Spinner:
            id: servico_spinner
            text: 'Selecione o serviço'
            values: []
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Data:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        TextInput:
            id: data_input
            hint_text: 'YYYY-MM-DD'
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Hora Início:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        TextInput:
            id: hora_inicio_input
            hint_text: 'HH:MM'
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Hora Fim:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        TextInput:
            id: hora_fim_input
            hint_text: 'HH:MM'
            size_hint_y: None
            height: dp(30)
        
        Label:
            text: 'Observações:'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(30)
        
        TextInput:
            id: observacoes_input
            hint_text: 'Observações do agendamento'
            size_hint_y: None
            height: dp(30)
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(40)
        spacing: dp(10)
        
        Button:
            text: '💾 Salvar'
            background_color: 0.2, 0.8, 0.2, 1
            on_press: root.save_appointment()
        
        Button:
            text: '❌ Cancelar'
            background_color: 0.8, 0.2, 0.2, 1
            on_press: root.cancel_form()

<AppointmentManagementScreen>:
    date_label: date_label
    appointments_list: appointments_list
    
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
                text: '📅 Gestão de Agendamentos'
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
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            
            # Left Panel - Calendar and Controls
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.3
                spacing: dp(10)
                
                # Date Navigation
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(40)
                    spacing: dp(5)
                    
                    Button:
                        text: '⏰ Hoje'
                        background_color: 0.1, 0.7, 0.5, 1
                        on_press: root.go_to_today()
                    
                    Button:
                        text: '⏰ Anterior'
                        background_color: 0.9, 0.9, 0.9, 1
                        on_press: root.previous_day()
                    
                    Button:
                        text: '⏰ Próximo'
                        background_color: 0.9, 0.9, 0.9, 1
                        on_press: root.next_day()
                
                # Current Date
                Label:
                    id: date_label
                    text: 'Carregando...'
                    font_size: '18sp'
                    color: 0.1, 0.1, 0.1, 1
                    size_hint_y: None
                    height: dp(30)
                
                # Calendar Widget
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: 1
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.9, 0.9, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    
                    Label:
                        text: '📅 Calendário'
                        font_size: '16sp'
                        color: 0.1, 0.1, 0.1, 1
                        size_hint_y: None
                        height: dp(30)
                    
                    Label:
                        text: 'Selecione uma data'
                        font_size: '14sp'
                        color: 0.1, 0.1, 0.1, 1
                        size_hint_y: None
                        height: dp(30)
                    
                    Button:
                        text: 'Selecionar Data'
                        background_color: 0.1, 0.7, 0.5, 1
                        on_press: root.select_date()
                
                # Quick Actions
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(120)
                    spacing: dp(5)
                    
                    Button:
                        text: '➕ Novo Agendamento'
                        background_color: 0.2, 0.8, 0.2, 1
                        on_press: root.show_new_appointment_form()
                    
                    Button:
                        text: '🔍 Buscar'
                        background_color: 0.1, 0.7, 0.5, 1
                        on_press: root.show_search_form()
                    
                    Button:
                        text: '📤 Relatório'
                        background_color: 0.1, 0.7, 0.5, 1
                        on_press: root.generate_report()
            
            # Right Panel - Appointments List
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.7
                spacing: dp(10)
                
                # Filters
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(40)
                    spacing: dp(10)
                    
                    Label:
                        text: 'Filtros:'
                        color: 0.1, 0.1, 0.1, 1
                        size_hint_x: None
                        width: dp(60)
                    
                    Spinner:
                        id: status_filter
                        text: 'Todos os Status'
                        values: ['Todos os Status', 'Agendado', 'Iniciado', 'Aguardando', 'Em Atendimento', 'Concluído', 'Cancelado']
                        size_hint_x: None
                        width: dp(150)
                        on_text: root.filter_appointments()
                    
                    Spinner:
                        id: academico_filter
                        text: 'Todos os Acadêmicos'
                        values: ['Todos os Acadêmicos']
                        size_hint_x: None
                        width: dp(150)
                        on_text: root.filter_appointments()
                    
                    Button:
                        text: '🔧 Aplicar'
                        background_color: 0.1, 0.7, 0.5, 1
                        on_press: root.apply_filters()
                
                # Appointments List
                ScrollView:
                    GridLayout:
                        id: appointments_list
                        cols: 1
                        spacing: dp(10)
                        size_hint_y: None
                        height: self.minimum_height
""")

class AppointmentCard(BoxLayout):
    def __init__(self, appointment_data, **kwargs):
        super().__init__(**kwargs)
        self.appointment_data = appointment_data
    
    def get_status_color(self):
        """Retorna a cor baseada no status do agendamento"""
        status_colors = {
            'agendado': [0.2, 0.6, 0.8, 1],
            'iniciado': [0.1, 0.7, 0.5, 1],
            'aguardando': [1.0, 0.6, 0.0, 1],
            'em_atendimento': [0.2, 0.8, 0.2, 1],
            'concluido': [0.2, 0.8, 0.2, 1],
            'cancelado': [0.8, 0.2, 0.2, 1]
        }
        return status_colors.get(self.appointment_data.get('status', 'agendado'), 
                               [0.1, 0.1, 0.1, 1])
    
    def edit_appointment(self):
        """Edita o agendamento"""
        print(f"Editando agendamento: {self.appointment_data.get('id')}")
    
    def start_appointment(self):
        """Inicia o agendamento"""
        print(f"Iniciando agendamento: {self.appointment_data.get('id')}")
    
    def cancel_appointment(self):
        """Cancela o agendamento"""
        print(f"Cancelando agendamento: {self.appointment_data.get('id')}")

class AppointmentForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = None
    
    def save_appointment(self):
        """Salva o agendamento"""
        # Implementar salvamento
        print("Salvando agendamento...")
        if self.popup:
            self.popup.dismiss()
    
    def cancel_form(self):
        """Cancela o formulário"""
        if self.popup:
            self.popup.dismiss()

class AppointmentManagementScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = datetime.now()
        self.appointments = []
        self.filtered_appointments = []
    
    def on_enter(self, *args):
        """Chamado quando a tela é exibida"""
        self.update_date_display()
        self.load_appointments()
        self.load_filters()
    
    def update_date_display(self):
        """Atualiza a exibição da data"""
        self.date_label.text = self.current_date.strftime('%d/%m/%Y - %A')
    
    def go_to_today(self):
        """Vai para hoje"""
        self.current_date = datetime.now()
        self.update_date_display()
        self.load_appointments()
    
    def previous_day(self):
        """Vai para o dia anterior"""
        self.current_date -= timedelta(days=1)
        self.update_date_display()
        self.load_appointments()
    
    def next_day(self):
        """Vai para o próximo dia"""
        self.current_date += timedelta(days=1)
        self.update_date_display()
        self.load_appointments()
    
    def select_date(self):
        """Seleciona uma data"""
        # Implementar seleção de data
        print("Selecionando data...")
    
    def load_appointments(self):
        """Carrega os agendamentos do dia"""
        # Implementar carregamento via API
        self.appointments = [
            {
                'id': '1',
                'paciente_nome': 'João Silva',
                'academico_nome': 'Dr. Maria Santos',
                'servico_nome': 'Consulta',
                'inicio': '2024-01-15 09:00:00',
                'status': 'agendado'
            },
            {
                'id': '2',
                'paciente_nome': 'Ana Costa',
                'academico_nome': 'Dr. Pedro Lima',
                'servico_nome': 'Exame',
                'inicio': '2024-01-15 10:30:00',
                'status': 'iniciado'
            }
        ]
        self.filtered_appointments = self.appointments.copy()
        self.update_appointments_display()
    
    def update_appointments_display(self):
        """Atualiza a exibição dos agendamentos"""
        self.appointments_list.clear_widgets()
        
        if not self.filtered_appointments:
            no_appointments = Label(
                text='Nenhum agendamento encontrado para esta data.',
                color=[0.1, 0.1, 0.1, 1],
                size_hint_y=None,
                height=dp(50)
            )
            self.appointments_list.add_widget(no_appointments)
            return
        
        for appointment in self.filtered_appointments:
            card = AppointmentCard(appointment)
            self.appointments_list.add_widget(card)
    
    def load_filters(self):
        """Carrega os filtros disponíveis"""
        # Implementar carregamento de filtros via API
        pass
    
    def filter_appointments(self):
        """Filtra os agendamentos"""
        status_filter = self.ids.status_filter.text
        academico_filter = self.ids.academico_filter.text
        
        self.filtered_appointments = self.appointments.copy()
        
        if status_filter != 'Todos os Status':
            self.filtered_appointments = [
                apt for apt in self.filtered_appointments
                if apt.get('status') == status_filter.lower()
            ]
        
        if academico_filter != 'Todos os Acadêmicos':
            self.filtered_appointments = [
                apt for apt in self.filtered_appointments
                if apt.get('academico_nome') == academico_filter
            ]
        
        self.update_appointments_display()
    
    def apply_filters(self):
        """Aplica os filtros"""
        self.filter_appointments()
    
    def show_new_appointment_form(self):
        """Mostra o formulário de novo agendamento"""
        form = AppointmentForm()
        
        popup = Popup(
            title='➕ Novo Agendamento',
            content=form,
            size_hint=(0.8, 0.9)
        )
        
        form.popup = popup
        popup.open()
    
    def show_search_form(self):
        """Mostra o formulário de busca"""
        # Implementar busca avançada
        print("Mostrando busca avançada...")
    
    def generate_report(self):
        """Gera relatório de agendamentos"""
        # Implementar geração de relatório
        print("Gerando relatório...")
