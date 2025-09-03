from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

class ExpenseManagementScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text='Tela de Gerenciamento de Despesas'))