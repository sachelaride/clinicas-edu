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

from kivy.uix.filechooser import FileChooserListView

import httpx
import asyncio
import datetime
import os

import api

class MaskedInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mask = "##/##/####"
        self.hint_text = "DD/MM/AAAA"

    def insert_text(self, substring, from_undo=False):
        if not from_undo:
            new_text = self.text
            for char in substring:
                if len(new_text) < len(self.mask):
                    if self.mask[len(new_text)] == '#':
                        if char.isdigit():
                            new_text += char
                    else:
                        new_text += self.mask[len(new_text)]
                        if char.isdigit():
                            new_text += char
            self.text = new_text
        else:
            super().insert_text(substring, from_undo=from_undo)

class PhoneMaskedInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mask = "(__)____-____"
        self.hint_text = "(__)____-____"

    def insert_text(self, substring, from_undo=False):
        if not from_undo:
            new_text = self.text
            for char in substring:
                if len(new_text) < len(self.mask):
                    if self.mask[len(new_text)] == '_':
                        if char.isdigit():
                            new_text += char
                    elif self.mask[len(new_text)] in '()- ':
                        new_text += self.mask[len(new_text)]
                        if char.isdigit():
                            new_text += char
            self.text = new_text
        else:
            super().insert_text(substring, from_undo=from_undo)

from kivy.uix.filechooser import FileChooserListView

# KV Language String
Builder.load_string("""
<PatientListItem>:
    patient_data: {}
    screen: None
    size_hint_y: None
    height: dp(50)
    padding: dp(5)
    spacing: dp(10)
    
    Label:
        text: root.display_nome if root.display_nome is not None else ''
        size_hint_x: 0.25
    Label:
        text: root.display_data_nascimento if root.display_data_nascimento is not None else ''
        size_hint_x: 0.15
    Label:
        text: root.display_genero if root.display_genero is not None else ''
        size_hint_x: 0.1
    Label:
        text: root.display_telefone if root.display_telefone is not None else ''
        size_hint_x: 0.15
    Label:
        text: root.display_client_code if root.display_client_code is not None else ''
        size_hint_x: 0.1
    Label:
        text: root.display_responsavel_nome if root.display_responsavel_nome is not None else ''
        size_hint_x: 0.1
    Button:
        text: 'Editar'
        size_hint_x: 0.05
        on_press: root.screen.open_edit_patient_popup(root.patient_data)
    Button:
        text: 'Prontuários'
        size_hint_x: 0.05
        on_press: root.screen.open_prontuarios_screen(root.patient_data)
    Button:
        text: 'Documentos'
        size_hint_x: 0.05
        on_press: root.screen.open_documents_screen(root.patient_data)

<PatientEditPopup>:
    title: "Editar Paciente" if self.patient_id else "Adicionar Novo Paciente"
    size_hint: 0.8, 0.9
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(5) # Reduced spacing

        ScrollView: # Add ScrollView for better handling of many fields
            size_hint_y: 0.8 # Allocate most space to scrollable content
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(5) # Reduced spacing

                TextInput:
                    id: nome_input
                    hint_text: 'Nome Completo'
                    text: root.patient_data.get('nome', '') if root.patient_data.get('nome') is not None else ''
                    size_hint_y: None
                    height: dp(35) # Reduced height
                MaskedInput:
                    id: data_nascimento_input
                    hint_text: 'Data de Nascimento (DD/MM/AAAA)'
                    text: root.patient_data.get('data_nascimento', '') if root.patient_data.get('data_nascimento') is not None else ''
                    on_text_validate: root.calculate_age(self.text)
                    on_focus: if not self.focus: root.calculate_age(self.text)
                    size_hint_y: None
                    height: dp(35) # Reduced height
                Spinner:
                    id: genero_input
                    text: root.patient_data.get('genero', 'Selecione o Gênero') if root.patient_data.get('genero') is not None else ''
                    values: ['Masculino', 'Feminino', 'Outro']
                    size_hint_y: None
                    height: dp(35) # Reduced height
                TextInput:
                    id: endereco_input
                    hint_text: 'Endereço'
                    text: root.patient_data.get('endereco', '') if root.patient_data.get('endereco') is not None else ''
                    size_hint_y: None
                    height: dp(35) # Reduced height
                TextInput:
                    id: telefone_input
                    hint_text: 'Telefone'
                    text: root.patient_data.get('telefone', '') if root.patient_data.get('telefone') is not None else ''
                    size_hint_y: None
                    height: dp(35) # Reduced height
                TextInput:
                    id: email_input
                    hint_text: 'Email'
                    text: root.patient_data.get('email', '') if root.patient_data.get('email') is not None else ''
                    size_hint_y: None
                    height: dp(35) # Reduced height

                # Add document section
                BoxLayout:
                    size_hint_y: None
                    height: dp(35) # Reduced height
                    Button:
                        text: 'Adicionar Documento'
                        on_press: root.select_document()
                    Label:
                        id: selected_document_label
                        text: 'Nenhum documento selecionado'

                # Responsible Party Section (visible only if patient is minor)
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None if root.is_minor else 0 # Hide if not minor
                    height: self.minimum_height if root.is_minor else 0 # Hide if not minor
                    opacity: 1 if root.is_minor else 0 # Hide if not minor
                    disabled: not root.is_minor # Disable if not minor
                    Label:
                        text: 'Responsável (para menores)'
                        size_hint_y: None
                        height: dp(30)
                    Spinner:
                        id: responsavel_spinner
                        text: root.patient_data.get('responsavel_nome', 'Selecione Responsável')
                        values: root.screen.responsavel_names
                        on_text: root.screen.on_responsavel_selected(self.text)
                        size_hint_y: None
                        height: dp(35) # Reduced height
                    Button:
                        text: 'Adicionar Novo Responsável'
                        size_hint_y: None
                        height: dp(35) # Reduced height

        BoxLayout:
            size_hint_y: None
            height: dp(40) # Reduced height for buttons
            Button:
                text: 'Salvar'
                on_press: root.save_patient()
            Button:
                text: 'Cancelar'
                on_press: root.dismiss()

<FileChooserPopup>:
    title: "Selecionar Arquivo"
    size_hint: 0.9, 0.9

    BoxLayout:
        orientation: 'vertical'

        FileChooserListView:
            id: filechooser

        BoxLayout:
            size_hint_y: None
            height: dp(50)

            Button:
                text: "Selecionar"
                on_press: root.select_file(filechooser.selection)

            Button:
                text: "Cancelar"
                on_press: root.dismiss()

<ResponsavelEditPopup>:
    title: "Editar Responsável" if self.responsavel_id else "Adicionar Novo Responsável"
    size_hint: 0.7, 0.7
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(5) # Reduced spacing

        TextInput:
            id: nome_input
            hint_text: 'Nome Completo'
            text: root.responsavel_data.get('nome', '') if root.responsavel_data.get('nome') is not None else ''
            size_hint_y: None
            height: dp(35) # Reduced height
        TextInput:
            id: telefone_input
            hint_text: 'Telefone'
            text: root.responsavel_data.get('telefone', '') if root.responsavel_.get('telefone') is not None else ''
            size_hint_y: None
            height: dp(35) # Reduced height
        TextInput:
            id: email_input
            hint_text: 'Email'
            text: root.responsavel_data.get('email', '') if root.responsavel_data.get('email') is not None else ''
            size_hint_y: None
            height: dp(35) # Reduced height
        TextInput:
            id: documento_input
            hint_text: 'Documento (CPF/RG)'
            text: root.responsavel_data.get('documento', '') if root.responsavel_data.get('documento') is not None else ''
            size_hint_y: None
            height: dp(35) # Reduced height

        BoxLayout:
            size_hint_y: None
            height: dp(40) # Reduced height for buttons
            Button:
                text: 'Salvar'
                on_press: root.save_responsavel()
            Button:
                text: 'Cancelar'
                on_press: root.dismiss()

<PatientManagementScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        # Top Bar
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            padding: dp(10)
            
            Button:
                text: 'Voltar'
                size_hint_x: 0.2
                on_press: app.root.current = 'clinic_menu'
            Label:
                text: 'Gerenciamento de Pacientes'
                font_size: '24sp'

        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            padding: dp(5)
            spacing: dp(10)
            
            Label:
                text: 'Nome'
                size_hint_x: 0.25
            Label:
                text: 'Nascimento'
                size_hint_x: 0.15
            Label:
                text: 'Gênero'
                size_hint_x: 0.1
            Label:
                text: 'Telefone'
                size_hint_x: 0.15
            Label:
                text: 'Cód. Cliente'
                size_hint_x: 0.1
            Label:
                text: 'Responsável'
                size_hint_x: 0.1
            Widget: # Spacer for buttons
                size_hint_x: 0.15
        
        # Patient List (RecycleView)
        RecycleView:
            id: patient_list_rv
            viewclass: 'PatientListItem'
            data: root.patient_list_data
            scroll_type: ['bars', 'content']
            bar_width: dp(10)
            
            RecycleBoxLayout:
                default_size: None, dp(50)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(5)

        # Bottom Bar
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: dp(10)
            
            Button:
                text: 'Adicionar Novo Paciente'
                on_press: root.open_add_patient_popup()
"""
)

class PatientListItem(BoxLayout):
    patient_data = ObjectProperty({})
    screen = ObjectProperty(None)
    display_nome = StringProperty('')
    display_data_nascimento = StringProperty('')
    display_genero = StringProperty('')
    display_telefone = StringProperty('', allownone=True)
    display_responsavel_nome = StringProperty('')
    display_client_code = StringProperty('', allownone=True)

    def on_patient_data(self, instance, value):
        self.display_nome = value.get('nome', '')
        self.display_data_nascimento = value.get('data_nascimento', '')
        self.display_genero = value.get('genero', '')
        self.display_telefone = value.get('telefone', '')
        self.display_client_code = value.get('client_code', '')
        # Fetch responsavel name if responsavel_id is present
        responsavel_id = value.get('responsavel_id')
        if responsavel_id and self.screen and self.screen.responsaveis_map:
            self.display_responsavel_nome = self.screen.responsaveis_map.get(str(responsavel_id), 'N/A')
        else:
            self.display_responsavel_nome = ''

class ResponsavelEditPopup(Popup):
    responsavel_data = ObjectProperty({})
    responsavel_id = StringProperty(None, allownone=True)
    screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.responsavel_id = self.responsavel_data.get('id')

    def save_responsavel(self):
        payload = {
            'nome': self.ids.nome_input.text,
            'telefone': self.ids.telefone_input.text,
            'email': self.ids.email_input.text,
            'documento': self.ids.documento_input.text,
        }
        self.screen.save_responsavel(payload, self.responsavel_id)
        self.dismiss()

class PatientEditPopup(Popup):
    patient_data = ObjectProperty({})
    patient_id = StringProperty(None, allownone=True)
    screen = ObjectProperty(None)
    is_minor = BooleanProperty(False) # New property
    selected_document_path = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.patient_id = self.patient_data.get('id')
        # Calculate age on init if data_nascimento is present
        if self.patient_data.get('data_nascimento'):
            self.calculate_age(self.patient_data['data_nascimento'])

    def calculate_age(self, dob_str):
        try:
            dob = datetime.datetime.strptime(dob_str, '%d/%m/%Y').date()
            today = datetime.date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            self.is_minor = age < 18
        except ValueError:
            self.is_minor = False # Invalid date, assume not minor or handle error

    def select_document(self):
        file_chooser_popup = FileChooserPopup()
        file_chooser_popup.bind(on_select=self.on_file_select)
        file_chooser_popup.open()

    def on_file_select(self, instance, selection):
        if selection:
            self.selected_document_path = selection[0]
            self.ids.selected_document_label.text = os.path.basename(self.selected_document_path)

    def save_patient(self):
        # Convert data_nascimento to date object
        data_nascimento_str = self.ids.data_nascimento_input.text
        data_nascimento_obj = None
        try:
            data_nascimento_obj = datetime.datetime.strptime(data_nascimento_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            # Handle invalid date format, e.g., show an error message
            print("Erro: Formato de data de nascimento inválido. Use DD/MM/AAAA.")
            return

        # Ensure responsavel_id is None if empty string
        responsavel_id_val = self.screen.selected_responsavel_id
        if responsavel_id_val == '': # If no responsavel is selected, it might be an empty string
            responsavel_id_val = None

        payload = {
            'nome': self.ids.nome_input.text,
            'data_nascimento': data_nascimento_obj,
            'genero': self.ids.genero_input.text,
            'endereco': self.ids.endereco_input.text,
            'telefone': self.ids.telefone_input.text,
            'email': self.ids.email_input.text,
            'responsavel_id': responsavel_id_val
        }
        self.screen.save_patient(payload, self.patient_id, self.selected_document_path)
        self.dismiss()

class FileChooserPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_select')

    def select_file(self, selection):
        self.dispatch('on_select', selection)
        self.dismiss()

    def on_select(self, *args):
        pass

class PatientManagementScreen(Screen):
    patient_list_data = ListProperty([])
    responsaveis_map = ObjectProperty({}) # Map responsavel_id to name
    responsavel_names = ListProperty([]) # List of responsavel names for spinner
    selected_responsavel_id = StringProperty(None, allownone=True)
    selected_document_path = StringProperty(None, allownone=True)

    def on_enter(self, *args):
        self.fetch_patients()
        self.fetch_responsaveis()

    def fetch_patients(self):
        Clock.schedule_once(self._run_fetch_patients_task)

    def _run_fetch_patients_task(self, dt):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._fetch_patients_async())
        finally:
            loop.close()

    async def _fetch_patients_async(self):
        self.patient_list_data = []
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{api.BASE_URL}/pacientes/", headers=headers)
                response.raise_for_status()
                patients_data = response.json()
                
                # Add responsavel_nome to each patient data
                processed_patients_data = []
                for patient in patients_data:
                    responsavel_id = patient.get('responsavel_id')
                    if responsavel_id:
                        patient['responsavel_nome'] = self.responsaveis_map.get(str(responsavel_id), 'N/A')
                    else:
                        patient['responsavel_nome'] = ''
                    processed_patients_data.append(patient)

                self.update_patient_list(processed_patients_data)
        except Exception as e:
            print(f"Erro ao buscar pacientes: {e}")

    @mainthread
    def update_patient_list(self, patients_data):
        self.patient_list_data = [{'patient_data': patient, 'screen': self} for patient in patients_data]
        self.ids.patient_list_rv.refresh_from_data()

    def fetch_responsaveis(self):
        Clock.schedule_once(self._run_fetch_responsaveis_task)

    def _run_fetch_responsaveis_task(self, dt):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._fetch_responsaveis_async())
        finally:
            loop.close()

    async def _fetch_responsaveis_async(self):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{api.BASE_URL}/responsaveis/", headers=headers)
                response.raise_for_status()
                responsaveis_data = response.json()
                
                self.responsaveis_map = {str(r['id']): r['nome'] for r in responsaveis_data}
                self.responsavel_names = [r['nome'] for r in responsaveis_data]
        except Exception as e:
            print(f"Erro ao buscar responsáveis: {e}")

    def on_responsavel_selected(self, responsavel_name):
        # Find the ID of the selected responsavel
        for responsavel_id, name in self.responsaveis_map.items():
            if name == responsavel_name:
                self.selected_responsavel_id = responsavel_id
                break
        else:
            self.selected_responsavel_id = None

    def open_add_patient_popup(self):
        popup = PatientEditPopup(screen=self, patient_data={})
        popup.open()

    def open_edit_patient_popup(self, patient_data):
        # Set selected_responsavel_id if editing an existing patient with a responsavel
        self.selected_responsavel_id = str(patient_data.get('responsavel_id')) if patient_data.get('responsavel_id') else None
        popup = PatientEditPopup(screen=self, patient_data=patient_data)
        popup.open()

    def save_patient(self, patient_data, patient_id, selected_document_path=None):
        self.selected_document_path = selected_document_path
        Clock.schedule_once(lambda dt: self._run_save_patient_task(patient_data, patient_id))

    def _run_save_patient_task(self, patient_data, patient_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._save_patient_async(patient_data, patient_id))
        finally:
            loop.close()

    async def _save_patient_async(self, patient_data, patient_id):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                if patient_id:
                    response = await client.put(
                        f"{api.BASE_URL}/pacientes/{patient_id}",
                        headers=headers,
                        json=patient_data
                    )
                    response.raise_for_status()
                else:
                    response = await client.post(
                        f"{api.BASE_URL}/pacientes/",
                        headers=headers,
                        json=patient_data
                    )
                    response.raise_for_status()
                    new_patient_data = response.json()
                    # Now, if there is a document to upload, do it
                    if self.selected_document_path:
                        await self._upload_document_async(new_patient_data['id'], self.selected_document_path)

                self.fetch_patients() # Refresh the list
        except Exception as e:
            print(f"Erro ao salvar paciente: {e}")

    async def _upload_document_async(self, patient_id, file_path):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            payload = {
                'paciente_id': patient_id,
                'tipo_documento': 'Documento Pessoal',
            }
            async with httpx.AsyncClient() as client:
                with open(file_path, "rb") as f:
                    files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                    response = await client.post(
                        f"{api.BASE_URL}/documentos-paciente/",
                        headers=headers,
                        data=payload,
                        files=files
                    )
                    response.raise_for_status()
        except Exception as e:
            print(f"Erro ao fazer upload do documento: {e}")

    def delete_patient(self, patient_id):
        if not patient_id:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text='Tem certeza que deseja excluir o paciente?'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        yes_btn = Button(text='Sim')
        no_btn = Button(text='Não')
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        popup = Popup(title='Confirmar Exclusão',
                      content=content,
                      size_hint=(0.6, 0.4),
                      auto_dismiss=False)

        def _delete_and_dismiss(instance):
            popup.dismiss()
            Clock.schedule_once(lambda dt: self._run_delete_patient_task(patient_id))

        yes_btn.bind(on_press=_delete_and_dismiss)
        no_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def _run_delete_patient_task(self, patient_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._delete_patient_async(patient_id))
        finally:
            loop.close()

    async def _delete_patient_async(self, patient_id):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{api.BASE_URL}/pacientes/{patient_id}",
                    headers=headers
                )
                response.raise_for_status()
                self.fetch_patients() # Refresh the list
        except Exception as e:
            print(f"Erro ao deletar paciente: {e}")

    def open_add_responsavel_popup(self):
        popup = ResponsavelEditPopup(screen=self, responsavel_data={})
        popup.open()

    def save_responsavel(self, responsavel_data, responsavel_id):
        Clock.schedule_once(lambda dt: self._run_save_responsavel_task(responsavel_data, responsavel_id))

    def _run_save_responsavel_task(self, responsavel_data, responsavel_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._save_responsavel_async(responsavel_data, responsavel_id))
        finally:
            loop.close()

    async def _save_responsavel_async(self, responsavel_data, responsavel_id):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                if responsavel_id:
                    response = await client.put(
                        f"{api.BASE_URL}/responsaveis/{responsavel_id}",
                        headers=headers,
                        json=responsavel_data
                    )
                else:
                    response = await client.post(
                        f"{api.BASE_URL}/responsaveis/",
                        headers=headers,
                        json=responsavel_data
                    )
                response.raise_for_status()
                self.fetch_responsaveis() # Refresh the list of responsaveis
        except Exception as e:
            print(f"Erro ao salvar responsável: {e}")

    def open_prontuarios_screen(self, patient_data):
        print(f"Opening prontuarios screen for patient: {patient_data.get('nome')}")
        self.manager.current = 'prontuario_management'
        self.manager.get_screen('prontuario_management').set_patient(patient_data)

    def open_documents_screen(self, patient_data):
        print(f"Opening documents screen for patient: {patient_data.get('nome')}")
        self.manager.current = 'document_management'
        self.manager.get_screen('document_management').set_patient(patient_data)
