import time
import hmac
import hashlib

from aiohttp import web
import aiohttp_jinja2


class LoginView:
    @aiohttp_jinja2.template("login.html")
    async def login_get(self, req):
        return dict(authenticated=False, **req.query)

    async def login_post(self, req):
        post_data = await req.post()
        location = req.app.router["login_page"].url_for()
        if "username" not in post_data:
            loc = location.with_query({"error": "Username missing"})
            raise web.HTTPFound(location=loc)

        if "password" not in post_data:
            loc = location.with_query({"error": "Password missing"})
            raise web.HTTPFound(location=loc)

        authenticated = (post_data["username"] == req.app["username"]) and (
            post_data["password"] == req.app["password"]
        )
        if not authenticated:
            loc = location.with_query({"error": "Wrong Username or Passowrd"})
            raise web.HTTPFound(location=loc)

        resp = web.Response(
            status=302, headers={"Location": str(req.app.router["home"].url_for())}
        )
        now = time.time()
        resp.set_cookie(
            name="_tgindex_session",
            value=str(now),
            max_age=60 * req.app["SESSION_COOKIE_LIFETIME"],
        )
        digest = hmac.new(
            req.app["SECRET_KEY"].encode(), str(now).encode(), hashlib.sha256
        ).hexdigest()
        resp.set_cookie(
            name="_tgindex_secret",
            value=digest,
            max_age=60 * req.app["SESSION_COOKIE_LIFETIME"],
        )
        return resp
