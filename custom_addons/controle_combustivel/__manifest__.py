{
    'name': 'Controle de Combustível',
    'version': '1.0',
    'summary': 'Gestão de Abastecimentos e Estoque de Tanque',
    'author': 'Seu Nome',
    'category': 'Operations',
    'depends': ['base', 'fleet' , 'purchase'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/combustivel_views.xml',
    ],
    'installable': True,
    'application': True,
}