http POST :8000/auth/register email=test@local.dev username=test password=secret
http -v :8000/auth/login email_or_username=test password=secret

http -v :8000/app/endpointA X-CSRF-Token:<csrf_from_cookie> "Cookie: access_token=<...>; csrf_token=<...>"  foo=bar
http -v :8000/apikeys name="Local Dev Key" "Cookie: access_token=<...>"
http -v POST :8000/v1/endpointA x-api-key:"vk_live_..." foo=bar
http :8000/me/usage "Cookie: access_token=<...>"
