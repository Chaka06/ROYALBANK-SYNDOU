#!/usr/bin/env python
"""Script pour créer un superuser Django"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sphinx.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser(username=None, email=None, password=None):
    """Crée un superuser avec les paramètres fournis"""
    
    # Valeurs par défaut si non fournies
    if not username:
        username = 'admin'
    if not email:
        email = 'admin@royal.local'
    if not password:
        password = 'admin123'
    
    print("=== Création d'un superuser Django ===\n")
    print(f"Nom d'utilisateur: {username}")
    print(f"Email: {email}")
    print(f"Mot de passe: {'*' * len(password)}\n")
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        print(f"L'utilisateur '{username}' existe déjà.")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        if email:
            user.email = email
        user.save()
        print(f"✓ Mot de passe mis à jour pour '{username}' et droits de superuser activés.")
        return
    
    # Créer le superuser
    try:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✓ Superuser '{username}' créé avec succès!")
        print(f"  - Email: {email}")
        print(f"  - Accès admin: http://127.0.0.1:8000/admin/")
    except Exception as e:
        print(f"✗ Erreur lors de la création: {e}")

if __name__ == '__main__':
    # Accepter les paramètres en ligne de commande
    username = sys.argv[1] if len(sys.argv) > 1 else None
    email = sys.argv[2] if len(sys.argv) > 2 else None
    password = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_superuser(username, email, password)
