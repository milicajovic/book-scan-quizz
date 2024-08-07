from flask import render_template, current_app
import traceback


def forbidden_error(error):
    print(error)
    return render_template('errors/403.html'), 403


def not_found_error(error):
    return render_template('errors/404.html'), 404


def internal_error(error):
    # Log the error
    current_app.logger.error('An internal error occurred: %s', str(error))

    # Get the full traceback
    tb = traceback.format_exc()

    # Determine if we're in debug mode
    debug_mode = True #current_app.debug

    # Render the 500.html template with error details if in debug mode
    return render_template('errors/500.html', error={
        'message': str(error),
        'traceback': tb if debug_mode else None
    }), 500


def register_error_handlers(app):
    app.register_error_handler(403, forbidden_error)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)