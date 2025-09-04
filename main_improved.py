from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

# Import your screens here
from screens.login_screen import LoginScreen
from screens.clinic_menu_screen import ClinicMenuScreen
from screens.user_management_screen import UserManagementScreen
from screens.tenant_management_screen import TenantManagementScreen
from screens.settings_screen import ThemeSettingsScreen
from screens.patient_management_screen import PatientManagementScreen
from screens.prontuario_management_screen import ProntuarioManagementScreen
from screens.appointment_management_screen import AppointmentManagementScreen
from screens.orcamento_management_screen import OrcamentoManagementScreen
from screens.document_management_screen import DocumentManagementScreen
from screens.payment_management_screen import PaymentManagementScreen
from screens.expense_management_screen import ExpenseManagementScreen
from screens.responsavel_management_screen import ResponsavelManagementScreen
from screens.service_management_screen import ServiceManagementScreen
from screens.stock_management_screen import StockManagementScreen
from screens.holiday_management_screen import HolidayManagementScreen
from screens.permission_management_screen import PermissionManagementScreen
from screens.free_time_management_screen import FreeTimeManagementScreen
from screens.treatment_management_screen import TreatmentManagementScreen
from screens.treatment_service_management_screen import TreatmentServiceManagementScreen
from screens.cost_plan_management_screen import CostPlanManagementScreen
from screens.consent_management_screen import ConsentManagementScreen
from screens.report_management_screen import ReportManagementScreen

# Import improved screens
from screens.improved_appointment_screen import ImprovedAppointmentScreen
from screens.improved_patient_screen import ImprovedPatientScreen
from screens.improved_theme_settings_screen import ImprovedThemeSettingsScreen

# Import theme manager
from app.core.theme_manager import theme_manager

class ClinicApp(App):
    def build(self):
        Window.maximize() # Maximize the window
        
        # Apply the default theme
        theme_manager.set_theme('dark_medical')
        
        sm = ScreenManager()
        
        # Original screens
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ClinicMenuScreen(name='clinic_menu'))
        sm.add_widget(UserManagementScreen(name='user_management'))
        sm.add_widget(TenantManagementScreen(name='tenant_management'))
        sm.add_widget(ThemeSettingsScreen(name='settings_screen'))
        sm.add_widget(PatientManagementScreen(name='patient_management'))
        sm.add_widget(ProntuarioManagementScreen(name='prontuario_management'))
        sm.add_widget(AppointmentManagementScreen(name='appointment_management'))
        sm.add_widget(OrcamentoManagementScreen(name='orcamento_management'))
        sm.add_widget(DocumentManagementScreen(name='document_management'))
        sm.add_widget(PaymentManagementScreen(name='payment_management'))
        sm.add_widget(ExpenseManagementScreen(name='expense_management'))
        sm.add_widget(ResponsavelManagementScreen(name='responsavel_management'))
        sm.add_widget(ServiceManagementScreen(name='service_management'))
        sm.add_widget(StockManagementScreen(name='stock_management'))
        sm.add_widget(HolidayManagementScreen(name='holiday_management'))
        sm.add_widget(PermissionManagementScreen(name='permission_management'))
        sm.add_widget(FreeTimeManagementScreen(name='free_time_management'))
        sm.add_widget(TreatmentManagementScreen(name='treatment_management'))
        sm.add_widget(TreatmentServiceManagementScreen(name='treatment_service_management'))
        sm.add_widget(CostPlanManagementScreen(name='cost_plan_management'))
        sm.add_widget(ConsentManagementScreen(name='consent_management'))
        sm.add_widget(ReportManagementScreen(name='report_management'))
        
        # Improved screens
        sm.add_widget(ImprovedAppointmentScreen(name='improved_appointment_management'))
        sm.add_widget(ImprovedPatientScreen(name='improved_patient_management'))
        sm.add_widget(ImprovedThemeSettingsScreen(name='improved_theme_settings'))
        
        return sm

if __name__ == '__main__':
    ClinicApp().run()

