"""
Ejecutor CLI Autónomo para Scripts de Automatización G.I.D.E.O.N.
Diseñado para ejecución en terminal, pipelines de CI/CD o integración en agentes de IA sin GUI.
"""

import sys
import os
import threading
import argparse

# Asegurar que el directorio raíz del script esté en el sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.config import cargar_configuracion
from automation.worker import crear_cuenta_individual
from automation.worker_ftth_ecommerce import ejecutar_worker_ftth_ecommerce
from automation.worker_ott import crear_cuenta_ott

def log_consola(mensaje: str):
    """Callback para volcar eventos de la automatización a la salida estándar."""
    print(f"[LOG] {mensaje}", flush=True)

def status_dummy(id_hilo, paso, inicio, estado):
    """Callback de estado de hilo."""
    pass

def kpi_dummy(exito=0, fallo=0):
    """Callback de KPIs de ejecución."""
    pass

def ejecutar_flujo_ftth_crm(headless=False):
    """Ejecuta el flujo FTTH en el CRM Evergent."""
    print("=" * 60)
    print("🚀 Iniciando Flujo FTTH CRM Evergent")
    print("=" * 60)
    sys_config = cargar_configuracion()
    cancel_event = threading.Event()

    config_cuenta = {
        "tipo_persona": "Persona natural",
        "ubicacion": "Caracas - Chacao",
        "plan_seleccionado": "Compra: 400 mbps + Gold",
        "aplicar_promocion": True,
        "modo_ejecucion": "completo"
    }

    resultado = crear_cuenta_individual(
        id_hilo=1,
        config_cuenta=config_cuenta,
        sys_config=sys_config,
        log_callback=log_consola,
        update_thread_status_callback=status_dummy,
        update_kpi_callback=kpi_dummy,
        cancel_event=cancel_event,
        headless=headless
    )
    print(f"\nResultado final: {resultado}")

def ejecutar_flujo_ecommerce(headless=False):
    """Ejecuta el flujo FTTH en la Tienda eCommerce Pública."""
    print("=" * 60)
    print("🚀 Iniciando Flujo FTTH eCommerce (Tienda Web)")
    print("=" * 60)
    sys_config = cargar_configuracion()
    cancel_event = threading.Event()

    config_cuenta = {
        "tipo_persona": "Persona natural",
        "plan_seleccionado": "Compra: 400 mbps + Gold",
        "ubicacion": "Caracas - Chacao",
        "cobertura_exacta": True
    }

    resultado = ejecutar_worker_ftth_ecommerce(
        id_hilo=1,
        config_cuenta=config_cuenta,
        sys_config=sys_config,
        log_callback=log_consola,
        update_thread_status_callback=status_dummy,
        update_kpi_callback=kpi_dummy,
        cancel_event=cancel_event,
        headless=headless
    )
    print(f"\nResultado final: {resultado}")

def ejecutar_flujo_ott(headless=False):
    """Ejecuta el flujo de suscripción OTT Streaming."""
    print("=" * 60)
    print("🚀 Iniciando Flujo OTT Streaming")
    print("=" * 60)
    sys_config = cargar_configuracion()
    cancel_event = threading.Event()

    config_cuenta = {
        "plan_ott": "Platino",
        "ubicacion": "Caracas - Chacao",
        "tipo_doc": "Venezuelan"
    }

    resultado = crear_cuenta_ott(
        id_hilo=1,
        config_cuenta=config_cuenta,
        sys_config=sys_config,
        log_callback=log_consola,
        update_thread_status_callback=status_dummy,
        update_kpi_callback=kpi_dummy,
        cancel_event=cancel_event,
        headless=headless
    )
    print(f"\nResultado final: {resultado}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutor CLI de Procesos de Automatización G.I.D.E.O.N.")
    parser.add_argument(
        "--flujo",
        choices=["ftth_crm", "ecommerce", "ott"],
        default="ftth_crm",
        help="Proceso a ejecutar (ftth_crm, ecommerce, ott)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar el navegador en modo sin cabeza (headless)"
    )
    args = parser.parse_args()

    if args.flujo == "ftth_crm":
        ejecutar_flujo_ftth_crm(headless=args.headless)
    elif args.flujo == "ecommerce":
        ejecutar_flujo_ecommerce(headless=args.headless)
    elif args.flujo == "ott":
        ejecutar_flujo_ott(headless=args.headless)
