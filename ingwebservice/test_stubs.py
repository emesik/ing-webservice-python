import logging

_log = logging.getLogger(__name__)

class WSClientStub(object):
    def __init__(self, *args, **kwargs):
        _log.debug(u'WSClientStub({}, {})'.format(
                u', '.join(args),
                u', '.join(u'{}={}'.format(*i) for i in kwargs.items())))

    def transfer_domestic(self, *args, **kwargs):
        return self._transfer('domestic', *args, **kwargs)

    def transfer_sepa(self, *args, **kwargs):
        return self._transfer('SEPA', *args, **kwargs)

    def transfer_swift(self, *args, **kwargs):
        return self._transfer('SWIFT', *args, **kwargs)

    def _transfer(self, mode, from_account, transfers, initiator=''):
        _log.debug(u'{:8s}: {:20s} by {}'.format(mode, from_account, initiator))
        for txfr in transfers:
            _log.debug((u'{end2end_id:_<20s} {account_number:20s} {amount:5.2f} '
                        u'{currency:3s} {account_holder_name:_<10.16s}').format(**txfr))
