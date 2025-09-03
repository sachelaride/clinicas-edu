from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock, mainthread
from kivy.metrics import dp

import httpx
import asyncio

import api

Builder.load_string("""
<TenantListItem>:
    screen: None
    size_hint_y: None
    height: dp(50)
    padding: dp(5)
    spacing: dp(10)
    
    Label:
        text: root.display_nome
        size_hint_x: 0.7
    Button:
        text: 'Editar'
        size_hint_x: 0.15
        on_press: root.screen.open_edit_tenant_popup(root.tenant_data)
    Button:
        text: 'Excluir'
        size_hint_x: 0.15
        on_press: root.screen.delete_tenant(root.tenant_data.get('id'))

<TenantEditPopup>:
    title: "Editar Clínica" if self.tenant_id else "Adicionar Nova Clínica"
    size_hint: 0.8, 0.6
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        TextInput:
            id: nome_input
            hint_text: 'Nome da Clínica'
            text: root.tenant_data.get('nome', '')
        
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            Label:
                text: 'Ativo:'
            CheckBox:
                id: ativo_input
                active: root.tenant_data.get('ativo', True)
        
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: 'Salvar'
                on_press: root.save_tenant()
            Button:
                text: 'Cancelar'
                on_press: root.dismiss()

<TenantManagementScreen>:
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
                text: 'Gerenciamento de Clínicas'
                font_size: '24sp'
        
        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            padding: dp(5)
            spacing: dp(10)
            Label:
                text: 'Nome da Clínica'
                size_hint_x: 0.7
            Widget:
                size_hint_x: 0.30

        # Tenant List
        RecycleView:
            id: tenant_list_rv
            viewclass: 'TenantListItem'
            data: root.tenant_list_data
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
                text: 'Adicionar Nova Clínica'
                on_press: root.open_add_tenant_popup()
""")

class TenantListItem(BoxLayout):
    tenant_data = ObjectProperty({})
    screen = ObjectProperty(None)
    display_nome = StringProperty('')

    def on_tenant_data(self, instance, value):
        self.display_nome = value.get('nome', '')

class TenantEditPopup(Popup):
    tenant_data = ObjectProperty({})
    tenant_id = StringProperty(None, allownone=True)
    screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tenant_id = self.tenant_data.get('id')

    def save_tenant(self):
        payload = {
            'nome': self.ids.nome_input.text,
            'ativo': self.ids.ativo_input.active,
        }
        self.screen.save_tenant(payload, self.tenant_id)
        self.dismiss()

class TenantManagementScreen(Screen):
    tenant_list_data = ListProperty([])

    def on_enter(self, *args):
        self.fetch_tenants()

    def fetch_tenants(self):
        Clock.schedule_once(self._run_fetch_tenants_task)

    def _run_fetch_tenants_task(self, dt):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._fetch_tenants_async())
        finally:
            loop.close()

    async def _fetch_tenants_async(self):
        self.tenant_list_data = []
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{api.BASE_URL}/tenants/", headers=headers)
                response.raise_for_status()
                self.update_tenant_list(response.json())
        except Exception as e:
            print(f"Erro ao buscar clínicas: {e}")

    @mainthread
    def update_tenant_list(self, tenants_data):
        self.tenant_list_data = [{'tenant_data': tenant, 'screen': self} for tenant in tenants_data]
        self.ids.tenant_list_rv.refresh_from_data()

    def open_add_tenant_popup(self):
        popup = TenantEditPopup(screen=self, tenant_data={})
        popup.open()

    def open_edit_tenant_popup(self, tenant_data):
        popup = TenantEditPopup(screen=self, tenant_data=tenant_data)
        popup.open()

    def save_tenant(self, tenant_data, tenant_id):
        Clock.schedule_once(lambda dt: self._run_save_tenant_task(tenant_data, tenant_id))

    def _run_save_tenant_task(self, tenant_data, tenant_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._save_tenant_async(tenant_data, tenant_id))
        finally:
            loop.close()

    async def _save_tenant_async(self, tenant_data, tenant_id):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                if tenant_id:
                    response = await client.put(f"{api.BASE_URL}/tenants/{tenant_id}", headers=headers, json=tenant_data)
                else:
                    response = await client.post(f"{api.BASE_URL}/tenants/", headers=headers, json=tenant_data)
                response.raise_for_status()
                self.fetch_tenants()
        except Exception as e:
            print(f"Erro ao salvar clínica: {e}")

    def delete_tenant(self, tenant_id):
        if not tenant_id:
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text='Tem certeza que deseja excluir a clínica?'))
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        yes_btn = Button(text='Sim')
        no_btn = Button(text='Não')
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        popup = Popup(title='Confirmar Exclusão', content=content, size_hint=(0.6, 0.4), auto_dismiss=False)
        
        def _delete_and_dismiss(instance):
            popup.dismiss()
            Clock.schedule_once(lambda dt: self._run_delete_tenant_task(tenant_id))

        yes_btn.bind(on_press=_delete_and_dismiss)
        no_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _run_delete_tenant_task(self, tenant_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._delete_tenant_async(tenant_id))
        finally:
            loop.close()

    async def _delete_tenant_async(self, tenant_id):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"{api.BASE_URL}/tenants/{tenant_id}", headers=headers)
                response.raise_for_status()
                self.fetch_tenants()
        except Exception as e:
            print(f"Erro ao deletar clínica: {e}")
