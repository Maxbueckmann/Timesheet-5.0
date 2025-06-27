import os
import sys
import subprocess
import venv
import platform

def is_venv():
    return (hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def create_venv():
    print("Erstelle virtuelle Python-Umgebung...")
    venv.create('venv', with_pip=True)

def get_venv_paths():
    if platform.system() == "Windows":
        scripts_dir = os.path.join("venv", "Scripts")
        return {
            'python': os.path.join(scripts_dir, "python.exe"),
            'pip': os.path.join(scripts_dir, "pip.exe"),
            'activate': os.path.join(scripts_dir, "activate.bat")
        }
    else:
        bin_dir = os.path.join("venv", "bin")
        return {
            'python': os.path.join(bin_dir, "python"),
            'pip': os.path.join(bin_dir, "pip"),
            'activate': os.path.join(bin_dir, "activate")
        }

def run_command(cmd, shell=False):
    if platform.system() == "Windows" and not shell:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return subprocess.run(cmd, startupinfo=startupinfo, check=True)
    return subprocess.run(cmd, shell=shell, check=True)

def activate_venv():
    paths = get_venv_paths()
    if platform.system() == "Windows":
        activate_cmd = f'"{paths["activate"]}" && set'
    else:
        activate_cmd = f'source "{paths["activate"]}"'
    
    run_command(activate_cmd, shell=True)

def install_requirements():
    print("Installiere Abhängigkeiten...")
    paths = get_venv_paths()
    run_command([paths['pip'], "install", "-r", "requirements.txt"])

def init_database():
    print("Initialisiere Datenbank...")
    paths = get_venv_paths()
    run_command([paths['python'], "init_db.py"])

def start_app():
    print("Starte Anwendung...")
    paths = get_venv_paths()
    run_command([paths['python'], "app.py"])

def setup_and_run():
    try:
        if not os.path.exists('venv'):
            create_venv()
        
        activate_venv()
        install_requirements()
        init_database()
        start_app()
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen eines Befehls: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_and_run() 