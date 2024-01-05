Title: A simple OpenID connect tutorial
Date: 2023-11-29 15:20
Tags: openid, openid-connect, oidc, http, keycloak
Category: python
Slug: openid-connect-tutorial
Author: Serafeim Papastefanos
Summary: A simple tutorial for OpenID connect using only HTTP requests


## Introduction

OpenID Connect is a simple identity layer on top of the OAuth 2.0 protocol. It allows clients to verify the identity of the user based on the authentication performed by an Authorization Server, as well as to obtain basic profile information about the user.

To learn more about the OpenID Connect protocol, you can read [how it works](https://openid.net/developers/how-connect-works/) or, even better
if you want to get a deeper understanding, you can read the [specification](https://openid.net/specs/openid-connect-core-1_0.html). 

The main difference between OpenID Connect and OAuth 2.0 is that OpenID Connect is an authentication protocol, while OAuth 2.0 is an authorization protocol; this means that OpenID Connect is used to verify the identity of the user, while OAuth 2.0 is used to verify
if the user has access to some resources (and if so also very his identity). 

In the following tutorial we'll try to authenticate a user using OpenID Connect without any external libraries so we can understand how the authentication works. We'll mainly work from the client side (i.e the web application) but we'll also be able to understand how the authentication server should work.

We'll use python and the requests library to make the HTTP requests however you can use any language you want, even command line with curl. To decode the JWT tokens we'll use the python cryptography library.

## Authentication flow

Some terminology

- user: The user that tries to log in to the client application
- client / client application: The application that the user tries to log in to; this is be a server side web application (however acts as a client for the OpenID Connect protocol)
- server / authorization server: The server that authenticates the user and returns an id token and optionally an access token. This is the server that implements the OpenID Connect protocol.

The authentication flow for OpenID connect is more or less the following:

- The user tries to "log in" on the client application
- The client application generates a URL that points to the authorization endpoint of the authorization server adding some parameters to that url query and *redirects* the user's browser there
- The user will get a log in screen and try to log in to the authorization server (or if he's already logged in he doesn't need to do anything)
- The authorization server redirects the user user back to the client application using a pre-agreed redirect url and passing it an authorization code
- The client application retrieves the authorization code through the redirect url (callback) and sends a request to the token endpoint of the authorization server passing the authorization code and the client secret
- The authorization server responds with an id token and optionally an access token
- The client application can now use the id token to read the user information and optionally the access token to access more resources (if available)

This is also explained in the section 1.3.  Overview of the [OpenID Connect specification](https://openid.net/specs/openid-connect-core-1_0.html#Overview).

## Authentication server

For the Authentication server for our tutorial we'll use [Keycloak](https://www.keycloak.org/), an open source Identity and Access Management server that implements OpenID Connect. I won't go into details on how to install and configure Keycloak,
the thing is that you need to setup a new client for your realm, enable authentication and add a client secret that will be used later.

Let's suppose that you have created a realm with the name `sample-realm` and your keycloak server is hosted on `https://kc.example.com`. This realm will have a *base* url with the value: `https://kc.example.gr/realms/sample-realm/`. This base url will be used to build other urls and will be stored as `OIDC_BASE_PROVIDER_URL`.

If you are using a different OpenID Connect server, you'll need to have the client id and client secret for your server and the token and authorization endpoints of your server.

## Automatic Discovery

Some OpenID Connect servers support automatic discovery of various information from authorization server (including the needed endpoints). This is called `WebFinger` and is described in detail in the [discovery specification](https://openid.net/specs/openid-connect-discovery-1_0.html). 

To use the automatic discovery you can send a GET request to the `/.well-known/openid-configuration` endpoint of the authorization server. In our keycloak case, the endpoint will be
`https://kc.example.gr/realms/sample-realm/.well-known/openid-configuration`. The response is a JSON object that contains the endpoints of the authorization server. For example, using python requests:

```python
finger = requests.get(
    settings.OIDC_BASE_PROVIDER_URL + ".well-known/openid-configuration"
).json()
```

This may return a lot of info but you are basically interested in the following:

```python
authorization_endpoint = finger["authorization_endpoint"]
token_endpoint = finger["token_endpoint"]
```

## The Authentication url

The first step of the authentication flow is to generate an authentication url and redirect the user to that. This means that when the user tries to log in to your app (by clicking a button or visiting some url etc) your web application will redirect the user to the authentication url.

The authentication url is the authorization endpoint of the authorization server with some parameters. The parameters are
(see 3.1.2.1.  Authentication Request of the [OpenID Connect specification](https://openid.net/specs/openid-connect-core-1_0.html) for more info if you want):

- `client_id`: The client id of your application. This will be used by the authorization server to identify your application
- `response_type`: The response type, in our case it's `code`. There are various response types that can be used however `code` is the one that should be used to initiate the *Authorization Code Flow* which is used for server-side applications (there are two more flows described in the sections 3.2 and 3.3 but they aren't used for traditional web applications).
- `scope`: The scope of the request, in our case it has to contain `openid` (it can also have more scopes but `openid` is the minimum)
- `redirect_uri`: The redirect uri of your application, in our case it's `http://localhost:8000/auth/callback`. This is the url that the authorization server will redirect the user after the authentication is complete. Please notice that the authentication server will only redirect the user to this url if it's in the list of allowed redirect uris of your application so make sure that you have added it to the list of allowed redirect uris.
- `state`: A random string that will be used to verify the response from the authorization server

So, to create the url from python we'll do something like: 


```python
from secrets import choice

def rndstr(size=16):
    # Pick a random string of size `size` from the alphabet
    alphabet = string.ascii_letters + string.digits
    return "".join([choice(alphabet) for _ in range(size)])

state = rndstr()

authorization_url = f"{authorization_endpoint}?client_id={settings.OIDC_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={settings.OIDC_REDIRECT_URIS[0]}&state={state}"
```

and the uri will be similar to:

```
https://kc.example.gr/realms/sample-realm/protocol/openid-connect/auth?client_id=sample-client&response_type=code&scope=openid&redirect_uri=http://localhost:8000/auth/callback&state=skldfj98sdfjio12
```


## User Authentication and redirect

Our application will now redirect the user to the authentication url. To test for this tutorial, we'll just copy paste the authentication url on our browser; the user will need to log in to the authorization server and then he'll be redirected back to our redirect_uri we provided with an authorization code. 

If we don't have anything running on localhost:8000 we'll get an error but we'll be able to see the redict URL on our browser's bar(!). So, we'll see something like `http://localhost:8000/auth/callback?state=KpT23RpwimxzXzHa&session_state=d54e38e1-8dfa-4658-ab4e-817ef6d4029b&code=b4938b28-12b4-463b-b2bc-ffc91b29e79e.d54e38e1-8dfa-4658-ab4e-817ef6d4029b.f9302f16-4765-4f2a-b7bc-381208ec71d6`. There are three parameters that are returned:

- `code`: The authorization code. This is the code that we'll use to get the id token.
- `state`: The state we provided earlier. We need to check that this is the same as the one we provided earlier to make sure that the response is valid.
- `session_state`: The session state. This is optional and can be used to check if the user is still logged in to the authorization server. We won't use this in our tutorial but if you want to learn more you can read the [session specification](https://openid.net/specs/openid-connect-session-1_0.html#CreatingUpdatingSessions).

```python
query = urlparse(next_url).query
query_dict = {k: v[0] for k, v in parse_qs(query).items()}
```

Now query_dict will contain all the parameters of the url as a dictionary. So we can check that we got the correct state:

```python
assert query_dict["state"] == state
```

## Getting the token

The next step is for our web application to retrieve 
the id token. For that it'll need to send a POST request to the token endpoint of the authorization server passing it the following parameters (see 3.1.3.1.  Token Request of the [OpenID Connect specification](https://openid.net/specs/openid-connect-core-1_0.html)):

- `client_id`: The client id of your application
- `client_secret`: The client secret of your application
- `grant_type`: The grant type, in our case it must be `authorization_code` .
- `code`: The authorization code we got from the authorization server
- `redirect_uri`: The redirect uri we used before

Here's the request we need to do. Please notice that this request will be done by your server-side application and not by the user's browser (so the client secret will be safe).

```python
resp = requests.post(
    token_endpoint,
    data={
        "client_id": settings.OIDC_CLIENT_ID,
        "client_secret": settings.OIDC_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": query_dict["code"],
        "redirect_uri": settings.OIDC_REDIRECT_URIS[0],
    },
)
```

The above response will return a bunch of parameters depending on the authentication server. The most important of these parameters are:

- `id_token`: The id token that contains information about the user. This is a JWT token and needs to be decoded and verified. We'll see how to do that later.
- `access_token`: The access token that can be used to access the user information.
- `token_type`: This has the `Bearer` value


## Decoding a JWT (JSON Web Token)

Although there are libraries  that can be used for decoding and verifying the token ([pyjwt](https://github.com/jpadilla/pyjwt)), we'll do it using only python (and [the cryptography library](https://github.com/pyca/cryptography/)) to understand how it works.

The JWT token is a string that contains three parts separated by a dot (`.`). The first part is the header, the second part is the payload and the third part is the signature. Each part is base64 encoded. To decode the token we can use the following function:

```python
def decode_jwt(jwt_token):
    header, payload, signature = jwt_token.split(".")

    decoded_header = base64.urlsafe_b64decode(header + "=" * (-len(header) % 4))
    decoded_payload = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))

    return json.loads(decoded_header), json.loads(decoded_payload)
```

The signature will be used later to verify the token.

The decoded header will be similar to this 

```python
{'alg': 'RS256',
'kid': 'NjVBRjY5MDlCMUIwNzU4RTA2QzZFMDQ4QzQ2MDAyQjVDNjk1RTM2Qg',
'typ': 'JWT'}
```

defining the type as JWT, the algorithm used to sing the JWT (RS256) and the public key that was used for the signing (we'll see later how we can retrieve that public key).

The decoded payload may have various fields depending on the authentication server. The most important fields are (see 
2.  ID Token of the [OpenID Connect specification](https://openid.net/specs/openid-connect-core-1_0.html#IDToken)):

- `iss`: The issuer of the token. This *must* be the same as the `OIDC_BASE_PROVIDER_URL` we defined earlier.
- `sub`: The subject of the token. This is more or less a unique id for that particular user that identified. Please notice that this usually is not the username of the user but some internal and unique key of that user.
- `aud`: The audience of the token. This *must* contain the `OIDC_CLIENT_ID` we defined earlier (i.e sample-client).
- `exp`: Expiration time of the JWT (in seconds since epoch)
- `iat`: The time the JWT was issued (in seconds since epoch)
- `auth_time`: The time the user was authenticated (in seconds since epoch)

For example the decoded payload may be something like:

```python
{
'aud': 'sample-client',
'auth_time': 1701168800,
'exp': 1701169100,
'iat': 1701168800,
'iss': 'https://kc.example.gr/realms/sample-realm',
'email': 'sample@example.com',
'preferred_username': 'sample',
'name': 'Sample',
'sub': 'e22f5a0d-e5ac-472d-b41b-06ecb9e4b3f6',
'typ': 'ID'
}
```

As you see the payload may contain some extra information about the user (like the email, name etc). This information is not guaranteed to be there and it depends on the authentication server. If the information you want is there you can
*verify the JWT* and finish the authentication flow here.

If not you can call the *userinfo endpoint* with the help of the `access_token` to get more information about the user.

## Retrieving the public key

The JWT token is signed by the authentication server using a private key. To verify the token we need to get the public key of the authentication server and use it to verify the signature of the token. 

There are multiple ways to retrieve the public key. The simplest is to get it directly from the authentication server (i.e keycloak has an option to export the RS256 public key as text from the realm settings - keys of your realm). Also, if you visit the base url we defined later you'll get a JSON with the public key of the server i.e

```python
base_info = requests.get(settings.OIDC_BASE_PROVIDER_URL).json()
public_key = base_info["public_key"]
```

I'm not sure if this is supported by other server beyond keycloak though.

Finally you can use the `jwks_uri` of the authentication server to get the public key. The jwks_uri would be returned from the WebFinger response we described earlier. There you'll see a JSON object named `keys` that contains JSON array with the list of the keys that the server has.

Each key will have the following fields:

- `kid`: The key id; this can be used to correlate the key with the one in the header of the JWT token
- `kty`: The key type; this should be `RSA`
- `alg`: The algorithm used to sign the JWT token; this should be `RS256`
- `use`: The use of the key; this should be `sig` (for signing)
- `n`: The modulus of the RSA key
- `e`: The exponent of the RSA key
- `x5c`: The x509 certificate chain of the key
- `x5t`: The x509 certificate SHA-1 thumbprint of the key
- `x5t#S256`: The x509 certificate SHA-256 thumbprint of the key


Although the public key isn't there it is rather straightforward to produce it either from the `n` and `e` or by reading the x509 certificate through the `x5c` field. 

Since we have now entered the cryptography fields we *need* to use the python cryptography library.

If we have the public key as a string we can use the following function to get the public key:

```python
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

public_key_str = "-----BEGIN PUBLIC KEY-----\n{0}\n-----END PUBLIC KEY-----".format(
    settings.OIDC_PUBLIC_KEY_STR
)
public_key = default_backend().load_pem_public_key(public_key_str.encode("utf-8"))
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print(public_key_pem.decode())
```

If we want to produce the public key using the `n` and `e` fields we can use the following function:


```python
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

n_bytes = base64.urlsafe_b64decode(key['n'] + "===")
n = int.from_bytes(n_bytes, 'big')

e_bytes = base64.urlsafe_b64decode(key['e'] + "===")
e = int.from_bytes(e_bytes, 'big')

public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())

public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print(public_key_pem.decode())
```

Or, to get the public key from the x509 certificate:

```python
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

certificate_str = key["x5c"][0]
decoded_certificate_str = base64.b64decode(certificate_str)
certificate = x509.load_der_x509_certificate(decoded_certificate_str, default_backend())
pub_key = certificate.public_key()
public_key_pem = pub_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print(public_key_pem.decode())
```

In all three above cases we should see the *same* public key. 

## Verifying the JWT token

Finally after retrieving the public key (using any of the above methods) we can verify the JWT token. 

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def verify_rs256_signature(jwt_token, pub_key):
    header, payload, signature = jwt_token.split(".")

    data = (header + "." + payload).encode("utf-8")

    decoded_signature = base64.urlsafe_b64decode(
        signature + "=" * (-len(signature) % 4)
    )

    try:
        pub_key.verify(
            signature, data, padding.PKCS1v15(), hashes.SHA256()
        )
        print("Signature verified")
    except Exception as e:
        print("Signature verification failed!", e)
```

And call it like:

```python
verify_rs256_signature(id_token, pub_key)
```

Where the id_token is the JWT token we got earlier from the token endpoint (i.e `id_token = resp.json()["id_token"]`) and the pub_key is the public key object.

Notice that beyond the signature verification we also need to verify that the token has valid values the `iss` and `aud` fields and also that it has valid times
(i.e not expired, not issued in the future etc). We can do that using the `exp`, `iat` and `auth_time` fields of the payload. These times are in UTC and in seconds since epoch. So we can do something like:

```python
import datetime

exp_datetime = datetime.datetime.utcfromtimestamp(decoded_payload['exp'])
```

to convert them to datetime objects and then compare them with the current time (in UTC). 

After the id token is verified we can safely use the information contained in the payload to authenticate the user. If this information is enough we can finish the authentication flow here. If not we can use the access token to call the userinfo endpoint.

## Calling the userinfo endpoint

Calling the userinfo endpoint is rather straightforward. We just need to send a GET request to the userinfo endpoint of the authentication server passing it the access token as a bearer token. The userinfo endpoint is returned from the WebFinger response we described earlier. 

```python
userinfo_endpoint = finger["userinfo_endpoint"]
resp = requests.get(
    userinfo_endpoint,
    headers={"Authorization": f"Bearer {access_token}"},
)
```

The resp may be also a JWT token so you'll need to decode and verify it as we did before. If it's not a JWT token it'll be a JSON object with the user information. Notice that it may not have more information than the id token so could avoid calling the userinfo endpoint. However this depends on the implementation so you probably should check it yourself.

## What about the authorization server?

What we would need to do if we wanted to implement the authorization server? It isn't so complicated:

We'll need to store the users with their passwords and the clients with their secrets and redirect urls. Then we'd need to implement the following urls:

- `/login`: A user facing login page. The client application will redirect the user's browser to that page. After the user connects the server would redirect the user's browser to the redirect url of the client passing it an authorization code.
- `/token`: The client would issue a post request to that url passing the authorization code and the client secret. The server now would return the id token encoded as a jwt token. The id token would contain the user information.

These two are more or less enough for a simple authentication server. Of course there are more things that can be implemented like the userinfo endpoint, the fingering etc but these are optional.

## Conclusion

In this tutorial we saw how we can authenticate a user using OpenID Connect without any external libraries. We saw how we can generate the authentication url, how we can get the authorization code and how we can use the authorization code to get the id token and access token. We also saw how we can decode and verify the id token, how we can retrieve the public key of the authorization server and finally and how we can use the access token to call the userinfo endpoint.

