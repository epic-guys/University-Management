from flask_roles import RoleManager
import flask_login
from flask import render_template, jsonify

"""
Questa funzione viene chiamata quando un utente non autorizzato tenta di accedere ad una pagina.
Restituisce una pagina HTML con un messaggio di errore.
"""
def view_unauthorized_callback():
    return render_template('unauthorized.html'), 403


"""
Questa funzione viene chiamata quando un utente non autorizzato tenta di accedere ad una risorsa API.
Restituisce un messaggio JSON con un messaggio di errore.
"""
def api_unauthorized_callback():
    return jsonify({'status': 'fail', 'data': {'message': 'User is not authorized'}}), 403


"""
Questa funzione viene chiamata per caricare l'utente corrente.
"""
def role_loader():
    return flask_login.current_user


"""
Questo oggetto viene utilizzato per gestire i ruoli.
"""
view_role_manager = RoleManager(
    role_loader=role_loader,
    default_unauthorized_callback=view_unauthorized_callback,
    other_decorator=flask_login.login_required
)

"""
Questo oggetto viene utilizzato per gestire i ruoli per le risorse API.
"""
api_role_manager = RoleManager(
    role_loader=role_loader,
    default_unauthorized_callback=api_unauthorized_callback,
    other_decorator=flask_login.login_required
)
