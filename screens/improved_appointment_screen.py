from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty, StringProperty, BooleanProperty
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
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
import asyncio
import httpx
from datetime import datetime, timedelta, date
import json
import calendar

# Import the api module
import api

Builder.load_string("""
<CalendarDay>:
    size_hint: None, None
    size: dp(40), dp(40)
    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6]
        Color:
            rgba: root.border_color
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, 6
            width: 1
    
    Label:
        text: str(root.day_number) if root.day_number > 0 else ""
        color: root.text_color
        font_size: '14sp'
        bold: root.is_today

<AppointmentCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(140)
    padding: dp(12)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: root.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
        Color:
            rgba: root.border_color
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, 12
            width: 1
    
    # Header com paciente e horário
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(35)
        
        Label:
            text: root.appointment_data.get('paciente_nome', 'Paciente não informado')
            font_size: '18sp'
            bold: True
            color: root.text_color
            size_hint_x: 0.6
            halign: 'left'
            text_size: self.size
        
        Label:
            text: root.format_time(root.appointment_data.get('inicio', ''))
            font_size: '16sp'
            color: root.accent_color
            size_hint_x: 0.4
            halign: 'right'
            text_size: self.size
    
    # Informações do agendamento
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(25)
        
        Label:
            text: f"👨‍🎓 {root.appointment_data.get('academico_nome', 'N/A')}"
            font_size: '14sp'
            color: root.text_color
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
        
        Label:
            text: f"🩺 {root.appointment_data.get('servico_nome', 'N/A')}"
            font_size: '14sp'
            color: root.text_color
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
    
    # Status e orientador
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(25)
        
        Label:
            text: f"📋 Status: {root.get_status_display()}"
            font_size: '14sp'
            color: root.get_status_color()
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
        
        Label:
            text: f"👨‍⚕️ {root.appointment_data.get('orientador_nome', 'Sem orientador')}"
            font_size: '14sp'
            color: root.text_color
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
    
    # Botões de ação
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(35)
        spacing: dp(8)
        
        Button:
            text: '✏️ Editar'
            size_hint_x: 0.25
            background_color: root.primary_color
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.edit_appointment(root.appointment_data)
        
        Button:
            text: '📋 Prontuário'
            size_hint_x: 0.25
            background_color: root.accent_color
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.open_prontuario(root.appointment_data)
        
        Button:
            text: '🏁 Finalizar'
            size_hint_x: 0.25
            background_color: root.success_color
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.finish_appointment(root.appointment_data)
        
        Button:
            text: '❌ Cancelar'
            size_hint_x: 0.25
            background_color: root.error_color
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.cancel_appointment(root.appointment_data)

<AppointmentEditPopup>:
    title: "Editar Agendamento"
    size_hint: 0.8, 0.9
    auto_dismiss: False
    
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)
        
        # Seleção de paciente
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            
            Label:
                text: "Paciente:"
                size_hint_x: 0.3
                font_size: '16sp'
            
            Spinner:
                id: patient_spinner
                size_hint_x: 0.7
                text: root.appointment_data.get('paciente_nome', 'Selecione um paciente')
                values: root.screen.patient_names
                font_size: '16sp'
        
        # Data e hora
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            spacing: dp(10)
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.5
                
                Label:
                    text: "Data:"
                    size_hint_x: 0.4
                    font_size: '16sp'
                
                TextInput:
                    id: date_input
                    size_hint_x: 0.6
                    hint_text: "DD/MM/AAAA"
                    font_size: '16sp'
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.5
                
                Label:
                    text: "Hora:"
                    size_hint_x: 0.4
                    font_size: '16sp'
                
                TextInput:
                    id: time_input
                    size_hint_x: 0.6
                    hint_text: "HH:MM"
                    font_size: '16sp'
        
        # Acadêmico e orientador
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            spacing: dp(10)
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.5
                
                Label:
                    text: "Acadêmico:"
                    size_hint_x: 0.4
                    font_size: '16sp'
                
                Spinner:
                    id: academic_spinner
                    size_hint_x: 0.6
                    text: root.appointment_data.get('academico_nome', 'Selecione')
                    values: root.screen.academic_names
                    font_size: '16sp'
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_x: 0.5
                
                Label:
                    text: "Orientador:"
                    size_hint_x: 0.4
                    font_size: '16sp'
                
                Spinner:
                    id: supervisor_spinner
                    size_hint_x: 0.6
                    text: root.appointment_data.get('orientador_nome', 'Selecione')
                    values: root.screen.supervisor_names
                    font_size: '16sp'
        
        # Serviço
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            
            Label:
                text: "Serviço:"
                size_hint_x: 0.3
                font_size: '16sp'
            
            Spinner:
                id: service_spinner
                size_hint_x: 0.7
                text: root.appointment_data.get('servico_nome', 'Selecione um serviço')
                values: root.screen.service_names
                font_size: '16sp'
        
        # Observações
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(80)
            
            Label:
                text: "Observações:"
                size_hint_x: 0.3
                font_size: '16sp'
                valign: 'top'
            
            TextInput:
                id: observations_input
                size_hint_x: 0.7
                multiline: True
                text: root.appointment_data.get('observacoes', '')
                font_size: '16sp'
        
        # Botões
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            Button:
                text: 'Salvar'
                background_color: 0.0, 0.69, 0.31, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.save_appointment()
            
            Button:
                text: 'Cancelar'
                background_color: 0.5, 0.5, 0.5, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.dismiss()

<ImprovedAppointmentScreen>:
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
                text: 'Gerenciamento de Agendamentos'
                font_size: '24sp'
                color: 1, 1, 1, 1
                bold: True
            
            Button:
                text: '+ Novo'
                size_hint_x: None
                width: dp(100)
                background_color: 0.0, 0.73, 0.83, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.add_new_appointment()
        
        # Filtros e visualização
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: dp(15)
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: 0.96, 0.97, 0.98, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Spinner:
                id: view_mode_spinner
                text: 'Visualização: Lista'
                values: ['Visualização: Lista', 'Visualização: Calendário', 'Visualização: Agenda']
                size_hint_x: 0.3
                font_size: '16sp'
                on_text: root.change_view_mode(self.text)
            
            Spinner:
                id: filter_status_spinner
                text: 'Todos os Status'
                values: ['Todos os Status', 'Agendado', 'Em Atendimento', 'Concluído', 'Cancelado']
                size_hint_x: 0.3
                font_size: '16sp'
                on_text: root.filter_by_status(self.text)
            
            Spinner:
                id: filter_date_spinner
                text: 'Hoje'
                values: ['Hoje', 'Esta Semana', 'Este Mês', 'Todos']
                size_hint_x: 0.3
                font_size: '16sp'
                on_text: root.filter_by_date(self.text)
            
            Button:
                text: '🔄 Atualizar'
                size_hint_x: 0.1
                background_color: 0.0, 0.47, 0.84, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.refresh_appointments()
        
        # Conteúdo principal
        BoxLayout:
            id: main_content
            orientation: 'vertical'
            
            # Lista de agendamentos
            ScrollView:
                id: appointments_scroll
                
                BoxLayout:
                    id: appointments_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(15)
                    spacing: dp(10)
"""
)

class CalendarDay(Button):
    day_number = ObjectProperty(0)
    is_today = BooleanProperty(False)
    has_appointments = BooleanProperty(False)
    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0.13, 0.13, 0.13, 1])
    border_color = ListProperty([0.9, 0.9, 0.9, 1])

class AppointmentCard(BoxLayout):
    appointment_data = ObjectProperty({})
    screen = ObjectProperty(None)
    
    # Cores do tema
    primary_color = ListProperty([0.0, 0.47, 0.84, 1])
    accent_color = ListProperty([0.0, 0.73, 0.83, 1])
    success_color = ListProperty([0.0, 0.69, 0.31, 1])
    error_color = ListProperty([0.96, 0.26, 0.21, 1])
    text_color = ListProperty([0.13, 0.13, 0.13, 1])
    card_color = ListProperty([1, 1, 1, 1])
    border_color = ListProperty([0.9, 0.9, 0.9, 1])

    def format_time(self, datetime_str):
        if not datetime_str:
            return "Horário não definido"
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime('%H:%M')
        except:
            return datetime_str[:5] if len(datetime_str) >= 5 else datetime_str

    def get_status_display(self):
        status = self.appointment_data.get('status', 'agendado')
        status_map = {
            'agendado': 'Agendado',
            'iniciado': 'Iniciado',
            'aguardando': 'Aguardando',
            'em_atendimento': 'Em Atendimento',
            'concluido': 'Concluído',
            'cancelado': 'Cancelado'
        }
        return status_map.get(status, status.title())

    def get_status_color(self):
        status = self.appointment_data.get('status', 'agendado')
        if status in ['concluido']:
            return self.success_color
        elif status in ['cancelado']:
            return self.error_color
        elif status in ['em_atendimento', 'iniciado']:
            return self.accent_color
        else:
            return self.text_color

class AppointmentEditPopup(Popup):
    appointment_data = ObjectProperty({})
    screen = ObjectProperty(None)

    def save_appointment(self):
        # Implementar lógica de salvamento
        self.screen.save_appointment_data(self.appointment_data)
        self.dismiss()

class ImprovedAppointmentScreen(Screen):
    appointments_data = ListProperty([])
    patient_names = ListProperty([])
    academic_names = ListProperty([])
    supervisor_names = ListProperty([])
    service_names = ListProperty([])
    
    current_view_mode = StringProperty('lista')
    current_status_filter = StringProperty('todos')
    current_date_filter = StringProperty('hoje')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load_initial_data, 0.5)

    def load_initial_data(self, dt):
        """Carrega os dados iniciais necessários"""
        asyncio.create_task(self.fetch_appointments())
        asyncio.create_task(self.fetch_patients())
        asyncio.create_task(self.fetch_users())
        asyncio.create_task(self.fetch_services())

    async def fetch_appointments(self):
        """Busca os agendamentos da API"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                response = await client.get(f"{api.BASE_URL}/agendamentos/", headers=headers)
                if response.status_code == 200:
                    self.appointments_data = response.json()
                    self.update_appointments_display()
        except Exception as e:
            print(f"Erro ao buscar agendamentos: {e}")

    async def fetch_patients(self):
        """Busca a lista de pacientes"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                response = await client.get(f"{api.BASE_URL}/pacientes/", headers=headers)
                if response.status_code == 200:
                    patients = response.json()
                    self.patient_names = [p.get('nome', 'N/A') for p in patients]
        except Exception as e:
            print(f"Erro ao buscar pacientes: {e}")

    async def fetch_users(self):
        """Busca a lista de usuários (acadêmicos e orientadores)"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                response = await client.get(f"{api.BASE_URL}/users/", headers=headers)
                if response.status_code == 200:
                    users = response.json()
                    self.academic_names = [u.get('nome', 'N/A') for u in users if u.get('role') == 'academico']
                    self.supervisor_names = [u.get('nome', 'N/A') for u in users if u.get('role') == 'orientador']
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")

    async def fetch_services(self):
        """Busca a lista de serviços"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                response = await client.get(f"{api.BASE_URL}/servicos/", headers=headers)
                if response.status_code == 200:
                    services = response.json()
                    self.service_names = [s.get('nome', 'N/A') for s in services]
        except Exception as e:
            print(f"Erro ao buscar serviços: {e}")

    @mainthread
    def update_appointments_display(self):
        """Atualiza a exibição dos agendamentos"""
        container = self.ids.appointments_container
        container.clear_widgets()
        
        filtered_appointments = self.filter_appointments()
        
        if not filtered_appointments:
            no_data_label = Label(
                text="Nenhum agendamento encontrado",
                font_size='18sp',
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=dp(100)
            )
            container.add_widget(no_data_label)
            return
        
        for appointment in filtered_appointments:
            card = AppointmentCard(appointment_data=appointment, screen=self)
            container.add_widget(card)

    def filter_appointments(self):
        """Filtra os agendamentos baseado nos filtros selecionados"""
        filtered = self.appointments_data.copy()
        
        # Filtro por status
        if self.current_status_filter != 'todos':
            status_map = {
                'Agendado': 'agendado',
                'Em Atendimento': 'em_atendimento',
                'Concluído': 'concluido',
                'Cancelado': 'cancelado'
            }
            target_status = status_map.get(self.current_status_filter)
            if target_status:
                filtered = [a for a in filtered if a.get('status') == target_status]
        
        # Filtro por data
        if self.current_date_filter != 'todos':
            today = date.today()
            if self.current_date_filter == 'hoje':
                filtered = [a for a in filtered if self.is_same_date(a.get('inicio'), today)]
            elif self.current_date_filter == 'esta_semana':
                week_start = today - timedelta(days=today.weekday())
                week_end = week_start + timedelta(days=6)
                filtered = [a for a in filtered if self.is_date_in_range(a.get('inicio'), week_start, week_end)]
            elif self.current_date_filter == 'este_mes':
                month_start = today.replace(day=1)
                next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                month_end = next_month - timedelta(days=1)
                filtered = [a for a in filtered if self.is_date_in_range(a.get('inicio'), month_start, month_end)]
        
        return filtered

    def is_same_date(self, datetime_str, target_date):
        """Verifica se uma data/hora é do mesmo dia que a data alvo"""
        if not datetime_str:
            return False
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.date() == target_date
        except:
            return False

    def is_date_in_range(self, datetime_str, start_date, end_date):
        """Verifica se uma data/hora está dentro do intervalo especificado"""
        if not datetime_str:
            return False
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return start_date <= dt.date() <= end_date
        except:
            return False

    def change_view_mode(self, mode_text):
        """Muda o modo de visualização"""
        if 'Lista' in mode_text:
            self.current_view_mode = 'lista'
        elif 'Calendário' in mode_text:
            self.current_view_mode = 'calendario'
        elif 'Agenda' in mode_text:
            self.current_view_mode = 'agenda'
        
        self.update_appointments_display()

    def filter_by_status(self, status_text):
        """Filtra por status"""
        if 'Todos' in status_text:
            self.current_status_filter = 'todos'
        else:
            self.current_status_filter = status_text
        
        self.update_appointments_display()

    def filter_by_date(self, date_text):
        """Filtra por data"""
        date_map = {
            'Hoje': 'hoje',
            'Esta Semana': 'esta_semana',
            'Este Mês': 'este_mes',
            'Todos': 'todos'
        }
        self.current_date_filter = date_map.get(date_text, 'todos')
        self.update_appointments_display()

    def refresh_appointments(self):
        """Atualiza a lista de agendamentos"""
        asyncio.create_task(self.fetch_appointments())

    def add_new_appointment(self):
        """Adiciona um novo agendamento"""
        popup = AppointmentEditPopup(appointment_data={}, screen=self)
        popup.open()

    def edit_appointment(self, appointment_data):
        """Edita um agendamento existente"""
        popup = AppointmentEditPopup(appointment_data=appointment_data, screen=self)
        popup.open()

    def open_prontuario(self, appointment_data):
        """Abre o prontuário do paciente"""
        # Implementar navegação para prontuário
        print(f"Abrindo prontuário para: {appointment_data.get('paciente_nome')}")

    def finish_appointment(self, appointment_data):
        """Finaliza um agendamento"""
        asyncio.create_task(self.update_appointment_status(appointment_data.get('id'), 'concluido'))

    def cancel_appointment(self, appointment_data):
        """Cancela um agendamento"""
        asyncio.create_task(self.update_appointment_status(appointment_data.get('id'), 'cancelado'))

    async def update_appointment_status(self, appointment_id, new_status):
        """Atualiza o status de um agendamento"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                data = {"status": new_status}
                response = await client.patch(f"{api.BASE_URL}/agendamentos/{appointment_id}", 
                                            headers=headers, json=data)
                if response.status_code == 200:
                    await self.fetch_appointments()
        except Exception as e:
            print(f"Erro ao atualizar status do agendamento: {e}")

    def save_appointment_data(self, appointment_data):
        """Salva os dados do agendamento"""
        # Implementar lógica de salvamento
        asyncio.create_task(self.fetch_appointments())

