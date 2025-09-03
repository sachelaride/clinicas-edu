from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from kivy.metrics import dp

import httpx
import asyncio

# Import the api module to access its global variables
import api
from app.models.roles import UserRole # Import UserRole to use in the Spinner

# KV Language String
Builder.load_string("""
#:import UserRole app.models.roles.UserRole

<UserListItem>:
    screen: None
    size_hint_y: None
    height: dp(50)
    padding: dp(5)
    spacing: dp(10)
    
    Label:
        text: root.display_nome
        size_hint_x: 0.3
    Label:
        text: root.display_role
        size_hint_x: 0.2
    Label:
        id: clinic_name_label
        text: root.display_clinic_name
        size_hint_x: 0.25
    Button:
        text: 'Editar'
        size_hint_x: 0.125
        on_press: root.screen.open_edit_user_popup(root.user_data); print(f"UserListItem: Editar button pressed for user: {root.user_data.get('nome')}")
    Button:
        text: 'Excluir'
        size_hint_x: 0.125
        on_press: root.screen.delete_user(root.user_data.get('id'))

<UserEditPopup>:
    title: "Editar Usuário" if self.user_id else "Adicionar Novo Usuário"
    size_hint: 0.8, 0.8
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        TextInput:
            id: nome_input
            hint_text: 'Nome Completo'
            text: root.user_data.get('nome', '')
        TextInput:
            id: username_input
            hint_text: 'Username'
            text: root.user_data.get('username', '')
        TextInput:
            id: email_input
            hint_text: 'Email'
            text: root.user_data.get('email', '')
        TextInput:
            id: password_input
            hint_text: 'Senha (deixe em branco para não alterar)'
        Spinner:
            id: role_input
            text: root.user_data.get('role', 'Selecione a Função')
            values: [role.value for role in UserRole]
        
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Button:
                text: 'Salvar'
                on_press: root.save_user()
            Button:
                text: 'Cancelar'
                on_press: root.dismiss()

<UserManagementScreen>:
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
                text: 'Gerenciamento de Usuários'
                font_size: '24sp'

        # Header
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            padding: dp(5)
            spacing: dp(10)
            
            Label:
                text: 'Nome'
                size_hint_x: 0.3
            Label:
                text: 'Função'
                size_hint_x: 0.2
            Label:
                id: clinic_name_label
                text: root.user_data.get('clinic_name', '')
                size_hint_x: 0.25
            Widget: # Spacer for the buttons
                size_hint_x: 0.25
        
        # User List (RecycleView)
        RecycleView:
            id: user_list_rv
            viewclass: 'UserListItem'
            data: root.user_list_data
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
                text: 'Adicionar Novo Usuário'
                on_press: root.open_add_user_popup()

""")

class UserListItem(BoxLayout):
    user_data = ObjectProperty({})
    screen = ObjectProperty(None)
    display_nome = StringProperty('')
    display_role = StringProperty('')
    display_clinic_name = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # The print here will still show N/A initially, but it's okay now
        print(f"DEBUG: UserListItem __init__ called. user_data: {self.user_data.get('nome', 'N/A')}")

    def on_user_data(self, instance, value):
        # This method is called when the user_data property changes
        self.display_nome = value.get('nome', '')
        self.display_role = value.get('role', '')
        self.display_clinic_name = value.get('clinic_name', '')
        print(f"DEBUG: on_user_data called. Nome: {self.display_nome}, Clinic: {self.display_clinic_name}")

    # Removed on_user_data method, relying on KV binding directly

class UserEditPopup(Popup):
    user_data = ObjectProperty({})
    user_id = StringProperty(None, allownone=True)
    screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = self.user_data.get('id')
        print(f"UserEditPopup: __init__ called for user: {self.user_data.get('nome')}")

    def save_user(self):
        # Collect data from inputs
        payload = {
            'nome': self.ids.nome_input.text,
            'username': self.ids.username_input.text,
            'email': self.ids.email_input.text,
            'role': self.ids.role_input.text,
        }
        # Only include password if it's not empty
        if self.ids.password_input.text:
            payload['password'] = self.ids.password_input.text
        
        # Call the screen's method to save the user
        self.screen.save_user(payload, self.user_id)
        self.dismiss()

from kivy.properties import ListProperty, ObjectProperty # Adicionado ObjectProperty

class UserManagementScreen(Screen):
    user_list_data = ListProperty([])
    user_data = ObjectProperty({}) # Adicionado user_data

    def on_enter(self, *args):
        self.user_data = api.global_user_data # Set user_data from global api
        self.fetch_users()

    def fetch_users(self):
        Clock.schedule_once(self._run_fetch_users_task)

    def _run_fetch_users_task(self, dt):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._fetch_users_async())
        finally:
            loop.close()

    async def _fetch_users_async(self):
        self.clear_user_list()
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                # Fetch all users
                users_response = await client.get(f"{api.BASE_URL}/users/", headers=headers)
                users_response.raise_for_status()
                users_data = users_response.json()
                print(f"DEBUG: Fetched users_data: {users_data}") # Debug print

                # Fetch all tenants and create a mapping
                tenants_response = await client.get(f"{api.BASE_URL}/tenants/", headers=headers)
                tenants_response.raise_for_status()
                tenants_data = tenants_response.json()
                print(f"DEBUG: Fetched tenants_data: {tenants_data}") # Debug print
                tenant_name_map = {tenant['id']: tenant['nome'] for tenant in tenants_data}

                # Add clinic_name to each user
                processed_users_data = []
                for user in users_data:
                    tenant_id = user.get('default_tenant_id')
                    user['clinic_name'] = tenant_name_map.get(tenant_id, 'N/A') # 'N/A' if tenant not found
                    processed_users_data.append(user)
                print(f"DEBUG: Processed users_data with clinic_name: {processed_users_data}") # Debug print

                self.update_user_list(processed_users_data)
        except Exception as e:
            print(f"Erro ao buscar usuários ou clínicas: {e}")

    @mainthread
    def update_user_list(self, users_data):
        print(f"DEBUG: update_user_list called with {len(users_data)} users. First user's clinic_name: {users_data[0].get('clinic_name') if users_data else 'N/A'}") # Debug print
        self.user_list_data = [{'user_data': user, 'screen': self} for user in users_data]
        self.ids.user_list_rv.refresh_from_data() # Force refresh

    @mainthread
    def clear_user_list(self):
        self.user_list_data = []

    def open_add_user_popup(self):
        popup = UserEditPopup(screen=self, user_data={})
        popup.open()

    def open_edit_user_popup(self, user_data):
        print(f"UserManagementScreen: open_edit_user_popup called with user_data: {user_data.get('nome')}")
        popup = UserEditPopup(screen=self, user_data=user_data)
        popup.open()

    def save_user(self, user_data, user_id):
        Clock.schedule_once(lambda dt: self._run_save_user_task(user_data, user_id))

    def _run_save_user_task(self, user_data, user_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._save_user_async(user_data, user_id))
        finally:
            loop.close()

    async def _save_user_async(self, user_data, user_id):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                if user_id: # Update existing user
                    print(f"Atualizando usuário {user_id}: {user_data}")
                    response = await client.put(
                        f"{api.BASE_URL}/users/{user_id}",
                        headers=headers,
                        json=user_data
                    )
                else: # Create new user
                    print(f"Criando novo usuário: {user_data}")
                    response = await client.post(
                        f"{api.BASE_URL}/users/",
                        headers=headers,
                        json=user_data
                    )
                response.raise_for_status()
                self.fetch_users() # Refresh the list
        except Exception as e:
            print(f"Erro ao salvar usuário: {e}")

    def delete_user(self, user_id):
        if not user_id:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text=f'Tem certeza que deseja excluir o usuário?'))
        
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
            Clock.schedule_once(lambda dt: self._run_delete_user_task(user_id))

        yes_btn.bind(on_press=_delete_and_dismiss)
        no_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def _run_delete_user_task(self, user_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._delete_user_async(user_id))
        finally:
            loop.close()

    async def _delete_user_async(self, user_id):
        try:
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                print(f"Deletando usuário {user_id}")
                response = await client.delete(
                    f"{api.BASE_URL}/users/{user_id}",
                    headers=headers
                )
                response.raise_for_status()
                self.fetch_users() # Refresh the list
        except Exception as e:
            print(f"Erro ao deletar usuário: {e}")