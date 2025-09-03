from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, mainthread
from kivy.metrics import dp

import httpx
import asyncio
import api
import os

# KV Language String
Builder.load_string("""
<DocumentListItem>:
    document_data: {}
    screen: None
    size_hint_y: None
    height: dp(50)
    padding: dp(5)
    spacing: dp(10)
    
    Label:
        text: root.display_nome_arquivo
        size_hint_x: 0.4
    Label:
        text: root.display_tipo_documento
        size_hint_x: 0.2
    Label:
        text: root.display_created_at
        size_hint_x: 0.2
    Button:
        text: 'Ver Arquivo'
        size_hint_x: 0.1
        on_press: root.screen.view_document_file(root.document_data.get('id'))
    Button:
        text: 'Excluir'
        size_hint_x: 0.1
        on_press: root.screen.delete_document(root.document_data.get('id'))

<DocumentEditPopup>:
    title: "Adicionar Novo Documento"
    size_hint: 0.8, 0.8
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        TextInput:
            id: tipo_documento_input
            hint_text: 'Tipo de Documento (Ex: Consentimento, Exame)'
            multiline: False
            size_hint_y: None
            height: dp(40)
        
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: 'Selecionar Arquivo'
                on_press: root.screen.select_document_file()
            Label:
                id: selected_file_label
                text: 'Nenhum arquivo selecionado'
                size_hint_x: 0.7

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: 'Salvar'
                on_press: root.save_document()
            Button:
                text: 'Cancelar'
                on_press: root.dismiss()

<DocumentManagementScreen>:
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
                on_press: app.root.current = 'patient_management'
            Label:
                id: patient_name_label
                text: 'Documentos do Paciente: ' + root.patient_data.get('nome', '')
                font_size: '24sp'

        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            padding: dp(5)
            spacing: dp(10)
            
            Label:
                text: 'Nome do Arquivo'
                size_hint_x: 0.4
            Label:
                text: 'Tipo'
                size_hint_x: 0.2
            Label:
                text: 'Data'
                size_hint_x: 0.2
            Widget: # Spacer for buttons
                size_hint_x: 0.2
        
        # Document List (RecycleView)
        RecycleView:
            id: document_list_rv
            viewclass: 'DocumentListItem'
            data: root.document_list_data
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
                text: 'Adicionar Novo Documento'
                on_press: root.open_add_document_popup()
"""
)

class DocumentListItem(BoxLayout):
    document_data = ObjectProperty({})
    screen = ObjectProperty(None)
    display_nome_arquivo = StringProperty('')
    display_tipo_documento = StringProperty('')
    display_created_at = StringProperty('')

    def on_document_data(self, instance, value):
        self.display_nome_arquivo = value.get('nome_arquivo', '')
        self.display_tipo_documento = value.get('tipo_documento', '')
        self.display_created_at = value.get('created_at', '')[:10] # Display only date

class DocumentEditPopup(Popup):
    patient_id = StringProperty('')
    screen = ObjectProperty(None)
    selected_file_path = StringProperty(None, allownone=True)

    def save_document(self):
        tipo_documento = self.ids.tipo_documento_input.text
        file_path = self.selected_file_path

        if not file_path:
            # Show error message
            return

        # Prepare payload for API call
        payload = {
            'paciente_id': self.patient_id,
            'tipo_documento': tipo_documento,
        }

        self.screen.save_document(payload, file_path)
        self.dismiss()

class DocumentManagementScreen(Screen):
    patient_data = ObjectProperty({}) # Data of the patient whose documents are being viewed
    document_list_data = ListProperty([])

    def set_patient(self, patient_data):
        self.patient_data = patient_data
        self.fetch_documents()

    def on_enter(self, *args):
        # This might be called before set_patient, so handle gracefully
        if self.patient_data:
            self.fetch_documents()

    def fetch_documents(self):
        if not self.patient_data.get('id'):
            print("No patient ID to fetch documents for.")
            return
        Clock.schedule_once(self._run_fetch_documents_task)

    def _run_fetch_documents_task(self, dt):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._fetch_documents_async())
        finally:
            loop.close()

    async def _fetch_documents_async(self):
        self.document_list_data = []
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{api.BASE_URL}/documentos-paciente/paciente/{self.patient_data.get('id')}",
                    headers=headers
                )
                response.raise_for_status()
                self.update_document_list(response.json())
        except Exception as e:
            print(f"Erro ao buscar documentos: {e}")

    @mainthread
    def update_document_list(self, documents_data):
        self.document_list_data = [{'document_data': d, 'screen': self} for d in documents_data]
        self.ids.document_list_rv.refresh_from_data()

    def open_add_document_popup(self):
        popup = DocumentEditPopup(screen=self, patient_id=str(self.patient_data.get('id')))
        popup.open()

    def select_document_file(self):
        # This would typically open a file browser dialog
        # For now, just a placeholder
        print("File selection dialog would open here.")
        # Example: self.selected_file_path = '/path/to/selected/file.pdf'

    def save_document(self, payload, file_path):
        Clock.schedule_once(lambda dt: self._run_save_document_task(payload, file_path))

    def _run_save_document_task(self, payload, file_path):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._save_document_async(payload, file_path))
        finally:
            loop.close()

    async def _save_document_async(self, payload, file_path):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                # For file upload, use multipart/form-data
                files = None
                if file_path:
                    with open(file_path, "rb") as f:
                        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                
                response = await client.post(
                    f"{api.BASE_URL}/documentos-paciente/",
                    headers=headers,
                    data=payload, # Use data for form fields
                    files=files
                )
                response.raise_for_status()
                self.fetch_documents() # Refresh the list
        except Exception as e:
            print(f"Erro ao salvar documento: {e}")

    def view_document_file(self, document_id):
        # This would typically open the file using a system viewer
        print(f"Viewing document file for ID: {document_id}")
        # You would fetch the file path from the API and then open it
        # For now, just a placeholder

    def delete_document(self, document_id):
        if not document_id:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text='Tem certeza que deseja excluir o documento?'))
        
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
            Clock.schedule_once(lambda dt: self._run_delete_document_task(document_id))

        yes_btn.bind(on_press=_delete_and_dismiss)
        no_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def _run_delete_document_task(self, document_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._delete_document_async(document_id))
        finally:
            loop.close()

    async def _delete_document_async(self, document_id):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{api.BASE_URL}/documentos-paciente/{document_id}",
                    headers=headers
                )
                response.raise_status()
                self.fetch_documents() # Refresh the list
        except Exception as e:
            print(f"Erro ao deletar documento: {e}")
