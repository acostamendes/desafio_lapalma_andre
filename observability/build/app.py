import os
import logging
import time
from random import randint

from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry import metrics


APP_NAME = "dice-api"



def create_app() -> Flask:
    app = Flask(__name__)

    app.config["JSON_SORT_KEYS"] = False

    configure_logging(app)

    FlaskInstrumentor().instrument_app(app) # fazer a configuração da capturar das métricas (Response-time, Throughput, Error rate)


    # Prometheus com label padrão
    metrics = PrometheusMetrics(
        app,
        defaults={
            "app": APP_NAME
        }
    )

    metrics.info(
        "app_info",
        "Application info",
        version=os.getenv("APP_VERSION", "dev"),
    )

    register_routes(app)
    register_error_handlers(app)

    return app


def configure_logging(app: Flask) -> None:

    LoggingInstrumentor().instrument(set_logging_format=True) # caputar os trace_id e span_id
    

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app.logger.setLevel(logging.getLogger().level)


def register_routes(app: Flask) -> None:
    @app.route("/", methods=["GET"])
    def roll_dice():
        dice_value = randint(1, 6)
        app.logger.info(
            "Dice rolled",
            extra={"dice_value": dice_value, "app": APP_NAME},
        )
        return jsonify({"dice_value": dice_value})

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify(
            {
                "status": "ok",
                "app": APP_NAME,
                "version": os.getenv("APP_VERSION", "dev"),
            }
        ), 200

    @app.route("/fail", methods=["GET"])
    def fail():
        raise RuntimeError("Intentional failure")
    
    @app.route("/business", methods=["GET"])
    def business():
        return jsonify(
            {
                "status": "Unauthorized ",
                "message": "Unauthorized ",
            }
        ), 401
    
    @app.route("/latest", methods=["GET"])
    def latest():
        delay_seconds = randint(10, 1500) / 1000.0
        time.sleep(delay_seconds)
        
        app.logger.info(
            "Slow request processed", 
            extra={"delay_seconds": delay_seconds, "app": APP_NAME}
        )
        return jsonify(
            {
                "status": "success",
                "message": f"Simulated latency of {delay_seconds} seconds",
                "app": APP_NAME
            }
        ), 200
    

def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception("Unhandled exception")
        return jsonify(
            {
                "error": "internal_server_error",
                "app": APP_NAME,
                "message": str(error),
            }
        ), 500


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
    )
