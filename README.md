Flask-SubscriptionFlags
Adapted from Flask FeatureFlags
===================

This is a Flask extension that adds subscription-based flagging to your applications. This lets you turn parts of your site on or off based on a user's subscription.
This is modified from Flask FeatureFlags to handle company_id field of the flask_login current_user for looking up company subscriptions.

Docs
====

For similar documentation, please see: [https://flask-featureflags.readthedocs.org/en/latest/](https://flask-featureflags.readthedocs.org/en/latest/) 

Setup
=====

Adding the extension is simple:

    from flask import Flask
    from flask_featureflags import FeatureFlag

    app = Flask(__name__)

    feature_flags = FeatureFlag(app)

In your Flask app.config, create a ``FEATURE_FLAGS`` dictionary, and add any features you want as keys. Any UTF-8 string is a valid feature name.

For example, to have 'unfinished_feature' hidden in production but active in development:

    class ProductionConfig(Config):

        FEATURE_FLAGS = {
            'unfinished_feature' : False,
        }


    class DevelopmentConfig(Config):

        FEATURE_FLAGS = {
          'unfinished_feature' : True,
        }

**Note**: If a feature flag is used in code but not defined in ``FEATURE_FLAGS``, it's assumed to be off. Beware of typos.

If you want your app to throw an exception in dev when a feature flag is used in code but not defined, add this to your configuration:

    RAISE_ERROR_ON_MISSING_FEATURES = True

If ``app.debug=True``, this will throw a ``KeyError`` instead of silently ignoring the error.

Usage
=====

Controllers/Views
-----------------

If you want to protect an entire view:

    from flask import Flask
    import flask_featureflags as feature

    @feature.is_active_feature('unfinished_feature', redirect_to='/old/url')
    def index():
      # unfinished view code here

The redirect_to parameter is optional. If you don't specify, the url will return a 404.

If your needs are more complicated, you can check inside the view:

    from flask import Flask
    import flask_featureflags as feature

    def index():
        if feature.is_active('unfinished_feature') and some_other_condition():
            # do new stuff
        else:
            # do old stuff

Templates
---------

You can also check for features in Jinja template code:

    {% if 'unfinished_feature' is active_feature %}
        new behavior here!
    {% else %}
        old behavior...
    {% endif %}

Using other backends
====================

Want to store your flags somewhere other than the config file? There are third-party contrib modules for other backends.

Please see the documentation here: [https://flask-featureflags.readthedocs.org/en/latest/contrib.html](https://flask-featureflags.readthedocs.org/en/latest/contrib.html)

Feel free to add your own - see CONTRIBUTING.rst for help.

Customization
=============

If you need custom behavior, you can write your own feature flag handler.

A feature flag handler is simply a function that takes the feature name as input, and returns True (the feature is on) or False (the feature is off).

For example, if you want to enable features on Tuesdays:

    from datetime import date

    def is_it_tuesday(feature):
      return date.today().weekday() == 2:

You can register the handler like so:

    from flask import Flask
    from flask_featureflags import FeatureFlag

    app = Flask(__name__)

    feature_flags = FeatureFlag(app)
    feature_flags.add_handler(is_it_tuesday)

If you want to remove a handler for any reason, simply do:

    feature_flags.remove_handler(is_it_tuesday)

If you try to remove a handler that was never added, the code will silently ignore you.

To clear all handlers (thus effectively turning all features off):

    feature_flags.clear_handlers()

Clearing handlers is also useful when you want to remove the built-in behavior of checking the ``FEATURE_FLAGS`` dictionary.

To enable all features on Tuesdays, no matter what the ``FEATURE_FLAGS`` setting says:

    from flask import Flask
    from flask_featureflags import FeatureFlag

    app = Flask(__name__)

    feature_flags = FeatureFlag(app)
    feature_flags.clear_handlers()
    feature_flags.add_handler(is_it_tuesday)


Chaining multiple handlers
--------------------------

You can define multiple handlers. If any of them return true, the feature is considered on.

For example, if you want features to be enabled on Tuesdays *or* Fridays:

    feature_flags.add_handler(is_it_tuesday)
    feature_flags.add_handler(is_it_friday)


**Important:** the order of handlers matters!  The first handler to return True stops the chain. So given the above example,
if it's Tuesday, ``is_it_tuesday`` will return True and ``is_it_friday`` will not run.

You can override this behavior by raising the StopCheckingFeatureFlags exception in your custom handler:

    from flask_featureflags import StopCheckingFeatureFlags

    def run_only_on_tuesdays(feature):
      if date.today().weekday() == 2:
        return True
      else:
        raise StopCheckingFeatureFlags

If it isn't Tuesday, this will cause the chain to return False and any other handlers won't run.


Acknowledgements
================

A big thank you to LinkedIn for letting me opensource this, and for my coworkers for all their feedback on this project. You guys are great. :)

Questions?
==========

Feel free to ping me on twitter [@trustrachel](https://twitter.com/trustrachel) or on the [Github](https://github.com/trustrachel/Flask-FeatureFlags) project page.
