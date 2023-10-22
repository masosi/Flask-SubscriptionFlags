from flask import current_app
from flask_subscriptionflags import SUBSCRIPTION_FLAGS_CONFIG
from flask_subscriptionflags import NoSubscriptionFlagFound
from flask_subscriptionflags import log


class InlineSubscriptionFlag(object):
  def __call__(self, subscription):
    if not current_app:
      log.warn("Got a request to check for {subscription} but we're outside the request context. Returning False".format(subscription=subscription))
      return False

    subscription_cfg = "{prefix}_{subscription}".format(prefix=SUBSCRIPTION_FLAGS_CONFIG, subscription=subscription)

    try:
      return current_app.config[subscription_cfg]
    except KeyError:
      raise NoSubscriptionFlagFound()
