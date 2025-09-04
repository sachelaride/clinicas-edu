from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

import httpx
import asyncio
import datetime
import os

import api

Builder.load_string("""
<PatientCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(180)
    padding: dp(15)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
        Color:
            rgba: 0.9, 0.9, 0.9, 1
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, 12
            width: 1
    
    # Header com nome e idade
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(35)
        
        Label:
            text: root.patient_data.get('nome', 'Nome não informado')
            font_size: '20sp'
            bold: True
            color: 0.13, 0.13, 0.13, 1
            size_hint_x: 0.7
            halign: 'left'
            text_size: self.size
        
        Label:
            text: root.get_age_display()
            font_size: '16sp'
            color: 0.0, 0.47, 0.84, 1
            size_hint_x: 0.3
            halign: 'right'
            text_size: self.size
    
    # Informações básicas
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(25)
        
        Label:
            text: f"📞 {root.patient_data.get('telefone', 'Não informado')}"
            font_size: '14sp'
            color: 0.13, 0.13, 0.13, 1
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
        
        Label:
            text: f"👤 {root.patient_data.get('genero', 'N/A')}"
            font_size: '14sp'
            color: 0.13, 0.13, 0.13, 1
            size_hint_x: 0.5
            halign: 'left'
            text_size: self.size
    
    # Email e código do cliente
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(25)
        
        Label:
            text: f"📧 {root.patient_data.get('email', 'Não informado')}"
            font_size: '14sp'
            color: 0.13, 0.13, 0.13, 1
            size_hint_x: 0.6
            halign: 'left'
            text_size: self.size
        
        Label:
            text: f"🆔 {root.patient_data.get('client_code', 'N/A')}"
            font_size: '14sp'
            color: 0.0, 0.73, 0.83, 1
            size_hint_x: 0.4
            halign: 'right'
            text_size: self.size
    
    # Responsável (se menor)
    Label:
        text: f"👨‍👩‍👧‍👦 Responsável: {root.get_responsavel_display()}"
        font_size: '14sp'
        color: 0.96, 0.76, 0.03, 1 if root.is_minor() else 0.5, 0.5, 0.5, 1
        size_hint_y: None
        height: dp(25)
        halign: 'left'
        text_size: self.size
    
    # Botões de ação
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        
        Button:
            text: '✏️ Editar'
            size_hint_x: 0.2
            background_color: 0.0, 0.47, 0.84, 1
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.edit_patient(root.patient_data)
        
        Button:
            text: '📋 Prontuários'
            size_hint_x: 0.2
            background_color: 0.0, 0.73, 0.83, 1
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.open_prontuarios(root.patient_data)
        
        Button:
            text: '📄 Documentos'
            size_hint_x: 0.2
            background_color: 0.0, 0.59, 0.53, 1
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.open_documents(root.patient_data)
        
        Button:
            text: '💰 Orçamentos'
            size_hint_x: 0.2
            background_color: 0.0, 0.69, 0.31, 1
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.open_orcamentos(root.patient_data)
        
        Button:
            text: '📅 Agendar'
            size_hint_x: 0.2
            background_color: 1.0, 0.76, 0.03, 1
            color: 1, 1, 1, 1
            font_size: '14sp'
            on_press: root.screen.schedule_appointment(root.patient_data)

<PatientEditPopup>:
    title: "Editar Paciente" if self.patient_id else "Adicionar Novo Paciente"
    size_hint: 0.85, 0.95
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)

        ScrollView:
            size_hint_y: 0.85
            
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(15)

                # Nome completo
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(40)
                    
                    Label:
                        text: "Nome Completo:"
                        size_hint_x: 0.3
                        font_size: '16sp'
                    
                    TextInput:
                        id: nome_input
                        size_hint_x: 0.7
                        text: root.patient_data.get('nome', '')
                        font_size: '16sp'
                        multiline: False

                # Data de nascimento e gênero
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(40)
                    spacing: dp(10)
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.5
                        
                        Label:
                            text: "Data Nascimento:"
                            size_hint_x: 0.5
                            font_size: '16sp'
                        
                        TextInput:
                            id: data_nascimento_input
                            size_hint_x: 0.5
                            hint_text: "DD/MM/AAAA"
                            text: root.patient_data.get('data_nascimento', '')
                            font_size: '16sp'
                            multiline: False
                            on_text_validate: root.calculate_age(self.text)
                            on_focus: if not self.focus: root.calculate_age(self.text)
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.5
                        
                        Label:
                            text: "Gênero:"
                            size_hint_x: 0.4
                            font_size: '16sp'
                        
                        Spinner:
                            id: genero_input
                            size_hint_x: 0.6
                            text: root.patient_data.get('genero', 'Selecione')
                            values: ['Masculino', 'Feminino', 'Outro']
                            font_size: '16sp'

                # Telefone e email
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(40)
                    spacing: dp(10)
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.5
                        
                        Label:
                            text: "Telefone:"
                            size_hint_x: 0.4
                            font_size: '16sp'
                        
                        TextInput:
                            id: telefone_input
                            size_hint_x: 0.6
                            text: root.patient_data.get('telefone', '')
                            font_size: '16sp'
                            multiline: False
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.5
                        
                        Label:
                            text: "Email:"
                            size_hint_x: 0.4
                            font_size: '16sp'
                        
                        TextInput:
                            id: email_input
                            size_hint_x: 0.6
                            text: root.patient_data.get('email', '')
                            font_size: '16sp'
                            multiline: False

                # Endereço
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(40)
                    
                    Label:
                        text: "Endereço:"
                        size_hint_x: 0.3
                        font_size: '16sp'
                    
                    TextInput:
                        id: endereco_input
                        size_hint_x: 0.7
                        text: root.patient_data.get('endereco', '')
                        font_size: '16sp'
                        multiline: False

                # Seção do responsável (visível apenas para menores)
                BoxLayout:
                    id: responsavel_section
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(120) if root.is_minor else 0
                    opacity: 1 if root.is_minor else 0
                    spacing: dp(10)
                    canvas.before:
                        Color:
                            rgba: 1.0, 0.96, 0.8, 1 if root.is_minor else 0, 0, 0, 0
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8]
                    padding: dp(10) if root.is_minor else 0
                    
                    Label:
                        text: "👨‍👩‍👧‍👦 Informações do Responsável (Paciente menor de idade)"
                        font_size: '16sp'
                        bold: True
                        color: 1.0, 0.76, 0.03, 1
                        size_hint_y: None
                        height: dp(30)
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(10)
                        
                        Label:
                            text: "Responsável:"
                            size_hint_x: 0.3
                            font_size: '16sp'
                        
                        Spinner:
                            id: responsavel_spinner
                            size_hint_x: 0.5
                            text: root.get_responsavel_name()
                            values: root.screen.responsavel_names
                            font_size: '16sp'
                        
                        Button:
                            text: "+ Novo"
                            size_hint_x: 0.2
                            background_color: 0.0, 0.69, 0.31, 1
                            color: 1, 1, 1, 1
                            font_size: '14sp'
                            on_press: root.add_new_responsavel()

        # Botões de ação
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            Button:
                text: 'Salvar'
                background_color: 0.0, 0.69, 0.31, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.save_patient()
            
            Button:
                text: 'Cancelar'
                background_color: 0.5, 0.5, 0.5, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.dismiss()

<ImprovedPatientScreen>:
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
                text: 'Gerenciamento de Pacientes'
                font_size: '24sp'
                color: 1, 1, 1, 1
                bold: True
            
            Button:
                text: '+ Novo Paciente'
                size_hint_x: None
                width: dp(150)
                background_color: 0.0, 0.73, 0.83, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.add_new_patient()
        
        # Filtros e busca
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
            
            TextInput:
                id: search_input
                hint_text: "🔍 Buscar paciente por nome..."
                size_hint_x: 0.4
                font_size: '16sp'
                multiline: False
                on_text: root.filter_patients(self.text)
            
            Spinner:
                id: age_filter_spinner
                text: 'Todas as Idades'
                values: ['Todas as Idades', 'Menores (< 18)', 'Adultos (≥ 18)']
                size_hint_x: 0.2
                font_size: '16sp'
                on_text: root.filter_by_age(self.text)
            
            Spinner:
                id: gender_filter_spinner
                text: 'Todos os Gêneros'
                values: ['Todos os Gêneros', 'Masculino', 'Feminino', 'Outro']
                size_hint_x: 0.2
                font_size: '16sp'
                on_text: root.filter_by_gender(self.text)
            
            Button:
                text: '🔄 Atualizar'
                size_hint_x: 0.1
                background_color: 0.0, 0.47, 0.84, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.refresh_patients()
            
            Button:
                text: '📊 Relatório'
                size_hint_x: 0.1
                background_color: 0.0, 0.59, 0.53, 1
                color: 1, 1, 1, 1
                font_size: '16sp'
                on_press: root.generate_report()
        
        # Lista de pacientes
        ScrollView:
            id: patients_scroll
            
            GridLayout:
                id: patients_container
                cols: 2
                size_hint_y: None
                height: self.minimum_height
                padding: dp(15)
                spacing: dp(15)
"""
)

class PatientCard(BoxLayout):
    patient_data = ObjectProperty({})
    screen = ObjectProperty(None)

    def get_age_display(self):
        """Calcula e retorna a idade do paciente"""
        data_nascimento = self.patient_data.get('data_nascimento')
        if not data_nascimento:
            return "Idade não informada"
        
        try:
            if isinstance(data_nascimento, str):
                # Tenta diferentes formatos de data
                for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
                    try:
                        birth_date = datetime.datetime.strptime(data_nascimento, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return "Data inválida"
            else:
                birth_date = data_nascimento
            
            today = datetime.date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 18:
                return f"👶 {age} anos (menor)"
            else:
                return f"👤 {age} anos"
                
        except Exception as e:
            return "Idade não calculada"

    def is_minor(self):
        """Verifica se o paciente é menor de idade"""
        data_nascimento = self.patient_data.get('data_nascimento')
        if not data_nascimento:
            return False
        
        try:
            if isinstance(data_nascimento, str):
                for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
                    try:
                        birth_date = datetime.datetime.strptime(data_nascimento, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return False
            else:
                birth_date = data_nascimento
            
            today = datetime.date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age < 18
            
        except:
            return False

    def get_responsavel_display(self):
        """Retorna o nome do responsável ou mensagem apropriada"""
        if not self.is_minor():
            return "Não aplicável (maior de idade)"
        
        responsavel_nome = self.patient_data.get('responsavel_nome')
        if responsavel_nome:
            return responsavel_nome
        else:
            return "⚠️ Responsável não cadastrado"

class PatientEditPopup(Popup):
    patient_data = ObjectProperty({})
    patient_id = StringProperty(None, allownone=True)
    screen = ObjectProperty(None)
    is_minor = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.patient_id = self.patient_data.get('id')
        if self.patient_data.get('data_nascimento'):
            self.calculate_age(self.patient_data['data_nascimento'])

    def calculate_age(self, dob_str):
        """Calcula a idade e define se é menor"""
        try:
            for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
                try:
                    dob = datetime.datetime.strptime(dob_str, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                self.is_minor = False
                return
            
            today = datetime.date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            self.is_minor = age < 18
        except:
            self.is_minor = False

    def get_responsavel_name(self):
        """Retorna o nome do responsável atual"""
        return self.patient_data.get('responsavel_nome', 'Selecione um responsável')

    def add_new_responsavel(self):
        """Adiciona um novo responsável"""
        # Implementar popup para adicionar responsável
        print("Adicionar novo responsável")

    def save_patient(self):
        """Salva os dados do paciente"""
        patient_data = {
            'nome': self.ids.nome_input.text,
            'data_nascimento': self.ids.data_nascimento_input.text,
            'genero': self.ids.genero_input.text,
            'telefone': self.ids.telefone_input.text,
            'email': self.ids.email_input.text,
            'endereco': self.ids.endereco_input.text,
        }
        
        if self.is_minor:
            responsavel_nome = self.ids.responsavel_spinner.text
            if responsavel_nome != 'Selecione um responsável':
                patient_data['responsavel_nome'] = responsavel_nome
        
        self.screen.save_patient_data(patient_data, self.patient_id)
        self.dismiss()

class ImprovedPatientScreen(Screen):
    patients_data = ListProperty([])
    responsavel_names = ListProperty([])
    filtered_patients = ListProperty([])
    
    current_search_text = StringProperty('')
    current_age_filter = StringProperty('todas')
    current_gender_filter = StringProperty('todos')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load_initial_data, 0.5)

    def load_initial_data(self, dt):
        """Carrega os dados iniciais"""
        asyncio.create_task(self.fetch_patients())
        asyncio.create_task(self.fetch_responsaveis())

    async def fetch_patients(self):
        """Busca os pacientes da API"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                response = await client.get(f"{api.BASE_URL}/pacientes/", headers=headers)
                if response.status_code == 200:
                    self.patients_data = response.json()
                    self.apply_filters()
        except Exception as e:
            print(f"Erro ao buscar pacientes: {e}")

    async def fetch_responsaveis(self):
        """Busca a lista de responsáveis"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                response = await client.get(f"{api.BASE_URL}/responsaveis/", headers=headers)
                if response.status_code == 200:
                    responsaveis = response.json()
                    self.responsavel_names = [r.get('nome', 'N/A') for r in responsaveis]
        except Exception as e:
            print(f"Erro ao buscar responsáveis: {e}")

    @mainthread
    def update_patients_display(self):
        """Atualiza a exibição dos pacientes"""
        container = self.ids.patients_container
        container.clear_widgets()
        
        if not self.filtered_patients:
            no_data_label = Label(
                text="Nenhum paciente encontrado",
                font_size='18sp',
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=dp(100)
            )
            container.add_widget(no_data_label)
            return
        
        for patient in self.filtered_patients:
            card = PatientCard(patient_data=patient, screen=self)
            container.add_widget(card)

    def apply_filters(self):
        """Aplica todos os filtros ativos"""
        filtered = self.patients_data.copy()
        
        # Filtro por texto de busca
        if self.current_search_text:
            search_lower = self.current_search_text.lower()
            filtered = [p for p in filtered if search_lower in p.get('nome', '').lower()]
        
        # Filtro por idade
        if self.current_age_filter == 'menores':
            filtered = [p for p in filtered if self.is_patient_minor(p)]
        elif self.current_age_filter == 'adultos':
            filtered = [p for p in filtered if not self.is_patient_minor(p)]
        
        # Filtro por gênero
        if self.current_gender_filter != 'todos':
            filtered = [p for p in filtered if p.get('genero', '').lower() == self.current_gender_filter.lower()]
        
        self.filtered_patients = filtered
        self.update_patients_display()

    def is_patient_minor(self, patient_data):
        """Verifica se um paciente é menor de idade"""
        data_nascimento = patient_data.get('data_nascimento')
        if not data_nascimento:
            return False
        
        try:
            if isinstance(data_nascimento, str):
                for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
                    try:
                        birth_date = datetime.datetime.strptime(data_nascimento, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return False
            else:
                birth_date = data_nascimento
            
            today = datetime.date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age < 18
            
        except:
            return False

    def filter_patients(self, search_text):
        """Filtra pacientes por texto de busca"""
        self.current_search_text = search_text
        self.apply_filters()

    def filter_by_age(self, age_filter_text):
        """Filtra pacientes por idade"""
        if 'Menores' in age_filter_text:
            self.current_age_filter = 'menores'
        elif 'Adultos' in age_filter_text:
            self.current_age_filter = 'adultos'
        else:
            self.current_age_filter = 'todas'
        
        self.apply_filters()

    def filter_by_gender(self, gender_filter_text):
        """Filtra pacientes por gênero"""
        if 'Todos' in gender_filter_text:
            self.current_gender_filter = 'todos'
        else:
            self.current_gender_filter = gender_filter_text
        
        self.apply_filters()

    def refresh_patients(self):
        """Atualiza a lista de pacientes"""
        asyncio.create_task(self.fetch_patients())

    def generate_report(self):
        """Gera relatório de pacientes"""
        print("Gerando relatório de pacientes...")

    def add_new_patient(self):
        """Adiciona um novo paciente"""
        popup = PatientEditPopup(patient_data={}, screen=self)
        popup.open()

    def edit_patient(self, patient_data):
        """Edita um paciente existente"""
        popup = PatientEditPopup(patient_data=patient_data, screen=self)
        popup.open()

    def open_prontuarios(self, patient_data):
        """Abre os prontuários do paciente"""
        print(f"Abrindo prontuários para: {patient_data.get('nome')}")
        # Implementar navegação para prontuários

    def open_documents(self, patient_data):
        """Abre os documentos do paciente"""
        print(f"Abrindo documentos para: {patient_data.get('nome')}")
        # Implementar navegação para documentos

    def open_orcamentos(self, patient_data):
        """Abre os orçamentos do paciente"""
        print(f"Abrindo orçamentos para: {patient_data.get('nome')}")
        # Implementar navegação para orçamentos

    def schedule_appointment(self, patient_data):
        """Agenda um novo atendimento para o paciente"""
        print(f"Agendando atendimento para: {patient_data.get('nome')}")
        # Implementar navegação para agendamento

    def save_patient_data(self, patient_data, patient_id=None):
        """Salva os dados do paciente"""
        if patient_id:
            asyncio.create_task(self.update_patient(patient_id, patient_data))
        else:
            asyncio.create_task(self.create_patient(patient_data))

    async def create_patient(self, patient_data):
        """Cria um novo paciente"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                response = await client.post(f"{api.BASE_URL}/pacientes/", 
                                           headers=headers, json=patient_data)
                if response.status_code == 201:
                    await self.fetch_patients()
        except Exception as e:
            print(f"Erro ao criar paciente: {e}")

    async def update_patient(self, patient_id, patient_data):
        """Atualiza um paciente existente"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api.global_access_token}"}
                response = await client.put(f"{api.BASE_URL}/pacientes/{patient_id}", 
                                          headers=headers, json=patient_data)
                if response.status_code == 200:
                    await self.fetch_patients()
        except Exception as e:
            print(f"Erro ao atualizar paciente: {e}")

