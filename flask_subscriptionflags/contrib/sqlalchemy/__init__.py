from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app
from flask_subscriptionflags import NoSubscriptionFlagFound, log
from flask_login import current_user


class SQLAlchemySubscriptionFlags(object):

  def __init__(self, db, model=None):
    if not model:
      model = self._make_model(db)
    self.model = model

  def __call__(self, subscription=None):
    if not current_app:
      log.warn("Got a request to check for {subscription} but we're outside the request context. Returning False".format(subscription=subscription))
      return False

    try:
      return self.model.check(subscription)
    except NoResultFound:
      raise NoSubscriptionFlagFound()

  def _make_model(self, db):

    class SubscriptionFlag(db.Model):
      id = Column(Integer, primary_key=True)
      company_id = Column(Integer, nullable=False)
      subscription = Column(String(255), nullable=False, unique=True)
      is_active = Column(Boolean, default=False)

      @classmethod
      def check(cls, subscription):
        r = cls.query.filter_by(company_id=current_user.company_id).filter_by(subscription=subscription).one()
        return r.is_active

    return SubscriptionFlag
