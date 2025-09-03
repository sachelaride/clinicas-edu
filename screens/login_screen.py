from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.clock import mainthread, Clock

import httpx
import asyncio

# Import the api module to access its functions and global variables
import api

# Load the KV language string for the simplified UI
Builder.load_string("""
#:import api api

<LoginScreen>:
    username_input: username_input
    password_input: password_input
    message_label: message_label

    AnchorLayout:
        anchor_x: 'center'
        anchor_y: 'center'
        canvas.before:
            Color:
                rgba: api.global_primary_color
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            orientation: 'vertical'
            size_hint: None, None
            width: dp(350)
            height: self.minimum_height
            padding: dp(20)
            spacing: dp(10)
            
            Label:
                text: 'Login'
                font_size: '30sp'
                size_hint_y: None
                height: self.texture_size[1]

            TextInput:
                id: username_input
                hint_text: 'Usuário'
                multiline: False
                size_hint_y: None
                height: dp(40)
                on_text_validate: password_input.focus = True

            TextInput:
                id: password_input
                hint_text: 'Senha'
                password: True
                multiline: False
                size_hint_y: None
                height: dp(40)
                on_text_validate: root.login()

            Button:
                text: 'Entrar'
                size_hint_y: None
                height: dp(50)
                on_press: root.login()

            Label:
                id: message_label
                text: ''
                color: 1,0,0,1 # Red color for error messages
                size_hint_y: None
                height: self.texture_size[1]
""")

class LoginScreen(Screen):
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    message_label = ObjectProperty(None)

    def login(self):
        username = self.username_input.text
        password = self.password_input.text
        self.message_label.text = '' # Clear previous messages

        if not username or not password:
            self.update_message("Por favor, preencha usuário e senha.", (1,0,0,1))
            return

        # Run the async login operation in a separate thread
        def _run_async_login_task(dt):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._perform_login_and_fetch_data_async(username, password))
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.update_message("Credenciais inválidas. Tente novamente.", (1,0,0,1))
                else:
                    self.update_message(f"Erro HTTP: {e.response.status_code} - {e.response.text}", (1,0,0,1))
            except httpx.RequestError as e:
                self.update_message(f"Erro de conexão: {e}", (1,0,0,1))
            except Exception as e:
                self.update_message(f"Ocorreu um erro inesperado: {e}", (1,0,0,1))
            finally:
                loop.close()

        Clock.schedule_once(_run_async_login_task, 0)

    async def _perform_login_and_fetch_data_async(self, username, password):
        # Step 1: Login and get token
        token_data = await api.login_user(username, password)
        
        api.global_access_token = token_data.get("access_token")
        api.global_default_tenant_id = token_data.get("default_tenant_id")

        if api.global_access_token:
            # Fetch user details
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                user_response = await client.get(f"{api.BASE_URL}/users/me", headers=headers)
                user_response.raise_for_status()
                user_data = user_response.json()

                # Fetch all tenants
                tenants_response = await client.get(f"{api.BASE_URL}/tenants/", headers=headers)
                tenants_response.raise_for_status()
                tenants_data = tenants_response.json()

                # Create tenant name map
                tenant_name_map = {tenant['id']: tenant['nome'] for tenant in tenants_data}

                # Add clinic_name to user_data
                tenant_id = user_data.get('default_tenant_id')
                user_data['clinic_name'] = tenant_name_map.get(tenant_id, 'N/A')

                # Store in global_user_data
                api.global_user_data = user_data

            self.update_message("Login bem-sucedido!", (0,1,0,1)) # Green color
            # Navigate to the main clinic menu screen
            self.manager.current = 'clinic_menu'

    @mainthread
    def update_message(self, message, color=(1,1,1,1)):
        self.message_label.text = message
        self.message_label.color = color