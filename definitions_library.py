
class columnsHolder:

    def __init__(self):
        self.possible_column_names = [[
                    'description', 'transaction description', 'details', 'transaction details', 'description',
                    'memo', 'transaction details',
                    'remarks', "narration",
                    'explanation', 'comment', 'note', 'purpose', 'message'], ['amount',
                                                                              'transaction amount', 'currency'],
                    ['account', 'account number', 'account name', 'counterparty'], ['reference',
                                                                                    'transaction reference', 'UTR',
                                                                                    'chq.', 'cheque', 'ref no.', 'ref chq no.'],
                    ['category', 'type'],
                    ['balance', 'opening balance'], [
                        'closing balance', "balance",
                        'running balance', 'available balance'], ["withdrawal", 'debit'],
                    ['deposit',
                     'credit'],
                    ["date", "day", "time", 'transaction date', 'posting date', 'account activity date',
                     'statement date', 'entry date', 'record date', 'event date',
                     'transaction timestamp', 'financial activity date', 'recorded date', 'dt.', 'dt', 'txn dt']
                ]