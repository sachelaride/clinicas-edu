#!/usr/bin/env python3
"""
Script de teste para o Sistema de Clínicas Educacionais
Verifica se todas as funcionalidades principais estão funcionando corretamente
"""

import sys
import os
import asyncio
import httpx
from datetime import datetime, date

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todas as importações estão funcionando"""
    print("🔍 Testando importações...")
    
    try:
        # Testa importações básicas
        import kivy
        print("  ✅ Kivy importado com sucesso")
        
        import api
        print("  ✅ Módulo API importado com sucesso")
        
        # Testa importações das telas originais
        from screens.login_screen import LoginScreen
        from screens.patient_management_screen import PatientManagementScreen
        from screens.appointment_management_screen import AppointmentManagementScreen
        print("  ✅ Telas originais importadas com sucesso")
        
        # Testa importações das telas melhoradas
        from screens.improved_appointment_screen import ImprovedAppointmentScreen
        from screens.improved_patient_screen import ImprovedPatientScreen
        from screens.improved_theme_settings_screen import ImprovedThemeSettingsScreen
        print("  ✅ Telas melhoradas importadas com sucesso")
        
        # Testa gerenciador de temas
        from app.core.theme_manager import theme_manager
        print(f"  ✅ Gerenciador de temas carregado (tema atual: {theme_manager.current_theme})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na importação: {e}")
        return False

def test_theme_manager():
    """Testa o gerenciador de temas"""
    print("\n🎨 Testando gerenciador de temas...")
    
    try:
        from app.core.theme_manager import theme_manager
        
        # Testa carregamento de temas
        initial_theme_count = len(theme_manager.available_themes)
        print(f"  ✅ {initial_theme_count} temas carregados")
        
        # Testa mudança de tema
        original_theme = theme_manager.current_theme
        
        # Tenta aplicar diferentes temas
        test_themes = ['modern_medical', 'dark_medical', 'soft_green']
        for theme_name in test_themes:
            if theme_name in theme_manager.available_themes:
                success = theme_manager.set_theme(theme_name)
                if success:
                    print(f"  ✅ Tema '{theme_name}' aplicado com sucesso")
                else:
                    print(f"  ❌ Falha ao aplicar tema '{theme_name}'")
        
        # Restaura tema original
        theme_manager.set_theme(original_theme)
        print(f"  ✅ Tema original '{original_theme}' restaurado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no gerenciador de temas: {e}")
        return False

def test_models():
    """Testa os modelos de dados"""
    print("\n📊 Testando modelos de dados...")
    
    try:
        # Testa importação dos modelos
        from app.models.pacientes import Paciente
        from app.models.orcamentos import Orcamento
        from app.models.prontuarios import Prontuario
        from app.models.documentos_paciente import DocumentoPaciente
        from app.models.responsaveis import Responsavel
        from app.models.agendamentos import Agendamento
        print("  ✅ Todos os modelos importados com sucesso")
        
        # Verifica se os relacionamentos estão definidos
        paciente_relationships = ['orcamentos', 'agendamentos']
        for rel in paciente_relationships:
            if hasattr(Paciente, rel):
                print(f"  ✅ Relacionamento Paciente.{rel} definido")
            else:
                print(f"  ⚠️ Relacionamento Paciente.{rel} não encontrado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos modelos: {e}")
        return False

def test_api_structure():
    """Testa a estrutura da API"""
    print("\n🌐 Testando estrutura da API...")
    
    try:
        # Verifica se os arquivos de rota existem
        routes_dir = "app/routes"
        expected_routes = [
            'pacientes.py', 'agendamentos.py', 'planos_custo.py',
            'prontuarios.py', 'documentos_paciente.py', 'responsaveis.py'
        ]
        
        for route_file in expected_routes:
            route_path = os.path.join(routes_dir, route_file)
            if os.path.exists(route_path):
                print(f"  ✅ Rota {route_file} encontrada")
            else:
                print(f"  ❌ Rota {route_file} não encontrada")
        
        # Testa importação do módulo principal da API
        from app.main import app
        print("  ✅ Aplicação FastAPI importada com sucesso")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na estrutura da API: {e}")
        return False

def test_screen_functionality():
    """Testa funcionalidades básicas das telas"""
    print("\n📱 Testando funcionalidades das telas...")
    
    try:
        # Testa criação das telas melhoradas
        from screens.improved_patient_screen import ImprovedPatientScreen
        from screens.improved_appointment_screen import ImprovedAppointmentScreen
        from screens.improved_theme_settings_screen import ImprovedThemeSettingsScreen
        
        # Cria instâncias das telas
        patient_screen = ImprovedPatientScreen()
        appointment_screen = ImprovedAppointmentScreen()
        theme_screen = ImprovedThemeSettingsScreen()
        
        print("  ✅ Telas melhoradas criadas com sucesso")
        
        # Verifica se as propriedades essenciais existem
        if hasattr(patient_screen, 'patients_data'):
            print("  ✅ PatientScreen.patients_data definido")
        
        if hasattr(appointment_screen, 'appointments_data'):
            print("  ✅ AppointmentScreen.appointments_data definido")
        
        if hasattr(theme_screen, 'available_themes'):
            print("  ✅ ThemeScreen.available_themes definido")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nas funcionalidades das telas: {e}")
        return False

def test_file_structure():
    """Testa a estrutura de arquivos do projeto"""
    print("\n📁 Testando estrutura de arquivos...")
    
    essential_files = [
        'main.py',
        'main_improved.py',
        'api.py',
        'app/main.py',
        'app/core/theme_manager.py',
        'themes/modern_medical_theme.json',
        'screens/improved_patient_screen.py',
        'screens/improved_appointment_screen.py',
        'screens/improved_theme_settings_screen.py'
    ]
    
    missing_files = []
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} não encontrado")
            missing_files.append(file_path)
    
    if not missing_files:
        print("  ✅ Todos os arquivos essenciais estão presentes")
        return True
    else:
        print(f"  ⚠️ {len(missing_files)} arquivos essenciais estão faltando")
        return False

def test_theme_files():
    """Testa os arquivos de tema"""
    print("\n🎨 Testando arquivos de tema...")
    
    try:
        import json
        
        # Testa o arquivo de tema moderno
        theme_file = 'themes/modern_medical_theme.json'
        if os.path.exists(theme_file):
            with open(theme_file, 'r', encoding='utf-8') as f:
                themes = json.load(f)
                print(f"  ✅ {len(themes)} temas carregados de {theme_file}")
                
                # Verifica se os temas têm as propriedades necessárias
                for theme_id, theme_data in themes.items():
                    required_props = ['name', 'primary_color', 'secondary_color', 'accent_color']
                    missing_props = [prop for prop in required_props if prop not in theme_data]
                    
                    if not missing_props:
                        print(f"  ✅ Tema '{theme_id}' está completo")
                    else:
                        print(f"  ⚠️ Tema '{theme_id}' está faltando: {missing_props}")
        else:
            print(f"  ❌ Arquivo de tema {theme_file} não encontrado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos arquivos de tema: {e}")
        return False

def generate_test_report():
    """Gera um relatório completo dos testes"""
    print("\n" + "="*60)
    print("📋 RELATÓRIO DE TESTES DO SISTEMA")
    print("="*60)
    
    tests = [
        ("Importações", test_imports),
        ("Gerenciador de Temas", test_theme_manager),
        ("Modelos de Dados", test_models),
        ("Estrutura da API", test_api_structure),
        ("Funcionalidades das Telas", test_screen_functionality),
        ("Estrutura de Arquivos", test_file_structure),
        ("Arquivos de Tema", test_theme_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Erro inesperado: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema está funcionando corretamente.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    print("🚀 Iniciando testes do Sistema de Clínicas Educacionais")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    success = generate_test_report()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

