"""Utilities for the paypal_express_checkout app."""
import urllib


def urlencode(data):
    for key, value in data.iteritems():
        data[key] = unicode(value).encode('utf-8')
    return urllib.urlencode(data)
