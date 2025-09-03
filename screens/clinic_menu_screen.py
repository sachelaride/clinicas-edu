from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.uix.spinner import Spinner
from kivy.metrics import dp # Import dp
from kivy.app import App # Import App to access root widget
from kivy.properties import ListProperty, NumericProperty, StringProperty # Import properties

import httpx
import asyncio

# Import the api module to access its global variables
import api
from app.core.theme_manager import theme_manager # Import theme_manager

Builder.load_string("""
#:import api api
#:import theme_manager app.core.theme_manager.theme_manager

<ClinicMenuScreen>:
    primary_color: api.global_primary_color
    text_color: api.global_text_color
    error_color: api.global_error_color
    exit_icon: theme_manager.get_icon_set().get('close', '')

    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: root.primary_color
            Rectangle:
                pos: self.pos
                size: self.size
        
        # Top Bar for Clinic Name
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            padding: dp(10)
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: 0.1, 0.5, 0.8, 1 # Blue background for top bar (this can also be themed later)
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                id: clinic_name_label
                text: 'Carregando nome da clínica...'
                font_size: '24sp'
                color: root.text_color # Use root.text_color
                size_hint_x: 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size

        # Main Menu Bar
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)
            padding: dp(5)
            spacing: dp(5)

            Spinner:
                id: cadastros_spinner
                text: 'Cadastros'
                values: ['Usuários', 'Clínicas', 'Pacientes', 'Responsáveis', 'Serviços', 'Estoque', 'Feriados', 'Configurações', 'Permissões']
                on_text: root.handle_menu_selection('cadastros', self.text)

            Spinner:
                id: agendamentos_spinner
                text: 'Agendamentos'
                values: ['Agendamentos', 'Horários Livres']
                on_text: root.handle_menu_selection('agendamentos', self.text)

            Spinner:
                id: prontuarios_spinner
                text: 'Prontuários'
                values: ['Prontuários']
                on_text: root.handle_menu_selection('prontuarios', self.text)

            Spinner:
                id: tratamentos_spinner
                text: 'Tratamentos'
                values: ['Tratamentos', 'Serviços de Tratamento', 'Planos de Custo', 'Orçamentos']
                on_text: root.handle_menu_selection('tratamentos', self.text)

            Spinner:
                id: financeiro_spinner
                text: 'Financeiro'
                values: ['Pagamentos', 'Despesas']
                on_text: root.handle_menu_selection('financeiro', self.text)

            Spinner:
                id: documentos_spinner
                text: 'Documentos'
                values: ['Documentos do Paciente', 'Consentimentos']
                on_text: root.handle_menu_selection('documentos', self.text)

            Spinner:
                id: relatorios_spinner
                text: 'Relatórios'
                values: ['Relatórios']
                on_text: root.handle_menu_selection('relatorios', self.text)
            
            Button:
                id: exit_button # Add an ID to the button
                background_color: root.error_color # Use root.error_color
                font_name: 'DejaVuSans' # Specify a unicode-friendly font
                halign: 'center'
                valign: 'middle'
                size_hint_x: None
                width: dp(120) # Make button wider
                on_press: app.root.current = 'login'
        
        # Spacer to fill the rest of the screen
        BoxLayout:
            orientation: 'vertical'
""")

class ClinicMenuScreen(Screen):
    primary_color = ListProperty([0.2, 0.6, 0.8, 1])
    text_color = ListProperty([0.1, 0.1, 0.1, 1])
    error_color = ListProperty([0.8, 0.2, 0.2, 1])
    exit_icon = StringProperty('❌')

    MENU_DEFAULTS = {
        'cadastros': 'Cadastros',
        'agendamentos': 'Agendamentos',
        'prontuarios': 'Prontuários',
        'tratamentos': 'Tratamentos',
        'financeiro': 'Financeiro',
        'documentos': 'Documentos',
        'relatorios': 'Relatórios',
    }

    def on_enter(self, *args):
        # Schedule the async task to run
        Clock.schedule_once(self._run_async_load_task, 0)
        # Reset spinners to default text when entering the screen
        for menu_name, default_text in self.MENU_DEFAULTS.items():
            spinner_id = f"{menu_name}_spinner"
            if spinner_id in self.ids:
                self.ids[spinner_id].text = default_text
        self.apply_theme_to_ui() # Apply theme when entering the screen

    def apply_theme_to_ui(self):
        # Update properties directly
        self.primary_color = api.global_primary_color
        self.text_color = api.global_text_color
        self.error_color = api.global_error_color
        self.exit_icon = theme_manager.get_icon_set().get('close', '')
        # Set the text of the exit button directly
        if 'exit_button' in self.ids:
            self.ids.exit_button.text = f"{self.exit_icon}\nSair"

    def _run_async_load_task(self, dt):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._load_clinic_name_async())
        finally:
            loop.close()

    def handle_menu_selection(self, menu_name, selection):
        print(f"handle_menu_selection called. menu_name: {menu_name}, selection: {selection}") # Debug print
        default_text = self.MENU_DEFAULTS.get(menu_name)
        
        if selection != default_text:
            print(f"Selection is different from default. Navigating to: {selection}") # Debug print
            # Reset the spinner text after a selection is made
            spinner_id = f"{menu_name}_spinner"
            Clock.schedule_once(lambda dt: self.reset_spinner_text(spinner_id, default_text), 0.2)

            # Navigation logic
            if selection == 'Usuários':
                self.manager.current = 'user_management'
            elif selection == 'Clínicas':
                self.manager.current = 'tenant_management'
            elif selection == 'Configurações':
                self.manager.current = 'settings_screen' # New navigation
            elif selection == 'Pacientes': # New navigation for Patients
                self.manager.current = 'patient_management'
            elif selection == 'Agendamentos': # New navigation for Appointments
                self.manager.current = 'appointment_management'
            elif selection == 'Orçamentos': # New navigation for Orcamentos
                self.manager.current = 'orcamento_management'
            elif selection == 'Pagamentos':
                self.manager.current = 'payment_management'
            elif selection == 'Despesas':
                self.manager.current = 'expense_management'
            elif selection == 'Responsáveis':
                self.manager.current = 'responsavel_management'
            elif selection == 'Serviços':
                self.manager.current = 'service_management'
            elif selection == 'Estoque':
                self.manager.current = 'stock_management'
            elif selection == 'Feriados':
                self.manager.current = 'holiday_management'
            elif selection == 'Permissões':
                self.manager.current = 'permission_management'
            elif selection == 'Horários Livres':
                self.manager.current = 'free_time_management'
            elif selection == 'Prontuários':
                self.manager.current = 'prontuario_management'
            elif selection == 'Tratamentos':
                self.manager.current = 'treatment_management'
            elif selection == 'Serviços de Tratamento':
                self.manager.current = 'treatment_service_management'
            elif selection == 'Planos de Custo':
                self.manager.current = 'cost_plan_management'
            elif selection == 'Documentos do Paciente':
                self.manager.current = 'document_management'
            elif selection == 'Consentimentos':
                self.manager.current = 'consent_management'
            elif selection == 'Relatórios':
                self.manager.current = 'report_management'
            else:
                print(f"Navegação não implementada para: {selection}")

    @mainthread
    def reset_spinner_text(self, spinner_id, text):
        if spinner_id in self.ids:
            self.ids[spinner_id].text = text

    async def _load_clinic_name_async(self):
        self.ids.clinic_name_label.text = 'Carregando nome da clínica...'
        try:
            if not api.global_default_tenant_id:
                self.update_clinic_name("Nenhuma clínica associada.")
                return
            headers = {"Authorization": f"Bearer {api.global_access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{api.BASE_URL}/tenants/{api.global_default_tenant_id}",
                    headers=headers
                )
                response.raise_for_status()
                tenant_data = response.json()
                self.update_clinic_name(tenant_data.get("nome", "Nome da Clínica Desconhecido"))
        except Exception as e:
            self.update_message(f"Erro ao carregar nome da clínica: {e}")
            self.update_clinic_name("Erro ao carregar nome.")

    @mainthread
    def update_clinic_name(self, name):
        self.ids.clinic_name_label.text = name

    @mainthread
    def update_message(self, message, color=(1,0,0,1)):
        print(f"Mensagem: {message}")
