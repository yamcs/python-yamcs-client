import requests
import urllib3
from google.protobuf.message import DecodeError
from yamcs import clientversion
from yamcs.api import exception_pb2
from yamcs.core.exceptions import ConnectionFailure, NotFound, Unauthorized, YamcsError


class Context:

    credentials = None

    def __init__(
        self,
        address,
        tls=False,
        credentials=None,
        user_agent=None,
        on_token_update=None,
        tls_verify=True,
    ):
        if ":" in address:
            self.address = address
        else:
            self.address = address + ":8090"

        if tls:
            self.url = f"https://{self.address}"
            self.auth_root = f"https://{self.address}/auth"
            self.api_root = f"https://{self.address}/api"
            self.ws_root = f"wss://{self.address}/api/websocket"
        else:
            self.url = f"http://{self.address}"
            self.auth_root = f"http://{self.address}/auth"
            self.api_root = f"http://{self.address}/api"
            self.ws_root = f"ws://{self.address}/api/websocket"

        self.session = requests.Session()
        if not tls_verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.session.verify = False

        if credentials:
            self.credentials = credentials.login(
                self.session, self.auth_root, on_token_update
            )

        if not user_agent:
            user_agent = "python-yamcs-client v" + clientversion.__version__
        self.session.headers.update({"User-Agent": user_agent})

    def get_proto(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Accept"] = "application/protobuf"
        kwargs.update({"headers": headers})
        return self.request("get", path, **kwargs)

    def put_proto(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/protobuf"
        headers["Accept"] = "application/protobuf"
        kwargs.update({"headers": headers})
        return self.request("put", path, **kwargs)

    def patch_proto(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/protobuf"
        headers["Accept"] = "application/protobuf"
        kwargs.update({"headers": headers})
        return self.request("patch", path, **kwargs)

    def post_proto(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/protobuf"
        headers["Accept"] = "application/protobuf"
        kwargs.update({"headers": headers})
        return self.request("post", path, **kwargs)

    def delete_proto(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["Accept"] = "application/protobuf"
        kwargs.update({"headers": headers})
        return self.request("delete", path, **kwargs)

    def request(self, method, path, **kwargs):
        path = f"{self.api_root}{path}"

        if self.credentials:
            self.credentials.before_request(self.session, self.auth_root)

        try:
            response = self.session.request(method, path, **kwargs)
        except requests.exceptions.SSLError as ssl_error:
            msg = f"Connection to {self.address} failed: {ssl_error}"
            raise ConnectionFailure(msg) from None
        except requests.exceptions.ConnectionError as e:
            # Requests gives us a horribly confusing error when a connection
            # is refused. Confirm and unwrap.
            if e.args and isinstance(e.args[0], urllib3.exceptions.MaxRetryError):
                # This is a string (which is still confusing ....)
                msg = e.args[0].args[0]
                if "refused" in msg:
                    msg = f"Connection to {self.address} failed: connection refused"
                    raise ConnectionFailure(msg) from None

            raise ConnectionFailure(f"Connection to {self.address} failed: {e}")

        if 200 <= response.status_code < 300:
            return response

        exception_message = exception_pb2.ExceptionMessage()
        try:
            exception_message.ParseFromString(response.content)
        except DecodeError:
            pass

        if response.status_code == 401:
            raise Unauthorized("401 Client Error: Unauthorized")
        elif response.status_code == 404:
            msg = getattr(exception_message, "msg")
            raise NotFound(f"404 Client Error: {msg}")
        elif 400 <= response.status_code < 500:
            msg = getattr(exception_message, "msg")
            raise YamcsError(f"{response.status_code} Client Error: {msg}")
        msg = getattr(exception_message, "msg")
        raise YamcsError(f"{response.status_code} Server Error: {msg}")
