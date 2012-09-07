from flask import Flask



def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.from_object(config)

    from controllers import common
    app.register_blueprint(common.app)

    return app


def run_develop():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=51000)
