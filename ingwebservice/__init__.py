# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime
import random
import re
from requests import Session
from unidecode import unidecode
import zeep
from zeep.client import Client
from zeep.transports import Transport

from .utils import purepolish, cleanaddress

class WSClient(object):
    endpoint = 'https://ws.ingbusinessonline.pl/ing-ccs/cdc00101?wsdl'
    cert = None
    ca_cert = None
    key = None
    company = ''
    username = ''
    timeout = 300

    def __init__(self, *args, **kwargs):
        self.cert = kwargs.get('cert', self.cert)
        self.ca_cert = kwargs.get('ca_cert', self.ca_cert)
        self.key = kwargs.get('key', self.key)
        self.company = kwargs.get('company', self.company)
        self.username = kwargs.get('username', self.username)
        self.timeout = kwargs.get('timeout', self.timeout)
        session = Session()
        if self.cert and self.key and self.ca_cert:
            session.cert = (self.cert, self.key)
            session.verify = self.ca_cert
        elif self.cert or self.key or self.ca_cert:
            raise ValueError("Must provide cert, ca_cert and key")
        self.client = Client(
            self.endpoint,
            transport=Transport(session=session, timeout=self.timeout))

    def get_headers(self):
        hdr = self.client.get_element('ns21:CcsHeader')
        data = {
            'FinInstID': 'INGBankŚląski',
            'PartnerID': self.company,
            'PassID': self.username,
            'ProdID': {
                'manufacturer': 'zeep',
                'ver': zeep.__version__,
                'langVer': 'en',
                },
            'Version': 2,
            'Revision': 2,
            }
        return hdr(**data)

    def get_msg_id(self):
        prefix = 'REQ'
        rnd = ''.join([random.choice('123456789ABCDEFGHJKLMNQRSTUVWXYZ') for i in range(16)])
        return '%s%s' % (prefix, rnd)

    def get_history(self, account_number, start_date, end_date):
        method = self.client.service.GetAccountReport
        doctype = self.client.get_type('ns1:GetAccountReportRequestType')
        data = {
            'MsgId': {'Id': self.get_msg_id()},
            'AcctRptQryDef': {
                'AcctRptCrit': {
                    'NewCrit': {
                        'SchCrit': {
                            'AcctId': {
                                'EQ': {
                                    'IBAN': account_number,
                                    }
                                },
                            'AcctRptValDt': {
                                'DtSch': {
                                    'FrDt': start_date,
                                    'ToDt': end_date,
                                    },
                                },
                            }
                        }
                    }
                }
            }
        document = doctype({'GetAcctRpt': data})
        resp = method(document['Document'], _soapheaders=[self.get_headers()])
        return History(resp.Rpt)

    def transfer_domestic(self, account_number, transfers, initiator=''):
        method = self.client.service.DomesticTransfer
        doctype = self.client.get_type('ns1:TransferRequestType')
        _country = re.compile(r'^[A-Z]{2}')
        _charfilter = re.compile(r'[^A-Za-z0-9/\-+()/\']')
        dmstc_from_acc = _country.sub('', account_number)
        now = datetime.now()
        to_send = []
        for txf in transfers:
            dmstc_to_acc = _country.sub('', txf['account_number'])
            transfer = {
                'PmtId': {
                    'EndToEndId': _charfilter.sub('',
                            unidecode(txf.get('description', 'not provided').replace(u' ', u'_')))[:32],
                    },
                'Amt': {
                    'InstdAmt': {
                        '_value_1': txf['amount'],
                        'Ccy': txf.get('currency', 'PLN'),
                        },
                    },
                'CdtrAgt': {
                    'FinInstnId': {
                        'ClrSysMmbId': {
                            'MmbId': dmstc_to_acc[2:10],
                            }
                        }
                    },
                'Cdtr': {
                    'Nm': purepolish(txf['account_holder_name']),
                    'PstlAdr': {
                        'AdrLine': cleanaddress(txf.get('account_holder_address', ''))[:35],
                        'Ctry': txf.get('account_holder_country', 'pl').upper(),
                        }
                    },
                'CdtrAcct': {
                    'Id': {
                        'Othr': {
                            'Id': dmstc_to_acc,
                            }
                        }
                    },
                'RmtInf': {
                    'Ustrd': purepolish(txf.get('description', ''))[:140].strip(),
                    }
                }
            to_send.append(transfer)
        data = {
            'GrpHdr': {
                'MsgId': self.get_msg_id(),
                'CreDtTm': now,
                'NbOfTxs': len(transfers),
                'InitgPty': {
                    'Nm': initiator,
                    },
                },
            'PmtInf': {
                'PmtInfId': now.strftime('%Y%m%d%H%M%S'),
                'PmtMtd': 'TRF',
                'ReqdExctnDt': now.date(),
                'Dbtr': {
                    'Nm': self.company,
                    },
                'DbtrAcct': {
                    'Id': {
                        'Othr': {
                            'Id': dmstc_from_acc,
                            }
                        }
                    },
                'DbtrAgt': {
                    'FinInstnId': {
                        'ClrSysMmbId': {
                            'ClrSysId': {
                                'Cd': 'PLKNR',
                                },
                            'MmbId': dmstc_from_acc[2:10],
                            },
                        }
                    },
                'CdtTrfTxInf': to_send,
                }
            }
        document = doctype({'CstmrCdtTrfInitn': data})
        resp = method(document['Document'])
        return [(sts.TxSts, sts.AccptncDtTm) for sts in resp.OrgnlPmtInfAndSts[0].TxInfAndSts]


Transfer = namedtuple('Transfer', ['id',
                                   'type',
                                   'status',
                                   'amount',
                                   'currency',
                                   'posting_date',
                                   'operation_date',
                                   'account_number',
                                   'account_holder_name',
                                   'account_holder_address',
                                   'account_holder_country',
                                   'transaction_name'])


class History(object):
    payments = None
    charges = None

    def __init__(self, report):
        self.payments = []
        self.charges = []
        self.process_transactions(report[0].Ntry)

    def process_transactions(self, txns):
        for txn in txns:
            txndata = {}
            txndata['type'] = txn.CdtDbtInd
            txndata['status'] = txn.Sts
            txndata['posting_date'] = txn.BookgDt.DtTm
            txndata['operation_date'] = txn.ValDt.DtTm
            details = txn.NtryDtls[0].TxDtls[0]
            txndata['id'] = details.Refs.InstrId
            txndata['amount'] = txn.Amt._value_1
            txndata['currency'] = txn.Amt.Ccy
            txndata['transaction_name'] = "\n".join(details.RmtInf.Ustrd)
            creditor = getattr(details.RltdPties, 'CdtrAcct', None) # for charges
            debitor = getattr(details.RltdPties, 'DbtrAcct', None)  # for payments
            if bool(creditor) == bool(debitor):
                raise ValueError("Transfer {id} is both incoming and outgoing".format(**txndata))
            role = creditor or debitor
            txndata['account_number'] = role.Id.Othr.Id
            party_data = details.RltdPties.Cdtr or details.RltdPties.Dbtr
            txndata['account_holder_name'] = party_data.Nm
            if hasattr(party_data, 'PstlAddr'):
                txndata['account_holder_address'] = party_data.PstlAdr.AdrLine
                txndata['account_holder_country'] = party_data.PstlAdr.Ctry
            else:
                txndata['account_holder_address'] = ''
                txndata['account_holder_country'] = ''
            if creditor:
                self.charges.append(Transfer(**txndata))
            else:
                self.payments.append(Transfer(**txndata))
