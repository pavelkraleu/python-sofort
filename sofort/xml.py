import datetime
import collections
from lxml import etree

def multipay(config):
    root = etree.Element('multipay')

    prime_mandatory = ['project_id', 'amount', 'currency_code',
                       'success_url', 'abort_url']
    prime_optional = ['interface_version', 'language_code', 'timeout',
                      'email_customer', 'phone_customer', 'timeout_url',
                      'success_link_redirect']
    prime_lists = {
        'user_variables': 'user_variable',
        'reasons': 'reason'
    }

    notification_addresses = {
        'notification_urls': 'notification_url',
        'notification_emails': 'notification_email'
    }

    for attr_name in prime_mandatory:
        etree.SubElement(root, attr_name).text = str(getattr(config, attr_name))

    for attr_name in prime_optional:
        value = getattr(config, attr_name, None)

        if value is None:
            continue

        etree.SubElement(root, attr_name).text = __serialize(value)

    for collection_name, item_name in prime_lists.items():
        if not config.has(collection_name):
            continue

        collection = etree.SubElement(root, collection_name)
        for value in getattr(config, collection_name):
            etree.SubElement(collection, item_name).text = value

    for collection_name, item_name in notification_addresses.items():
        if not config.has(collection_name):
            continue

        collection = etree.SubElement(root, collection_name)
        addresses = __compact_notification_addresses(getattr(config, collection_name))
        for notify_on, address in addresses.items():
            node = etree.SubElement(collection, item_name)
            node.text = address
            if notify_on != 'default':
                node.set('notify_on', notify_on)

    su = etree.SubElement(root, 'su')

    return etree.tostring(root)

def transaction_request_by_ids(ids):
    root = etree.Element('transaction_request')
    root.set('version', '2')
    for id in ids:
        etree.SubElement(root, 'transaction').text = id
    return etree.tostring(root)

def transaction_request_by_params(params):
    root = etree.Element('transaction_request')
    root.set('version', '2')
    for name, value in params.items():
        etree.SubElement(root, name).text = __serialize(value)
    return etree.tostring(root)

def __compact_notification_addresses(addresses):
    result = {}
    default = addresses.pop('default', None)

    for key, value in __reverse_group_dict(addresses).items():
        result[','.join(value)] = key

    if not default is None:
        result['default'] = default

    return result

def __reverse_group_dict(dictionary):
    result = collections.defaultdict(list)

    for key, value in dictionary.items():
        result[value].append(key)

    return result

def __serialize(value):
    if isinstance(value, bool):
        value = int(value)

    if isinstance(value, datetime.datetime):
        value = value.isoformat()

    if isinstance(value, int):
        value = str(value)

    return value