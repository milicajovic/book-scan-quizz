from flask import Request, redirect
from werkzeug.wrappers import Response
from urllib.parse import urljoin

PRIMARY_DOMAIN = 'ai-quizzer.com'


def redirect_middleware(app):
    def middleware(environ, start_response):
        request = Request(environ)

        # Only apply redirects if running on Cloud Run
        if 'X-Forwarded-Proto' in request.headers:
            original_scheme = request.headers.get('X-Forwarded-Proto', 'http')
            host = request.headers.get('Host', '')

            # Check if we need to redirect
            if original_scheme != 'https' or host != PRIMARY_DOMAIN:
                # Construct the new URL
                new_url = urljoin(f'https://{PRIMARY_DOMAIN}', request.full_path)

                # Perform the redirect
                response = redirect(new_url, code=301)
                return response(environ, start_response)

        # If no redirect is needed, pass through to the main app
        return app(environ, start_response)

    return middleware