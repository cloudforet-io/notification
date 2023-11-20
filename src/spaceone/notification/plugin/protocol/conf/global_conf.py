LOG = {
    'filters': {
        'masking': {
            'rules': {
                'Protocol.verify': [
                    'secret_data'
                ],
                'Protocol.dispatch': [
                    'secret_data'
                ]
            }
        }
    }
}