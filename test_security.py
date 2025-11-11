# test_security.py - Créez ce fichier pour tester
import os
import subprocess

# ❌ Ce code devrait être détecté comme dangereux
password = "monpassword123"  # Secret hardcodé
result = eval("2 + 2")  # Fonction dangereuse
subprocess.call("ls -la", shell=True)  # Commande shell non sécurisée

print("Test sécurité")