# Copyright (C) 2021-2022 Wind River Systems, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from flask import request
from flask_restx._http import HTTPStatus
from werkzeug.exceptions import (
    BadRequest,
    MethodNotAllowed,
    NotFound,
    InternalServerError,
    HTTPException,
    Conflict,
)


from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class BadRequestException(BadRequest):
    def __init__(self, desc=None, resp=None):
        super().__init__(description=desc, response=resp)


class NotFoundException(NotFound):
    def __init__(self, desc=None, resp=None):
        super().__init__(description=desc, response=resp)

class ConflictException(Conflict):
    def __init__(self, desc=None, resp=None):
        super().__init__(description=desc, response=resp)

class ProblemDetails():
    def __init__(self, code: int, detail: str,
                 title=None, instance=None
                 ) -> None:
        self.status = code
        self.detail = detail
        self.type = request.path
        self.title = title if title is not None else self.getTitle(code)
        self.instance = instance if instance is not None else []

    def getTitle(self, code):
        return HTTPStatus(code).phrase

    def serialize(self):
        details = {}
        for key in dir(self):
            if key == 'ns' or key.startswith('__') or \
                    callable(getattr(self, key)):
                continue
            else:
                details[key] = getattr(self, key)
        return details


def configure_exception(app):

    @app.errorhandler(HTTPException)
    def default_error_handler(error):
        '''Default error handler'''
        status_code = getattr(error, 'code', 500)
        problem = ProblemDetails(status_code, str(error))
        return problem.serialize(), status_code

    @app.errorhandler(NotFound)
    def handle_notfound(error):
        '''notfound handler'''
        problem = ProblemDetails(404, str(error))
        return problem.serialize(), 404

    @app.errorhandler(BadRequestException)
    def handle_badrequest_exception(error):
        '''Return a custom message and 400 status code'''
        type(error)
        problem = ProblemDetails(400, str(error))
        return problem.serialize(), 400

    @app.errorhandler(NotFoundException)
    def handle_notfound_exception(error):
        '''Return a custom message and 404 status code'''
        problem = ProblemDetails(404, str(error))
        return problem.serialize(), 404

    @app.errorhandler(ConflictException)
    def handle_conflict_exception(error):
        '''Return a custom message and 409 status code'''
        problem = ProblemDetails(409, str(error))
        return problem.serialize(), 409

    @app.errorhandler(MethodNotAllowed)
    def handle_methodnotallowed_exception(error):
        '''Return a custom message and 405 status code'''
        problem = ProblemDetails(405, "Method not allowed")
        return problem.serialize(), 405

    @app.errorhandler(InternalServerError)
    def handle_internalservererror_exception(error):
        '''Return a custom message and 500 status code'''
        problem = ProblemDetails(500, "Internal Server Error")
        return problem.serialize(), 500

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        '''Return a custom message and 500 status code'''
        problem = ProblemDetails(500, "Internal Server Error")
        return problem.serialize(), 500
