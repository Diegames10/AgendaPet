from authlib.integrations.flask_client import OAuth


oauth = OAuth()


def init_oauth(app):

    oauth.init_app(app)

    # =====================================================
    # GOOGLE
    # =====================================================

    oauth.register(
        name="google",

        server_metadata_url=(
            "https://accounts.google.com/"
            ".well-known/openid-configuration"
        ),

        client_id=app.config.get(
            "GOOGLE_CLIENT_ID"
        ),

        client_secret=app.config.get(
            "GOOGLE_CLIENT_SECRET"
        ),

        client_kwargs={
            "scope": "openid email profile"
        }
    )

    # =====================================================
    # MICROSOFT
    # =====================================================

    oauth.register(
        name="microsoft",

        server_metadata_url=(
            "https://login.microsoftonline.com/"
            "consumers/v2.0/"
            ".well-known/openid-configuration"
        ),

        client_id=app.config.get(
            "MICROSOFT_CLIENT_ID"
        ),

        client_secret=app.config.get(
            "MICROSOFT_CLIENT_SECRET"
        ),

        
        client_kwargs={
            "scope": (
                "openid "
                "email "
                "profile "
                "User.Read"
            )
        }
    )