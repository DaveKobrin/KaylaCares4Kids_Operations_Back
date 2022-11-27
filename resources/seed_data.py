role_data = [
        { 'name': 'admin' },
        { 'name': 'guest' },
        { 'name': 'internal' },
        { 'name': 'manage_user' },
        ]

permission_data = [
        { 'permission': 'read:org-data',        'role_id': 1 },
        { 'permission': 'write:org-data',       'role_id': 1 },
        { 'permission': 'read:inventory',       'role_id': 3 },
        { 'permission': 'write:inventory',      'role_id': 3 },
        { 'permission': 'read:users',           'role_id': 4 },
        { 'permission': 'update:users',         'role_id': 4 },
        ]

lookup_data = [
        { 'description': 'Clatter of Jars (Book)',                                      'value': 8.99,          'kids_served': 1 },
        { 'description': 'Castle In The Mist (Book)',                                   'value': 11.99,         'kids_served': 1 },
        { 'description': 'Starlink PS4 game',                                           'value': 41.99,         'kids_served': 1 },
        { 'description': 'Starlink XboxOne game',                                       'value': 44.99,         'kids_served': 1 },
        { 'description': 'Used Books - paperback',                                      'value': 2.00,          'kids_served': 1 },
        { 'description': 'Used Books - hard cover',                                     'value': 3.00,          'kids_served': 1 },
        { 'description': 'Used DVDs',                                                   'value': 5.00,          'kids_served': 1 },
        { 'description': 'New DVDs',                                                    'value': 12.00,         'kids_served': 1 },
        { 'description': 'Used CDs',                                                    'value': 5.00,          'kids_served': 1 },
        { 'description': 'New CDs',                                                     'value': 12.00,         'kids_served': 1 },
        { 'description': 'Used DVD player',                                             'value': 16.00,         'kids_served': 1 },
        { 'description': 'New DVD player',                                              'value': 35.00,         'kids_served': 1 },
        { 'description': 'Crafts',                                                      'value': 1.50,          'kids_served': 1 },
        { 'description': 'NY Giants Rydell Mini Helmets',                               'value': 30.00,         'kids_served': 1 },
        { 'description': 'new craft supplies - scissors, glitter glue, beads, pompoms', 'value': 4.00,          'kids_served': 1 },
        { 'description': 'new toys, games, puzzles',                                    'value': 10.00,         'kids_served': 1 },
        { 'description': 'new stuffed bears',                                           'value': 20.00,         'kids_served': 1 },
        { 'description': 'new coloring/activity books, crayons, markers, paint',        'value': 5.00,          'kids_served': 1 },
        ]

facility_data = [
        { 
                'name': 'My test Faciliy',
                'address1': '1313 Mockingbird Lane',
                'address2': '',
                'city': 'Erie',
                'state': 'IN',
                'country': 'USA',
                'zipcode': '00000',
                'contact_id': '1' 
        }
        ]

destination_data = [
        { 
                'name': 'My test Destination',
                'address1': '1313 Mockingbird Lane',
                'address2': '',
                'city': 'Erie',
                'state': 'IN',
                'country': 'USA',
                'zipcode': '00000',
                'contact_name': 'Some Bloke',
                'contact_email': 'me@here.net',
                'contact_phone': '555-555-5555' 
        }
        ]
