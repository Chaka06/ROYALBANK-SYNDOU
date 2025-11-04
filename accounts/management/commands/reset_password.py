from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Reset password for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to reset password')
        parser.add_argument('password', type=str, help='New password')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Mot de passe réinitialisé avec succès pour {username}'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'✗ Utilisateur "{username}" non trouvé')
            )

