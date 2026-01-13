from django.contrib.auth.models import User

from get_docker_secret import get_docker_secret


def create_sfu_admin():

	username = get_docker_secret('server_cred_username', 'admin')
	password = get_docker_secret('server_cred_pass', 'admin')

	if User.objects.filter(username=username).exists():
		print("user exists already")
		return True

	User.objects.create_superuser(username=username, password=password)

	return True

create_sfu_admin()