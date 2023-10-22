"""
(c) 2023 Tom Nicolosi.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

masosi-1

"""

from functools import wraps
import logging

from flask import abort, current_app, url_for
from flask import redirect as _redirect
from flask.signals import Namespace

__version__ = '0.1'

log = logging.getLogger('flask-subscriptionflags')

RAISE_ERROR_ON_MISSING_SUBSCRIPTIONS = 'RAISE_ERROR_ON_MISSING_SUBSCRIPTIONS'
SUBSCRIPTION_FLAGS_CONFIG = 'SUBSCRIPTION_FLAGS'

EXTENSION_NAME = "SubscriptionFlags"


class StopCheckingSubscriptionFlags(Exception):
  """ Raise this inside of a subscription flag handler to immediately return False and stop any further handers from running """
  pass


class NoSubscriptionFlagFound(Exception):
  """ Raise this when the subscription flag does not exist. """
  pass


_ns = Namespace()
missing_subscription = _ns.signal('missing-subscription')


def AppConfigFlagHandler(company_id=None, subscription=None):
  """ This is the default handler. It checks for subscription flags in the current app's configuration.

  For example, to have 'feature_subscription' hidden in production but active in development:

  config.py

  class ProductionConfig(Config):

    SUBSCRIPTION_FLAGS = {
      'feature_subscription' : False,
    }


  class DevelopmentConfig(Config):

    SUBSCRIPTION_FLAGS = {
      'feature_subscription' : True,
    }

  """
  if not current_app:
    log.warn("Got a request to check for {subscription} but we're outside the request context. Returning False".format(subscription=subscription))
    return False

  try:
    return current_app.config[SUBSCRIPTION_FLAGS_CONFIG][subscription]
  except (AttributeError, KeyError):
    raise NoSubscriptionFlagFound()


class SubscriptionFlag(object):

  JINJA_TEST_NAME = 'active_subscription'

  def __init__(self, app=None):
    if app is not None:
      self.init_app(app)

    # The default out-of-the-box handler looks up subscriptions in Flask's app config.
    self.handlers = [AppConfigFlagHandler]

  def init_app(self, app):
    """ Add ourselves into the app config and setup, and add a jinja function test """

    app.config.setdefault(SUBSCRIPTION_FLAGS_CONFIG, {})
    app.config.setdefault(RAISE_ERROR_ON_MISSING_SUBSCRIPTIONS, False)

    if hasattr(app, "add_template_global"):
      # flask 0.10 and higher has a proper hook
      app.add_template_global(self.check, name=self.JINJA_TEST_NAME)

    if not hasattr(app, 'extensions'):
      app.extensions = {}
    app.extensions[EXTENSION_NAME] = self

  def clear_handlers(self):
    """ Clear all handlers. This effectively turns every subscription off."""
    self.handlers = []

  def add_handler(self, function):
    """ Add a new handler to the end of the chain of handlers. """
    self.handlers.append(function)

  def remove_handler(self, function):
    """ Remove a handler from the chain of handlers.  """
    try:
      self.handlers.remove(function)
    except ValueError:  # handler wasn't in the list, pretend we don't notice
      pass

  def check(self, company_id, subscription):
    """ Loop through all our subscription flag checkers and return true if any of them are true.

    The order of handlers matters - we will immediately return True if any handler returns true.

    If you want to a handler to return False and stop the chain, raise the StopCheckingSubscriptionFlags exception."""
    found = False
    for handler in self.handlers:
      try:
        if handler(company_id, subscription):
          return True
      except StopCheckingSubscriptionFlags:
        return False
      except NoSubscriptionFlagFound:
        pass
      else:
        found = True

    if not found:
      message = "No subscription flag defined for {subscription}".format(subscription=subscription)
      if current_app.debug and current_app.config.get(RAISE_ERROR_ON_MISSING_SUBSCRIPTIONS, False):
        raise KeyError(message)
      else:
        log.info(message)
        missing_subscription.send(self, subscription=subscription)

    return False


def is_active(company_id, subscription):
  """ Check if a subscription is active """

  if current_app:
    subscription_flagger = current_app.extensions.get(EXTENSION_NAME)
    if subscription_flagger:
      return subscription_flagger.check(company_id, subscription)
    else:
      raise AssertionError("Oops. This application doesn't have the Flask-SubscriptionFlag extention installed.")

  else:
    log.warn("Got a request to check for {subscription} but we're running outside the request context. Check your setup. Returning False".format(subscription=subscription))
    return False


def is_active_subscription(company_id, subscription, redirect_to=None, redirect=None):
  """
  Decorator for Flask views. If a subscription is off, it can either return a 404 or redirect to a URL if you'd rather.
  """
  def _is_active_subscription(func):
    @wraps(func)
    def wrapped(*args, **kwargs):

      if not is_active(company_id, subscription):
        url = redirect_to
        if redirect:
          url = url_for(redirect)

        if url:
          log.info('Subscription {subscription} is off, redirecting to {url}'.format(subscription=subscription, url=url))
          return _redirect(url, code=302)
        else:
          log.info('Subscription {subscription} is off, aborting request'.format(subscription=subscription))
          abort(404)

      return func(*args, **kwargs)
    return wrapped
  return _is_active_subscription


# Silence that annoying No handlers could be found for logger "flask-subscriptionflags"
class NullHandler(logging.Handler):
  def emit(self, record):
    pass


log.addHandler(NullHandler())
