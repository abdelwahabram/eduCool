from django.conf import settings

from rest_framework.response import Response

from rest_framework.exceptions import AuthenticationFailed

# we deliver fresh cookies baked with fun either raw or stuffed with tokens
# check the menu below or scan the qr code 24/7

# the old classic programming cookie pun ain't totally cringe sometimes, anyway


def set_access_cookie(response, token):

	key = settings.SIMPLE_JWT["AUTH_COOKIE_ACCESS"]

	max_age = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]

	set_token_cookie(response, key, token, max_age)


def set_refresh_cookie(response, token):

	key = settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"]

	max_age = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

	path = settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_PATH"]

	set_token_cookie(response, key, token, max_age, path)


def set_token_cookie(response, key, value, max_age, path = "/"):

	domain = settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"]

	secure = settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"]

	httponly = settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"]

	samesite = settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]

	response.set_cookie(key=key, value=value, max_age=max_age, path=path, domain=domain, secure=secure, httponly=httponly, samesite=samesite)


def scan_refresh_cookie(request):

	key = settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"]

	refresh_token = request.COOKIES.get(key)

	if not refresh_token:
		
		raise AuthenticationFailed(detail="invalid token")

	return refresh_token


def remove_cookie(response) -> None:

	domain = settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"]

	samesite = settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]

	path = settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_PATH"]

	access_key = settings.SIMPLE_JWT["AUTH_COOKIE_ACCESS"]

	refresh_key = settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"]


	response.delete_cookie(key=access_key, domain=domain, samesite=samesite)

	response.delete_cookie(key=refresh_key, path=path, domain=domain, samesite=samesite)


def have_cookies(response) -> bool:

	access_key = settings.SIMPLE_JWT["AUTH_COOKIE_ACCESS"]

	refresh_key = settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"]

	if response.cookies.get(access_key) and response.cookies.get(access_key).value:
		return True

	if response.cookies.get(refresh_key) and response.cookies.get(refresh_key).value:
		return True

	return False

# all of these functions are wrappers for the Response object set and delete cookies, it extracts stored values from the settings and pass it
# for reference, the dj httpresponse object cookie setter is documented here: 
#https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.HttpResponse.set_cookie

# also we need to use type hints for functions here
# tech_debt += 1