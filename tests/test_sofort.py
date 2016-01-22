import unittest
import logging
import datetime
import ConfigParser

import sofort

if hasattr(unittest, 'mock'):
    from unittest.mock import MagicMock
else:
    from mock import MagicMock

class TestSofort(unittest.TestCase):
    def setUp(self):
        config = ConfigParser.ConfigParser()
        config.readfp(open('config.spree.ini'))

        username = config.get('sofort', 'user_id')
        password = config.get('sofort', 'api_key')
        project = config.get('sofort', 'project_id')

        self.client = sofort.Client(username, password, project)

    def test_defaults_init(self):
        c = sofort.Client('user', 'password', '123', test_field='test')
        self.assertEqual('user', c.config.user_id)
        self.assertEqual('password', c.config.api_key)
        self.assertEqual('123', c.config.project_id)
        self.assertEqual('test', c.config.test_field)
        self.assertEqual('EUR', c.config.currency_code)

        c = sofort.Client('user', 'password', '321', currency_code='USD')

        self.assertEqual('USD', c.config.currency_code)

    def test_pay(self):
        self.client._request_xml = MagicMock(return_value=TRANSACTION_RESPONSE)
        tran = self.client.payment(12.2,
            success_url = 'http://sli.tw1.ru/sofort/success.php?trn={}'.format(sofort.TRANSACTION_ID),
            abort_url = 'http://sli.tw1.ru/sofort/abort.php?trn={}'.format(sofort.TRANSACTION_ID),
            notification_urls={
                'default': 'http://sli.tw1.ru/sofort/notify.php?trn={}'.format(sofort.TRANSACTION_ID),
                'loss': 'http://sli.tw1.ru/sofort/notify.php?trn={}'.format(sofort.TRANSACTION_ID),
                'refund': 'http://sli.tw1.ru/sofort/notify.php?trn={}'.format(sofort.TRANSACTION_ID)
            },
            reasons=[
                'Invoice 0001 payment',
                sofort.TRANSACTION_ID
            ]
        )
        self.assertEqual('123456-123456-56A3BE0E-ACAB', tran.transaction)
        self.assertEqual('https://www.sofort.com/payment/go/136b2012718da0160fac20c2ec2f51100c90406e', tran.payment_url)

    def test_details_multiple_transaction_ids(self):
        self.client._request_xml = MagicMock(return_value=TRANSACTION_LIST_BY_IDS_RESPONSE)
        tran_id = [
            '123456-123456-56A29EC6-066A',
            '123456-123456-56A2A0C3-CA99'
        ]
        info = self.client.details(tran_id)
        self.assertEqual(2, len(info.transaction_details))
        for tran in info.transaction_details:
            self.assertTrue(tran.transaction in tran_id)

    def test_details_single_transaction_id(self):
        self.client._request_xml = MagicMock(return_value=TRANSACTION_BY_ID_RESPONSE)
        info = self.client.details('123456-123456-56A29EC6-066A')
        self.assertEqual(1, len(info.transaction_details))
        self.assertEqual('123456-123456-56A29EC6-066A', info.transaction_details.transaction)

TRANSACTION_RESPONSE = u"""<?xml version="1.0" encoding="UTF-8" ?>
<new_transaction>
    <transaction>123456-123456-56A3BE0E-ACAB</transaction>
    <payment_url>https://www.sofort.com/payment/go/136b2012718da0160fac20c2ec2f51100c90406e</payment_url>
</new_transaction>
"""

TRANSACTION_LIST_BY_IDS_RESPONSE = u"""<?xml version="1.0" encoding="UTF-8" ?>
<transactions>
    <transaction_details>
        <project_id>123456</project_id>
        <transaction>123456-123456-56A29EC6-066A</transaction>
        <test>1</test>
        <time>2016-01-22T22:28:14+01:00</time>
        <status>untraceable</status>
        <status_reason>sofort_bank_account_needed</status_reason>
        <status_modified>2016-01-22T22:28:14+01:00</status_modified>
        <payment_method>su</payment_method>
        <language_code>en</language_code>
        <amount>2.20</amount>
        <amount_refunded>0.00</amount_refunded>
        <currency_code>EUR</currency_code>
        <reasons>
            <reason>Testueberweisung</reason>
            <reason>123456-123456-56A29EC6-066A</reason>
        </reasons>
        <user_variables>
            <user_variable>test</user_variable>
        </user_variables>
        <sender>
            <holder>Warnecke Hans-Gerd</holder>
            <account_number>12345678</account_number>
            <bank_code>88888888</bank_code>
            <bank_name>Demo Bank</bank_name>
            <bic>SFRTDE20XXX</bic>
            <iban>DE52000000000012345678</iban>
            <country_code>DE</country_code>
        </sender>
        <recipient>
            <holder>My Company GmbH</holder>
            <account_number>0000000000</account_number>
            <bank_code>00000000</bank_code>
            <bank_name>Raiffeisenbank Oberteuringen</bank_name>
            <bic>AAAAAAAAAAA</bic>
            <iban>DE00000000000000000001</iban>
            <country_code>DE</country_code>
        </recipient>
        <email_customer />
        <phone_customer />
        <exchange_rate>1.0000</exchange_rate>
        <costs>
            <fees>0.00</fees>
            <currency_code>EUR</currency_code>
            <exchange_rate>1.0000</exchange_rate>
        </costs>
        <su>
            <consumer_protection>0</consumer_protection>
        </su>
        <status_history_items>
            <status_history_item>
                <status>untraceable</status>
                <status_reason>sofort_bank_account_needed</status_reason>
                <time>2016-01-22T22:28:14+01:00</time>
            </status_history_item>
        </status_history_items>
    </transaction_details>
    <transaction_details>
        <project_id>123456</project_id>
        <transaction>123456-123456-56A2A0C3-CA99</transaction>
        <test>1</test>
        <time>2016-01-22T22:36:47+01:00</time>
        <status>untraceable</status>
        <status_reason>sofort_bank_account_needed</status_reason>
        <status_modified>2016-01-22T22:36:47+01:00</status_modified>
        <payment_method>su</payment_method>
        <language_code>en</language_code>
        <amount>2.20</amount>
        <amount_refunded>0.00</amount_refunded>
        <currency_code>EUR</currency_code>
        <reasons>
            <reason>Testueberweisung</reason>
            <reason>123456-123456-56A2A0C3-CA99</reason>
        </reasons>
        <user_variables>
            <user_variable>test</user_variable>
        </user_variables>
        <sender>
            <holder>Musterman, Petra</holder>
            <account_number>2345678902</account_number>
            <bank_code>88888888</bank_code>
            <bank_name>Demo Bank</bank_name>
            <bic>SFRTDE20XXX</bic>
            <iban>DE86000000002345678902</iban>
            <country_code>DE</country_code>
        </sender>
        <recipient>
            <holder>My Company GmbH</holder>
            <account_number>0000000000</account_number>
            <bank_code>00000000</bank_code>
            <bank_name>Raiffeisenbank Oberteuringen</bank_name>
            <bic>AAAAAAAAAAA</bic>
            <iban>DE00000000000000000001</iban>
            <country_code>DE</country_code>
        </recipient>
        <email_customer />
        <phone_customer />
        <exchange_rate>1.0000</exchange_rate>
        <costs>
            <fees>0.00</fees>
            <currency_code>EUR</currency_code>
            <exchange_rate>1.0000</exchange_rate>
        </costs>
        <su>
            <consumer_protection>0</consumer_protection>
        </su>
        <status_history_items>
            <status_history_item>
                <status>untraceable</status>
                <status_reason>sofort_bank_account_needed</status_reason>
                <time>2016-01-22T22:36:47+01:00</time>
            </status_history_item>
        </status_history_items>
    </transaction_details>
</transactions>"""

TRANSACTION_BY_ID_RESPONSE = u"""<?xml version="1.0" encoding="UTF-8" ?>
<transactions>
    <transaction_details>
        <project_id>123456</project_id>
        <transaction>123456-123456-56A29EC6-066A</transaction>
        <test>1</test>
        <time>2016-01-22T22:28:14+01:00</time>
        <status>untraceable</status>
        <status_reason>sofort_bank_account_needed</status_reason>
        <status_modified>2016-01-22T22:28:14+01:00</status_modified>
        <payment_method>su</payment_method>
        <language_code>en</language_code>
        <amount>2.20</amount>
        <amount_refunded>0.00</amount_refunded>
        <currency_code>EUR</currency_code>
        <reasons>
            <reason>Testueberweisung</reason>
            <reason>123456-123456-56A29EC6-066A</reason>
        </reasons>
        <user_variables>
            <user_variable>test</user_variable>
        </user_variables>
        <sender>
            <holder>Warnecke Hans-Gerd</holder>
            <account_number>12345678</account_number>
            <bank_code>88888888</bank_code>
            <bank_name>Demo Bank</bank_name>
            <bic>SFRTDE20XXX</bic>
            <iban>DE52000000000012345678</iban>
            <country_code>DE</country_code>
        </sender>
        <recipient>
            <holder>My Company GmbH</holder>
            <account_number>0000000000</account_number>
            <bank_code>00000000</bank_code>
            <bank_name>Raiffeisenbank Oberteuringen</bank_name>
            <bic>AAAAAAAAAAA</bic>
            <iban>DE00000000000000000001</iban>
            <country_code>DE</country_code>
        </recipient>
        <email_customer />
        <phone_customer />
        <exchange_rate>1.0000</exchange_rate>
        <costs>
            <fees>0.00</fees>
            <currency_code>EUR</currency_code>
            <exchange_rate>1.0000</exchange_rate>
        </costs>
        <su>
            <consumer_protection>0</consumer_protection>
        </su>
        <status_history_items>
            <status_history_item>
                <status>untraceable</status>
                <status_reason>sofort_bank_account_needed</status_reason>
                <time>2016-01-22T22:28:14+01:00</time>
            </status_history_item>
        </status_history_items>
    </transaction_details>
</transactions>"""