import os

CLIENTS = {
    'demo_vinoteca': {
        'client_id': 'demo_vinoteca',
        'client_name': 'Demo Vinoteca Premium',
        'client_slug': 'demo_vinoteca',
        'logo_url': '/static/images/logo_demo_vinoteca.png',
        'whatsapp_number': '5491123456789',
        'ecommerce_url': 'https://www.demovinoteca.com.ar'
    }
}

def get_client_config(client_slug):
    """
    Retorna la configuración del cliente en base a su slug.
    """
    return CLIENTS.get(client_slug)
