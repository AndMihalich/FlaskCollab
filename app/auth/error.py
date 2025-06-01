from flask import render_template, request, jsonify
from . import auth 

def error_handler(e):
    return_json = request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html
    match e.code:
        case 404:
            if return_json:
                response = jsonify({'error': 'not found'})
                response.status_code=404
                return response
            return render_template("error.html", errname="This page does not exist", errcode=e.code), 404
        case 500:
            if return_json:
                response = jsonify({'error': 'internal server error'})
                response.status_code=500
                return response
            return render_template("error.html", errname="Error 505", errcode=e.code), 500
    return render_template("error.html", errname=str(e), errcode=e.code), e.code


@auth.app_errorhandler(404)
def err404(e):
    return error_handler(e)

@auth.app_errorhandler(401)
def err401(e):
    return error_handler(e)


@auth.app_errorhandler(500)
def err500(e):
    return error_handler(e)

