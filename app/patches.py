# -*- coding: utf-8 -*-

from functools import wraps
from flask import abort, request, redirect, render_template, current_app, make_response
from flask_login import current_user


def forbidden(e):
    pass
